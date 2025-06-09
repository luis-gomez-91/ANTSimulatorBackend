# routers/versions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db # Importa tu dependencia de base de datos
import models
import schemas

router = APIRouter(
    prefix="/versions",
    tags=["Versions"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.Version])
async def get_all_versions(db: Session = Depends(get_db)):
    versions = db.query(models.Version).all()
    return versions

# Puedes añadir más endpoints aquí, por ejemplo:
# @router.get("/{version_id}", response_model=schemas.Version)
# async def get_version_by_id(version_id: int, db: Session = Depends(get_db)):
#     version = db.query(models.Version).filter(models.Version.id == version_id).first()
#     if not version:
#         raise HTTPException(status_code=404, detail="Version not found")
#     return version