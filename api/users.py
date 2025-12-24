from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from database.engine import get_session
from model.user import User, UserCreate, UserUpdate, UserResponse, UserRole
from api.auth import get_current_user, get_current_admin_user
from services.user_service import UserService

router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_user(
    user_create: UserCreate, 
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """创建新用户（需要管理员权限）"""
    user = UserService.create_user(session, user_create)
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
    users = UserService.get_users(session, skip, limit, username, email, role, is_active)
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """获取单个用户信息（需要登录权限）"""
    user = UserService.get_user_by_id(session, user_id)
    return UserResponse.model_validate(user)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """更新用户信息（需要管理员权限）"""
    updated_user = UserService.update_user(session, user_id, user_update)
    return UserResponse.model_validate(updated_user)

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """删除用户（需要管理员权限）"""
    user = UserService.get_user_by_id(session, user_id)
    UserService.delete_user(session, user)
    return {"message": "User deleted successfully"}

@router.patch("/users/{user_id}/activate", response_model=UserResponse)
def activate_user(user_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """激活用户（需要管理员权限）"""
    user = UserService.get_user_by_id(session, user_id)
    activated_user = UserService.set_user_active_status(session, user, True)
    return UserResponse.model_validate(activated_user)

@router.patch("/users/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """停用用户（需要管理员权限）"""
    user = UserService.get_user_by_id(session, user_id)
    deactivated_user = UserService.set_user_active_status(session, user, False)
    return UserResponse.model_validate(deactivated_user)

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
    updated_user = UserService.update_user(session, current_user, user_update)
    return UserResponse.model_validate(updated_user)