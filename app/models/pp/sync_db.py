
import sys
import os
from sqlmodel import SQLModel, create_engine

# Добавляем текущую папку в путь
sys.path.append(os.path.dirname(__file__))

# Импортируем модель (после переименования)
from app.models.pp.product_model import Product

# Создаем подключение к БД
engine = create_engine("sqlite:///database.db")

# Создаем таблицы
SQLModel.metadata.create_all(engine)

print("✅ Таблица Product успешно создана!")
print(f"📁 База данных: {os.path.abspath('database.db')}")