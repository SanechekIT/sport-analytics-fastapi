from app.models.meal_item import MealItem
from typing import Dict, List, Optional


class MealItemRepository:
    def __init__(self):
        self._meal_items: Dict[int, MealItem] = {}  # словарь для хранения
        self._next_id: int = 1  # счетчик для ID

    
    def create(self, meal_item: MealItem) -> MealItem:
        """
        Сохраняет блюдо/продукт в репозитории.
        Присваивает ID автоматически.
        """
        meal_item.id = self._next_id
        self._meal_items[self._next_id] = meal_item
        self._next_id += 1

        return meal_item

    # READ ALL (получить все)
    def get_all(self) -> List[MealItem]:
        """
        Возвращает список всех блюд
        """
        return list(self._meal_items.values())

    # READ ONE (получить одно по ID)
    def get_by_id(self, item_id: int) -> Optional[MealItem]:
        """
        Возвращает блюдо по ID или None, если не найдено
        """
        return self._meal_items.get(item_id)

    
    def update(self, item_id: int, updated_data: MealItem) -> Optional[MealItem]:
        """
        Обновляет существующее блюдо
        """
        if item_id not in self._meal_items:
            return None

        # Сохраняем старый ID и обновляем данные
        updated_data.id = item_id
        self._meal_items[item_id] = updated_data

        return updated_data

   
    def delete(self, item_id: int) -> bool:
        """
        Удаляет блюдо. Возвращает True если удалено, False если не найдено
        """
        if item_id in self._meal_items:
            del self._meal_items[item_id]
            return True
        return False

    # Дополнительно: очистить всё (может пригодиться для тестов)
    def clear(self):
        """
        Очищает репозиторий
        """
        self._meal_items.clear()
        self._next_id = 1
