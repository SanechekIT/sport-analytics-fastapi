from pydantic import BaseModel
from typing import Optional

class WorkoutExerciseBase(BaseModel):
    """
    Базовая схема для упражнения в тренировке.
    Содержит поля, которые есть во всех операциях.
    """
    exercise_id: int
    sets: int
    reps: int
    weight: Optional[float] = None  # Вес может быть None (например, упражнения с весом тела)
    notes: Optional[str] = None
    
    class Config:
        orm_mode = True

class WorkoutExerciseCreate(WorkoutExerciseBase):
    """
    Схема для создания записи об упражнении в тренировке.
    Наследует все поля от Base.
    При создании нам не нужен id и workout_id, 
    потому что workout_id мы возьмем из URL или контекста.
    """
    pass

class WorkoutExercise(WorkoutExerciseBase):
    """
    Полная схема для чтения/ответа.
    Содержит все поля, включая id и workout_id.
    """
    id: int
    workout_id: int
    
    class Config:
        orm_mode = True
