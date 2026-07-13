from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app import models, schemas
from app.database import get_db
from app.utils.text_parser import parse_meal_text
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


@router.get("/", response_model=schemas.MealPaginatedResponse)
def list_meals(
    skip: int = 0, 
    limit: int = 100,
    meal_type: str = None,
    date_from: datetime = None,
    date_to: datetime = None,
    db: Session = Depends(get_db)
):
    """Список приемов с пагинацией и фильтрацией"""
    query = db.query(models.Meal)
    
    if meal_type:
        query = query.filter(models.Meal.meal_type == meal_type)
    
    if date_from:
        query = query.filter(models.Meal.date_time >= date_from)
    if date_to:
        query = query.filter(models.Meal.date_time <= date_to)
    
    # Подсчёт общего количества
    total = query.count()
    
    meals = query.order_by(models.Meal.date_time.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": meals,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/daily/", response_model=list[schemas.Meal])
def get_meals_by_date(
    date: str = None,
    db: Session = Depends(get_db)
):
    """
    Получить все приёмы пищи за конкретную дату.
    Пример: /meals/daily/?date=2025-04-15
    """
    if not date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Параметр 'date' обязателен. Пример: ?date=2025-04-15"
        )
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        start_of_day = target_date.replace(hour=0, minute=0, second=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте ГГГГ-ММ-ДД, например: 2025-04-15"
        )
    
    meals = db.query(models.Meal).filter(
        models.Meal.date_time >= start_of_day,
        models.Meal.date_time <= end_of_day
    ).order_by(models.Meal.date_time).all()
    
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
    meal = db.query(models.Meal).filter(models.Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прием пищи с id {meal_id} не найден"
        )
    
    food = db.query(models.Food).filter(models.Food.id == item.food_id).first()
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукт с id {item.food_id} не найден"
        )
    
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
        )

@router.post("/from-text", response_model=schemas.Meal, status_code=status.HTTP_201_CREATED)
def create_meal_from_text(
    request: schemas.MealFromTextRequest,
    db: Session = Depends(get_db)
):
    """
    Создать приём пищи из текста.
    
    Пример запроса:
    {
        "text": "курица 200г рис 150г",
        "meal_type": "lunch"
    }
    """
    # Проверка на пустой текст
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текст не может быть пустым"
        )
    
    try:
        # 1. Парсим текст
        items = parse_meal_text(request.text)
        
        if not items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось распознать продукты в тексте. Пример: 'курица 200г рис 150г'"
            )
        
        # 2. Создаём приём пищи
        db_meal = models.Meal(
            name=f"Приём из текста: {request.text[:50]}..." if len(request.text) > 50 else f"Приём из текста: {request.text}",
            meal_type=request.meal_type,
            date_time=datetime.now(),
            notes=request.text
        )
        db.add(db_meal)
        db.flush()
        
        # 3. Для каждого продукта ищем в БД или создаём
        for item in items:
            food = db.query(models.Food).filter(
                models.Food.name.ilike(f"%{item['name']}%")
            ).first()
            
            if not food:
                food = models.Food(
                    name=item['name'],
                    calories_per_100g=0,
                    protein_per_100g=0,
                    fats_per_100g=0,
                    carbs_per_100g=0
                )
                db.add(food)
                db.flush()
            
            meal_item = models.MealItem(
                meal_id=db_meal.id,
                food_id=food.id,
                quantity=item['weight'],
                unit="g"
            )
            db.add(meal_item)
        
        db.commit()
        db.refresh(db_meal)
        return db_meal
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании приёма из текста: {str(e)}"
        )
