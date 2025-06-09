from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import json
from database import get_db
import models
import schemas
import cloudinary.uploader

router = APIRouter(
    prefix="/questions",
    tags=["Questions"],
    responses={404: {"description": "Question not found"}},
)


@router.get("/by_licence/{licence_id}", response_model=List[schemas.Question])
async def get_questions_by_licence_id(
    licence_id: int, 
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las preguntas con sus respuestas para un ID de licencia específico.
    """
    licence_exists = (
        db.query(models.LicenceType).filter(models.LicenceType.id == licence_id).first()
    )
    if not licence_exists:
        raise HTTPException(
            status_code=404, detail=f"Licencia con ID {licence_id} no encontrada."
        )

    questions = (
        db.query(models.Question)
        .options(
            joinedload(models.Question.choices)
        )  # Carga anticipada de las opciones
        .options(joinedload(models.Question.question_type))
        .filter(models.Question.licence_type_id == licence_id)
        .all()
    )
    return questions

@router.get("/types/", response_model=List[schemas.QuestionType])
async def get_all_question_types(db: Session = Depends(get_db)):
    """
    Obtiene una lista de todos los tipos de pregunta disponibles (ej. 'Señales', 'Reglamentos').
    """
    question_types = db.query(models.QuestionType).all()
    
    # FastAPI serializará automáticamente la lista de objetos SQLAlchemy
    # a la lista de esquemas Pydantic (List[schemas.QuestionType])
    return question_types


@router.post("/", response_model=schemas.Question, status_code=status.HTTP_201_CREATED)
async def create_question(
    text: str = Form(...),
    # num: int = Form(...), # ¡RECOMENDACIÓN! El número de pregunta es mejor gestionarlo en el backend
    licence_type_id: int = Form(...),
    question_type_id: int = Form(...),
    choices_json: str = Form(..., alias='choices_json'), # 'choices_json' para coincidir con el JS
    image: Optional[UploadFile] = File(None), # Imagen de la pregunta, opcional
    db: Session = Depends(get_db)
):
    try:
        # 1. Validar existencia de la licencia y tipo de pregunta
        licence = db.query(models.LicenceType).filter(models.LicenceType.id == licence_type_id).first()
        if not licence:
            raise HTTPException(status_code=404, detail=f"Licencia con ID {licence_type_id} no encontrada.")
        
        question_type = db.query(models.QuestionType).filter(models.QuestionType.id == question_type_id).first()
        if not question_type:
            raise HTTPException(status_code=404, detail=f"Tipo de pregunta con ID {question_type_id} no encontrado.")

        # 2. Determinar el número secuencial de la pregunta (mejor gestionado por el backend)
        # Busca el número más alto de pregunta para esta licencia y suma 1
        last_question = db.query(models.Question)\
                          .filter(models.Question.licence_type_id == licence_type_id)\
                          .order_by(models.Question.num.desc())\
                          .first()
        new_question_num = (last_question.num + 1) if last_question else 1

        # 3. Subir imagen a Cloudinary si se proporcionó
        image_url = None
        if image and image.filename: # Asegurarse de que hay un archivo real
            try:
                # Cloudinary.uploader.upload acepta el objeto UploadFile.file directamente
                upload_result = cloudinary.uploader.upload(image.file, resource_type="image")
                image_url = upload_result.get("secure_url")
                if not image_url:
                    raise HTTPException(status_code=500, detail="No se pudo obtener la URL de la imagen de Cloudinary.")
            except Exception as e:
                # Cloudinary podría fallar por credenciales, red, etc.
                raise HTTPException(status_code=500, detail=f"Error al subir la imagen a Cloudinary: {e}")

        # 4. Crear la instancia de la pregunta
        db_question = models.Question(
            text=text,
            num=new_question_num, # Usamos el número calculado por el backend
            licence_type_id=licence_type_id,
            question_type_id=question_type_id,
            image=image_url,  # Guarda la URL pública de Cloudinary
        )
        db.add(db_question)
        db.flush() # Guarda la pregunta para obtener su ID antes de añadir las opciones

        # 5. Parsear y crear las opciones de respuesta
        choices_list = json.loads(choices_json)
        if not choices_list:
             raise HTTPException(status_code=400, detail="Debe proporcionar al menos una opción de respuesta.")

        correct_choice_found = False
        db_choices = []
        for choice_data in choices_list:
            # Validar el esquema de cada opción usando Pydantic
            try:
                parsed_choice = schemas.ChoiceCreate(**choice_data)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Formato de opción de respuesta inválido: {e}")

            if parsed_choice.is_correct:
                correct_choice_found = True

            db_choice = models.Choice(
                text=parsed_choice.text,
                image=parsed_choice.image, # Aquí podrías procesar imágenes para opciones si fuera necesario
                is_correct=parsed_choice.is_correct,
                question_id=db_question.id # Asocia la opción a la pregunta recién creada
            )
            db_choices.append(db_choice)
            db.add(db_choice) # Añadir cada opción a la sesión

        # 6. Validar que al menos una opción sea correcta
        if not correct_choice_found:
            # Si no hay ninguna opción correcta, la transacción se revertirá automáticamente con el rollback en el except
            raise HTTPException(status_code=400, detail="Debe haber al menos una opción de respuesta marcada como correcta.")

        db.commit() # Confirmar la pregunta y todas sus opciones
        db.refresh(db_question) # Recargar la pregunta para incluir sus opciones y relaciones

        # Cargar explícitamente las relaciones para el response_model
        # Esto es necesario porque db.refresh() solo carga lo que ya estaba en la sesión
        # y no las relaciones anidadas por defecto.
        db_question_loaded = db.query(models.Question)\
                               .options(joinedload(models.Question.choices),
                                        joinedload(models.Question.question_type))\
                               .filter(models.Question.id == db_question.id)\
                               .first()
        
        return db_question_loaded
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato JSON de opciones inválido.")
    except HTTPException as http_exc:
        # Re-lanza las excepciones HTTPException para que FastAPI las maneje
        db.rollback() # Asegúrate de hacer rollback en caso de error HTTP
        raise http_exc
    except Exception as e:
        # Cualquier otro error inesperado
        db.rollback() # Deshacer cualquier cambio en la base de datos
        print(f"ERROR al crear pregunta: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al crear la pregunta: {e}")
