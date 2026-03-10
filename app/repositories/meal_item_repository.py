from app.models.mealitem import MealItem
from typing import Dict, List, Optional


class MealItemRepository:
    def __init__(self):
        self._meal_items: Dict[int, MealItem] = {}
        self._next_id: int = 1

    def create(self, meal_item: MealItem) -> MealItem:
        meal_item.id = self._next_id
        self._meal_items[self._next_id] = meal_item
        self._next_id += 1
        return meal_item

    def get_all(self) -> List[MealItem]:
        return list(self._meal_items.values())

    def get_by_id(self, item_id: int) -> Optional[MealItem]:
        return self._meal_items.get(item_id)

    def update(self, item_id: int, updated_data: MealItem) -> Optional[MealItem]:
        if item_id not in self._meal_items:
            return None
        updated_data.id = item_id
        self._meal_items[item_id] = updated_data
        return updated_data

    def delete(self, item_id: int) -> bool:
        if item_id in self._meal_items:
            del self._meal_items[item_id]
            return True
        return False
