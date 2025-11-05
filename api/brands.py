from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session

from database.engine import get_session
from model.brand import Brand, BrandCreate, BrandUpdate, BrandResponse, BrandQuery
from model.user import User
from api.auth import get_current_user, get_current_admin_user
from services.brand_service import BrandService

router = APIRouter()

@router.post("/brands/", response_model=BrandResponse)
def create_brand(
    brand: BrandCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """创建品牌（需要管理员或编辑者权限）"""
    return BrandService.create_brand(session, brand.dict())

@router.get("/brands/", response_model=List[BrandResponse])
def read_brands(
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = None,
    brand_type: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """获取品牌列表（允许所有用户访问）"""
    return BrandService.get_brands(session, skip, limit, is_active, brand_type)

@router.get("/brands/{brand_id}", response_model=BrandResponse)
def read_brand(brand_id: int, session: Session = Depends(get_session)):
    """根据ID获取品牌信息"""
    return BrandService.get_brand_by_id(session, brand_id)

@router.get("/brands/name/{brand_name}", response_model=BrandResponse)
def read_brand_by_name(brand_name: str, session: Session = Depends(get_session)):
    """根据品牌名称获取品牌信息"""
    return BrandService.get_brand_by_name(session, brand_name)

@router.put("/brands/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int, 
    brand_update: BrandUpdate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """更新品牌信息（需要管理员或编辑者权限）"""
    return BrandService.update_brand(session, brand_id, brand_update.dict(exclude_unset=True))

@router.delete("/brands/{brand_id}")
def delete_brand(brand_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """删除品牌（需要管理员权限）"""
    return BrandService.delete_brand(session, brand_id)

@router.patch("/brands/{brand_id}/activate")
def activate_brand(brand_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """激活品牌（需要管理员权限）"""
    return BrandService.set_brand_active_status(session, brand_id, True)

@router.patch("/brands/{brand_id}/deactivate")
def deactivate_brand(brand_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """停用品牌（需要管理员权限）"""
    return BrandService.set_brand_active_status(session, brand_id, False)

@router.get("/brands/types/")
def get_brand_types():
    """获取品牌类型列表（允许所有用户访问）"""
    return BrandService.get_brand_types()