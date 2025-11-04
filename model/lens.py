from model.base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from model.brand import Brand
    from model.mount import Mount

class LensType(str, Enum):
    """镜头类型枚举"""
    ZOOM = "zoom"      # 变焦镜头
    PRIME = "prime"     # 定焦镜头

class FocusType(str, Enum):
    """对焦方式枚举"""
    AUTO = "auto"      # 自动对焦
    MANUAL = "manual"   # 手动对焦

class Lens(BaseModel, table=True):
    # 品牌关联
    brand_id: int = Field(foreign_key="brand.id", description="品牌外键")
    brand: "Brand" = Relationship(back_populates="lenses", sa_relationship_kwargs={"lazy": "joined"})
    
    # 卡口关联
    mount_id: int = Field(foreign_key="mount.id", description="卡口外键")
    mount: "Mount" = Relationship(back_populates="lenses", sa_relationship_kwargs={"lazy": "joined"})
    
    # 型号信息
    model: str = Field(index=True, description="镜头型号")
    
    # 系列
    series: Optional[str] = Field(default=None, description="镜头系列")
    
    # 焦距范围
    min_focal_length: float = Field(description="最小焦距(mm)")
    max_focal_length: float = Field(description="最大焦距(mm)")
    
    # 镜头类型（根据焦距自动判断）
    lens_type: LensType = Field(description="镜头类型: 变焦或定焦")
    
    # 光圈范围
    max_aperture_min: float = Field(description="最大光圈（最小焦距端）")
    max_aperture_max: Optional[float] = Field(default=None, description="最大光圈（最大焦距端）")
    
    # 是否恒定光圈
    is_constant_aperture: bool = Field(default=False, description="是否恒定最大光圈")
    
    # 物理属性
    weight: Optional[float] = Field(default=None, description="重量(克)")
    height: Optional[float] = Field(default=None, description="高度(mm)")
    diameter: Optional[float] = Field(default=None, description="直径(mm)")
    filter_size: Optional[float] = Field(default=None, description="滤镜口径(mm)")
    
    # 对焦方式
    focus_type: FocusType = Field(default=FocusType.AUTO, description="对焦方式")
    
    # 防抖功能
    has_stabilization: bool = Field(default=False, description="是否支持防抖")
    
    # 光学性能
    min_focus_distance: Optional[float] = Field(default=None, description="最近对焦距离(m)")
    magnification: Optional[float] = Field(default=None, description="放大倍率")
    
    # 发布信息
    release_date: Optional[str] = Field(default=None, description="发布日期")
    release_price: Optional[float] = Field(default=None, description="发布价格(元)")
    
    # 状态信息
    is_active: bool = Field(default=True, description="是否在用")
    
    # 描述信息
    description: Optional[str] = Field(default=None, description="备注说明")

    class Config:
        from_attributes = True
        
    def __init__(self, **kwargs):
        # 自动判断镜头类型
        if 'min_focal_length' in kwargs and 'max_focal_length' in kwargs:
            if kwargs['min_focal_length'] == kwargs['max_focal_length']:
                kwargs['lens_type'] = LensType.PRIME
            else:
                kwargs['lens_type'] = LensType.ZOOM
                
        # 自动判断是否恒定光圈
        if 'max_aperture_min' in kwargs and 'max_aperture_max' in kwargs:
            if kwargs['max_aperture_min'] == kwargs['max_aperture_max']:
                kwargs['is_constant_aperture'] = True
            else:
                kwargs['is_constant_aperture'] = False
                
        super().__init__(**kwargs)
        
    def __str__(self):
        focal_range = f"{self.min_focal_length}mm" if self.lens_type == LensType.PRIME else f"{self.min_focal_length}-{self.max_focal_length}mm"
        aperture = f"f/{self.max_aperture_min}" if self.is_constant_aperture else f"f/{self.max_aperture_min}-{self.max_aperture_max}"
        return f"{self.brand.name if self.brand else '未知品牌'} {self.model} {focal_range} {aperture}"