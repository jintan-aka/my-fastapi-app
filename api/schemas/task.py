from typing import Optional
from pydantic import BaseModel, Field, ConfigDict  # ← ConfigDictを追加
from datetime import datetime


class TaskBase(BaseModel):
    title: Optional[str] = Field(None, json_schema_extra={"example": "クリーニングを取りに行く"})
    due_date: Optional[datetime] = Field(None, json_schema_extra={"example": "2025-04-30T12:00:00"})


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    id: int
    due_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class Task(TaskBase):
    id: int
    done: bool = Field(False, description="完了フラグ")

    model_config = ConfigDict(from_attributes=True)
