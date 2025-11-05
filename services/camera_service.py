from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlmodel import Session, select

from model.camera import Camera, SensorSize
from model.brand import Brand
from model.mount import Mount


class CameraService:
    """相机服务类，处理相机相关的业务逻辑"""
    
    @staticmethod
    def create_camera(session: Session, camera_data: Dict[str, Any]) -> Camera:
        """创建相机"""
        # 检查相机型号是否已存在
        existing_camera = session.exec(
            select(Camera).where(Camera.model == camera_data.get("model"))
        ).first()
        if existing_camera:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="相机型号已存在"
            )
        
        # 检查品牌是否存在
        brand = session.get(Brand, camera_data.get("brand_id"))
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="品牌不存在"
            )
        
        # 检查卡口是否存在
        mount = session.get(Mount, camera_data.get("mount_id"))
        if not mount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="卡口不存在"
            )
        
        camera = Camera(**camera_data)
        session.add(camera)
        session.commit()
        session.refresh(camera)
        return camera
    
    @staticmethod
    def get_cameras(
        session: Session, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None,
        brand_id: Optional[int] = None,
        mount_id: Optional[int] = None,
        sensor_size: Optional[SensorSize] = None
    ) -> List[Camera]:
        """获取相机列表"""
        query = select(Camera)
        
        if is_active is not None:
            query = query.where(Camera.is_active == is_active)
        
        if brand_id is not None:
            query = query.where(Camera.brand_id == brand_id)
            
        if mount_id is not None:
            query = query.where(Camera.mount_id == mount_id)
            
        if sensor_size is not None:
            query = query.where(Camera.sensor_size == sensor_size)
        
        cameras = session.exec(query.offset(skip).limit(limit)).all()
        return cameras
    
    @staticmethod
    def get_camera_by_id(session: Session, camera_id: int) -> Camera:
        """根据ID获取相机"""
        camera = session.get(Camera, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        return camera
    
    @staticmethod
    def get_camera_by_model(session: Session, model: str) -> Camera:
        """根据型号获取相机"""
        camera = session.exec(select(Camera).where(Camera.model == model)).first()
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        return camera
    
    @staticmethod
    def update_camera(session: Session, camera_id: int, camera_data: Dict[str, Any]) -> Camera:
        """更新相机信息"""
        camera = session.get(Camera, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        
        # 如果更新型号，检查型号是否已存在
        if "model" in camera_data and camera_data["model"] != camera.model:
            existing_camera = session.exec(
                select(Camera).where(Camera.model == camera_data["model"])
            ).first()
            if existing_camera:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="相机型号已存在"
                )
        
        # 如果更新品牌，检查品牌是否存在
        if "brand_id" in camera_data:
            brand = session.get(Brand, camera_data["brand_id"])
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="品牌不存在"
                )
        
        # 如果更新卡口，检查卡口是否存在
        if "mount_id" in camera_data:
            mount = session.get(Mount, camera_data["mount_id"])
            if not mount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="卡口不存在"
                )
        
        # 更新相机信息
        for key, value in camera_data.items():
            setattr(camera, key, value)
        
        session.add(camera)
        session.commit()
        session.refresh(camera)
        return camera
    
    @staticmethod
    def delete_camera(session: Session, camera_id: int) -> Dict[str, str]:
        """删除相机"""
        camera = session.get(Camera, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        
        session.delete(camera)
        session.commit()
        return {"message": "相机删除成功"}
    
    @staticmethod
    def set_camera_active_status(session: Session, camera_id: int, is_active: bool) -> Dict[str, str]:
        """设置相机激活状态"""
        camera = session.get(Camera, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        
        camera.is_active = is_active
        session.add(camera)
        session.commit()
        
        action = "激活" if is_active else "停用"
        return {"message": f"相机{action}成功"}

    @staticmethod
    def activate_camera(session: Session, camera_id: int) -> Dict[str, str]:
        """激活相机"""
        return CameraService.set_camera_active_status(session, camera_id, True)

    @staticmethod
    def deactivate_camera(session: Session, camera_id: int) -> Dict[str, str]:
        """停用相机"""
        return CameraService.set_camera_active_status(session, camera_id, False)

    @staticmethod
    def get_sensor_sizes() -> List[str]:
        """获取传感器尺寸列表"""
        return [size.value for size in SensorSize]