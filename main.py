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
#КОРНЕВОЙ РОУТ
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
