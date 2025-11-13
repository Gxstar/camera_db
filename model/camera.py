from model.base import BaseModel
from sqlmodel import Field, Relationship
from typing import Optional, TYPE_CHECKING
from enum import Enum
from datetime import datetime

if TYPE_CHECKING:
    from model.brand import Brand
    from model.mount import Mount

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
    brand_id: int = Field(foreign_key="brand.id", description="品牌外键")
    brand: "Brand" = Relationship(back_populates="cameras", sa_relationship_kwargs={"lazy": "joined"})
    
    # 卡口
    mount_id: int = Field(foreign_key="mount.id", description="卡口外键")
    mount: "Mount" = Relationship(back_populates="cameras", sa_relationship_kwargs={"lazy": "joined"})
    
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
        from_attributes = True


class CameraCreate(BaseModel):
    """相机创建数据模型"""
    brand_id: int
    mount_id: int
    sensor_size: Optional[SensorSize] = None
    series: Optional[str] = None
    model: str
    megapixels: Optional[float] = None
    ibis_level: Optional[str] = None
    has_hot_shoe: bool = True
    has_built_in_flash: bool = False
    has_wifi: bool = True
    has_bluetooth: bool = True
    release_date: Optional[str] = None
    release_price: Optional[float] = None
    weight: Optional[float] = None
    description: Optional[str] = None


class CameraUpdate(BaseModel):
    """相机更新数据模型"""
    brand_id: Optional[int] = None
    mount_id: Optional[int] = None
    sensor_size: Optional[SensorSize] = None
    series: Optional[str] = None
    model: Optional[str] = None
    megapixels: Optional[float] = None
    ibis_level: Optional[str] = None
    has_hot_shoe: Optional[bool] = None
    has_built_in_flash: Optional[bool] = None
    has_wifi: Optional[bool] = None
    has_bluetooth: Optional[bool] = None
    release_date: Optional[str] = None
    release_price: Optional[float] = None
    weight: Optional[float] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class CameraResponse(BaseModel):
    """相机响应数据模型"""
    brand_id: int
    mount_id: int
    sensor_size: Optional[SensorSize] = None
    series: Optional[str] = None
    model: str
    megapixels: Optional[float] = None
    ibis_level: Optional[str] = None
    has_hot_shoe: bool = True
    has_built_in_flash: bool = False
    has_wifi: bool = True
    has_bluetooth: bool = True
    release_date: Optional[str] = None
    release_price: Optional[float] = None
    weight: Optional[float] = None
    is_active: bool = True
    description: Optional[str] = None


class CameraQuery(BaseModel):
    """相机查询数据模型"""
    skip: int = 0
    limit: int = 100
    is_active: Optional[bool] = None
    brand_id: Optional[int] = None
    mount_id: Optional[int] = None
    sensor_size: Optional[SensorSize] = None