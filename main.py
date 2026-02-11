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

class ExerciseCreate(BaseModel):
    name:str
    muscle_group: str
    difficulty: str

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

    new_exercise = {
        "name": exercise.name,
        "muscle_group": exercise.muscle_group,
        "difficulty": exercise.difficulty
    }

    new_exercise["id"] = exercise_id_counter
    exercise_id_counter += 1
    exercises_db.append(new_exercise)
    return new_exercise


@app.get("/exercises/{exercise_id}")
async def get_exercise_by_id(exercise_id: int):
     for exercise in exercises_db:
        if exercise["id"] == exercise_id:
            return exercise

    # Если не нашли — ошибка 404
    raise HTTPException(status_code=404, detail="Exercise not found")
