"""
Репозиторий для работы с упражнениями.
Инкапсулирует хранение и доступ к данным.
"""

from app.models.exercise import Exercise
from typing import Dict, List, Optional


class ExerciseRepository:
    """Класс для работы с данными упражнений."""

    def __init__(self):
        # ПРИВАТНЫЕ ПОЛЯ (с подчеркиванием)
        self._exercises: Dict[int, Exercise] = {}  # ID → Exercise объект
        self._next_id: int = 1  # счетчик для генерации ID

    def create(self, exercise: Exercise) -> Exercise:
        """
        Сохраняет упражнение в репозитории.
        Присваивает ID автоматически.
        """
        # Присваиваем ID из приватного счетчика
        exercise.id = self._next_id

        # Сохраняем объект Exercise в приватном хранилище
        self._exercises[self._next_id] = exercise

        # Увеличиваем приватный счетчик
        self._next_id += 1

        return exercise