from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlmodel import Session, select

from model.lens import Lens, LensType, FocusType
from model.brand import Brand
from model.mount import Mount


class LensService:
    """镜头服务类，处理镜头相关的业务逻辑"""
    
    @staticmethod
    def create_lens(session: Session, lens_data: Dict[str, Any]) -> Lens:
        """创建镜头"""
        # 检查镜头型号是否已存在
        existing_lens = session.exec(
            select(Lens).where(Lens.model == lens_data.get("model"))
        ).first()
        if existing_lens:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="镜头型号已存在"
            )
        
        # 检查品牌是否存在
        brand = session.get(Brand, lens_data.get("brand_id"))
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="品牌不存在"
            )
        
        # 检查卡口是否存在
        mount = session.get(Mount, lens_data.get("mount_id"))
        if not mount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="卡口不存在"
            )
        
        # 验证焦距范围
        min_focal = lens_data.get("min_focal_length")
        max_focal = lens_data.get("max_focal_length")
        if min_focal and max_focal and min_focal > max_focal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="最小焦距不能大于最大焦距"
            )
        
        # 验证光圈范围
        min_aperture = lens_data.get("max_aperture_min")
        max_aperture = lens_data.get("max_aperture_max")
        if min_aperture and max_aperture and min_aperture < max_aperture:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="最小光圈值应小于最大光圈值"
            )
        
        lens = Lens(**lens_data)
        session.add(lens)
        session.commit()
        session.refresh(lens)
        return lens
    
    @staticmethod
    def get_lenses(
        session: Session, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        brand_id: Optional[int] = None,
        mount_id: Optional[int] = None,
        lens_type: Optional[LensType] = None,
        focus_type: Optional[FocusType] = None,
        has_stabilization: Optional[bool] = None
    ) -> List[Lens]:
        """获取镜头列表"""
        query = select(Lens)
        
        if is_active is not None:
            query = query.where(Lens.is_active == is_active)
        
        if brand_id is not None:
            query = query.where(Lens.brand_id == brand_id)
            
        if mount_id is not None:
            query = query.where(Lens.mount_id == mount_id)
            
        if lens_type is not None:
            query = query.where(Lens.lens_type == lens_type)
            
        if focus_type is not None:
            query = query.where(Lens.focus_type == focus_type)
            
        if has_stabilization is not None:
            query = query.where(Lens.has_stabilization == has_stabilization)
        
        lenses = session.exec(query.offset(skip).limit(limit)).all()
        return lenses
    
    @staticmethod
    def get_lens_by_id(session: Session, lens_id: int) -> Lens:
        """根据ID获取镜头"""
        lens = session.get(Lens, lens_id)
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        return lens
    
    @staticmethod
    def get_lens_by_model(session: Session, model: str) -> Lens:
        """根据型号获取镜头"""
        lens = session.exec(select(Lens).where(Lens.model == model)).first()
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        return lens
    
    @staticmethod
    def update_lens(session: Session, lens_id: int, lens_data: Dict[str, Any]) -> Lens:
        """更新镜头信息"""
        lens = session.get(Lens, lens_id)
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        
        # 如果更新型号，检查型号是否已存在
        if "model" in lens_data and lens_data["model"] != lens.model:
            existing_lens = session.exec(
                select(Lens).where(Lens.model == lens_data["model"])
            ).first()
            if existing_lens:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="镜头型号已存在"
                )
        
        # 如果更新品牌，检查品牌是否存在
        if "brand_id" in lens_data:
            brand = session.get(Brand, lens_data["brand_id"])
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="品牌不存在"
                )
        
        # 如果更新卡口，检查卡口是否存在
        if "mount_id" in lens_data:
            mount = session.get(Mount, lens_data["mount_id"])
            if not mount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="卡口不存在"
                )
        
        # 验证焦距范围
        if "min_focal_length" in lens_data and "max_focal_length" in lens_data:
            min_focal = lens_data["min_focal_length"]
            max_focal = lens_data["max_focal_length"]
            if min_focal > max_focal:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="最小焦距不能大于最大焦距"
                )
        
        # 更新镜头信息
        for key, value in lens_data.items():
            setattr(lens, key, value)
        
        session.add(lens)
        session.commit()
        session.refresh(lens)
        return lens
    
    @staticmethod
    def delete_lens(session: Session, lens_id: int) -> Dict[str, str]:
        """删除镜头"""
        lens = session.get(Lens, lens_id)
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        
        session.delete(lens)
        session.commit()
        return {"message": "镜头删除成功"}
    
    @staticmethod
    def set_lens_active_status(session: Session, lens_id: int, is_active: bool) -> Dict[str, str]:
        """设置镜头激活状态"""
        lens = session.get(Lens, lens_id)
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        
        lens.is_active = is_active
        session.add(lens)
        session.commit()
        
        action = "激活" if is_active else "停用"
        return {"message": f"镜头{action}成功"}
    
    @staticmethod
    def activate_lens(session: Session, lens_id: int) -> Dict[str, str]:
        """激活镜头"""
        return LensService.set_lens_active_status(session, lens_id, True)

    @staticmethod
    def deactivate_lens(session: Session, lens_id: int) -> Dict[str, str]:
        """停用镜头"""
        return LensService.set_lens_active_status(session, lens_id, False)
    
    @staticmethod
    def get_lens_types() -> List[str]:
        """获取镜头类型列表"""
        return [lens_type.value for lens_type in LensType]
    
    @staticmethod
    def get_focus_types() -> List[str]:
        """获取对焦方式列表"""
        return [focus_type.value for focus_type in FocusType]
    
    @staticmethod
    def search_lenses(
        session: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Lens]:
        """搜索镜头"""
        search_query = select(Lens).where(
            Lens.model.contains(query) | 
            Lens.series.contains(query) |
            Lens.description.contains(query)
        )
        
        lenses = session.exec(search_query.offset(skip).limit(limit)).all()
        return lenses