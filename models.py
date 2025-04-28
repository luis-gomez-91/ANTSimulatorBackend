from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Version(Base):
    __tablename__ = "versions"

    id = Column(Integer, primary_key=True, index=True)
    enable = Column(Boolean, default=True)
    year = Column(Integer, index=True)
    licences = relationship("LicenceType", back_populates="version")  # corregido

class Type(Base):  # Profesionales y no profesionales
    __tablename__ = "types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    licences = relationship("LicenceType", back_populates="type")  # corregido

class LicenceType(Base):
    __tablename__ = "licence_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    questions = relationship("Question", back_populates="licence_type")

    type_id = Column(Integer, ForeignKey("types.id"))
    type = relationship("Type", back_populates="licences")  # corregido

    version_id = Column(Integer, ForeignKey("versions.id"))
    version = relationship("Version", back_populates="licences")  # corregido

class QuestionType(Base):  # Tipos de preguntas
    __tablename__ = "questions_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    questions = relationship("Question", back_populates="question_type")  # añadido (faltaba)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    image = Column(String)
    num = Column(Integer, index=True)

    licence_type_id = Column(Integer, ForeignKey("licence_types.id"))
    licence_type = relationship("LicenceType", back_populates="questions")

    question_type_id = Column(Integer, ForeignKey("questions_type.id"))
    question_type = relationship("QuestionType", back_populates="questions")

    choices = relationship("Choice", back_populates="question")

class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    image = Column(String)
    is_correct = Column(Boolean, default=False)

    question_id = Column(Integer, ForeignKey("questions.id"))
    question = relationship("Question", back_populates="choices")

