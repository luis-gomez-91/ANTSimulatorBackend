from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL_DATABASE = 'postgresql://postgres:luis@localhost:5432/ant'
URL_DATABASE = 'postgresql://ant_nf5j_user:Uu2c5w5a5sKp39IpiYjIJyid3nOPV4zf@dpg-d07vrus9c44c73bcjak0-a/ant_nf5j'
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()