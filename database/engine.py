import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库URL，默认为SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///camera.db")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """创建数据库和表"""
    from model import BaseModel, User, Brand, Camera, Lens, Mount, BrandMount
    # 使用SQLModel的元数据来创建所有表
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

def drop_db_and_tables():
    """删除数据库表（用于开发环境）"""
    from model import BaseModel, User, Brand, Camera, Lens, Mount, BrandMount
    # 使用SQLModel的元数据来删除所有表
    from sqlmodel import SQLModel
    SQLModel.metadata.drop_all(engine)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
