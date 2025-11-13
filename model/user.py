from model.base import BaseModel
from sqlmodel import Field
from typing import Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    """用户角色枚举（简化权限体系）"""
    USER = "user"          # 普通用户 - 基础权限
    ADMIN = "admin"        # 管理员 - 完全权限

# 数据库表模型
class User(BaseModel, table=True):
    """用户数据库表模型"""
    username: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, index=True)
    hash_password: str
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)
    
    class Config:
        from_attributes = True

# 用户创建模型（API输入）
class UserCreate(BaseModel):
    """用户创建模型 - 用于API输入"""
    username: str
    email: Optional[str] = None
    password: str  # 明文密码，将在API层加密
    role: UserRole = UserRole.USER

# 用户更新模型（API输入）
class UserUpdate(BaseModel):
    """用户更新模型 - 用于API输入"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None  # 可选更新密码
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

# 用户响应模型（API输出）
class UserResponse(BaseModel):
    """用户响应模型 - 用于API输出，不包含敏感信息"""
    username: str
    email: Optional[str]
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True

# 用户查询模型（API查询参数）
class UserQuery(BaseModel):
    """用户查询模型 - 用于API查询参数"""
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

