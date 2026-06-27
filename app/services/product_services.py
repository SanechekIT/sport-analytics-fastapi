from sqlalchemy.orm import Session
from datetime import datetime
from app.models.product import Product
from app.schemas.products import ProductCreate, ProductUpdate


class ProductService:
    """Сервис для работы с продуктами (CRUD + бизнес-логика)"""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def create_product(self, product_data: ProductCreate) -> Product:
        """Создаёт новый продукт"""
        # Проверяем дубликат
        existing = self.db.query(Product).filter(
            Product.name == product_data.name,
            Product.user_id == self.user_id
        ).first()

        if existing:
            raise ValueError(f"Продукт с названием '{product_data.name}' уже существует")

        # Создаём продукт
        new_product = Product(
            name=product_data.name,
            calories=product_data.calories,
            proteins=product_data.proteins,
            fats=product_data.fats,
            carbs=product_data.carbs,
            user_id=self.user_id,
            created_at=datetime.utcnow()
        )

        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product

    def get_products(self, skip: int = 0, limit: int = 100) -> list[Product]:
        """Получает все продукты пользователя"""
        return self.db.query(Product).filter(
            Product.user_id == self.user_id
        ).offset(skip).limit(limit).all()

    def get_product(self, product_id: int) -> Product | None:
        """Получает продукт по ID"""
        return self.db.query(Product).filter(
            Product.id == product_id,
            Product.user_id == self.user_id
        ).first()

    def update_product(self, product_id: int, update_data: ProductUpdate) -> Product | None:
        """Обновляет продукт"""
        product = self.get_product(product_id)
        if not product:
            return None

        # Обновляем только переданные поля
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(product, key, value)

        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> bool:
        """Удаляет продукт"""
        product = self.get_product(product_id)
        if not product:
            return False

        self.db.delete(product)
        self.db.commit()
        return True
