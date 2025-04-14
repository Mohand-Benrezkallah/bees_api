from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Bee(Base):
    __tablename__ = "bee"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    origin = Column(String, nullable=False)
    image_path = Column(String, nullable=True)  # Store relative path like 'images/bee1.jpg'
    species = Column(String, nullable=False)
    captured_date = Column(Date, nullable=False)

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, default=datetime.utcnow)