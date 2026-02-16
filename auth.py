# app/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Импорт модели пользователя (путь может отличаться!)
from models import User

# Конфигурация
SECRET_KEY = "cdsfzxcvfr1333468hdbsyzm_extra_chars_here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ========== ХЕШИРОВАНИЕ (новое) ==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)


# ========== СОЗДАНИЕ ТОКЕНА (уже есть) ==========
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создаёт JWT токен"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ========== ПРОВЕРКА ТОКЕНА (новое) ==========
def verify_token(token: str) -> Optional[dict]:
    """Проверяет токен, возвращает данные или None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ========== ПОЛУЧЕНИЕ ПОЛЬЗОВАТЕЛЯ (новое) ==========
def get_current_user(token: str, db: Session) -> Optional[User]:
    """По токену находит пользователя в БД"""
    # 1. Проверяем токен
    payload = verify_token(token)
    if not payload:
        return None

    # 2. Достаем email
    email = payload.get("sub")
    if not email:
        return None

    # 3. Ищем в БД
    return db.query(User).filter(User.email == email).first()
