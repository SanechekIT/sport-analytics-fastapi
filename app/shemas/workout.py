from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration: int  # в минутах
    calories_burned: int

class Workout(WorkoutBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

# Схема для создания тренировки (то, что приходит в запросе)
class WorkoutCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None
