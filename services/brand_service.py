from typing import List, Optional
from sqlmodel import Session, select
from fastapi import HTTPException, status

from model.brand import Brand


class BrandService:
    """品牌服务类，处理所有品牌相关的业务逻辑"""

    @staticmethod
    def create_brand(session: Session, brand_data: dict) -> Brand:
        """创建品牌"""
        # 检查品牌名称是否已存在
        existing_brand = session.exec(select(Brand).where(Brand.name == brand_data["name"])).first()
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="品牌名称已存在"
            )
        
        # 创建品牌对象
        brand = Brand(**brand_data)
        session.add(brand)
        session.commit()
        session.refresh(brand)
        return brand

    @staticmethod
    def get_brands(
        session: Session, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        brand_type: Optional[str] = None
    ) -> List[Brand]:
        """获取品牌列表"""
        query = select(Brand)
        
        if is_active is not None:
            query = query.where(Brand.is_active == is_active)
        
        if brand_type:
            query = query.where(Brand.brand_type == brand_type)
        
        brands = session.exec(query.offset(skip).limit(limit)).all()
        return brands

    @staticmethod
    def get_brand_by_id(session: Session, brand_id: int) -> Brand:
        """根据ID获取品牌"""
        brand = session.get(Brand, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        return brand

    @staticmethod
    def get_brand_by_name(session: Session, brand_name: str) -> Brand:
        """根据品牌名称获取品牌"""
        brand = session.exec(select(Brand).where(Brand.name == brand_name)).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        return brand

    @staticmethod
    def update_brand(session: Session, brand_id: int, brand_update_data: dict) -> Brand:
        """更新品牌信息"""
        brand = session.get(Brand, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        
        # 检查品牌名称是否与其他品牌冲突
        if "name" in brand_update_data and brand_update_data["name"] != brand.name:
            existing_brand = session.exec(select(Brand).where(Brand.name == brand_update_data["name"])).first()
            if existing_brand:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="品牌名称已存在"
                )
        
        # 更新品牌信息
        for key, value in brand_update_data.items():
            setattr(brand, key, value)
        
        session.add(brand)
        session.commit()
        session.refresh(brand)
        return brand

    @staticmethod
    def delete_brand(session: Session, brand_id: int) -> dict:
        """删除品牌"""
        brand = session.get(Brand, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        
        # 检查是否有相机关联该品牌
        from model.camera import Camera
        cameras_count = session.exec(select(Camera).where(Camera.brand_id == brand_id)).count()
        if cameras_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该品牌下有{cameras_count}个相机，无法删除"
            )
        
        session.delete(brand)
        session.commit()
        return {"message": "品牌删除成功"}

    @staticmethod
    def set_brand_active_status(session: Session, brand_id: int, is_active: bool) -> dict:
        """设置品牌激活状态"""
        brand = session.get(Brand, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        
        brand.is_active = is_active
        session.add(brand)
        session.commit()
        
        action = "激活" if is_active else "停用"
        return {"message": f"品牌{action}成功"}

    @staticmethod
    def get_brand_types() -> dict:
        """获取品牌类型列表"""
        return {
            "brand_types": [
                {"value": "camera", "label": "相机"},
                {"value": "lens", "label": "镜头"},
                {"value": "accessory", "label": "配件"},
                {"value": "other", "label": "其他"}
            ]
        }