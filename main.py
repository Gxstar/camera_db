import os
from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from dotenv import load_dotenv

from database.engine import engine, create_db_and_tables
from model import User, Camera

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title=os.getenv("APP_NAME", "Camera DB"),
    version=os.getenv("APP_VERSION", "0.1.0"),
    description="Camera management system with FastAPI and SQLModel"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库会话依赖
def get_session():
    with Session(engine) as session:
        yield session

# 启动时创建数据库表
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Camera Management System",
        "version": app.version,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 导入API路由
from api import users, cameras, brands

# 注册路由
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(cameras.router, prefix="/api/v1", tags=["cameras"])
app.include_router(brands.router, prefix="/api/v1", tags=["brands"])

