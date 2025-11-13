from model.base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from model.brand_mount import BrandMount
from datetime import datetime

if TYPE_CHECKING:
    from model.camera import Camera
    from model.lens import Lens
    from model.brand import Brand

class Mount(BaseModel, table=True):
    # 卡口基本信息
    name: str = Field(index=True, description="卡口名称")
    
    # 技术参数
    flange_distance: Optional[float] = Field(default=None, description="法兰距(mm)")
    
    # 发布信息
    release_year: Optional[int] = Field(default=None, description="发布年份")
    
    # 状态信息
    is_active: bool = Field(default=True, description="是否在用")
    
    # 描述信息
    description: Optional[str] = Field(default=None, description="备注说明")
    
    # 一对多关系：使用该卡口的相机
    cameras: List["Camera"] = Relationship(back_populates="mount", sa_relationship_kwargs={"lazy": "selectin"})
    
    # 一对多关系：使用该卡口的镜头
    lenses: List["Lens"] = Relationship(back_populates="mount", sa_relationship_kwargs={"lazy": "selectin"})
    
    # 多对多关系：支持该卡口的品牌
    brands: List["Brand"] = Relationship(back_populates="mounts", link_model=BrandMount, sa_relationship_kwargs={"lazy": "selectin"})

    class Config:
        from_attributes = True
        
    def __str__(self):
        brand_names = ", ".join([brand.name for brand in self.brands]) if self.brands else "未知品牌"
        return f"{self.name} ({brand_names})"


# 卡口数据模型类
class MountCreate(BaseModel):
    """卡口创建数据模型"""
    name: str
    flange_distance: Optional[float] = None
    release_year: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


class MountUpdate(BaseModel):
    """卡口更新数据模型"""
    name: Optional[str] = None
    flange_distance: Optional[float] = None
    release_year: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class MountResponse(BaseModel):
    """卡口响应数据模型"""
    name: str
    flange_distance: Optional[float] = None
    release_year: Optional[int] = None
    is_active: bool = True
    description: Optional[str] = None


class MountQuery(BaseModel):
    """卡口查询参数模型"""
    skip: int = 0
    limit: int = 100
    is_active: Optional[bool] = None


class BrandMountCreate(BaseModel):
    """品牌卡口关联创建模型"""
    brand_id: int
    mount_id: int
    is_primary: bool = False
    compatibility_notes: str = ""


class BrandMountResponse(BaseModel):
    """品牌卡口关联响应模型"""
    brand_id: int
    mount_id: int
    is_primary: bool
    compatibility_notes: str