# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

# Schemas para el modelo Version
class VersionBase(BaseModel):
    year: int
    enable: bool

class VersionCreate(VersionBase):
    pass # No hay campos adicionales para la creación

class Version(VersionBase):
    id: int
    
    class Config:
        from_attributes = True
        
# Schemas para el modelo Type
class TypeBase(BaseModel):
    name: str

class Type(TypeBase):
    id: int

    class Config:
        from_attributes = True

# Schemas para el modelo LicenceType
class LicenceTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    image: Optional[str] = None
    question_bank: Optional[str] = None
    order: Optional[int] = None
    enable: bool = False
    
    type_id: int
    version_id: int

class LicenceTypeCreate(LicenceTypeBase):
    pass

class LicenceType(LicenceTypeBase):
    id: int
    
    # Para incluir las relaciones anidadas en la respuesta
    version: Version # Opcional: Si quieres incluir la versión completa
    type: Type # Opcional: Si quieres incluir el tipo completo

    class Config:
        from_attributes = True

# Si también necesitas schemas para Question y Choice
class QuestionTypeBase(BaseModel):
    name: str

class QuestionType(QuestionTypeBase):
    id: int
    class Config:
        from_attributes = True

class ChoiceBase(BaseModel):
    text: str
    image: Optional[str] = None
    is_correct: bool = False

class Choice(ChoiceBase):
    id: int
    question_id: int
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    text: str
    image: Optional[str] = None
    num: int
    licence_type_id: int
    question_type_id: int

class Question(QuestionBase):
    id: int
    choices: List[Choice] = [] # Para incluir las opciones en la pregunta
    question_type: QuestionType # Para incluir el tipo de pregunta
    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    # Campos que vienen directamente del formulario
    text: str
    num: int
    licence_type_id: int
    question_type_id: int
    
    # Este campo 'choices_json' es el que recibiremos del FormData en el frontend
    # y contendrá la lista de opciones serializada como JSON.
    choices_json: str = Field(..., alias='choices_json') 

class ChoiceCreate(ChoiceBase):
    pass 