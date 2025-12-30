from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Query
from fastapi.responses import FileResponse
import os
from sqlmodel import Session, select

from database.engine import get_session
from model.camera import Camera, CameraCreate, CameraUpdate, CameraResponse, CameraQuery
from model.query import CameraQueryParams, QueryResponse
from model.user import User
from api.auth import get_current_user, get_current_admin_user
from services.camera_service import CameraService
from services.query_service import CameraQueryService
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

@router.get("/cameras/query", response_model=QueryResponse, summary="高级查询相机")
def query_cameras(
    # 分页参数
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    
    # 排序参数
    sort_by: Optional[str] = Query(None, description="排序字段，如: model, megapixels, release_price"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向: asc(升序) 或 desc(降序)"),
    
    # 搜索参数
    search: Optional[str] = Query(None, description="搜索关键词，搜索型号、系列和描述"),
    
    # 品牌过滤
    brand_id: Optional[int] = Query(None, description="品牌ID"),
    brand_ids: Optional[str] = Query(None, description="品牌ID列表，逗号分隔，如: 1,2,3"),
    
    # 卡口过滤
    mount_id: Optional[int] = Query(None, description="卡口ID"),
    mount_ids: Optional[str] = Query(None, description="卡口ID列表，逗号分隔，如: 1,2,3"),
    
    # 传感器尺寸过滤
    sensor_size: Optional[str] = Query(None, description="传感器尺寸"),
    sensor_sizes: Optional[str] = Query(None, description="传感器尺寸列表，逗号分隔"),
    
    # 像素范围过滤
    megapixels_min: Optional[float] = Query(None, ge=0, description="最小像素(百万)"),
    megapixels_max: Optional[float] = Query(None, ge=0, description="最大像素(百万)"),
    
    # 价格范围过滤
    price_min: Optional[float] = Query(None, ge=0, description="最低价格(元)"),
    price_max: Optional[float] = Query(None, ge=0, description="最高价格(元)"),
    
    # 重量范围过滤
    weight_min: Optional[float] = Query(None, ge=0, description="最轻重量(克)"),
    weight_max: Optional[float] = Query(None, ge=0, description="最重重量(克)"),
    
    # 功能特性过滤
    has_wifi: Optional[bool] = Query(None, description="是否有WiFi"),
    has_bluetooth: Optional[bool] = Query(None, description="是否有蓝牙"),
    has_hot_shoe: Optional[bool] = Query(None, description="是否有热靴"),
    has_built_in_flash: Optional[bool] = Query(None, description="是否有内置闪光灯"),
    
    # 发布年份过滤
    release_year_min: Optional[int] = Query(None, ge=2000, description="最早发布年份"),
    release_year_max: Optional[int] = Query(None, ge=2000, description="最晚发布年份"),
    
    # 系列和型号过滤
    series: Optional[str] = Query(None, description="产品系列关键词"),
    model: Optional[str] = Query(None, description="型号关键词"),
    
    # 状态过滤
    is_active: Optional[bool] = Query(None, description="是否只返回活跃记录"),
    
    session: Session = Depends(get_session)
):
    """
    高级查询相机接口，支持多字段组合查询
    
    ## 使用示例:
    
    ### 1. 基础查询
    - 查询前10个相机: `/cameras/query?limit=10`
    - 按价格降序排列: `/cameras/query?sort_by=release_price&sort_order=desc`
    
    ### 2. 品牌和卡口过滤
    - 查询佳能相机: `/cameras/query?brand_id=1`
    - 查询索尼和尼康相机: `/cameras/query?brand_ids=1,2`
    - 查询使用E卡口的相机: `/cameras/query?mount_id=3`
    
    ### 3. 传感器和像素过滤
    - 查询全画幅相机: `/cameras/query?sensor_size=full_frame`
    - 查询高像素相机: `/cameras/query?megapixels_min=30`
    - 查询特定像素范围: `/cameras/query?megapixels_min=20&megapixels_max=30`
    
    ### 4. 价格和重量过滤
    - 查询万元以下相机: `/cameras/query?price_max=10000`
    - 查询轻便相机: `/cameras/query?weight_max=500`
    
    ### 5. 功能特性过滤
    - 查询有WiFi的相机: `/cameras/query?has_wifi=true`
    - 查询有内置闪光灯的相机: `/cameras/query?has_built_in_flash=true`
    
    ### 6. 搜索功能
    - 搜索包含"R5"的相机: `/cameras/query?search=R5`
    - 搜索EOS系列: `/cameras/query?series=EOS`
    - 搜索特定型号: `/cameras/query?model=A7`
    
    ### 7. 组合查询
    - 查询索尼全画幅微单，价格1-2万: `/cameras/query?brand_id=3&sensor_size=full_frame&price_min=10000&price_max=20000`
    - 查询2020年后发布的轻便高像素相机: `/cameras/query?megapixels_min=30&weight_max=600&release_year_min=2020`
    """
    # 构建查询参数
    query_params = CameraQueryParams(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        brand_id=brand_id,
        mount_id=mount_id,
        sensor_size=sensor_size,
        megapixels_min=megapixels_min,
        megapixels_max=megapixels_max,
        price_min=price_min,
        price_max=price_max,
        weight_min=weight_min,
        weight_max=weight_max,
        has_wifi=has_wifi,
        has_bluetooth=has_bluetooth,
        has_hot_shoe=has_hot_shoe,
        has_built_in_flash=has_built_in_flash,
        release_year_min=release_year_min,
        release_year_max=release_year_max,
        series=series,
        model=model,
        is_active=is_active
    )
    
    # 处理ID列表
    if brand_ids:
        query_params.brand_ids = [int(id.strip()) for id in brand_ids.split(',') if id.strip().isdigit()]
    
    if mount_ids:
        query_params.mount_ids = [int(id.strip()) for id in mount_ids.split(',') if id.strip().isdigit()]
    
    if sensor_sizes:
        query_params.sensor_sizes = [size.strip() for size in sensor_sizes.split(',') if size.strip()]
    
    # 执行查询
    query_service = CameraQueryService()
    result = query_service.query_with_pagination(session, query_params)
    
    return result

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