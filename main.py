from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from app.database.connection import get_db as get_session
from app.models.user import User
from app.models.workout import Workout
from app.models.exercise import Exercise
from schemas import UserCreate, WorkoutCreate, ExerciseCreate

@app.get("/")
async def root():
    return {
        "message": "Fitness Tracker API",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/register")
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    # Проверяю, нет ли уже такого пользователя
    existing = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Создаю пользователя (пароль нужно хешировать)
    user = User(email=user_data.email, password=user_data.password)  # TODO: хешировать пароль
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Пользователь создан", "user_id": user.id}

@app.post("/login")
def login(user_data: UserCreate, session: Session = Depends(get_session)):
    # Ищу пользователя по email
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяю пароль (в реальности сравниваем хеши)
    if user.password != user_data.password:  # TODO: сравнивать хеши
        raise HTTPException(status_code=400, detail="Неверный пароль")
    
    return {"message": "Успешный вход", "user_id": user.id}

@app.get("/users/me")
def get_current_user(user_id: int, session: Session = Depends(get_session)):
    # В реальности user_id берется из токена
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@app.post("/exercises")
def create_exercise(exercise_data: ExerciseCreate, session: Session = Depends(get_session)):
    exercise = Exercise(**exercise_data.dict())
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise

@app.get("/exercises")
def get_all_exercises(session: Session = Depends(get_session)):
    exercises = session.exec(select(Exercise)).all()
    return exercises

@app.get("/exercises/{exercise_id}")
def get_exercise_by_id(exercise_id: int, session: Session = Depends(get_session)):
    exercise = session.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Упражнение не найдено")
    return exercise

@app.post("/workouts", response_model=WorkoutSchema)
def create_workout(
    workout_data: WorkoutCreate,
    user_id: int,  # В реальности из токена
    session: Session = Depends(get_session)
):
    workout = Workout(**workout_data.dict(), user_id=user_id)
    session.add(workout)
    session.commit()
    session.refresh(workout)
    return workout

@app.get("/workouts")
def get_workouts(
    user_id: int,  # В реальности из токена
    session: Session = Depends(get_session)
):
    workouts = session.exec(select(Workout).where(Workout.user_id == user_id)).all()
    return workouts

@app.post("/workouts/{workout_id}/exercises")
def add_exercise_to_workout(
    workout_id: int,
    exercise_data: dict,  # Тут будет {exercise_id, sets, reps, weight}
    user_id: int,  # В реальности из токена
    session: Session = Depends(get_session)
):
    # Проверяю, что тренировка существует и принадлежит пользователю
    workout = session.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    if workout.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой тренировке")
    
    # Проверяю, что упражнение существует
    exercise = session.get(Exercise, exercise_data["exercise_id"])
    if not exercise:
        raise HTTPException(status_code=404, detail="Упражнение не найдено")
    
    # Создаю запись упражнения в тренировке
    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        **exercise_data
    )
    session.add(workout_exercise)
    session.commit()
    session.refresh(workout_exercise)
    return workout_exercise

@app.get("/workouts/{workout_id}")
def get_workout_by_id(
    workout_id: int,
    user_id: int,  # В реальности из токена
    session: Session = Depends(get_session)
):
    # Загружаю тренировку с упражнениями
    workout = session.get(Workout, workout_id)
    if not workout:
        raise HTTPException(status_code=404, detail="Тренировка не найдена")
    if workout.user_id != user_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой тренировке")
    
    # Подгружаю упражнения
    exercises = session.exec(
        select(WorkoutExercise).where(WorkoutExercise.workout_id == workout_id)
    ).all()
    
    return {
        "workout": workout,
        "exercises": exercises
    }

@app.get("/workouts/history")
def get_workouts_history(
    user_id: int,  # В реальности из токена
    session: Session = Depends(get_session)
):
    # Получаю все тренировки пользователя с упражнениями
    workouts = session.exec(
        select(Workout).where(Workout.user_id == user_id).order_by(Workout.date.desc())
    ).all()
    
    # Собираю статистику по упражнениям
    exercise_stats = {}
    all_workout_exercises = []
    
    for workout in workouts:
        exercises = session.exec(
            select(WorkoutExercise).where(WorkoutExercise.workout_id == workout.id)
        ).all()
        all_workout_exercises.extend(exercises)
        
        # Считаю частоту упражнений
        for we in exercises:
            if we.exercise_id not in exercise_stats:
                exercise_stats[we.exercise_id] = {
                    "count": 0,
                    "max_weight": 0,
                    "exercise": session.get(Exercise, we.exercise_id)
                }
            exercise_stats[we.exercise_id]["count"] += 1
            if we.weight > exercise_stats[we.exercise_id]["max_weight"]:
                exercise_stats[we.exercise_id]["max_weight"] = we.weight
    
    # Топ упражнений (по частоте)
    top_exercises = sorted(
        [{"name": v["exercise"].name, "count": v["count"], "max_weight": v["max_weight"]} 
         for v in exercise_stats.values()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]  # Топ-5
    
    # Прогресс (рост весов по датам)
    progress = {}
    for we in sorted(all_workout_exercises, key=lambda x: x.date):
        if we.exercise_id not in progress:
            progress[we.exercise_id] = []
        progress[we.exercise_id].append({
            "date": we.date,
            "weight": we.weight,
            "reps": we.reps
        })
    
    return {
        "trainings": workouts,
        "top_exercises": top_exercises,
        "progress": progress
    }
