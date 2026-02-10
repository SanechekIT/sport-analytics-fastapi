from pydantic import BaseModel, EmailStr, validator, Field
from datetime import datetime
from typing import Optional


# 1. Схема для создания пользователя (регистрация)
class UserCreate(BaseModel):
    """
    Схема для регистрации нового пользователя.
    Используется в POST /register
    """
    email: EmailStr  # EmailStr автоматически проверяет формат email
    username: str = Field(..., min_length=3, max_length=50)  # от 3 до 50 символов
    password: str = Field(..., min_length=6)  # минимум 6 символов
    password_confirm: str  # поле для подтверждения пароля

    # Валидатор - проверяет, что password и password_confirm совпадают
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """
        Этот метод вызывается Pydantic при валидации.
        v - значение password_confirm
        values - уже проверенные значения других полей
        """
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    # Опционально: можно добавить валидатор для сложности пароля
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        # Можно добавить проверку на наличие цифр/букв и т.д.
        return v


# 2. Схема для входа пользователя
class UserLogin(BaseModel):
    """
    Схема для входа пользователя.
    Используется в POST /login
    """
    email: EmailStr  # Вход по email
    password: str

    # Альтернатива: можно сделать вход по username ИЛИ email
    # Для этого нужно было бы использовать Union или сделать поле необязательным


# 3. Схема для ответа с информацией о пользователе
class UserResponse(BaseModel):
    """
    Схема для ответа API с информацией о пользователе.
    НИКОГДА не включает пароль!
    Используется как response_model в эндпоинтах.
    """
    id: int  # ID из базы данных
    email: EmailStr
    username: str
    is_active: bool = True  # по умолчанию True
    created_at: datetime  # когда создан пользователь

    class Config:
        """
        Конфигурация Pydantic.
        from_attributes позволяет создавать схему из SQLAlchemy модели
        (заменяет orm_mode = True из Pydantic v1)
        """
        from_attributes = True


# 4. Схема для ответа с JWT токеном
class Token(BaseModel):
    """
    Схема для ответа с JWT токеном после успешного логина.
    """
    access_token: str  # сам JWT токен
    token_type: str = "bearer"  # тип токена, обычно "bearer"

    # Можно добавить время жизни токена, если хочешь
    # expires_in: int = 3600  # в секундах


# 5. Опционально: схема для данных внутри JWT токена
class TokenData(BaseModel):
    """
    Схема для данных, которые хранятся внутри JWT токена.
    Используется при декодировании токена.
    """
    email: Optional[str] = None  # 'sub' (subject) в JWT обычно содержит email/id пользователя
    # Можно добавить другие данные: user_id, permissions и т.д.


# 6. Опционально: схема для обновления профиля
class UserUpdate(BaseModel):
    """
    Схема для обновления данных пользователя.
    Все поля необязательные - можно обновлять только то, что нужно.
    """
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

    # Пароль обычно обновляется отдельным эндпоинтом
    # current_password: Optional[str] = None
    # new_password: Optional[str] = None
