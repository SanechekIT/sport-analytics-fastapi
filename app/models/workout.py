from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from app.models.base_entry import BaseEntry

class Workout(BaseEntry, table=True):
    __tablename__ = "workouts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)  # ← дата тренировки, оставляем
    duration: Optional[int] = None
    # user_id удалён (есть в BaseEntry)
    # created_at и updated_at удалены (есть в BaseEntry)
