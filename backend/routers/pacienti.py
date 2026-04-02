from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from database.db import get_session
from database.models import Pacienti

router = APIRouter()

class PacientSchema(BaseModel):
    nume: str
    cnp: str
    phone: str | None = None
    nastere: date | None = None

@router.get("/")
def get_pacienti():
    session = get_session()
    try:
        return session.query(Pacienti).all()
    finally:
        session.close()

@router.get("/{cnp}")
def get_pacient(cnp: str):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.cnp == cnp).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacient negasit")
        return pacient
    finally:
        session.close()

@router.post("/")
def create_pacient(pacient: PacientSchema):
    session = get_session()
    try:
        existent = session.query(Pacienti).filter(Pacienti.cnp == pacient.cnp).first()
        if existent:
            raise HTTPException(status_code=400, detail="CNP deja existent")
        nou = Pacienti(**pacient.model_dump())
        session.add(nou)
        session.commit()
        session.refresh(nou)
        return nou
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.delete("/{id}")
def delete_pacient(id: int):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.id == id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacient negasit")
        session.delete(pacient)
        session.commit()
        return {"detail": "Pacient sters"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()