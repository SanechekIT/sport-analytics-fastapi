
from app.models.exercise import Exercise
from typing import Dict, List, Optional


class ExerciseRepository:
    def __init__(self):
        self._exercises: Dict[int, Exercise] = {} 
        self._next_id: int = 1 

    def create(self, exercise: Exercise) -> Exercise:
        """
        Сохраняет упражнение в репозитории.
        Присваивает ID автоматически.
        """
        exercise.id = self._next_id
        self._exercises[self._next_id] = exercise
        self._next_id += 1

        return exercise
