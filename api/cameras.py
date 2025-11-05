from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database.engine import get_session
from model.camera import Camera, CameraCreate, CameraUpdate, CameraResponse, CameraQuery
from model.user import User
from api.auth import get_current_user, get_current_admin_user
from services.camera_service import CameraService

router = APIRouter()

@router.post("/cameras/", response_model=CameraResponse)
def create_camera(
    camera: CameraCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """创建相机（需要管理员权限）"""
    return CameraService.create_camera(session, camera.dict())

@router.get("/cameras/", response_model=List[CameraResponse])
def read_cameras(
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = None,
    brand_id: Optional[int] = None,
    mount_id: Optional[int] = None,
    sensor_size: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """获取相机列表（允许所有用户访问）"""
    return CameraService.get_cameras(session, skip, limit, is_active, brand_id, mount_id, sensor_size)

@router.get("/cameras/{camera_id}", response_model=CameraResponse)
def read_camera(camera_id: int, session: Session = Depends(get_session)):
    """根据ID获取相机信息（允许所有用户访问）"""
    return CameraService.get_camera_by_id(session, camera_id)

@router.put("/cameras/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, camera_update: CameraUpdate, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """更新相机信息（需要管理员权限）"""
    return CameraService.update_camera(session, camera_id, camera_update.dict(exclude_unset=True))

@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """删除相机（需要管理员权限）"""
    return CameraService.delete_camera(session, camera_id)

@router.patch("/cameras/{camera_id}/activate")
def activate_camera(camera_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """激活相机（需要管理员权限）"""
    return CameraService.activate_camera(session, camera_id)

@router.patch("/cameras/{camera_id}/deactivate")
def deactivate_camera(camera_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """停用相机（需要管理员权限）"""
    return CameraService.deactivate_camera(session, camera_id)