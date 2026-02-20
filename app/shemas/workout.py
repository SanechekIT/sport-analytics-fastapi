from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Базовый класс - только общие поля
class WorkoutBase(SQLModel):  # Наследуем от SQLModel, но НЕ table=True
    name: str
    date: datetime  # date это дата/время, поэтому datetime, а не int
    duration_minutes: int
    notes: str

# Для создания - все поля из Base (обязательные)
class WorkoutCreate(WorkoutBase):
    pass  # Пустой, потому что берет все поля из Base

# Для чтения/работы с БД - Base + служебные поля
class Workout(WorkoutBase, table=True):  # table=True - это таблица в БД
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
