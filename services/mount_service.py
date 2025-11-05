from sqlmodel import Session, select
from typing import List, Optional
from model.mount import Mount
from model.brand import Brand
from model.brand_mount import BrandMount
from model.camera import Camera
from model.lens import Lens


class MountService:
    """卡口服务类，处理卡口相关的业务逻辑"""

    @staticmethod
    def create_mount(db: Session, name: str, flange_distance: Optional[float] = None, 
                    release_year: Optional[int] = None, description: Optional[str] = None,
                    is_active: bool = True) -> Mount:
        """创建卡口"""
        # 检查卡口名称是否已存在
        existing_mount = db.exec(select(Mount).where(Mount.name == name)).first()
        if existing_mount:
            raise ValueError(f"卡口名称 '{name}' 已存在")
        
        mount = Mount(
            name=name,
            flange_distance=flange_distance,
            release_year=release_year,
            description=description,
            is_active=is_active
        )
        
        db.add(mount)
        db.commit()
        db.refresh(mount)
        return mount

    @staticmethod
    def get_mounts(db: Session, skip: int = 0, limit: int = 100, 
                  is_active: Optional[bool] = None) -> List[Mount]:
        """获取卡口列表"""
        query = select(Mount)
        
        if is_active is not None:
            query = query.where(Mount.is_active == is_active)
            
        query = query.offset(skip).limit(limit)
        
        mounts = db.exec(query).all()
        return mounts

    @staticmethod
    def get_mount_by_id(db: Session, mount_id: int) -> Optional[Mount]:
        """根据ID获取卡口"""
        return db.get(Mount, mount_id)

    @staticmethod
    def get_mount_by_name(db: Session, name: str) -> Optional[Mount]:
        """根据名称获取卡口"""
        return db.exec(select(Mount).where(Mount.name == name)).first()

    @staticmethod
    def update_mount(db: Session, mount_id: int, name: Optional[str] = None,
                    flange_distance: Optional[float] = None, 
                    release_year: Optional[int] = None,
                    description: Optional[str] = None,
                    is_active: Optional[bool] = None) -> Optional[Mount]:
        """更新卡口信息"""
        mount = db.get(Mount, mount_id)
        if not mount:
            return None
            
        if name is not None:
            # 检查新名称是否与其他卡口冲突
            if name != mount.name:
                existing_mount = db.exec(select(Mount).where(Mount.name == name)).first()
                if existing_mount:
                    raise ValueError(f"卡口名称 '{name}' 已存在")
            mount.name = name
            
        if flange_distance is not None:
            mount.flange_distance = flange_distance
            
        if release_year is not None:
            mount.release_year = release_year
            
        if description is not None:
            mount.description = description
            
        if is_active is not None:
            mount.is_active = is_active
            
        db.commit()
        db.refresh(mount)
        return mount

    @staticmethod
    def delete_mount(db: Session, mount_id: int) -> bool:
        """删除卡口"""
        mount = db.get(Mount, mount_id)
        if not mount:
            return False
            
        # 检查是否有相机使用该卡口
        cameras_count = db.exec(select(Camera).where(Camera.mount_id == mount_id)).count()
        if cameras_count > 0:
            raise ValueError(f"无法删除卡口，有 {cameras_count} 台相机使用该卡口")
            
        # 检查是否有镜头使用该卡口
        lenses_count = db.exec(select(Lens).where(Lens.mount_id == mount_id)).count()
        if lenses_count > 0:
            raise ValueError(f"无法删除卡口，有 {lenses_count} 个镜头使用该卡口")
            
        # 删除品牌关联关系
        brand_mounts = db.exec(select(BrandMount).where(BrandMount.mount_id == mount_id)).all()
        for brand_mount in brand_mounts:
            db.delete(brand_mount)
            
        db.delete(mount)
        db.commit()
        return True

    @staticmethod
    def set_mount_active_status(db: Session, mount_id: int, is_active: bool) -> Optional[Mount]:
        """设置卡口激活状态"""
        mount = db.get(Mount, mount_id)
        if not mount:
            return None
            
        mount.is_active = is_active
        db.commit()
        db.refresh(mount)
        return mount

    @staticmethod
    def activate_mount(db: Session, mount_id: int) -> Optional[Mount]:
        """激活卡口"""
        return MountService.set_mount_active_status(db, mount_id, True)

    @staticmethod
    def deactivate_mount(db: Session, mount_id: int) -> Optional[Mount]:
        """停用卡口"""
        return MountService.set_mount_active_status(db, mount_id, False)

    @staticmethod
    def add_brand_to_mount(db: Session, mount_id: int, brand_id: int, 
                          is_primary: bool = False, compatibility_notes: str = "") -> BrandMount:
        """为卡口添加品牌支持"""
        # 检查卡口和品牌是否存在
        mount = db.get(Mount, mount_id)
        if not mount:
            raise ValueError(f"卡口 ID {mount_id} 不存在")
            
        brand = db.get(Brand, brand_id)
        if not brand:
            raise ValueError(f"品牌 ID {brand_id} 不存在")
            
        # 检查是否已存在关联
        existing_association = db.exec(
            select(BrandMount)
            .where(BrandMount.mount_id == mount_id)
            .where(BrandMount.brand_id == brand_id)
        ).first()
        
        if existing_association:
            raise ValueError(f"品牌 {brand.name} 已支持卡口 {mount.name}")
            
        brand_mount = BrandMount(
            mount_id=mount_id,
            brand_id=brand_id,
            is_primary=is_primary,
            compatibility_notes=compatibility_notes
        )
        
        db.add(brand_mount)
        db.commit()
        db.refresh(brand_mount)
        return brand_mount

    @staticmethod
    def remove_brand_from_mount(db: Session, mount_id: int, brand_id: int) -> bool:
        """从卡口移除品牌支持"""
        brand_mount = db.exec(
            select(BrandMount)
            .where(BrandMount.mount_id == mount_id)
            .where(BrandMount.brand_id == brand_id)
        ).first()
        
        if not brand_mount:
            return False
            
        db.delete(brand_mount)
        db.commit()
        return True

    @staticmethod
    def get_mount_brands(db: Session, mount_id: int) -> List[Brand]:
        """获取支持该卡口的品牌列表"""
        mount = db.get(Mount, mount_id)
        if not mount:
            return []
            
        return mount.brands

    @staticmethod
    def get_mount_cameras(db: Session, mount_id: int) -> List[Camera]:
        """获取使用该卡口的相机列表"""
        mount = db.get(Mount, mount_id)
        if not mount:
            return []
            
        return mount.cameras

    @staticmethod
    def get_mount_lenses(db: Session, mount_id: int) -> List[Lens]:
        """获取使用该卡口的镜头列表"""
        mount = db.get(Mount, mount_id)
        if not mount:
            return []
            
        return mount.lenses

    @staticmethod
    def search_mounts(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Mount]:
        """搜索卡口"""
        search_query = select(Mount).where(
            Mount.name.contains(query) | 
            Mount.description.contains(query)
        ).offset(skip).limit(limit)
        
        mounts = db.exec(search_query).all()
        return mounts