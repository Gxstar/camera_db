from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.engine import get_session
from model.brand import Brand
from model.user import User
from api.auth import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/brands/", response_model=Brand)
def create_brand(
    brand: Brand, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """创建品牌（需要管理员或编辑者权限）"""
    # 检查品牌名称是否已存在
    existing_brand = session.exec(select(Brand).where(Brand.name == brand.name)).first()
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="品牌名称已存在"
        )
    
    session.add(brand)
    session.commit()
    session.refresh(brand)
    return brand

@router.get("/brands/", response_model=List[Brand])
def read_brands(
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = None,
    brand_type: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """获取品牌列表（需要登录）"""
    query = select(Brand)
    
    if is_active is not None:
        query = query.where(Brand.is_active == is_active)
    
    if brand_type:
        query = query.where(Brand.brand_type == brand_type)
    
    brands = session.exec(query.offset(skip).limit(limit)).all()
    return brands

@router.get("/brands/{brand_id}", response_model=Brand)
def read_brand(brand_id: int, session: Session = Depends(get_session)):
    """根据ID获取品牌信息"""
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="品牌不存在"
        )
    return brand

@router.get("/brands/name/{brand_name}", response_model=Brand)
def read_brand_by_name(brand_name: str, session: Session = Depends(get_session)):
    """根据品牌名称获取品牌信息"""
    brand = session.exec(select(Brand).where(Brand.name == brand_name)).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="品牌不存在"
        )
    return brand

@router.put("/brands/{brand_id}", response_model=Brand)
def update_brand(
    brand_id: int, 
    brand_update: Brand, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """更新品牌信息（需要管理员或编辑者权限）"""
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="品牌不存在"
        )
    
    # 检查品牌名称是否与其他品牌冲突
    if brand_update.name != brand.name:
        existing_brand = session.exec(select(Brand).where(Brand.name == brand_update.name)).first()
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="品牌名称已存在"
            )
    
    # 更新品牌信息
    brand_data = brand_update.dict(exclude_unset=True)
    for key, value in brand_data.items():
        setattr(brand, key, value)
    
    session.add(brand)
    session.commit()
    session.refresh(brand)
    return brand

@router.delete("/brands/{brand_id}")
def delete_brand(brand_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """删除品牌（需要管理员权限）"""
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

@router.patch("/brands/{brand_id}/activate")
def activate_brand(brand_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """激活品牌（需要管理员权限）"""
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="品牌不存在"
        )
    
    brand.is_active = True
    session.add(brand)
    session.commit()
    return {"message": "品牌激活成功"}

@router.patch("/brands/{brand_id}/deactivate")
def deactivate_brand(brand_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """停用品牌（需要管理员权限）"""
    brand = session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="品牌不存在"
        )
    
    brand.is_active = False
    session.add(brand)
    session.commit()
    return {"message": "品牌停用成功"}

@router.get("/brands/types/")
def get_brand_types():
    """获取品牌类型列表"""
    return {
        "brand_types": [
            {"value": "camera", "label": "相机"},
            {"value": "lens", "label": "镜头"},
            {"value": "accessory", "label": "配件"},
            {"value": "other", "label": "其他"}
        ]
    }