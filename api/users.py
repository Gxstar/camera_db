from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from database.engine import get_session
from model.user import User, UserCreate, UserUpdate, UserResponse, UserQuery, UserRole
from api.auth import get_current_user, get_current_admin_user, get_password_hash

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_user(
    user_create: UserCreate, 
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """创建新用户（需要管理员权限）"""
    # 检查用户名是否已存在
    existing_user = session.exec(select(User).where(User.username == user_create.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    if user_create.email:
        existing_email = session.exec(select(User).where(User.email == user_create.email)).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 创建数据库用户对象
    user = User(
        username=user_create.username,
        email=user_create.email,
        hash_password=get_password_hash(user_create.password),
        role=user_create.role,
        is_active=True
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # 返回响应模型（不包含密码哈希）
    return UserResponse.model_validate(user)

@router.get("/users/", response_model=List[UserResponse])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    username: Optional[str] = Query(None, description="按用户名筛选"),
    email: Optional[str] = Query(None, description="按邮箱筛选"),
    role: Optional[UserRole] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按激活状态筛选"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取用户列表（支持筛选，需要登录权限）"""
    query = select(User)
    
    # 应用筛选条件
    if username:
        query = query.where(User.username.contains(username))
    if email:
        query = query.where(User.email.contains(email))
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    users = session.exec(query.offset(skip).limit(limit)).all()
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """获取单个用户信息（需要登录权限）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """更新用户信息（需要管理员权限）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查用户名是否冲突（如果更新用户名）
    if user_update.username and user_update.username != user.username:
        existing_user = session.exec(select(User).where(User.username == user_update.username)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # 检查邮箱是否冲突（如果更新邮箱）
    if user_update.email and user_update.email != user.email:
        existing_email = session.exec(select(User).where(User.email == user_update.email)).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    
    # 如果更新密码，需要重新加密
    if "password" in update_data:
        update_data["hash_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse.model_validate(user)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """删除用户（需要管理员权限）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}

@router.patch("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(user_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """激活用户（需要管理员权限）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse.model_validate(user)

@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """停用用户（需要管理员权限）"""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse.model_validate(user)

@router.get("/users/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return UserResponse.model_validate(current_user)

@router.put("/users/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """更新当前登录用户信息"""
    # 检查用户名是否冲突（如果更新用户名）
    if user_update.username and user_update.username != current_user.username:
        existing_user = session.exec(select(User).where(User.username == user_update.username)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # 检查邮箱是否冲突（如果更新邮箱）
    if user_update.email and user_update.email != current_user.email:
        existing_email = session.exec(select(User).where(User.email == user_update.email)).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    
    # 如果更新密码，需要重新加密
    if "password" in update_data:
        update_data["hash_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return UserResponse.model_validate(current_user)