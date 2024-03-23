import uuid
from db.engine.db import Base, engine
from sqlalchemy import Column, String, Boolean


class BaseMixin:
    def dict(self, columns):
        return {column: getattr(self, column) for column in columns}

class Customer(Base, BaseMixin):

    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True, default=str(uuid.uuid4()), unique=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    #apiKey = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    database = Column(String)
    
    is_active = Column(Boolean, default=True)

# Optional call to create database
def create_db():
    Base.metadata.create_all(engine)