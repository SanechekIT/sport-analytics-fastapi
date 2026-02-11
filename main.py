from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator, Field
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

# ========== ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ==========
load_dotenv()

# ========== НАСТРОЙКИ JWT ==========
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_32BYTES")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# ========== НАСТРОЙКИ БЕЗОПАСНОСТИ ==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ========== ИНИЦИАЛИЗАЦИЯ APP ==========
app = FastAPI(
    title="Fitness API",
    description="API для управления упражнениями и пользователями",
    version="1.1.0"
)

# ========== CORS НАСТРОЙКИ ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== БАЗА ДАННЫХ (ВРЕМЕННАЯ) ==========
# TODO: Заменить на реальную БД (PostgreSQL/MySQL)
users_db = []
user_id_counter = 1

exercises_db = []
exercise_id_counter = 1


# ========== PYDANTIC СХЕМЫ ==========
class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    muscle_group: str = Field(..., min_length=2, max_length=50)
    difficulty: str

    @validator('difficulty')
    def validate_difficulty(cls, v):
        allowed = ['beginner', 'intermediate', 'advanced']
        v_lower = v.lower()
        if v_lower not in allowed:
            raise ValueError(f'Difficulty must be one of {allowed}')
        return v_lower


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(ExerciseBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    muscle_group: Optional[str] = Field(None, min_length=2, max_length=50)
    difficulty: Optional[str] = None


class Exercise(ExerciseBase):
    id: int
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


# СХЕМЫ ПОЛЬЗОВАТЕЛЯ
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    password_confirm: str

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60


class TokenData(BaseModel):
    email: Optional[str] = None


# ========== МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ ==========
class User:
    def __init__(self, id: int, email: str, username: str, hashed_password: str):
        self.id = id
        self.email = email
        self.username = username
        self.hashed_password = hashed_password
        self.is_active = True
        self.created_at = datetime.now()

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.hashed_password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at
        }


# ========== ФУНКЦИИ JWT ==========
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def find_user_by_email(email: str) -> Optional[User]:
    """Поиск пользователя по email"""
    return next((u for u in users_db if u.email == email), None)


def find_user_by_username(username: str) -> Optional[User]:
    """Поиск пользователя по username"""
    return next((u for u in users_db if u.username == username), None)


def find_exercise_by_id(exercise_id: int) -> Optional[dict]:
    """Поиск упражнения по ID"""
    return next((e for e in exercises_db if e["id"] == exercise_id), None)


# ========== ЗАВИСИМОСТИ ==========
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Проверяет токен и возвращает пользователя из временной БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    inactive_user_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Неактивный пользователь"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = find_user_by_email(token_data.email)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise inactive_user_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверка активности пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неактивный пользователь"
        )
    return current_user


def check_exercise_ownership(exercise: dict, user: User) -> bool:
    """Проверка владения упражнением"""
    return exercise["created_by"] == user.email


# ========== ПУБЛИЧНЫЕ ЭНДПОИНТЫ ==========
@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Fitness API!",
        "version": "1.1.0",
        "documentation": "/docs",
        "endpoints": {
            "register": "POST /register - Регистрация",
            "login": "POST /login - Вход в систему",
            "exercises": "GET /exercises - Список упражнений",
            "exercise_by_id": "GET /exercises/{id} - Упражнение по ID",
            "create_exercise": "POST /exercises (auth) - Создать упражнение",
            "update_exercise": "PATCH /exercises/{id} (auth) - Обновить упражнение",
            "delete_exercise": "DELETE /exercises/{id} (auth) - Удалить упражнение",
            "users_me": "GET /users/me (auth) - Профиль пользователя"
        }
    }


@app.get("/health")
async


health_check():
"""Проверка работоспособности API"""
return {
    "status": "healthy",
    "timestamp": datetime.utcnow(),
    "users_count": len(users_db),
    "exercises_count": len(exercises_db)
}


# ========== ЭНДПОИНТЫ АУТЕНТИФИКАЦИИ ==========
@app.post("/register",
          response_model=UserResponse,
          status_code=status.HTTP_201_CREATED,
          summary="Регистрация нового пользователя")
async def register(user_data: UserCreate):
    """
    Регистрация нового пользователя в системе.

    - **email**: Email пользователя (должен быть уникальным)
    - **username**: Имя пользователя (должно быть уникальным)
    - **password**: Пароль (минимум 6 символов)
    - **password_confirm**: Подтверждение пароля
    """
    global user_id_counter

    # Проверяем существование пользователя
    if find_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    if find_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    # Создаём нового пользователя
    hashed_password = User.hash_password(user_data.password)
    new_user = User(
        id=user_id_counter,
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )

    users_db.append(new_user)
    user_id_counter += 1

    return new_user


