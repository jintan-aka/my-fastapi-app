from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.engine import Result

import api.models.task as task_model
import api.schemas.task as task_schema


# タスク作成
async def create_task(
    db: AsyncSession, task_create: task_schema.TaskCreate
) -> task_model.Task:
    task = task_model.Task(**task_create.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


# タスク一覧取得（done状態含む）
async def get_tasks_with_done(db: AsyncSession) -> List[Tuple[int, str, bool]]:
    result: Result = await db.execute(
        select(
            task_model.Task.id,
            task_model.Task.title,
            task_model.Done.id.isnot(None).label("done"),
        ).outerjoin(task_model.Done)
    )
    return result.all()


# 単一タスク取得
async def get_task(db: AsyncSession, task_id: int) -> Optional[task_model.Task]:
    result: Result = await db.execute(
        select(task_model.Task).filter(task_model.Task.id == task_id)
    )
    task: Optional[Tuple[task_model.Task]] = result.first()
    return task[0] if task is not None else None


# タスク更新
async def update_task(
    db: AsyncSession, task_create: task_schema.TaskCreate, original: task_model.Task
) -> task_model.Task:
    original.title = task_create.title
    original.due_date = task_create.due_date
    db.add(original)
    await db.commit()
    await db.refresh(original)
    return original


# タスク削除
async def delete_task(db: AsyncSession, original: task_model.Task) -> None:
    await db.delete(original)
    await db.commit()


# 今日が締切のタスク一覧取得
async def get_tasks_due_today(db: AsyncSession) -> List[Dict]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    result: Result = await db.execute(
        select(task_model.Task)
        .filter(task_model.Task.due_date >= today, task_model.Task.due_date < tomorrow)
        .options(joinedload(task_model.Task.done))  # ← これで事前ロードOK
    )
    tasks = result.scalars().all()

    return [
        {
            "id": task.id,
            "title": task.title,
            "due_date": task.due_date.isoformat(),
            "done": task.done is not None
        }
        for task in tasks
    ]
