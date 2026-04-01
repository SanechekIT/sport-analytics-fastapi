from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app import models, schemas
from app.database import get_db
from datetime import datetime

router = APIRouter(prefix="/meals", tags=["meals"])

@router.post("/", response_model=schemas.Meal, status_code=status.HTTP_201_CREATED)
def create_meal(meal: schemas.MealCreate, db: Session = Depends(get_db)):
    """Создать прием пищи"""
    try:
        db_meal = models.Meal(
            name=meal.name,
            meal_type=meal.meal_type,
            date_time=meal.date_time,
            notes=meal.notes
        )
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        return db_meal
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании приема пищи: {str(e)}"
        )

@router.get("/", response_model=list[schemas.Meal])
def list_meals(
    skip: int = 0, 
    limit: int = 100,
    meal_type: str = None,
    date_from: datetime = None,
    date_to: datetime = None,
    db: Session = Depends(get_db)
):
    """Список приемов с возможностью фильтрации"""
    query = db.query(models.Meal)
    
    # Фильтрация по типу приема
    if meal_type:
        query = query.filter(models.Meal.meal_type == meal_type)
    
    # Фильтрация по дате
    if date_from:
        query = query.filter(models.Meal.date_time >= date_from)
    if date_to:
        query = query.filter(models.Meal.date_time <= date_to)
    
    meals = query.order_by(models.Meal.date_time.desc()).offset(skip).limit(limit).all()
    return meals

@router.get("/{id}", response_model=schemas.Meal)
def get_meal(id: int, db: Session = Depends(get_db)):
    """Детали приема с продуктами"""
    meal = db.query(models.Meal).filter(models.Meal.id == id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прием пищи с id {id} не найден"
        )
    return meal

@router.put("/{id}", response_model=schemas.Meal)
def update_meal(id: int, meal_update: schemas.MealUpdate, db: Session = Depends(get_db)):
    """Обновить прием пищи"""
    db_meal = db.query(models.Meal).filter(models.Meal.id == id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прием пищи с id {id} не найден"
        )
    
    try:
        update_data = meal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_meal, field, value)
        
        db.commit()
        db.refresh(db_meal)
        return db_meal
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при обновлении: {str(e)}"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(id: int, db: Session = Depends(get_db)):
    """Удалить прием пищи"""
    db_meal = db.query(models.Meal).filter(models.Meal.id == id).first()
    if not db_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прием пищи с id {id} не найден"
        )
    
    try:
        db.delete(db_meal)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при удалении: {str(e)}"
        )

@router.post("/{meal_id}/items/", response_model=schemas.MealItem, status_code=status.HTTP_201_CREATED)
def add_item(meal_id: int, item: schemas.MealItemCreate, db: Session = Depends(get_db)):
    """Добавить продукт в прием пищи"""
    # Проверяем существует ли прием пищи
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прием пищи с id {meal_id} не найден"
        )
    
    # Проверяем существует ли продукт
    food = db.query(models.Food).filter(models.Food.id == item.food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукт с id {item.food_id} не найден"
        )
    
    # Проверяем нет ли уже такого продукта в этом приеме
    existing_item = db.query(models.MealItem).filter(
        models.MealItem.meal_id == meal_id,
        models.MealItem.food_id == item.food_id
    ).first()
    
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Этот продукт уже добавлен в прием. Используйте PUT для изменения количества"
        )
    
    try:
        db_item = models.MealItem(
            meal_id=meal_id,
            food_id=item.food_id,
            quantity=item.quantity,
            unit=item.unit
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при добавлении продукта: {str(e)}"
        )

@router.put("/items/{item_id}", response_model=schemas.MealItem)
def update_item(item_id: int, item_update: schemas.MealItemUpdate, db: Session = Depends(get_db)):
    """Изменить количество продукта в приеме"""
    db_item = db.query(models.MealItem).filter(models.MealItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент приема с id {item_id} не найден"
        )
    
    try:
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при обновлении: {str(e)}"
        )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Удалить продукт из приема"""
    db_item = db.query(models.MealItem).filter(models.MealItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент приема с id {item_id} не найден"
        )
    
    try:
        db.delete(db_item)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при удалении: {str(e)}"
        )pass
