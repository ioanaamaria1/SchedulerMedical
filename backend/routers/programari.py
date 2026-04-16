from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database.db import get_session
from database.models import Programari, Pacienti, Sloturi, StareProgramare

router = APIRouter()

class ProgramareSchema(BaseModel):
    pacienti_id: int
    slot_id: int
    type: Optional[str] = None

class ProgramareResponse(BaseModel):
    id: int
    pacienti_id: int
    slot_id: int
    type: Optional[str] = None
    stare: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_custom(cls, obj):
        return cls(
            id=obj.id,
            pacienti_id=obj.pacienti_id,
            slot_id=obj.slot_id,
            type=obj.type,
            stare=obj.stare.value if obj.stare else "programat"
        )

@router.get("/")
def get_programari():
    session = get_session()
    try:
        items = session.query(Programari).all()
        return [ProgramareResponse.from_orm_custom(p) for p in items]
    finally:
        session.close()

@router.post("/")
def create_programare(programare: ProgramareSchema):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.id == programare.pacienti_id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacient negasit")

        slot = session.query(Sloturi).filter(Sloturi.id == programare.slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail="Slot negasit")

        ocupat = session.query(Programari).filter(Programari.slot_id == programare.slot_id).first()
        if ocupat:
            raise HTTPException(status_code=400, detail="Slot deja ocupat")

        nou = Programari(**programare.model_dump())
        session.add(nou)
        session.commit()
        session.refresh(nou)
        return ProgramareResponse.from_orm_custom(nou)
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
