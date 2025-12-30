from typing import Type, List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from sqlmodel import Session, select, func, SQLModel
from sqlalchemy import and_, or_, asc, desc, text

from model.query import BaseQueryParams, FilterCondition, FilterOperator, SortOrder, QueryResponse


class QueryService(ABC):
    """通用查询服务基类"""
    
    def __init__(self, model_class: Type[SQLModel]):
        self.model_class = model_class
    
    def build_query(self, session: Session, params: BaseQueryParams):
        """构建查询"""
        # 基础查询
        query = select(self.model_class)
        
        # 构建过滤条件
        query = self._apply_filters(query, params)
        
        # 应用搜索
        if params.search:
            query = self._apply_search(query, params)
        
        # 应用排序
        if params.sort_by:
            query = self._apply_sorting(query, params)
        
        return query
    
    def _apply_filters(self, query, params: BaseQueryParams):
        """应用过滤条件"""
        conditions = []
        
        # 应用通用过滤条件
        if params.is_active is not None and hasattr(self.model_class, 'is_active'):
            conditions.append(self.model_class.is_active == params.is_active)
        
        # 应用自定义过滤条件
        if params.filters:
            for filter_cond in params.filters:
                condition = self._build_filter_condition(filter_cond)
                if condition is not None:
                    conditions.append(condition)
        
        # 应用模型特定的过滤条件
        model_conditions = self._build_model_specific_conditions(params)
        conditions.extend(model_conditions)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        return query
    
    def _build_filter_condition(self, filter_cond: FilterCondition):
        """构建单个过滤条件"""
        if not hasattr(self.model_class, filter_cond.field):
            return None
        
        field = getattr(self.model_class, filter_cond.field)
        operator = filter_cond.operator
        value = filter_cond.value
        
        if operator == FilterOperator.EQ:
            return field == value
        elif operator == FilterOperator.NE:
            return field != value
        elif operator == FilterOperator.GT:
            return field > value
        elif operator == FilterOperator.GTE:
            return field >= value
        elif operator == FilterOperator.LT:
            return field < value
        elif operator == FilterOperator.LTE:
            return field <= value
        elif operator == FilterOperator.IN:
            return field.in_(value) if isinstance(value, list) else field.in_([value])
        elif operator == FilterOperator.NOT_IN:
            return field.notin_(value) if isinstance(value, list) else field.notin_([value])
        elif operator == FilterOperator.LIKE:
            return field.like(f"%{value}%")
        elif operator == FilterOperator.ILIKE:
            return field.ilike(f"%{value}%")
        elif operator == FilterOperator.IS_NULL:
            return field.is_(None)
        elif operator == FilterOperator.IS_NOT_NULL:
            return field.isnot(None)
        
        return None
    
    def _apply_search(self, query, params: BaseQueryParams):
        """应用搜索条件"""
        if not params.search:
            return query
        
        search_fields = params.search_fields or self._get_default_search_fields()
        search_conditions = []
        
        for field_name in search_fields:
            if hasattr(self.model_class, field_name):
                field = getattr(self.model_class, field_name)
                search_conditions.append(field.ilike(f"%{params.search}%"))
        
        if search_conditions:
            query = query.where(or_(*search_conditions))
        
        return query
    
    def _apply_sorting(self, query, params: BaseQueryParams):
        """应用排序"""
        if not params.sort_by or not hasattr(self.model_class, params.sort_by):
            return query
        
        field = getattr(self.model_class, params.sort_by)
        
        if params.sort_order == SortOrder.ASC:
            query = query.order_by(asc(field))
        else:
            query = query.order_by(desc(field))
        
        return query
    
    @abstractmethod
    def _build_model_specific_conditions(self, params: BaseQueryParams) -> List:
        """构建模型特定的过滤条件"""
        pass
    
    @abstractmethod
    def _get_default_search_fields(self) -> List[str]:
        """获取默认搜索字段"""
        pass
    
    def query_with_pagination(self, session: Session, params: BaseQueryParams) -> QueryResponse:
        """执行分页查询"""
        # 构建查询
        query = self.build_query(session, params)
        
        # 获取总数
        count_query = select(func.count(self.model_class.id))
        count_query = self._apply_filters(count_query, params)
        if params.search:
            count_query = self._apply_search(count_query, params)
        
        total = session.scalar(count_query)
        
        # 应用分页
        query = query.offset(params.skip).limit(params.limit)
        
        # 执行查询
        items = session.exec(query).all()
        
        # 转换为字典
        data = []
        for item in items:
            item_dict = item.model_dump()
            # 添加关联数据
            if hasattr(item, 'brand') and item.brand:
                item_dict['brand_name'] = item.brand.name
            if hasattr(item, 'mount') and item.mount:
                item_dict['mount_name'] = item.mount.name
            data.append(item_dict)
        
        # 计算是否有更多数据
        has_more = (params.skip + params.limit) < total
        
        return QueryResponse(
            data=data,
            total=total,
            skip=params.skip,
            limit=params.limit,
            has_more=has_more
        )


