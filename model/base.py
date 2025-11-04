# sqlmodel构建的基础模型
from sqlmodel import Field, SQLModel
from datetime import datetime

class BaseModel(SQLModel):
    id: int = Field(default=None, primary_key=True)
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)