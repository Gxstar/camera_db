from model.base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from model.camera import Camera
    from model.lens import Lens

class Brand(BaseModel, table=True):
    """品牌模型，用于存储相机和镜头厂商信息"""
    # 品牌名称（唯一，建立索引）
    name: str = Field(index=True, unique=True, description="品牌名称")
    # 品牌描述（可选）
    description: Optional[str] = Field(default=None, description="品牌描述")
    # 官方网站（可选）
    website: Optional[str] = Field(default=None, description="官方网站")
    # 国家/地区（可选）
    country: Optional[str] = Field(default=None, description="国家/地区")
    # 是否活跃
    is_active: bool = Field(default=True, description="是否活跃")
    # 品牌类型（相机、镜头、配件等）
    brand_type: str = Field(default="camera", description="品牌类型: camera, lens, accessory")
    # 与Camera的反向关系
    cameras: List["Camera"] = Relationship(back_populates="brand", sa_relationship_kwargs={"lazy": "selectin"})
    # 与Lens的反向关系
    lenses: List["Lens"] = Relationship(back_populates="brand", sa_relationship_kwargs={"lazy": "selectin"})
    
    class Config:
        orm_mode = True
        
    def __str__(self):
        return f"{self.name} ({self.country})" if self.country else self.name