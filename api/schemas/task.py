from typing import Optional

from pydantic import BaseModel, Field

from datetime import datetime


class TaskBase(BaseModel):
    title: Optional[str] = Field(None, example="クリーニングを取りに行く")
    due_date: Optional[datetime] = Field(None, example="2025-04-30T12:00:00")  # ← 追加！


class TaskCreate(TaskBase):
    pass


class TaskCreateResponse(TaskCreate):
    id: int

    class Config:
        orm_mode = True


class Task(TaskBase):
    id: int
    done: bool = Field(False, description="完了フラグ")

    class Config:
        orm_mode = True