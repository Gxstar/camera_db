from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Query
from fastapi.responses import FileResponse
import os
from sqlmodel import Session

from database.engine import get_session
from model.lens import Lens, LensCreate, LensUpdate, LensResponse, LensQuery, LensType, FocusType
from model.query import LensQueryParams, QueryResponse
from model.user import User
from api.auth import get_current_user, get_current_admin_user
from services.lens_service import LensService
from services.query_service import LensQueryService
from services.import_service import ImportService
from utils.limiter import limiter

router = APIRouter()

@router.post("/lenses/", response_model=LensResponse, summary="创建镜头")
def create_lens(
    lens: LensCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """创建镜头（需要管理员权限）"""
    lens_result = LensService.create_lens(session, lens.model_dump())
    return LensResponse.model_validate(lens_result)

@router.post("/lenses/import", summary="批量导入镜头")
async def import_lenses(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """从 Excel 文件批量导入镜头（需要管理员权限）"""
    content = await file.read()
    return ImportService.import_lenses(session, content)

@router.get("/lenses/template", summary="下载镜头导入模板")
@limiter.limit("5/minute")
def download_lenses_template(request: Request):
    """下载镜头导入 Excel 模板"""
    file_path = os.path.join("static", "templates", "lens_template.xlsx")
    return FileResponse(
        path=file_path,
        filename="lens_import_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/lenses/", response_model=List[LensResponse], summary="获取镜头列表")
def read_lenses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    brand_id: Optional[int] = None,
    mount_id: Optional[int] = None,
    lens_type: Optional[LensType] = None,
    focus_type: Optional[FocusType] = None,
    has_stabilization: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """获取镜头列表（允许所有用户访问）"""
    lenses = LensService.get_lenses(
        session, skip, limit, is_active, brand_id, mount_id,
        lens_type, focus_type, has_stabilization
    )
    return [LensResponse.model_validate(lens) for lens in lenses]

@router.get("/lenses/query", response_model=QueryResponse, summary="高级查询镜头")
def query_lenses(
    # 分页参数
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    
    # 排序参数
    sort_by: Optional[str] = Query(None, description="排序字段，如: model, min_focal_length, max_aperture_min, release_price"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="排序方向: asc(升序) 或 desc(降序)"),
    
    # 搜索参数
    search: Optional[str] = Query(None, description="搜索关键词，搜索型号、系列和描述"),
    
    # 品牌过滤
    brand_id: Optional[int] = Query(None, description="品牌ID"),
    brand_ids: Optional[str] = Query(None, description="品牌ID列表，逗号分隔，如: 1,2,3"),
    
    # 卡口过滤
    mount_id: Optional[int] = Query(None, description="卡口ID"),
    mount_ids: Optional[str] = Query(None, description="卡口ID列表，逗号分隔，如: 1,2,3"),
    
    # 镜头类型过滤
    lens_type: Optional[str] = Query(None, description="镜头类型: prime(定焦) 或 zoom(变焦)"),
    lens_types: Optional[str] = Query(None, description="镜头类型列表，逗号分隔"),
    
    # 对焦方式过滤
    focus_type: Optional[str] = Query(None, description="对焦方式: auto(自动) 或 manual(手动)"),
    focus_types: Optional[str] = Query(None, description="对焦方式列表，逗号分隔"),
    
    # 焦距范围过滤
    focal_length_min: Optional[float] = Query(None, ge=0, description="最短焦距(mm)"),
    focal_length_max: Optional[float] = Query(None, ge=0, description="最长焦距(mm)"),
    
    # 光圈范围过滤
    aperture_min: Optional[float] = Query(None, ge=1, description="最大光圈最小值"),
    aperture_max: Optional[float] = Query(None, ge=1, description="最大光圈最大值"),
    
    # 价格范围过滤
    price_min: Optional[float] = Query(None, ge=0, description="最低价格(元)"),
    price_max: Optional[float] = Query(None, ge=0, description="最高价格(元)"),
    
    # 重量范围过滤
    weight_min: Optional[float] = Query(None, ge=0, description="最轻重量(克)"),
    weight_max: Optional[float] = Query(None, ge=0, description="最重重量(克)"),
    
    # 功能特性过滤
    has_stabilization: Optional[bool] = Query(None, description="是否有防抖"),
    is_constant_aperture: Optional[bool] = Query(None, description="是否恒定光圈"),
    
    # 滤镜口径范围过滤
    filter_size_min: Optional[float] = Query(None, ge=0, description="最小滤镜口径(mm)"),
    filter_size_max: Optional[float] = Query(None, ge=0, description="最大滤镜口径(mm)"),
    
    # 发布年份过滤
    release_year_min: Optional[int] = Query(None, ge=2000, description="最早发布年份"),
    release_year_max: Optional[int] = Query(None, ge=2000, description="最晚发布年份"),
    
    # 系列和型号过滤
    series: Optional[str] = Query(None, description="镜头系列关键词"),
    model: Optional[str] = Query(None, description="型号关键词"),
    
    # 状态过滤
    is_active: Optional[bool] = Query(None, description="是否只返回活跃记录"),
    
    session: Session = Depends(get_session)
):
    """
    高级查询镜头接口，支持多字段组合查询
    
    ## 使用示例:
    
    ### 1. 基础查询
    - 查询前10个镜头: `/lenses/query?limit=10`
    - 按价格升序排列: `/lenses/query?sort_by=release_price&sort_order=asc`
    
    ### 2. 品牌和卡口过滤
    - 查询佳能镜头: `/lenses/query?brand_id=1`
    - 查询索尼和尼康镜头: `/lenses/query?brand_ids=1,2`
    - 查询E卡口镜头: `/lenses/query?mount_id=3`
    
    ### 3. 镜头类型和对焦过滤
    - 查询定焦镜头: `/lenses/query?lens_type=prime`
    - 查询变焦镜头: `/lenses/query?lens_type=zoom`
    - 查询自动对焦镜头: `/lenses/query?focus_type=auto`
    
    ### 4. 焦距和光圈过滤
    - 查询广角镜头: `/lenses/query?focal_length_max=35`
    - 查询长焦镜头: `/lenses/query?focal_length_min=100`
    - 查询大光圈镜头: `/lenses/query?aperture_min=1.4&aperture_max=2.8`
    - 查询标准变焦: `/lenses/query?focal_length_min=24&focal_length_max=70`
    
    ### 5. 价格和重量过滤
    - 查询5000元以下镜头: `/lenses/query?price_max=5000`
    - 查询轻便镜头: `/lenses/query?weight_max=500`
    
    ### 6. 功能特性过滤
    - 查询带防抖的镜头: `/lenses/query?has_stabilization=true`
    - 查询恒定光圈镜头: `/lenses/query?is_constant_aperture=true`
    
    ### 7. 滤镜口径过滤
    - 查询77mm滤镜镜头: `/lenses/query?filter_size_min=77&filter_size_max=77`
    - 查询常用滤镜口径: `/lenses/query?filter_sizes=49,52,55,58,62,67,72,77,82`
    
    ### 8. 搜索功能
    - 搜索包含"24-70"的镜头: `/lenses/query?search=24-70`
    - 搜索L系列镜头: `/lenses/query?series=L`
    - 搜索特定型号: `/lenses/query?model=85mm`
    
    ### 9. 组合查询
    - 查询索尼全画幅大光圈定焦: `/lenses/query?brand_id=3&lens_type=prime&aperture_min=1.8`
    - 查询万元内防抖变焦镜头: `/lenses/query?lens_type=zoom&has_stabilization=true&price_max=10000`
    - 查询2020年后发布的轻便定焦: `/lenses/query?lens_type=prime&weight_max=400&release_year_min=2020`
    """
    # 构建查询参数
    query_params = LensQueryParams(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
        brand_id=brand_id,
        mount_id=mount_id,
        lens_type=lens_type,
        focus_type=focus_type,
        focal_length_min=focal_length_min,
        focal_length_max=focal_length_max,
        aperture_min=aperture_min,
        aperture_max=aperture_max,
        price_min=price_min,
        price_max=price_max,
        weight_min=weight_min,
        weight_max=weight_max,
        has_stabilization=has_stabilization,
        is_constant_aperture=is_constant_aperture,
        filter_size_min=filter_size_min,
        filter_size_max=filter_size_max,
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
    
    if lens_types:
        query_params.lens_types = [lens_type.strip() for lens_type in lens_types.split(',') if lens_type.strip()]
    
    if focus_types:
        query_params.focus_types = [focus_type.strip() for focus_type in focus_types.split(',') if focus_type.strip()]
    
    # 执行查询
    query_service = LensQueryService()
    result = query_service.query_with_pagination(session, query_params)
    
    return result

@router.get("/lenses/{lens_id}", response_model=LensResponse, summary="获取镜头详情")
def read_lens(lens_id: int, session: Session = Depends(get_session)):
    """根据ID获取镜头信息（允许所有用户访问）"""
    lens = LensService.get_lens_by_id(session, lens_id)
    return LensResponse.model_validate(lens)

@router.get("/lenses/model/{model}", response_model=LensResponse, summary="根据型号获取镜头")
def read_lens_by_model(model: str, session: Session = Depends(get_session)):
    """根据型号获取镜头信息（允许所有用户访问）"""
    lens = LensService.get_lens_by_model(session, model)
    return LensResponse.model_validate(lens)

@router.put("/lenses/{lens_id}", response_model=LensResponse, summary="更新镜头")
def update_lens(
    lens_id: int,
    lens_update: LensUpdate,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """更新镜头信息（需要管理员权限）"""
    lens = LensService.update_lens(session, lens_id, lens_update.model_dump(exclude_unset=True))
    return LensResponse.model_validate(lens)

@router.delete("/lenses/{lens_id}", summary="删除镜头")
def delete_lens(
    lens_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """删除镜头（需要管理员权限）"""
    return LensService.delete_lens(session, lens_id)

@router.patch("/lenses/{lens_id}/activate", summary="激活镜头")
def activate_lens(
    lens_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """激活镜头（需要管理员权限）"""
    return LensService.activate_lens(session, lens_id)

@router.patch("/lenses/{lens_id}/deactivate", summary="停用镜头")
def deactivate_lens(
    lens_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """停用镜头（需要管理员权限）"""
    return LensService.deactivate_lens(session, lens_id)

@router.get("/lenses/types/", summary="获取镜头类型")
def get_lens_types():
    """获取镜头类型列表（允许所有用户访问）"""
    return LensService.get_lens_types()

@router.get("/lenses/focus-types/", summary="获取对焦方式")
def get_focus_types():
    """获取对焦方式列表（允许所有用户访问）"""
    return LensService.get_focus_types()

@router.get("/lenses/search/", summary="搜索镜头")
def search_lenses(
    q: str,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """搜索镜头（允许所有用户访问）"""
    return LensService.search_lenses(session, q, skip, limit)