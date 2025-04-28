from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL_DATABASE = 'postgresql://postgres:luis@localhost:5432/ant'

URL_DATABASE = os.getenv("DATABASE_URL")
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()