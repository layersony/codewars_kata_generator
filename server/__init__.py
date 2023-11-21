from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Code Kata Generator API",
    description="Help Student to Practice for Codility",
    version="1.0",
    redoc_url="/api/redoc",
    root_path="/"
)

from . import routes

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

