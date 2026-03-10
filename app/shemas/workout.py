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
    user_id: int  # если привязано к пользователю

    class Config:
        from_attributes = True
        
# Схема для создания тренировки (то, что приходит в запросе)
class WorkoutCreate(BaseModel):
    name: str
    description: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None

# Схема для ответа с данными тренировки
class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str] = None
    date: datetime
    duration: Optional[int] = None
    
    class Config:
        from_attributes = True
