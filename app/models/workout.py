from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None  # или datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")
    notes: str

    # Добавил relationship:
    exercises: List["WorkoutExercise"] = Relationship(back_populates="workout")
