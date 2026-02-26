from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Workout(SQLModel, table=True):
    __tablename__ = "workouts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[int] = None
