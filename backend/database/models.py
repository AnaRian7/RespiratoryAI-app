from sqlalchemy import Column, Integer, String, Float
from backend.database.db import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True)
    age = Column(Integer)
    gender = Column(String)
    smoker = Column(Integer)
    asthma = Column(Integer)
    genetic_risk = Column(Integer)
    congenital_lung_defect = Column(Integer)

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    image_path = Column(String)
    label = Column(String)
    confidence = Column(Float)
