# app/auth.py
from datetime import datetime, timedelta
from jose import jwt
from typing import Optional

SECRET_KEY = "твой_секретный_ключ_минимум_32_символа"  # ЗАМЕНИ!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создаёт JWT токен.

    Args:
        data: Данные для кодирования (обычно {"sub": email})
        expires_delta: Время жизни токена

    Returns:
        JWT токен (строка)
    """
    to_encode = data.copy()

    # Определяем срок действия
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Добавляем время истечения в данные
    to_encode.update({"exp": expire})

    # Создаём токен
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt