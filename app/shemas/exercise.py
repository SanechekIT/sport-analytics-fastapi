from typing import Optional
from sqlmodel import SQLModel, Field


# Базовая схема с полями для создания/обновления(которые может указывать пользователь)
class ExerciseBase(SQLModel):
    name: str = Field(min_length=1, max_length=255, description="Название упражнения")
    workout_id: int = Field(foreign_key="workout.id", description="ID тренировки")
    description: Optional[str] = Field(default=None, description="Описание упражнения")
    sets: int = Field(gt=0, description="Количество подходов")
    reps: int = Field(gt=0, description="Количество повторений")
    weight: Optional[int] = Field(default=None, gt=0, description="Вес в кг (None если с весом тела)")


# Здесь создаю схему для создания упражнения
class ExerciseCreate(ExerciseBase):
    """
    Схема для создания нового упражнения.
    Используется при POST запросах.
    Не содержит id, так как его генерирует БД.
    """
    pass


# Схема для обновления упражнения
class ExerciseUpdate(SQLModel):
    """
    Схема для обновления упражнения.
    Все поля опциональные - можно обновить только указанные.
    """
    name: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Название упражнения")
    workout_id: Optional[int] = Field(default=None, foreign_key="workout.id", description="ID тренировки")
    description: Optional[str] = Field(default=None, description="Описание упражнения")
    sets: Optional[int] = Field(default=None, gt=0, description="Количество подходов")
    reps: Optional[int] = Field(default=None, gt=0, description="Количество повторений")
    weight: Optional[int] = Field(default=None, gt=0, description="Вес в кг")


# Схема для ответа от API
class ExercisePublic(ExerciseBase):
    """
    Схема упражнения для ответа API.
    Содержит все поля, включая ID из базы данных.
    """
    id: int = Field(description="Уникальный идентификатор упражнения") 
