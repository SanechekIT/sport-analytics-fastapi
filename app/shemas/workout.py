from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
