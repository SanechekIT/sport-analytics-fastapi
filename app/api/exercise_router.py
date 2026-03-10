from fastapi import APIRouter, HTTPException, status
from app.models.mealitem import MealItem
from app.shemas.meal_item import MealItemCreate, MealItemUpdate
from app.repositories.meal_item_repository import MealItemRepository
from typing import List
# Создаю роутер
router = APIRouter(prefix="/products", tags=["products"])

# Создаю один экземпляр репозитория для всех эндпоинтов
repository = MealItemRepository()


# POST /products/ - СОЗДАНИЕ (Create)
@router.post("/", response_model=MealItem, status_code=status.HTTP_201_CREATED)
def create_product(product: MealItemCreate):
    """
    Создает новый продукт

    - **name**: название продукта
    - **description**: описание (необязательно)
    - **calories**: калории
    - **protein**: белки
    - **fat**: жиры
    - **carbohydrates**: углеводы
    """
    # Преобразуем схему создания в модель
    new_product = MealItem(**product.dict())
    # Сохраняем в репозитории
    created = repository.create(new_product)
    return created


# GET /products/ - ПОЛУЧЕНИЕ ВСЕХ (Read All)
@router.get("/", response_model=List[MealItem])
def get_all_products():
    """
    Возвращает список всех продуктов
    """
    return repository.get_all()


# GET /products/{product_id} - ПОЛУЧЕНИЕ ОДНОГО (Read One)
@router.get("/{product_id}", response_model=MealItem)
def get_product(product_id: int):
    """
    Возвращает продукт по его ID
    """
    product = repository.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукт с ID {product_id} не найден"
        )
    return product


# PUT /products/{product_id} - ОБНОВЛЕНИЕ (Update)
@router.put("/{product_id}", response_model=MealItem)
def update_product(product_id: int, product_update: MealItemUpdate):
    """
    Обновляет существующий продукт

    - **product_id**: ID продукта для обновления
    - **product_update**: новые данные (все поля опциональны)
    """
    # Создаем продукт с обновленными данными
    updated_data = MealItem(**product_update.dict())
    updated = repository.update(product_id, updated_data)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукт с ID {product_id} не найден"
        )
    return updated


# DELETE /products/{product_id} - УДАЛЕНИЕ (Delete)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    """
    Удаляет продукт по ID
    """
    deleted = repository.delete(product_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Продукт с ID {product_id} не найден"
        )
    # Для 204 статуса ничего не возвращаем
    return None


# Дополнительно: поиск по названию (если нужен)
@router.get("/search/", response_model=List[MealItem])
def search_products(query: str):
    """
    Ищет продукты по названию (частичное совпадение)
    """
    all_products = repository.get_all()
    results = [
        product for product in all_products
        if query.lower() in product.name.lower()
    ]
    return results