class CameraQueryService(QueryService):
    """相机查询服务"""
    
    def __init__(self):
        from model.camera import Camera
        super().__init__(Camera)
    
    def _build_model_specific_conditions(self, params) -> List:
        """构建相机特定的过滤条件"""
        conditions = []
        
        # 品牌过滤
        if hasattr(params, 'brand_id') and params.brand_id is not None:
            conditions.append(self.model_class.brand_id == params.brand_id)
        
        if hasattr(params, 'brand_ids') and params.brand_ids:
            conditions.append(self.model_class.brand_id.in_(params.brand_ids))
        
        # 卡口过滤
        if hasattr(params, 'mount_id') and params.mount_id is not None:
            conditions.append(self.model_class.mount_id == params.mount_id)
        
        if hasattr(params, 'mount_ids') and params.mount_ids:
            conditions.append(self.model_class.mount_id.in_(params.mount_ids))
        
        # 传感器尺寸过滤
        if hasattr(params, 'sensor_size') and params.sensor_size is not None:
            conditions.append(self.model_class.sensor_size == params.sensor_size)
        
        if hasattr(params, 'sensor_sizes') and params.sensor_sizes:
            conditions.append(self.model_class.sensor_size.in_(params.sensor_sizes))
        
        # 像素范围过滤
        if hasattr(params, 'megapixels_min') and params.megapixels_min is not None:
            conditions.append(self.model_class.megapixels >= params.megapixels_min)
        
        if hasattr(params, 'megapixels_max') and params.megapixels_max is not None:
            conditions.append(self.model_class.megapixels <= params.megapixels_max)
        
        # 价格范围过滤
        if hasattr(params, 'price_min') and params.price_min is not None:
            conditions.append(self.model_class.release_price >= params.price_min)
        
        if hasattr(params, 'price_max') and params.price_max is not None:
            conditions.append(self.model_class.release_price <= params.price_max)
        
        # 重量范围过滤
        if hasattr(params, 'weight_min') and params.weight_min is not None:
            conditions.append(self.model_class.weight >= params.weight_min)
        
        if hasattr(params, 'weight_max') and params.weight_max is not None:
            conditions.append(self.model_class.weight <= params.weight_max)
        
        # 功能特性过滤
        if hasattr(params, 'has_wifi') and params.has_wifi is not None:
            conditions.append(self.model_class.has_wifi == params.has_wifi)
        
        if hasattr(params, 'has_bluetooth') and params.has_bluetooth is not None:
            conditions.append(self.model_class.has_bluetooth == params.has_bluetooth)
        
        if hasattr(params, 'has_hot_shoe') and params.has_hot_shoe is not None:
            conditions.append(self.model_class.has_hot_shoe == params.has_hot_shoe)
        
        if hasattr(params, 'has_built_in_flash') and params.has_built_in_flash is not None:
            conditions.append(self.model_class.has_built_in_flash == params.has_built_in_flash)
        
        # 发布年份过滤
        if hasattr(params, 'release_year_min') and params.release_year_min is not None:
            conditions.append(func.extract('year', self.model_class.release_date) >= params.release_year_min)
        
        if hasattr(params, 'release_year_max') and params.release_year_max is not None:
            conditions.append(func.extract('year', self.model_class.release_date) <= params.release_year_max)
        
        # 系列和型号过滤
        if hasattr(params, 'series') and params.series:
            conditions.append(self.model_class.series.ilike(f"%{params.series}%"))
        
        if hasattr(params, 'model') and params.model:
            conditions.append(self.model_class.model.ilike(f"%{params.model}%"))
        
        return conditions
    
    def _get_default_search_fields(self) -> List[str]:
        """获取相机默认搜索字段"""
        return ['model', 'series', 'description']


