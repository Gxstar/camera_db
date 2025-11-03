from model.base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from model.brand import Brand

class SensorSize(str, Enum):
    """传感器尺寸枚举"""
    MEDIUM_FORMAT = "medium_format"  # 中画幅
    FULL_FRAME = "full_frame"        # 全画幅
    APS_C = "aps_c"                  # 半画幅
    M43 = "m43"                      # M43
    ONE_INCH = "one_inch"            # 一英寸
    OTHER = "other"                  # 其他

class Camera(BaseModel, table=True):
    # 品牌关联
    brand_id: Optional[int] = Field(default=None, foreign_key="brand.id", nullable=True)
    brand: Optional["Brand"] = Relationship(back_populates="cameras", sa_relationship_kwargs={"lazy": "joined"})
    
    # 传感器尺寸
    sensor_size: Optional[SensorSize] = Field(default=None, description="传感器尺寸")
    
    # 系列信息
    series: Optional[str] = Field(default=None, description="产品系列")
    
    # 型号信息
    model: str = Field(index=True, description="具体型号")
    
    # 像素
    megapixels: Optional[float] = Field(default=None, description="有效像素(百万)")
    
    # 机身防抖级别
    ibis_level: Optional[str] = Field(default=None, description="机身防抖级别")
    
    # 卡口
    mount_type: Optional[str] = Field(default=None, description="卡口类型")
    
    # 热靴
    has_hot_shoe: bool = Field(default=True, description="是否有热靴")
    
    # 内置闪光灯
    has_built_in_flash: bool = Field(default=False, description="是否有内置闪光灯")
    
    # WiFi功能
    has_wifi: bool = Field(default=True, description="是否有WiFi")
    
    # 蓝牙功能
    has_bluetooth: bool = Field(default=True, description="是否有蓝牙")
    
    # 发布日期
    release_date: Optional[str] = Field(default=None, description="发布日期")
    
    # 发布价格
    release_price: Optional[float] = Field(default=None, description="发布价格(元)")
    
    # 重量
    weight: Optional[float] = Field(default=None, description="重量(克)")
    
    # 状态信息
    is_active: bool = Field(default=True, description="是否在用")
    
    # 描述信息
    description: Optional[str] = Field(default=None, description="备注说明")

    class Config:
        orm_mode = True