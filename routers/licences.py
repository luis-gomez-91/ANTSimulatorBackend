# routers/licences.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload # Necesitas joinedload para cargar las relaciones
from typing import List

from database import get_db # Importa tu dependencia de base de datos
import models             # Importa tus modelos SQLAlchemy
import schemas            # Importa tus esquemas Pydantic

# Crea una instancia de APIRouter para las licencias
router = APIRouter(
    prefix="/licences",  # Todas las rutas en este router comenzarán con /licences
    tags=["Licences"],   # Etiqueta para la documentación de Swagger UI
    responses={404: {"description": "Licence not found"}}, # Respuestas de error comunes
)

@router.get("/by_version/{version_id}", response_model=List[schemas.LicenceType])
async def get_licences_by_version_id(version_id: int, db: Session = Depends(get_db)):
    """
    Obtiene una lista de todas las licencias asociadas a un ID de versión (año) específico.
    """
    # 1. Opcional pero recomendado: Verificar si la versión existe antes de buscar licencias.
    # Esto da un error 404 más claro si el ID de versión es inválido.
    version_exists = db.query(models.Version).filter(models.Version.id == version_id).first()
    if not version_exists:
        raise HTTPException(status_code=404, detail=f"Versión con ID {version_id} no encontrada.")

    # 2. Obtener las licencias filtradas por version_id.
    # Usamos joinedload para cargar de forma anticipada las relaciones 'version' y 'type'.
    # Esto evita hacer múltiples consultas a la base de datos (problema N+1)
    # y asegura que Pydantic tenga los datos necesarios para la serialización.
    licences = db.query(models.LicenceType)\
                 .options(joinedload(models.LicenceType.version))\
                 .options(joinedload(models.LicenceType.type))\
                 .filter(models.LicenceType.version_id == version_id)\
                 .all()
    
    # FastAPI se encarga de serializar automáticamente la lista de objetos SQLAlchemy
    # a la lista de esquemas Pydantic (List[schemas.LicenceType]) gracias a response_model
    # y a Config.from_attributes = True en tus schemas.
    return licences

@router.get("/{licence_id}", response_model=schemas.LicenceType)
async def get_single_licence(licence_id: int, db: Session = Depends(get_db)):
    print(f"ID POSE: {licence_id}")
    licence = db.query(models.LicenceType)\
                .options(
                    joinedload(models.LicenceType.version), # Carga la relación con Version
                    joinedload(models.LicenceType.type)     # Carga la relación con Type
                )\
                .filter(models.LicenceType.id == licence_id)\
                .first()

    if not licence:
        raise HTTPException(status_code=404, detail=f"Licencia con ID {licence_id} no encontrada.")

    return licence