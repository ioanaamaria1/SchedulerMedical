from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from database.db import get_session
from database.models import ListaAsteptare, Pacienti

router = APIRouter()

class ListaAsteptareSchema(BaseModel):
    pacienti_id: int
    data_preferata: Optional[date] = None
    type: Optional[str] = None

class ListaAsteptareResponse(BaseModel):
    id: int
    pacienti_id: int
    data_preferata: Optional[date] = None
    type: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ListaAsteptareResponse])
def get_lista():
    session = get_session()
    try:
        return session.query(ListaAsteptare).all()
    finally:
        session.close()

@router.post("/", response_model=ListaAsteptareResponse)
def add_to_lista(intrare: ListaAsteptareSchema):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.id == intrare.pacienti_id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacient negasit")
        nou = ListaAsteptare(**intrare.model_dump())
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
def delete_din_lista(id: int):
    session = get_session()
    try:
        intrare = session.query(ListaAsteptare).filter(ListaAsteptare.id == id).first()
        if not intrare:
            raise HTTPException(status_code=404, detail="Intrare negasita")
        session.delete(intrare)
        session.commit()
        return {"detail": "Sters din lista de asteptare"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
