from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from typing import Dict, Any

from app.database.connection import get_db
from app.models.meal import Meal
from app.models.workout import Workout
from app.models.meal_item import MealItem
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    user_id: int = 1,  # временно, позже из auth
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Главная статистика дашборда:
    - общее количество калорий за сегодня
    - количество тренировок за сегодня
    - прогресс по целям (если есть)
    """
    today = date.today()
    
    # Сумма калорий из Meal (если у вас прямая связь)
    total_calories = db.query(func.sum(Meal.calories)).filter(
        Meal.user_id == user_id,
        Meal.date == today
    ).scalar() or 0
    
    # ИЛИ через MealItem (зависит от вашей схемы)
    # total_calories = db.query(func.sum(MealItem.calories)).filter(
    #     MealItem.user_id == user_id,
    #     MealItem.date == today
    # ).scalar() or 0
    
    # Количество тренировок за сегодня
    workouts_count = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date == today
    ).count()
    
    # (Опционально) Цель по калориям на день
    user = db.query(User).filter(User.id == user_id).first()
    daily_calorie_goal = user.daily_calorie_goal if user else 2000
    
    progress_percent = round((total_calories / daily_calorie_goal) * 100, 1) if daily_calorie_goal > 0 else 0
    
    return {
        "date": today.isoformat(),
        "total_calories": total_calories,
        "daily_goal": daily_calorie_goal,
        "progress_percent": progress_percent,
        "workouts_count": workouts_count,
        "message": f"✅ Сегодня: {total_calories}/{daily_calorie_goal} ккал, {workouts_count} тренировок"
    }


@router.get("/stats/{date_str}")
def get_stats_by_date(
    date_str: str,
    user_id: int = 1,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Статистика за конкретную дату
    Пример: /dashboard/stats/2025-05-04
    """
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте YYYY-MM-DD")
    
    total_calories = db.query(func.sum(Meal.calories)).filter(
        Meal.user_id == user_id,
        Meal.date == target_date
    ).scalar() or 0
    
    workouts_count = db.query(Workout).filter(
        Workout.user_id == user_id,
        Workout.date == target_date
    ).count()
    
    return {
        "date": target_date.isoformat(),
        "total_calories": total_calories,
        "workouts_count": workouts_count
    }
