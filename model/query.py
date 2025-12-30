from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class FilterOperator(str, Enum):
    """过滤操作符"""
    EQ = "eq"          # 等于
    NE = "ne"          # 不等于
    GT = "gt"          # 大于
    GTE = "gte"        # 大于等于
    LT = "lt"          # 小于
    LTE = "lte"        # 小于等于
    IN = "in"          # 在列表中
    NOT_IN = "not_in"  # 不在列表中
    LIKE = "like"      # 模糊匹配
    ILIKE = "ilike"    # 不区分大小写模糊匹配
    IS_NULL = "is_null"    # 为空
    IS_NOT_NULL = "is_not_null"  # 不为空


class SortOrder(str, Enum):
    """排序方向"""
    ASC = "asc"    # 升序
    DESC = "desc"  # 降序


class FilterCondition(BaseModel):
    """单个过滤条件"""
    field: str = Field(..., description="字段名")
    operator: FilterOperator = Field(FilterOperator.EQ, description="操作符")
    value: Optional[Union[str, int, float, bool, List]] = Field(None, description="值")


class SortCondition(BaseModel):
    """排序条件"""
    field: str = Field(..., description="字段名")
    order: SortOrder = Field(SortOrder.ASC, description="排序方向")


class BaseQueryParams(BaseModel):
    """通用查询参数基类"""
    # 分页参数
    skip: int = Field(0, ge=0, description="跳过的记录数")
    limit: int = Field(100, ge=1, le=1000, description="返回记录数")
    
    # 排序参数
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: SortOrder = Field(SortOrder.ASC, description="排序方向")
    
    # 搜索参数
    search: Optional[str] = Field(None, description="全文搜索关键词")
    search_fields: Optional[List[str]] = Field(None, description="搜索字段列表")
    
    # 过滤条件
    filters: Optional[List[FilterCondition]] = Field(None, description="过滤条件列表")
    
    # 是否只返回活跃记录
    is_active: Optional[bool] = Field(None, description="是否只返回活跃记录")


class CameraQueryParams(BaseQueryParams):
    """相机查询参数"""
    # 品牌ID
    brand_id: Optional[int] = Field(None, description="品牌ID")
    brand_ids: Optional[List[int]] = Field(None, description="品牌ID列表")
    
    # 卡口ID
    mount_id: Optional[int] = Field(None, description="卡口ID")
    mount_ids: Optional[List[int]] = Field(None, description="卡口ID列表")
    
    # 传感器尺寸
    sensor_size: Optional[str] = Field(None, description="传感器尺寸")
    sensor_sizes: Optional[List[str]] = Field(None, description="传感器尺寸列表")
    
    # 像素范围
    megapixels_min: Optional[float] = Field(None, ge=0, description="最小像素")
    megapixels_max: Optional[float] = Field(None, ge=0, description="最大像素")
    
    # 价格范围
    price_min: Optional[float] = Field(None, ge=0, description="最低价格")
    price_max: Optional[float] = Field(None, ge=0, description="最高价格")
    
    # 重量范围
    weight_min: Optional[float] = Field(None, ge=0, description="最轻重量")
    weight_max: Optional[float] = Field(None, ge=0, description="最重重量")
    
    # 功能特性
    has_wifi: Optional[bool] = Field(None, description="是否有WiFi")
    has_bluetooth: Optional[bool] = Field(None, description="是否有蓝牙")
    has_hot_shoe: Optional[bool] = Field(None, description="是否有热靴")
    has_built_in_flash: Optional[bool] = Field(None, description="是否有内置闪光灯")
    
    # 发布年份
    release_year_min: Optional[int] = Field(None, ge=2000, description="最早发布年份")
    release_year_max: Optional[int] = Field(None, ge=2000, description="最晚发布年份")
    
    # 系列和型号
    series: Optional[str] = Field(None, description="产品系列")
    model: Optional[str] = Field(None, description="型号关键词")


class LensQueryParams(BaseQueryParams):
    """镜头查询参数"""
    # 品牌ID
    brand_id: Optional[int] = Field(None, description="品牌ID")
    brand_ids: Optional[List[int]] = Field(None, description="品牌ID列表")
    
    # 卡口ID
    mount_id: Optional[int] = Field(None, description="卡口ID")
    mount_ids: Optional[List[int]] = Field(None, description="卡口ID列表")
    
    # 镜头类型
    lens_type: Optional[str] = Field(None, description="镜头类型")
    lens_types: Optional[List[str]] = Field(None, description="镜头类型列表")
    
    # 对焦方式
    focus_type: Optional[str] = Field(None, description="对焦方式")
    focus_types: Optional[List[str]] = Field(None, description="对焦方式列表")
    
    # 焦距范围
    focal_length_min: Optional[float] = Field(None, ge=0, description="最短焦距")
    focal_length_max: Optional[float] = Field(None, ge=0, description="最长焦距")
    
    # 光圈范围
    aperture_min: Optional[float] = Field(None, ge=1, description="最大光圈最小值")
    aperture_max: Optional[float] = Field(None, ge=1, description="最大光圈最大值")
    
    # 价格范围
    price_min: Optional[float] = Field(None, ge=0, description="最低价格")
    price_max: Optional[float] = Field(None, ge=0, description="最高价格")
    
    # 重量范围
    weight_min: Optional[float] = Field(None, ge=0, description="最轻重量")
    weight_max: Optional[float] = Field(None, ge=0, description="最重重量")
    
    # 功能特性
    has_stabilization: Optional[bool] = Field(None, description="是否有防抖")
    is_constant_aperture: Optional[bool] = Field(None, description="是否恒定光圈")
    
    # 滤镜口径
    filter_size_min: Optional[float] = Field(None, ge=0, description="最小滤镜口径")
    filter_size_max: Optional[float] = Field(None, ge=0, description="最大滤镜口径")
    
    # 发布年份
    release_year_min: Optional[int] = Field(None, ge=2000, description="最早发布年份")
    release_year_max: Optional[int] = Field(None, ge=2000, description="最晚发布年份")
    
    # 系列和型号
    series: Optional[str] = Field(None, description="镜头系列")
    model: Optional[str] = Field(None, description="型号关键词")


class QueryResponse(BaseModel):
    """查询响应模型"""
    data: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int
    has_more: bool