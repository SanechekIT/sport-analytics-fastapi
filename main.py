from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

#СОЗДАЁМ САМО API
app = FastAPI(
    title = "Fitness Tracker API",
    description = "API для отслеживания тренировок",
    version = "1.0.0"
)
#CORS ПРОСЛОЙКА
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {
        "message":"Fitness Tracker API",
        "docs":"/docs",
        "status":"running"
    }
@app.get("/health")
def health():
    return {"status":"healthy"}

@app.post("/register")
def register(user_data : UserCreate):
    email = user_data.email
    password = user_data.password
    return {"message": "user created"}


@app.post("/login")
def login(user_data: UserCreate):
    # Ищем пользователя по email
    for user in fake_users_db:
        if user["email"] == user_data.email:
            # Проверяем пароль (в реальности надо сравнивать хеши)
            if user["password"] == user_data.password:
                return {"message": "успешный вход"}
            else:
                raise HTTPException(status_code=400, detail="Неверный пароль")
# Если пользователь не найден
    raise HTTPException(status_code=404, detail="Пользователь не найден")


@app.get("/users/me")
def get_current_user():
    # Пока просто заглушка, потом будем проверять токен
    return {"message": "тут будут данные пользователя"}
