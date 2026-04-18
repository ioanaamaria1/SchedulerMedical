from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
from database.models import Pacienti

router = APIRouter()


class PacientRequest(BaseModel):
    nume: str
    cnp: str
    phone: str


class PacientUpdate(BaseModel):
    nume: str = None
    cnp: str = None
    phone: str = None


# ---- IA TOTI PACIENTII (Folosit de Doctor) ----
@router.get("/")
def get_pacienti():
    session = get_session()
    try:
        pacienti = session.query(Pacienti).all()
        return pacienti
    finally:
        session.close()


# ---- RUTA NOUĂ: IA UN SINGUR PACIENT (Folosit de formularul pacientului) ----
@router.get("/{id}")
def get_pacient(id: int):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.id == id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacientul nu exista")
        return pacient
    finally:
        session.close()


# ---- CREARE PACIENT ----
@router.post("/")
def create_pacient(pacient: PacientRequest):
    session = get_session()
    try:
        nou_pacient = Pacienti(nume=pacient.nume, cnp=pacient.cnp, phone=pacient.phone)
        session.add(nou_pacient)
        session.commit()
        return {"mesaj": "Pacient adaugat!"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


# ---- STERGE PACIENT ----
@router.delete("/{id}")
def delete_pacient(id: int):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.id == id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacientul nu exista")
        session.delete(pacient)
        session.commit()
        return {"mesaj": "Pacient sters"}
    finally:
        session.close()


# ---- ACTUALIZARE PACIENT ----
@router.put("/{id_pacient}")
def update_pacient(id_pacient: int, req: PacientUpdate):
    session = get_session()
    try:
        pacient = session.query(Pacienti).filter(Pacienti.id == id_pacient).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacientul nu exista")

        if req.nume: pacient.nume = req.nume
        if req.cnp: pacient.cnp = req.cnp
        if req.phone: pacient.phone = req.phone

        session.commit()
        return {"mesaj": "Date pacient actualizate!"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()