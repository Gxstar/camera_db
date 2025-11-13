import os
from typing import Union
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from sqlmodel import Session
from dotenv import load_dotenv

from database.engine import engine, create_db_and_tables

# 加载环境变量
load_dotenv()

# 定义lifespan事件处理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    create_db_and_tables()
    yield
    # 关闭时可以添加清理逻辑

# 创建FastAPI应用 - 禁用默认的Swagger UI和ReDoc
app = FastAPI(
    title=os.getenv("APP_NAME", "Camera DB"),
    version=os.getenv("APP_VERSION", "0.1.0"),
    description="Camera management system with FastAPI and SQLModel",
    docs_url=None,  # 禁用默认的/docs路由
    redoc_url=None,  # 禁用默认的/redoc路由
    lifespan=lifespan  # 使用新的lifespan事件处理器
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 数据库会话依赖
def get_session():
    with Session(engine) as session:
        yield session



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

# 自定义Swagger UI路由 - 禁用默认的Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_js_url="/static/swaggerui/swagger-ui-bundle.js",
        swagger_css_url="/static/swaggerui/swagger-ui.css",
        swagger_ui_parameters={
            "dom_id": "#swagger-ui",
            "layout": "BaseLayout",
            "deepLinking": True,
            "showExtensions": True,
            "showCommonExtensions": True
        }
    )

# 导入API路由
from api import auth, users, cameras, brands, mounts, lenses

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(cameras.router, prefix="/api/v1", tags=["cameras"])
app.include_router(brands.router, prefix="/api/v1", tags=["brands"])
app.include_router(lenses.router, prefix="/api/v1", tags=["lenses"])
app.include_router(mounts.router, prefix="/api/v1", tags=["mounts"])

# 启动服务器
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 启动服务器: http://{host}:{port}")
    print(f"📚 API文档: http://{host}:{port}/docs")
    print(f"🔧 健康检查: http://{host}:{port}/health")
    
    uvicorn.run(app, host=host, port=port)

