from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional

from database.engine import get_session
from model.mount import Mount, MountCreate, MountUpdate, MountResponse, MountQuery, BrandMountCreate, BrandMountResponse
from model.brand import Brand
from model.camera import Camera
from model.lens import Lens
from services.mount_service import MountService
from api.auth import get_current_user, UserRole
from model.user import User

router = APIRouter()


@router.post("/", response_model=MountResponse, tags=["mounts"])
async def create_mount(
    mount_data: MountCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """创建卡口（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        mount = MountService.create_mount(
            db=db,
            name=mount_data.name,
            flange_distance=mount_data.flange_distance,
            release_year=mount_data.release_year,
            description=mount_data.description,
            is_active=mount_data.is_active
        )
        return mount
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[MountResponse], tags=["mounts"])
async def read_mounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_session)
):
    """获取卡口列表（公开访问）"""
    mounts = MountService.get_mounts(db, skip=skip, limit=limit, is_active=is_active)
    return mounts


@router.get("/{mount_id}", response_model=MountResponse, tags=["mounts"])
async def read_mount(
    mount_id: int,
    db: Session = Depends(get_session)
):
    """根据ID获取卡口详情（公开访问）"""
    mount = MountService.get_mount_by_id(db, mount_id)
    if not mount:
        raise HTTPException(status_code=404, detail="卡口未找到")
    return mount


@router.get("/name/{name}", response_model=MountResponse, tags=["mounts"])
async def read_mount_by_name(
    name: str,
    db: Session = Depends(get_session)
):
    """根据名称获取卡口（公开访问）"""
    mount = MountService.get_mount_by_name(db, name)
    if not mount:
        raise HTTPException(status_code=404, detail="卡口未找到")
    return mount


@router.put("/{mount_id}", response_model=MountResponse, tags=["mounts"])
async def update_mount(
    mount_id: int,
    mount_data: MountUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """更新卡口信息（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        mount = MountService.update_mount(
            db=db,
            mount_id=mount_id,
            name=mount_data.name,
            flange_distance=mount_data.flange_distance,
            release_year=mount_data.release_year,
            description=mount_data.description,
            is_active=mount_data.is_active
        )
        if not mount:
            raise HTTPException(status_code=404, detail="卡口未找到")
        return mount
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{mount_id}", tags=["mounts"])
async def delete_mount(
    mount_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """删除卡口（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        success = MountService.delete_mount(db, mount_id)
        if not success:
            raise HTTPException(status_code=404, detail="卡口未找到")
        return {"message": "卡口删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{mount_id}/activate", response_model=MountResponse, tags=["mounts"])
async def activate_mount(
    mount_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """激活卡口（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    mount = MountService.activate_mount(db, mount_id)
    if not mount:
        raise HTTPException(status_code=404, detail="卡口未找到")
    return mount


@router.patch("/{mount_id}/deactivate", response_model=MountResponse, tags=["mounts"])
async def deactivate_mount(
    mount_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """停用卡口（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    mount = MountService.deactivate_mount(db, mount_id)
    if not mount:
        raise HTTPException(status_code=404, detail="卡口未找到")
    return mount


@router.post("/{mount_id}/brands", response_model=BrandMountResponse, tags=["mounts"])
async def add_brand_to_mount(
    mount_id: int,
    brand_data: BrandMountCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """为卡口添加品牌支持（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    try:
        brand_mount = MountService.add_brand_to_mount(
            db=db,
            mount_id=mount_id,
            brand_id=brand_data.brand_id,
            is_primary=brand_data.is_primary,
            compatibility_notes=brand_data.compatibility_notes
        )
        return brand_mount
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{mount_id}/brands/{brand_id}", tags=["mounts"])
async def remove_brand_from_mount(
    mount_id: int,
    brand_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """从卡口移除品牌支持（需要管理员权限）"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    
    success = MountService.remove_brand_from_mount(db, mount_id, brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="品牌卡口关联未找到")
    return {"message": "品牌卡口关联移除成功"}


@router.get("/{mount_id}/brands", response_model=List[Brand], tags=["mounts"])
async def get_mount_brands(
    mount_id: int,
    db: Session = Depends(get_session)
):
    """获取支持该卡口的品牌列表（公开访问）"""
    brands = MountService.get_mount_brands(db, mount_id)
    return brands


@router.get("/{mount_id}/cameras", response_model=List[Camera], tags=["mounts"])
async def get_mount_cameras(
    mount_id: int,
    db: Session = Depends(get_session)
):
    """获取使用该卡口的相机列表（公开访问）"""
    cameras = MountService.get_mount_cameras(db, mount_id)
    return cameras


@router.get("/{mount_id}/lenses", response_model=List[Lens], tags=["mounts"])
async def get_mount_lenses(
    mount_id: int,
    db: Session = Depends(get_session)
):
    """获取使用该卡口的镜头列表（公开访问）"""
    lenses = MountService.get_mount_lenses(db, mount_id)
    return lenses


@router.get("/search/", response_model=List[MountResponse], tags=["mounts"])
async def search_mounts(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_session)
):
    """搜索卡口（公开访问）"""
    mounts = MountService.search_mounts(db, query, skip=skip, limit=limit)
    return mounts