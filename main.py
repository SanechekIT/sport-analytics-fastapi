from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class Exercise(BaseModel):
    id: Optional[int]
    name:str
    muscle_group: str
    difficulty: str
exercises_db = []
exercise_id_counter = 1

@app.get("/")
async def root():
    return {
        "message": "Welcome to Fitness API!",
        "version": "1.0.0",
        "endpoints": {
            "get_exercises": "GET /exercises",
            "create_exercise": "POST /exercises"
        }
    }


@app.get("/exercises")
async def get_exercises():
    return {
        "count": len(exercises_db),
        "exercises": exercises_db
    }



@app.post("/exercises")
async def create_exercise(exercise: ExerciseCreate):
    global exercise_id_counter

    # TODO: Добавь здесь логику создания
    # 1. Создай новый словарь с данными упражнения
    # 2. Добавь поле "id" со значением exercise_id_counter
    # 3. Увеличь exercise_id_counter на 1
    # 4. Добавь упражнение в exercises_db
    # 5. Верни созданное упражнение

    pass


# Дополнительно можешь добавить (опционально):
@app.get("/exercises/{exercise_id}")
async def get_exercise_by_id(exercise_id: int):
    """
    Получить упражнение по ID.
    """
    # TODO: Найди упражнение в exercises_db по ID
    # Если не найдено - верни HTTP 404
    pass
