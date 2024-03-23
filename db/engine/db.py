from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os, psycopg2
from fastapi import Request
 
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") #"sqlite:///./webhookApi.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True) #, connect_args={"check_same_thread": False})
 
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
 
""" class Base(DeclarativeBase):
    pass """
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 
    
""" def get_db(request: Request):
    return request.state.db
 """