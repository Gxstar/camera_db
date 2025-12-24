from sqlmodel import Session, select
from typing import List, Optional
from fastapi import HTTPException, status
from model.mount import Mount
from model.brand import Brand
from model.brand_mount import BrandMount
from model.camera import Camera
from model.lens import Lens
from services.validation_service import ValidationService


class MountService:
    """卡口服务类，处理卡口相关的业务逻辑"""

    @staticmethod
    def create_mount(session: Session, name: str, flange_distance: Optional[float] = None, 
                    release_year: Optional[int] = None, description: Optional[str] = None,
                    is_active: bool = True) -> Mount:
        """创建卡口"""
        # 检查卡口名称是否已存在
        if ValidationService.check_mount_name_exists(session, name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"卡口名称 '{name}' 已存在"
            )
        
        mount = Mount(
            name=name,
            flange_distance=flange_distance,
            release_year=release_year,
            description=description,
            is_active=is_active
        )
        
        session.add(mount)
        session.commit()
        session.refresh(mount)
        return mount

    @staticmethod
    def get_mounts(session: Session, skip: int = 0, limit: int = 100, 
                  is_active: Optional[bool] = None) -> List[Mount]:
        """获取卡口列表"""
        query = select(Mount)
        
        if is_active is not None:
            query = query.where(Mount.is_active == is_active)
            
        query = query.offset(skip).limit(limit)
        
        mounts = session.exec(query).all()
        return mounts

    @staticmethod
    def get_mount_by_id(session: Session, mount_id: int) -> Mount:
        """根据ID获取卡口"""
        return ValidationService.validate_mount_exists(session, mount_id)

    @staticmethod
    def get_mount_by_name(session: Session, name: str) -> Mount:
        """根据名称获取卡口"""
        return ValidationService.validate_mount_by_name_exists(session, name)

    @staticmethod
    def update_mount(session: Session, mount_id: int, name: Optional[str] = None,
                    flange_distance: Optional[float] = None, 
                    release_year: Optional[int] = None,
                    description: Optional[str] = None,
                    is_active: Optional[bool] = None) -> Mount:
        """更新卡口信息"""
        mount = ValidationService.validate_mount_exists(session, mount_id)
            
        if name is not None:
            # 检查新名称是否与其他卡口冲突
            if name != mount.name:
                if ValidationService.check_mount_name_exists(session, name, exclude_id=mount_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"卡口名称 '{name}' 已存在"
                    )
            mount.name = name
            
        if flange_distance is not None:
            mount.flange_distance = flange_distance
            
        if release_year is not None:
            mount.release_year = release_year
            
        if description is not None:
            mount.description = description
            
        if is_active is not None:
            mount.is_active = is_active
            
        session.add(mount)
        session.commit()
        session.refresh(mount)
        return mount

    @staticmethod
    def delete_mount(session: Session, mount_id: int) -> bool:
        """删除卡口"""
        mount = ValidationService.validate_mount_exists(session, mount_id)
            
        # 检查是否有相机使用该卡口
        cameras_count = session.exec(select(Camera).where(Camera.mount_id == mount_id)).count()
        if cameras_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除卡口，有 {cameras_count} 台相机使用该卡口"
            )
            
        # 检查是否有镜头使用该卡口
        lenses_count = session.exec(select(Lens).where(Lens.mount_id == mount_id)).count()
        if lenses_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除卡口，有 {lenses_count} 个镜头使用该卡口"
            )
            
        # 删除品牌关联关系
        brand_mounts = session.exec(select(BrandMount).where(BrandMount.mount_id == mount_id)).all()
        for brand_mount in brand_mounts:
            session.delete(brand_mount)
            
        session.delete(mount)
        session.commit()
        return True

    @staticmethod
    def set_mount_active_status(session: Session, mount_id: int, is_active: bool) -> Mount:
        """设置卡口激活状态"""
        mount = ValidationService.validate_mount_exists(session, mount_id)
            
        mount.is_active = is_active
        session.add(mount)
        session.commit()
        session.refresh(mount)
        return mount

    @staticmethod
    def activate_mount(session: Session, mount_id: int) -> Mount:
        """激活卡口"""
        return MountService.set_mount_active_status(session, mount_id, True)

    @staticmethod
    def deactivate_mount(session: Session, mount_id: int) -> Mount:
        """停用卡口"""
        return MountService.set_mount_active_status(session, mount_id, False)

    @staticmethod
    def add_brand_to_mount(session: Session, mount_id: int, brand_id: int, 
                          is_primary: bool = False, compatibility_notes: str = "") -> BrandMount:
        """为卡口添加品牌支持"""
        # 验证卡口和品牌是否存在
        mount = ValidationService.validate_mount_exists(session, mount_id)
        brand = ValidationService.validate_brand_exists(session, brand_id)
            
        # 检查是否已存在关联
        from model.brand_mount import BrandMount as BM
        existing_association = session.exec(
            select(BM)
            .where(BM.mount_id == mount_id)
            .where(BM.brand_id == brand_id)
        ).first()
        
        if existing_association:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"品牌 {brand.name} 已支持卡口 {mount.name}"
            )
            
        brand_mount = BrandMount(
            mount_id=mount_id,
            brand_id=brand_id,
            is_primary=is_primary,
            compatibility_notes=compatibility_notes
        )
        
        session.add(brand_mount)
        session.commit()
        session.refresh(brand_mount)
        return brand_mount

    @staticmethod
    def remove_brand_from_mount(session: Session, mount_id: int, brand_id: int) -> bool:
        """从卡口移除品牌支持"""
        ValidationService.validate_brand_mount_association(session, mount_id, brand_id)
        
        from model.brand_mount import BrandMount as BM
        brand_mount = session.exec(
            select(BM)
            .where(BM.mount_id == mount_id)
            .where(BM.brand_id == brand_id)
        ).first()
        
        session.delete(brand_mount)
        session.commit()
        return True

    @staticmethod
    def get_mount_brands(session: Session, mount_id: int) -> List[Brand]:
        """获取支持该卡口的品牌列表"""
        ValidationService.validate_mount_exists(session, mount_id)