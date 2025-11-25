# Подключаемые библиотеки
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List, Optional
import enum
import uvicorn
from datetime import datetime

# Основа БД
SQLALCHEMY_DATABASE_URL = "sqlite:///./incidents.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель-форма
class IncidentStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentSource(str, enum.Enum):
    OPERATOR = "operator"
    MONITORING = "monitoring"
    PARTNER = "partner"

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.NEW)
    source = Column(Enum(IncidentSource), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Таблица
Base.metadata.create_all(bind=engine)

# Class Pydantic
class IncidentCreate(BaseModel):
    description: str
    source: IncidentSource

class IncidentUpdate(BaseModel):
    status: IncidentStatus

class IncidentResponse(IncidentCreate):
    id: int
    status: IncidentStatus
    created_at: datetime

    # Pydantic auto
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Post path
@app.post("/incidents/", response_model=IncidentResponse, status_code=201)
def create_incident(incident: IncidentCreate, db: Session = Depends(get_db)):
    db_incident = Incident(**incident.dict())
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident

@app.get("/incidents/", response_model=List[IncidentResponse])
def read_incidents(status: Optional[IncidentStatus] = None, db: Session = Depends(get_db)):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    return query.all()

@app.patch("/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident_status(incident_id: int, incident_update: IncidentUpdate, db: Session = Depends(get_db)):
    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=404, detail="Инцидент не найден")
    db_incident.status = incident_update.status
    db.commit()
    db.refresh(db_incident)
    return db_incident

@app.get("/")
def root():
    return {"message": "Incident API Service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
