from fastapi import FastAPI, Depends
import models
from database import engine, get_db
from sqlalchemy.orm import Session
from typing import Annotated
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import cloudinary
from routers import versions, licences, questions
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

origins = [
    "https://luis-gomez-91.github.io",        # GitHub Pages sin www
    "https://www.luis-gomez-91.github.io",    # GitHub Pages con www (por si acaso)
    "http://localhost:8000",                  # Para desarrollo local
    "http://127.0.0.1:8000",
]

# app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las URLs o especifica una lista
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)

models.Base.metadata.create_all(bind=engine)
db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def root():
    return {'status': 'success', 'message': 'Bienvenido a ANT Simulator - by Luis Gómez'}

app.include_router(versions.router)
app.include_router(licences.router)
app.include_router(questions.router)