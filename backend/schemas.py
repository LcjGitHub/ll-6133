"""Pydantic 请求/响应模型。"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """创建笔记请求体。"""

    content: str = Field(..., min_length=1, max_length=2000)


class NoteUpdate(BaseModel):
    """更新笔记请求体。"""

    content: str = Field(..., min_length=1, max_length=2000)


class NoteOut(BaseModel):
    """笔记响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    content: str
    created_at: datetime


class MeasurementCreate(BaseModel):
    """创建测量记录请求体。"""

    recorded_at: datetime
    temperature: float
    ph: float | None = None


class MeasurementOut(BaseModel):
    """测量记录响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    recorded_at: datetime
    temperature: float
    ph: float | None
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
    fermentation_days: int


class BatchDetail(BatchOut):
    """批次详情（含笔记和测量记录）。"""

    notes: list[NoteOut] = []
    measurements: list[MeasurementOut] = []


class RecipeStepCreate(BaseModel):
    """创建配方步骤请求体。"""

    step_order: int = Field(..., ge=1)
    description: str = Field(..., min_length=1, max_length=2000)


class RecipeStepUpdate(BaseModel):
    """更新配方步骤请求体。"""

    step_order: int | None = Field(None, ge=1)
    description: str | None = Field(None, min_length=1, max_length=2000)


class RecipeStepOut(BaseModel):
    """配方步骤响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    step_order: int
    description: str
    created_at: datetime


class RecipeCreate(BaseModel):
    """创建配方请求体。"""

    name: str = Field(..., min_length=1, max_length=200)
    ferment_type: str = Field(..., min_length=1, max_length=100)
    ingredients: str = Field(..., min_length=1, max_length=5000)
    steps: list[RecipeStepCreate] = []


class RecipeUpdate(BaseModel):
    """更新配方请求体。"""

    name: str | None = Field(None, min_length=1, max_length=200)
    ferment_type: str | None = Field(None, min_length=1, max_length=100)
    ingredients: str | None = Field(None, min_length=1, max_length=5000)
    steps: list[RecipeStepCreate] | None = None


class RecipeOut(BaseModel):
    """配方列表项响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    ferment_type: str
    ingredients: str
    created_at: datetime


class RecipeDetail(RecipeOut):
    """配方详情（含步骤）。"""

    steps: list[RecipeStepOut] = []


class StatisticsOut(BaseModel):
    """统计数据响应。"""

    model_config = ConfigDict(from_attributes=True)

    status_counts: dict[str, int]
    type_counts: dict[str, int]
    recent_notes_count: int


class ReminderCreate(BaseModel):
    """创建提醒请求体。"""

    batch_id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=200)
    reminder_date: date


class ReminderUpdate(BaseModel):
    """更新提醒请求体。"""

    batch_id: int | None = Field(None, ge=1)
    title: str | None = Field(None, min_length=1, max_length=200)
    reminder_date: date | None = None
    completed: bool | None = None


class ReminderOut(BaseModel):
    """提醒响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: int
    title: str
    reminder_date: date
    completed: bool
    created_at: datetime


class ImportResult(BaseModel):
    """数据导入结果。"""

    inserted_batches: int
    skipped_batches: int
    inserted_notes: int
    skipped_notes: int
    total_batches_in_file: int
    total_notes_in_file: int
