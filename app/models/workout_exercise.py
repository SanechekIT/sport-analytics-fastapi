from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class WorkoutExercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workout_id: int = Field(foreign_key="workout.id")
    exercise_id: int = Field(foreign_key="exercise.id")
    sets: int  # количество подходов
    reps: int  # количество повторений
    weight: Optional[float] = None  # вес (может быть None для упражнений с весом тела)
    notes: Optional[str] = None  # заметки к конкретному упражнению