from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.engine import get_session
from model.lens import Lens, LensCreate, LensUpdate, LensResponse, LensQuery, LensType, FocusType
from model.user import User
from api.auth import get_current_user, get_current_admin_user
from services.lens_service import LensService

router = APIRouter()

@router.post("/lenses/", response_model=LensResponse)
def create_lens(
    lens: LensCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """创建镜头（需要管理员权限）"""
    return LensService.create_lens(session, lens.dict())

@router.get("/lenses/", response_model=List[LensResponse])
def read_lenses(
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = None,
    brand_id: Optional[int] = None,
    mount_id: Optional[int] = None,
    lens_type: Optional[LensType] = None,
    focus_type: Optional[FocusType] = None,
    has_stabilization: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """获取镜头列表（允许所有用户访问）"""
    return LensService.get_lenses(
        session, skip, limit, is_active, brand_id, mount_id, 
        lens_type, focus_type, has_stabilization
    )

@router.get("/lenses/{lens_id}", response_model=LensResponse)
def read_lens(lens_id: int, session: Session = Depends(get_session)):
    """根据ID获取镜头信息（允许所有用户访问）"""
    return LensService.get_lens_by_id(session, lens_id)

@router.get("/lenses/model/{model}", response_model=LensResponse)
def read_lens_by_model(model: str, session: Session = Depends(get_session)):
    """根据型号获取镜头信息（允许所有用户访问）"""
    return LensService.get_lens_by_model(session, model)

@router.put("/lenses/{lens_id}", response_model=LensResponse)
def update_lens(
    lens_id: int, 
    lens_update: LensUpdate, 
    current_user: User = Depends(get_current_admin_user), 
    session: Session = Depends(get_session)
):
    """更新镜头信息（需要管理员权限）"""
    return LensService.update_lens(session, lens_id, lens_update.dict(exclude_unset=True))

@router.delete("/lenses/{lens_id}")
def delete_lens(
    lens_id: int, 
    current_user: User = Depends(get_current_admin_user), 
    session: Session = Depends(get_session)
):
    """删除镜头（需要管理员权限）"""
    return LensService.delete_lens(session, lens_id)

@router.patch("/lenses/{lens_id}/activate")
def activate_lens(
    lens_id: int, 
    current_user: User = Depends(get_current_admin_user), 
    session: Session = Depends(get_session)
):
    """激活镜头（需要管理员权限）"""
    return LensService.activate_lens(session, lens_id)

@router.patch("/lenses/{lens_id}/deactivate")
def deactivate_lens(
    lens_id: int, 
    current_user: User = Depends(get_current_admin_user), 
    session: Session = Depends(get_session)
):
    """停用镜头（需要管理员权限）"""
    return LensService.deactivate_lens(session, lens_id)

@router.get("/lenses/types/")
def get_lens_types():
    """获取镜头类型列表（允许所有用户访问）"""
    return LensService.get_lens_types()

@router.get("/lenses/focus-types/")
def get_focus_types():
    """获取对焦方式列表（允许所有用户访问）"""
    return LensService.get_focus_types()

@router.get("/lenses/search/")
def search_lenses(
    q: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """搜索镜头（允许所有用户访问）"""
    return LensService.search_lenses(session, q, skip, limit)