@app.post("/login", response_model=Token, summary="Вход в систему")
async def login(user_data: UserLogin):
    """
    Аутентификация пользователя и получение JWT токена.

    - **email**: Email пользователя
    - **password**: Пароль
    """
    user = find_user_by_email(user_data.email)

    if not user or not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )

    # Создаём токен
    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


# ========== ЗАЩИЩЁННЫЕ ЭНДПОИНТЫ ==========
@app.get("/users/me",
         response_model=UserResponse,
         summary="Информация о текущем пользователе")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Возвращает информацию о текущем авторизованном пользователе.
    """
    return current_user


@app.delete("/users/me",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Деактивация аккаунта")
async def deactivate_user(current_user: User = Depends(get_current_active_user)):
    """
    Деактивирует аккаунт текущего пользователя.
    """
    current_user.is_active = False
    return None


# ========== ЭНДПОИНТЫ УПРАЖНЕНИЙ ==========
@app.post("/exercises",
          response_model=Exercise,
          status_code=status.HTTP_201_CREATED,
          summary="Создание нового упражнения")
async def create_exercise(
        exercise: ExerciseCreate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Создает новое упражнение (только для авторизованных пользователей).

    - **name**: Название упражнения
    - **muscle_group**: Группа мышц
    - **difficulty**: Сложность (beginner/intermediate/advanced)
    """
    global exercise_id_counter

    new_exercise = Exercise(
        id=exercise_id_counter,
        name=exercise.name,
        muscle_group=exercise.muscle_group,
        difficulty=exercise.difficulty,
        created_by=current_user.email
    ).dict()

    exercise_id_counter += 1
    exercises_db.append(new_exercise)
    return new_exercise


@app.get("/exercises", response_model=dict, summary="Список упражнений")
async def get_exercises(
        muscle_group: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = Field(0, ge=0),
        limit: int = Field(20, ge=1, le=100)
):
    """
    Возвращает список упражнений с возможностью фильтрации.

    - **muscle_group**: Фильтр по группе мышц
    - **difficulty**: Фильтр по сложности
    - **search**: Поиск по названию
    - **skip**: Пропустить N записей
    - **limit**: Максимум записей
    """
    filtered = exercises_db.copy()

    if muscle_group:
        filtered = [e for e in filtered if e["muscle_group"].lower() == muscle_group.lower()]

    if difficulty:
        filtered = [e for e in filtered if e["difficulty"].lower() == difficulty.lower()]

    if search:
        filtered = [e for e in filtered if search.lower() in e["name"].lower()]

    # Сортировка по ID (новые сверху)
    filtered.sort(key=lambda x: x["id"], reverse=True)

    paginated = filtered[skip:skip + limit]

    return {
        "total": len(filtered),
        "skip": skip,
        "limit": limit,
        "exercises": paginated
    }


@app.get("/exercises/{exercise_id}", response_model=Exercise, summary="Получить упражнение по ID")
async def get_exercise_by_id(exercise_id: int):
    """
    Возвращает упражнение по его ID.
    """
    exercise = find_exercise_by_id(exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Упражнение с ID {exercise_id} не найдено"
        )

    return exercise


@app.patch("/exercises/{exercise_id}",
           response_model=Exercise,
           summary="Обновить упражнение")
async def update_exercise(
        exercise_id: int,
        exercise_update: ExerciseUpdate,
        current_user: User = Depends(get_current_active_user)
):
    """
    Обновляет существующее упражнение (только для автора).
    """
    exercise = find_exercise_by_id(exercise_id)

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Упражнение с ID {exercise_id} не найдено"
        )

    if not check_exercise_ownership(exercise, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете редактировать только свои упражнения"
        )

    # Обновляем только переданные поля
    update_data = exercise_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            exercise[field] = value

    return exercise


@app.delete("/exercises/{exercise_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Удалить упражнение")
async def delete_exercise(
        exercise_id: int,
        current_user: User = Depends(get_current_active_user)
):
    """
    Удаляет упражнение (только для автора).
    """
    for i, exercise in enumerate(exercises_db):
        if exercise["id"] == exercise_id:
            if not check_exercise_ownership(exercise, current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Вы можете удалять только свои упражнения"
                )

            del exercises_db[i]
            return None

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Упражнение с ID {exercise_id} не найдено"
    )


# ========== ОБРАБОТЧИКИ ОШИБОК ==========
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)