# app/api/products.py (добавляем новый эндпоинт)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.schemas.products import ProductCreate, Product as ProductSchema
from app.models.product import Product  # Твоя SQLAlchemy модель
from app.database.connection import get_db

router = APIRouter()

# ... (твои существующие эндпоинты)

@router.post("/manual", response_model=ProductSchema)
async def create_product_manually(
    product_data: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Создает новый продукт на основе ручного ввода пользователя.
    
    Поля:
    - **name**: Название продукта
    - **calories**: Калории на 100 г
    - **proteins**: Белки на 100 г
    - **fats**: Жиры на 100 г
    - **carbs**: Углеводы на 100 г
    """
    try:
        # Проверяем, нет ли уже продукта с таким названием у этого пользователя
        # TODO: Заменить user_id=1 на ID текущего авторизованного пользователя
        existing_product = db.query(Product).filter(
            Product.name == product_data.name,
            Product.user_id == 1
        ).first()
        
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Продукт с названием '{product_data.name}' уже существует"
            )
        
        # Создаём новый продукт
        new_product = Product(
            name=product_data.name,
            calories=product_data.calories,
            proteins=product_data.proteins,
            fats=product_data.fats,
            carbs=product_data.carbs,
            user_id=1,  # TODO: Взять из авторизации
            created_at=datetime.utcnow()
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Возвращаем созданный продукт
        return ProductSchema(
            id=new_product.id,
            name=new_product.name,
            calories=new_product.calories,
            proteins=new_product.proteins,
            fats=new_product.fats,
            carbs=new_product.carbs,
            user_id=new_product.user_id,
            created_at=new_product.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при создании продукта: {str(e)}"
        )
