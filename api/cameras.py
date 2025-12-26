from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request
from fastapi.responses import FileResponse
import os
from sqlmodel import Session, select

from database.engine import get_session
from model.camera import Camera, CameraCreate, CameraUpdate, CameraResponse, CameraQuery
from model.user import User
from api.auth import get_current_user, get_current_admin_user
from services.camera_service import CameraService
from services.import_service import ImportService
from utils.limiter import limiter

router = APIRouter()

@router.post("/cameras/", response_model=CameraResponse, summary="创建相机")
def create_camera(
    camera: CameraCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """创建相机（需要管理员权限）"""
    camera_result = CameraService.create_camera(session, camera.model_dump())
    return CameraResponse.model_validate(camera_result)

@router.post("/cameras/import", summary="批量导入相机")
async def import_cameras(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """从 Excel 文件批量导入相机（需要管理员权限）"""
    content = await file.read()
    return ImportService.import_cameras(session, content)

@router.get("/cameras/template", summary="下载相机导入模板")
@limiter.limit("5/minute")
def download_cameras_template(request: Request):
    """下载相机导入 Excel 模板"""
    file_path = os.path.join("static", "templates", "camera_template.xlsx")
    return FileResponse(
        path=file_path,
        filename="camera_import_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/cameras/", response_model=List[CameraResponse], summary="获取相机列表")
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
    cameras = CameraService.get_cameras(session, skip, limit, is_active, brand_id, mount_id, sensor_size)
    return [CameraResponse.model_validate(camera) for camera in cameras]

@router.get("/cameras/{camera_id}", response_model=CameraResponse, summary="获取相机详情")
def read_camera(camera_id: int, session: Session = Depends(get_session)):
    """根据ID获取相机信息（允许所有用户访问）"""
    camera = CameraService.get_camera_by_id(session, camera_id)
    return CameraResponse.model_validate(camera)

@router.put("/cameras/{camera_id}", response_model=CameraResponse, summary="更新相机")
def update_camera(camera_id: int, camera_update: CameraUpdate, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """更新相机信息（需要管理员权限）"""
    camera = CameraService.update_camera(session, camera_id, camera_update.model_dump(exclude_unset=True))
    return CameraResponse.model_validate(camera)

@router.delete("/cameras/{camera_id}", summary="删除相机")
def delete_camera(camera_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """删除相机（需要管理员权限）"""
    return CameraService.delete_camera(session, camera_id)

@router.patch("/cameras/{camera_id}/activate", summary="激活相机")
def activate_camera(camera_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """激活相机（需要管理员权限）"""
    return CameraService.activate_camera(session, camera_id)

@router.patch("/cameras/{camera_id}/deactivate", summary="停用相机")
def deactivate_camera(camera_id: int, current_user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """停用相机（需要管理员权限）"""
    return CameraService.deactivate_camera(session, camera_id)