"""Pydantic 请求/响应模型。"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """创建笔记请求体。"""

    content: str = Field(..., min_length=1, max_length=2000)


class NoteOut(BaseModel):
    """笔记响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    content: str
    created_at: datetime


class BatchCreate(BaseModel):
    """创建批次请求体。"""

    type: str = Field(..., min_length=1, max_length=100)
    start_date: date
    temperature: float
    status: str = Field(..., min_length=1, max_length=50)
    ph: float | None = None


class BatchUpdate(BaseModel):
    """更新批次请求体。"""

    type: str | None = Field(None, min_length=1, max_length=100)
    start_date: date | None = None
    temperature: float | None = None
    status: str | None = Field(None, min_length=1, max_length=50)
    ph: float | None = None


class BatchOut(BaseModel):
    """批次列表项响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    start_date: date
    temperature: float
    status: str
    ph: float | None
    created_at: datetime


class BatchDetail(BatchOut):
    """批次详情（含笔记）。"""

    notes: list[NoteOut] = []
