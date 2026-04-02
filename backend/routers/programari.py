from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
from database.models import Programari, Pacienti, Sloturi, StareProgramare

router = APIRouter()

class ProgramareSchema(BaseModel):
    pacienti_id: int
    slot_id: int
    type: str | None = None

@router.get("/")
def get_programari():
    session = get_session()
    try:
        return session.query(Programari).all()
    finally:
        session.close()

@router.post("/")
def create_programare(programare: ProgramareSchema):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(
            Pacienti.id == programare.pacienti_id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacient negasit")

        slot = session.query(Sloturi).filter(
            Sloturi.id == programare.slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail="Slot negasit")

        ocupat = session.query(Programari).filter(
            Programari.slot_id == programare.slot_id).first()
        if ocupat:
            raise HTTPException(status_code=400, detail="Slot deja ocupat")

        nou = Programari(**programare.model_dump())
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
def delete_programare(id: int):
    session = get_session()
    try:
        programare = session.query(Programari).filter(Programari.id == id).first()
        if not programare:
            raise HTTPException(status_code=404, detail="Programare negasita")
        session.delete(programare)
        session.commit()
        return {"detail": "Programare stearsa"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()