from model.base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from model.brand_mount import BrandMount

if TYPE_CHECKING:
    from model.camera import Camera
    from model.lens import Lens
    from model.mount import Mount

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
    # 一对多关系：品牌拥有的相机
    cameras: List["Camera"] = Relationship(back_populates="brand", sa_relationship_kwargs={"lazy": "selectin"})
    
    # 一对多关系：品牌拥有的镜头
    lenses: List["Lens"] = Relationship(back_populates="brand", sa_relationship_kwargs={"lazy": "selectin"})
    
    # 多对多关系：品牌支持的卡口
    mounts: List["Mount"] = Relationship(back_populates="brands", link_model=BrandMount, sa_relationship_kwargs={"lazy": "selectin"})
    
    class Config:
        from_attributes = True
        
    def __str__(self):
        return f"{self.name} ({self.country})" if self.country else self.name


class BrandCreate(BaseModel):
    """创建品牌时的数据模型"""
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    brand_type: str = "camera"
    is_active: bool = True


class BrandUpdate(BaseModel):
    """更新品牌时的数据模型"""
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None
    brand_type: Optional[str] = None
    is_active: Optional[bool] = None


class BrandResponse(BaseModel):
    """品牌响应数据模型"""
    id: int
    name: str
    description: Optional[str]
    website: Optional[str]
    country: Optional[str]
    brand_type: str
    is_active: bool
    create_time: str
    update_time: str


class BrandQuery(BaseModel):
    """品牌查询参数模型"""
    skip: int = 0
    limit: int = 100
    is_active: Optional[bool] = None
    brand_type: Optional[str] = None