class LensQueryService(QueryService):
    """镜头查询服务"""
    
    def __init__(self):
        from model.lens import Lens
        super().__init__(Lens)
    
    def _build_model_specific_conditions(self, params) -> List:
        """构建镜头特定的过滤条件"""
        conditions = []
        
        # 品牌过滤
        if hasattr(params, 'brand_id') and params.brand_id is not None:
            conditions.append(self.model_class.brand_id == params.brand_id)
        
        if hasattr(params, 'brand_ids') and params.brand_ids:
            conditions.append(self.model_class.brand_id.in_(params.brand_ids))
        
        # 卡口过滤
        if hasattr(params, 'mount_id') and params.mount_id is not None:
            conditions.append(self.model_class.mount_id == params.mount_id)
        
        if hasattr(params, 'mount_ids') and params.mount_ids:
            conditions.append(self.model_class.mount_id.in_(params.mount_ids))
        
        # 镜头类型过滤
        if hasattr(params, 'lens_type') and params.lens_type is not None:
            conditions.append(self.model_class.lens_type == params.lens_type)
        
        if hasattr(params, 'lens_types') and params.lens_types:
            conditions.append(self.model_class.lens_type.in_(params.lens_types))
        
        # 对焦方式过滤
        if hasattr(params, 'focus_type') and params.focus_type is not None:
            conditions.append(self.model_class.focus_type == params.focus_type)
        
        if hasattr(params, 'focus_types') and params.focus_types:
            conditions.append(self.model_class.focus_type.in_(params.focus_types))
        
        # 焦距范围过滤
        if hasattr(params, 'focal_length_min') and params.focal_length_min is not None:
            conditions.append(self.model_class.min_focal_length >= params.focal_length_min)
        
        if hasattr(params, 'focal_length_max') and params.focal_length_max is not None:
            conditions.append(self.model_class.max_focal_length <= params.focal_length_max)
        
        # 光圈范围过滤
        if hasattr(params, 'aperture_min') and params.aperture_min is not None:
            conditions.append(self.model_class.max_aperture_min >= params.aperture_min)
        
        if hasattr(params, 'aperture_max') and params.aperture_max is not None:
            conditions.append(self.model_class.max_aperture_min <= params.aperture_max)
        
        # 价格范围过滤
        if hasattr(params, 'price_min') and params.price_min is not None:
            conditions.append(self.model_class.release_price >= params.price_min)
        
        if hasattr(params, 'price_max') and params.price_max is not None:
            conditions.append(self.model_class.release_price <= params.price_max)
        
        # 重量范围过滤
        if hasattr(params, 'weight_min') and params.weight_min is not None:
            conditions.append(self.model_class.weight >= params.weight_min)
        
        if hasattr(params, 'weight_max') and params.weight_max is not None:
            conditions.append(self.model_class.weight <= params.weight_max)
        
        # 功能特性过滤
        if hasattr(params, 'has_stabilization') and params.has_stabilization is not None:
            conditions.append(self.model_class.has_stabilization == params.has_stabilization)
        
        if hasattr(params, 'is_constant_aperture') and params.is_constant_aperture is not None:
            conditions.append(self.model_class.is_constant_aperture == params.is_constant_aperture)
        
        # 滤镜口径范围过滤
        if hasattr(params, 'filter_size_min') and params.filter_size_min is not None:
            conditions.append(self.model_class.filter_size >= params.filter_size_min)
        
        if hasattr(params, 'filter_size_max') and params.filter_size_max is not None:
            conditions.append(self.model_class.filter_size <= params.filter_size_max)
        
        # 发布年份过滤
        if hasattr(params, 'release_year_min') and params.release_year_min is not None:
            conditions.append(func.extract('year', self.model_class.release_date) >= params.release_year_min)
        
        if hasattr(params, 'release_year_max') and params.release_year_max is not None:
            conditions.append(func.extract('year', self.model_class.release_date) <= params.release_year_max)
        
        # 系列和型号过滤
        if hasattr(params, 'series') and params.series:
            conditions.append(self.model_class.series.ilike(f"%{params.series}%"))
        
        if hasattr(params, 'model') and params.model:
            conditions.append(self.model_class.model.ilike(f"%{params.model}%"))
        
        return conditions
    
    def _get_default_search_fields(self) -> List[str]:
        """获取镜头默认搜索字段"""
        return ['model', 'series', 'description']