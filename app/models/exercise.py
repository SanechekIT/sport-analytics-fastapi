from sqlmodel import SQLModel,Field
from typing import Optional

class Exercise(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    workout_id: int = Field(foreign_key="workout.id")
    description : str
    sets : int =
    reps : int =
    weight : int =
