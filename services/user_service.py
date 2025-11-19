from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status
from passlib.context import CryptContext

from model.user import User, UserCreate, UserUpdate, UserResponse, UserRole

# 使用argon2算法（现代、安全、无长度限制）
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """使用argon2算法加密密码"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(password, hashed_password)


class UserService:
    """用户服务类，封装用户相关的CRUD操作"""
    
    @staticmethod
    def create_user(session: Session, user_create: UserCreate) -> User:
        """创建新用户"""
        # 检查用户名是否已存在
        existing_user = session.exec(select(User).where(User.username == user_create.username)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在（如果提供了邮箱）
        if user_create.email:
            existing_email = session.exec(select(User).where(User.email == user_create.email)).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        # 创建用户对象并哈希密码
        user = User(
            username=user_create.username,
            email=user_create.email,
            hash_password=hash_password(user_create.password),
            role=user_create.role
        )
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_users(
        session: Session, 
        skip: int = 0, 
        limit: int = 100,
        username: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """获取用户列表（支持筛选）"""
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
        
        return session.exec(query.offset(skip).limit(limit)).all()
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> User:
        """根据ID获取用户"""
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    
    @staticmethod
    def update_user(session: Session, user: User, user_update: UserUpdate) -> User:
        """更新用户信息"""
        # 检查用户名是否冲突（如果更新用户名）
        if user_update.username and user_update.username != user.username:
            existing_user = session.exec(select(User).where(User.username == user_update.username)).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在"
                )
        
        # 检查邮箱是否冲突（如果更新邮箱）
        if user_update.email and user_update.email != user.email:
            existing_email = session.exec(select(User).where(User.email == user_update.email)).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
        
        # 如果更新密码，需要重新加密
        if "password" in update_data:
            update_data["hash_password"] = hash_password(update_data.pop("password"))
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def delete_user(session: Session, user: User) -> None:
        """删除用户"""
        session.delete(user)
        session.commit()
    
    @staticmethod
    def set_user_active_status(session: Session, user: User, is_active: bool) -> User:
        """设置用户激活状态"""
        user.is_active = is_active
        session.add(user)
        session.commit()
        session.refresh(user)
        return user