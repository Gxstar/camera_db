from model.base import BaseModel
from sqlmodel import Field
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"          # 普通用户
    ADMIN = "admin"        # 管理员
    EDITOR = "editor"      # 编辑者
    VIEWER = "viewer"      # 查看者

class User(BaseModel, table=True):
    username: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, index=True)
    hash_password: str
    is_active: bool = Field(default=True)
    role: UserRole = Field(default=UserRole.USER)
    
    class Config:
        orm_mode = True

