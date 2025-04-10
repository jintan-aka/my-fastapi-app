from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from api.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(1024))
    due_date = Column(DateTime, nullable=True)

    # Doneとの1対1リレーション（uselist=False が超重要！）
    done = relationship("Done", back_populates="task", cascade="delete", uselist=False)


class Done(Base):
    __tablename__ = "dones"

    id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)

    # Taskとのリレーション
    task = relationship("Task", back_populates="done")
