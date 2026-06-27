
from app.services.product_service import ProductService

class ProviderFactory:
    """
    Фабрика для создания сервисов работы с продуктами.
    
    Сейчас поддерживает только ручной ввод (ProductService),
    но в будущем можно добавить:
    - OpenFoodProvider (автоматический поиск по штрих-коду)
    - USDAProvider (поиск в базе USDA)
    - CachedProvider (кэширование)
    
    Это позволяет легко подменять реализацию без изменения эндпоинтов.
    """
    
    @staticmethod
    def get_product_service(db, user_id: int) -> ProductService:
        """
        Возвращает сервис для работы с продуктами.
        
        Args:
            db: Сессия SQLAlchemy
            user_id: ID текущего пользователя
            
        Returns:
            ProductService: Экземпляр сервиса продуктов
        """
        return ProductService(db, user_id)
