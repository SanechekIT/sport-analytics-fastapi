from sqlmodel import SQLModel, Field
from typing import Optional

class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    workout_id: int = Field(foreign_key="workout.id")
    description: Optional[str] = Field(default=None)  
    sets: int
    reps: int
    weight: Optional[int] = Field(default=None)  # вес может быть None (упражнения с весом тела)
