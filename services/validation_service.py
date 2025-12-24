"""
公共验证服务 - 提供品牌、卡口等实体的存在性验证方法
"""
from sqlmodel import Session, select
from fastapi import HTTPException, status


class ValidationService:
    """验证服务类，提供通用的存在性验证方法"""
    
    # ==================== 品牌相关验证 ====================
    
    @staticmethod
    def validate_brand_exists(session: Session, brand_id: int):
        """
        验证品牌是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            brand_id: 品牌ID
            
        Raises:
            HTTPException: 品牌不存在
            
        Returns:
            Brand: 品牌对象
        """
        from model.brand import Brand
        brand = session.get(Brand, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        return brand
    
    @staticmethod
    def validate_brand_by_name_exists(session: Session, brand_name: str):
        """
        验证品牌名称是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            brand_name: 品牌名称
            
        Raises:
            HTTPException: 品牌不存在
            
        Returns:
            Brand: 品牌对象
        """
        from model.brand import Brand
        brand = session.exec(select(Brand).where(Brand.name == brand_name)).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌不存在"
            )
        return brand
    
    @staticmethod
    def check_brand_name_exists(session: Session, brand_name: str, exclude_id: int = None) -> bool:
        """
        检查品牌名称是否已存在（用于创建和更新时的唯一性验证）
        
        Args:
            session: 数据库会话
            brand_name: 品牌名称
            exclude_id: 排除的品牌ID（用于更新时排除自身）
            
        Returns:
            bool: 名称是否存在
        """
        from model.brand import Brand
        query = select(Brand).where(Brand.name == brand_name)
        if exclude_id is not None:
            query = query.where(Brand.id != exclude_id)
        existing = session.exec(query).first()
        return existing is not None
    
    # ==================== 卡口相关验证 ====================
    
    @staticmethod
    def validate_mount_exists(session: Session, mount_id: int):
        """
        验证卡口是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            mount_id: 卡口ID
            
        Raises:
            HTTPException: 卡口不存在
            
        Returns:
            Mount: 卡口对象
        """
        from model.mount import Mount
        mount = session.get(Mount, mount_id)
        if not mount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="卡口不存在"
            )
        return mount
    
    @staticmethod
    def validate_mount_by_name_exists(session: Session, mount_name: str):
        """
        验证卡口名称是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            mount_name: 卡口名称
            
        Raises:
            HTTPException: 卡口不存在
            
        Returns:
            Mount: 卡口对象
        """
        from model.mount import Mount
        mount = session.exec(select(Mount).where(Mount.name == mount_name)).first()
        if not mount:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="卡口不存在"
            )
        return mount
    
    @staticmethod
    def check_mount_name_exists(session: Session, mount_name: str, exclude_id: int = None) -> bool:
        """
        检查卡口名称是否已存在（用于创建和更新时的唯一性验证）
        
        Args:
            session: 数据库会话
            mount_name: 卡口名称
            exclude_id: 排除的卡口ID（用于更新时排除自身）
            
        Returns:
            bool: 名称是否存在
        """
        from model.mount import Mount
        query = select(Mount).where(Mount.name == mount_name)
        if exclude_id is not None:
            query = query.where(Mount.id != exclude_id)
        existing = session.exec(query).first()
        return existing is not None
    
    # ==================== 关联关系验证 ====================
    
    @staticmethod
    def validate_brand_mount_association(session: Session, mount_id: int, brand_id: int):
        """
        验证品牌-卡口关联是否存在
        
        Args:
            session: 数据库会话
            mount_id: 卡口ID
            brand_id: 品牌ID
            
        Raises:
            HTTPException: 关联不存在
            
        Returns:
            BrandMount: 关联对象
        """
        from model.brand_mount import BrandMount
        association = session.exec(
            select(BrandMount)
            .where(BrandMount.mount_id == mount_id)
            .where(BrandMount.brand_id == brand_id)
        ).first()
        
        if not association:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="品牌卡口关联不存在"
            )
        return association
    
    # ==================== 相机相关验证 ====================
    
    @staticmethod
    def validate_camera_exists(session: Session, camera_id: int):
        """
        验证相机是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            camera_id: 相机ID
            
        Raises:
            HTTPException: 相机不存在
            
        Returns:
            Camera: 相机对象
        """
        from model.camera import Camera
        camera = session.get(Camera, camera_id)
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        return camera
    
    @staticmethod
    def validate_camera_by_model_exists(session: Session, model: str):
        """
        验证相机型号是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            model: 相机型号
            
        Raises:
            HTTPException: 相机不存在
            
        Returns:
            Camera: 相机对象
        """
        from model.camera import Camera
        camera = session.exec(select(Camera).where(Camera.model == model)).first()
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="相机不存在"
            )
        return camera
    
    @staticmethod
    def check_camera_model_exists(session: Session, model: str, exclude_id: int = None) -> bool:
        """
        检查相机型号是否已存在（用于创建和更新时的唯一性验证）
        
        Args:
            session: 数据库会话
            model: 相机型号
            exclude_id: 排除的相机ID（用于更新时排除自身）
            
        Returns:
            bool: 型号是否存在
        """
        from model.camera import Camera
        query = select(Camera).where(Camera.model == model)
        if exclude_id is not None:
            query = query.where(Camera.id != exclude_id)
        existing = session.exec(query).first()
        return existing is not None
    
    # ==================== 镜头相关验证 ====================
    
    @staticmethod
    def validate_lens_exists(session: Session, lens_id: int):
        """
        验证镜头是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            lens_id: 镜头ID
            
        Raises:
            HTTPException: 镜头不存在
            
        Returns:
            Lens: 镜头对象
        """
        from model.lens import Lens
        lens = session.get(Lens, lens_id)
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        return lens
    
    @staticmethod
    def validate_lens_by_model_exists(session: Session, model: str):
        """
        验证镜头型号是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            model: 镜头型号
            
        Raises:
            HTTPException: 镜头不存在
            
        Returns:
            Lens: 镜头对象
        """
        from model.lens import Lens
        lens = session.exec(select(Lens).where(Lens.model == model)).first()
        if not lens:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="镜头不存在"
            )
        return lens
    
    @staticmethod
    def check_lens_model_exists(session: Session, model: str, exclude_id: int = None) -> bool:
        """
        检查镜头型号是否已存在（用于创建和更新时的唯一性验证）
        
        Args:
            session: 数据库会话
            model: 镜头型号
            exclude_id: 排除的镜头ID（用于更新时排除自身）
            
        Returns:
            bool: 型号是否存在
        """
        from model.lens import Lens
        query = select(Lens).where(Lens.model == model)
        if exclude_id is not None:
            query = query.where(Lens.id != exclude_id)
        existing = session.exec(query).first()
        return existing is not None
    
    # ==================== 用户相关验证 ====================
    
    @staticmethod
    def validate_user_exists(session: Session, user_id: int):
        """
        验证用户是否存在，不存在则抛出404异常
        
        Args:
            session: 数据库会话
            user_id: 用户ID
            
        Raises:
            HTTPException: 用户不存在
            
        Returns:
            User: 用户对象
        """
        from model.user import User
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    
    @staticmethod
    def check_username_exists(session: Session, username: str, exclude_id: int = None) -> bool:
        """
        检查用户名是否已存在（用于创建和更新时的唯一性验证）
        
        Args:
            session: 数据库会话
            username: 用户名
            exclude_id: 排除的用户ID（用于更新时排除自身）
            
        Returns:
            bool: 用户名是否存在
        """
        from model.user import User
        query = select(User).where(User.username == username)
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        existing = session.exec(query).first()
        return existing is not None
    
    @staticmethod
    def check_email_exists(session: Session, email: str, exclude_id: int = None) -> bool:
        """
        检查邮箱是否已存在（用于创建和更新时的唯一性验证）
        
        Args:
            session: 数据库会话
            email: 邮箱地址
            exclude_id: 排除的用户ID（用于更新时排除自身）
            
        Returns:
            bool: 邮箱是否存在
        """
        from model.user import User
        query = select(User).where(User.email == email)
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        existing = session.exec(query).first()
        return existing is not None
