import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from io import BytesIO
from sqlmodel import Session, select
import logging

from model.brand import Brand
from model.mount import Mount
from services.brand_service import BrandService
from services.camera_service import CameraService
from services.lens_service import LensService

logger = logging.getLogger(__name__)

class ImportService:
    """数据导入服务，处理 Excel 解析和批量插入逻辑"""

    @staticmethod
    def _get_df(file_content: bytes) -> Optional[pd.DataFrame]:
        try:
            df = pd.read_excel(BytesIO(file_content))
            return df if not df.empty else None
        except Exception as e:
            logger.error(f"Excel read error: {str(e)}")
            return None

    @staticmethod
    def _resolve_relation(session: Session, model: Any, name: str) -> Optional[int]:
        """根据名称解析关联表的 ID"""
        if not name or pd.isna(name):
            return None
        stmt = select(model.id).where(model.name == str(name).strip())
        result = session.exec(stmt).first()
        return result

    @staticmethod
    def _map_row(row: pd.Series, mapping: Dict[str, str], df_columns: List[str]) -> Dict[str, Any]:
        data = {}
        for chi, eng in mapping.items():
            if chi in df_columns:
                val = row[chi]
                if pd.isna(val):
                    data[eng] = None
                elif eng == "is_active":
                    data[eng] = str(val).strip().lower() in ['是', 'yes', 'true', '1', '激活']
                elif eng in ["has_hot_shoe", "has_built_in_flash", "has_wifi", "has_bluetooth", "has_stabilization"]:
                    data[eng] = str(val).strip().lower() in ['是', 'yes', 'true', '1', '有', '支持']
                else:
                    data[eng] = val
        return data

    @staticmethod
    def _batch_import(
        session: Session, 
        file_content: bytes, 
        mapping: Dict[str, str], 
        required_col: str,
        create_func: Callable,
        pre_process: Optional[Callable] = None
    ) -> Dict[str, Any]:
        df = ImportService._get_df(file_content)
        if df is None:
            return {"success": False, "message": "Excel 文件为空或读取失败", "results": []}

        if required_col not in df.columns:
            return {"success": False, "message": f"缺少必要列: {required_col}", "results": []}

        success, failure, results = 0, 0, []
        for index, row in df.iterrows():
            row_num = index + 2
            try:
                data = ImportService._map_row(row, mapping, df.columns)
                if not data.get(mapping[required_col]):
                    raise ValueError(f"{required_col}不能为空")
                
                if pre_process:
                    data = pre_process(session, data, row)
                
                create_func(session, data)
                success += 1
                results.append({"row": row_num, "item": data.get(mapping[required_col]), "status": "success"})
            except Exception as e:
                failure += 1
                results.append({"row": row_num, "item": str(row.get(required_col, "未知")), "status": "failure", "message": getattr(e, "detail", str(e))})

        return {"success": True, "summary": {"total": len(df), "success": success, "failure": failure}, "results": results}

    @staticmethod
    def import_brands(session: Session, file_content: bytes) -> Dict[str, Any]:
        mapping = {"品牌名称": "name", "国家": "country", "官方网站": "website", "品牌描述": "description", "品牌类型": "brand_type", "是否激活": "is_active"}
        
        def pre_proc(s, data, row):
            if data.get("brand_type"):
                t_map = {"相机": "camera", "镜头": "lens", "配件": "accessory"}
                data["brand_type"] = t_map.get(data["brand_type"], data["brand_type"].lower())
            return data

        return ImportService._batch_import(session, file_content, mapping, "品牌名称", BrandService.create_brand, pre_proc)

    @staticmethod
    def import_cameras(session: Session, file_content: bytes) -> Dict[str, Any]:
        mapping = {
            "品牌": "brand_id", "卡口": "mount_id", "型号": "model", "系列": "series", 
            "传感器尺寸": "sensor_size", "像素": "megapixels", "防抖": "ibis_level",
            "热靴": "has_hot_shoe", "内置闪光灯": "has_built_in_flash", "WiFi": "has_wifi",
            "蓝牙": "has_bluetooth", "发布日期": "release_date", "价格": "release_price",
            "重量": "weight", "描述": "description"
        }

        def pre_proc(s, data, row):
            # 解析名称到 ID
            brand_name = row.get("品牌")
            mount_name = row.get("卡口")
            data["brand_id"] = ImportService._resolve_relation(s, Brand, brand_name)
            data["mount_id"] = ImportService._resolve_relation(s, Mount, mount_name)
            if not data["brand_id"]: raise ValueError(f"找不到品牌: {brand_name}")
            if not data["mount_id"]: raise ValueError(f"找不到卡口: {mount_name}")
            return data

        return ImportService._batch_import(session, file_content, mapping, "型号", CameraService.create_camera, pre_proc)

    @staticmethod
    def import_lenses(session: Session, file_content: bytes) -> Dict[str, Any]:
        mapping = {
            "品牌": "brand_id", "卡口": "mount_id", "型号": "model", "系列": "series",
            "最小焦距": "min_focal_length", "最大焦距": "max_focal_length", 
            "最大光圈": "max_aperture_min", "最小光圈": "max_aperture_max",
            "是否恒定光圈": "is_constant_aperture", "防抖": "has_stabilization",
            "对焦方式": "focus_type", "最近对焦距离": "min_focus_distance",
            "重量": "weight", "长度": "length", "滤镜口径": "filter_thread",
            "发布日期": "release_date", "价格": "release_price", "描述": "description"
        }

        def pre_proc(s, data, row):
            brand_name = row.get("品牌")
            mount_name = row.get("卡口")
            data["brand_id"] = ImportService._resolve_relation(s, Brand, brand_name)
            data["mount_id"] = ImportService._resolve_relation(s, Mount, mount_name)
            if not data["brand_id"]: raise ValueError(f"找不到品牌: {brand_name}")
            if not data["mount_id"]: raise ValueError(f"找不到卡口: {mount_name}")
            return data

        return ImportService._batch_import(session, file_content, mapping, "型号", LensService.create_lens, pre_proc)
