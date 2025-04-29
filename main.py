from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, ValidationError
import models
from models import Question, Choice, LicenceType, QuestionType
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List, Annotated, Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import os
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

app = FastAPI()

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

app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
def root():
    return "Hola papi"


from fastapi import UploadFile, File, Form, HTTPException
import os
import json
import cloudinary.uploader  # Asegúrate de importar el uploader

@app.post("/question/")
async def create_question(
    db: db_dependency,
    text: str = Form(...),
    num: int = Form(...),
    licence_type_id: int = Form(...),
    question_type_id: int = Form(...),
    choices: str = Form(...),
    image: UploadFile = File(None),
):
    try:
        image_url = None

        # Subir imagen a Cloudinary si viene
        if image:
            contents = await image.read()

            # Cloudinary requiere un archivo tipo bytes, lo que tenemos en 'contents'
            upload_result = cloudinary.uploader.upload(contents, resource_type="image")

            # Obtener la URL de la imagen subida
            image_url = upload_result.get("secure_url")
            if not image_url:
                raise Exception("No se pudo subir la imagen a Cloudinary")

        # Parsear choices
        choices_list = json.loads(choices)

        db_question = Question(
            text=text,
            num=num,
            licence_type_id=licence_type_id,
            question_type_id=question_type_id,
            image=image_url,  # Ahora guarda la URL pública de Cloudinary
        )

        db_choices = []
        for choice in choices_list:
            db_choice = Choice(
                text=choice["text"],
                is_correct=choice["is_correct"],
                image=None  # Aquí también podrías subir imagen de choice si quieres
            )
            db_choices.append(db_choice)

        db_question.choices = db_choices
        db.add(db_question)
        db.commit()
        db.refresh(db_question)

        return {"message": "Pregunta creada correctamente", "question_id": db_question.id}
    
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    
@app.get("/questions/")
async def get_questions(db: db_dependency, id_licencia: int):
    try:
        # Obtener todas las preguntas
        licencia = db.query(LicenceType).filter(LicenceType.id == id_licencia).first()
        questions = db.query(Question).filter(Question.licence_type_id == id_licencia)
        licencias = db.query(LicenceType).all()
        questions_type = db.query(QuestionType).all()

        result = []
        for question in questions.all():
            question_data = {
                "id": question.id,
                "text": question.text,
                "num": question.num,
                "licence_type":  {
                    'id': question.licence_type_id,
                    'name': question.licence_type.name
                },
                "question_type": {
                    'id': question.question_type_id,
                    'name': question.question_type.name
                },
                "image": question.image,
                "choices": [{"text": choice.text, "is_correct": choice.is_correct} for choice in question.choices]
            }
            result.append(question_data)

        last_question_query = db.query(Question)
        if id_licencia:
            last_question_query = last_question_query.filter(Question.licence_type_id == id_licencia)

        last_question = last_question_query.order_by(Question.num.desc()).first()
        num = last_question.num if last_question else 0

        response = {
            "questions": result,
            "lastNum": num,
            "licencia": {
                'id': id_licencia,
                'name': licencia.name
            },
            "licencias": [
                {
                    'id': x.id,
                    'name': x.name
                } for x in licencias
            ],
            "tipo_preguntas": [
                {
                    'id': x.id,
                    'name': x.name
                } for x in questions_type
            ]
        }

        return response
    
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class LicenciaRequest(BaseModel):
    licencia_id: int

@app.post("/fetchQuestionNum/")
async def fetchQuestionNum(data: LicenciaRequest, db: db_dependency):
    last_question = db.query(models.Question.num).filter(
        models.Question.licence_type_id == data.licencia_id
    ).order_by(models.Question.num.desc()).first()

    if last_question is None:
        return {"num": 0}

    return {"num": last_question[0]}


@app.get("/licences/")
async def get_licences(db: db_dependency):
    try:
        # Obtener todas las preguntas
        licencias = db.query(LicenceType).all()

        response =  [
            {
                'id': x.id,
                'name': x.name,
                'description': x.description,
                'image': x.image
            } for x in licencias
        ]

        return response
    
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))