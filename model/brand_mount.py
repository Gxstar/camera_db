from sqlmodel import Field, SQLModel, Relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.brand import Brand
    from model.mount import Mount

class BrandMount(SQLModel, table=True):
    """品牌与卡口的关联表，实现多对多关系"""
    
    # 品牌ID
    brand_id: int = Field(foreign_key="brand.id", primary_key=True)
    
    # 卡口ID
    mount_id: int = Field(foreign_key="mount.id", primary_key=True)
    
    # 关联关系
    brand: "Brand" = Relationship()
    mount: "Mount" = Relationship()
    
    # 关联信息
    is_primary: bool = Field(default=False, description="是否为主要卡口")
    compatibility_notes: str = Field(default="", description="兼容性说明")
    
    class Config:
        from_attributes = True