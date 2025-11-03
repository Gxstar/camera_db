from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database.engine import get_session
from model.camera import Camera

router = APIRouter()

@router.post("/cameras/", response_model=Camera)
def create_camera(camera: Camera, session: Session = Depends(get_session)):
    # 检查相机名称是否已存在
    existing_camera = session.exec(select(Camera).where(Camera.name == camera.name)).first()
    if existing_camera:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera name already exists"
        )
    
    session.add(camera)
    session.commit()
    session.refresh(camera)
    return camera

@router.get("/cameras/", response_model=List[Camera])
def read_cameras(
    skip: int = 0, 
    limit: int = 100, 
    is_active: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    query = select(Camera)
    
    if is_active is not None:
        query = query.where(Camera.is_active == is_active)
    
    cameras = session.exec(query.offset(skip).limit(limit)).all()
    return cameras

@router.get("/cameras/{camera_id}", response_model=Camera)
def read_camera(camera_id: int, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    return camera

@router.put("/cameras/{camera_id}", response_model=Camera)
def update_camera(camera_id: int, camera_update: Camera, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # 更新相机信息
    camera_data = camera_update.dict(exclude_unset=True)
    
    for key, value in camera_data.items():
        setattr(camera, key, value)
    
    session.add(camera)
    session.commit()
    session.refresh(camera)
    return camera

@router.delete("/cameras/{camera_id}")
def delete_camera(camera_id: int, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    session.delete(camera)
    session.commit()
    return {"message": "Camera deleted successfully"}

@router.patch("/cameras/{camera_id}/activate")
def activate_camera(camera_id: int, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    camera.is_active = True
    session.add(camera)
    session.commit()
    return {"message": "Camera activated successfully"}

@router.patch("/cameras/{camera_id}/deactivate")
def deactivate_camera(camera_id: int, session: Session = Depends(get_session)):
    camera = session.get(Camera, camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    camera.is_active = False
    session.add(camera)
    session.commit()
    return {"message": "Camera deactivated successfully"}