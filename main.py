from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# ========== НАСТРОЙКИ JWT ==========
SECRET_KEY = "твой_секретный_ключ_минимум_32_символа_здесь"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ========== ИНИЦИАЛИЗАЦИЯ APP ==========
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ========== БАЗА ДАННЫХ (ВРЕМЕННАЯ) ==========
# TODO: Заменить на реальную БД
users_db = []  # временное хранилище пользователей
user_id_counter = 1

exercises_db = []
exercise_id_counter = 1


# ========== PYDANTIC СХЕМЫ ==========
class Exercise(BaseModel):
    id: Optional[int]
    name: str
    muscle_group: str
    difficulty: str

    class Config:
        from_attributes = True


class ExerciseCreate(BaseModel):
    name: str
    muscle_group: str
    difficulty: str


# СХЕМЫ ПОЛЬЗОВАТЕЛЯ
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str
    password_confirm: str

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
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


# ========== МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ (ВРЕМЕННАЯ) ==========
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
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, self.hashed_password)


# ========== ФУНКЦИИ JWT ==========
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ========== ЗАВИСИМОСТИ ==========
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Проверяет токен и возвращает пользователя из временной БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Ищем пользователя во временной БД
    user = None
    for u in users_db:
        if u.email == email:
            user = u
            break

    if user is None:
        raise credentials_exception

    return user


# ========== ПУБЛИЧНЫЕ ЭНДПОИНТЫ ==========
@app.get("/")
async def root():
    return {
        "message": "Welcome to Fitness API!",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "get_exercises": "GET /exercises",
            "create_exercise": "POST /exercises (auth)",
            "users_me": "GET /users/me (auth)"
        }
    }


# ========== ЭНДПОИНТЫ АУТЕНТИФИКАЦИИ ==========
@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    global user_id_counter

    # Проверяем, существует ли пользователь
    for user in users_db:
        if user.email == user_data.email or user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already exists"
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


@app.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    # Ищем пользователя
    user = None
    for u in users_db:
        if u.email == user_data.email:
            user = u
            break

    if not user or not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Создаём токен
    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ========== ЗАЩИЩЁННЫЕ ЭНДПОИНТЫ ==========
@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Возвращает информацию о текущем пользователе.
    Только для авторизованных!
    """
    return current_user


@app.post("/exercises")
async def create_exercise(
        exercise: ExerciseCreate,
        current_user: User = Depends(get_current_user)
):
    global exercise_id_counter

    print(f"Пользователь {current_user.email} создаёт упражнение")

    new_exercise = {
        "id": exercise_id_counter,
        "name": exercise.name,
        "muscle_group": exercise.muscle_group,
        "difficulty": exercise.difficulty,
        "created_by": current_user.email  # Добавил кто создал
    }

    exercise_id_counter += 1
    exercises_db.append(new_exercise)
    return new_exercise


@app.get("/exercises")
async def get_exercises():
    return {
        "count": len(exercises_db),
        "exercises": exercises_db
    }


@app.get("/exercises/{exercise_id}")
async def get_exercise_by_id(exercise_id: int):
    for exercise in exercises_db:
        if exercise["id"] == exercise_id:
            return exercise

    raise HTTPException(status_code=404, detail="Exercise not found")