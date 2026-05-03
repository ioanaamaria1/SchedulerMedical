from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
# Am adăugat Conturi și Programari la import
from database.models import Pacienti, Conturi, Programari

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
    # Validare: CNP-ul trebuie să aibă fix 13 caractere și să conțină doar cifre
    if len(pacient.cnp) != 13 or not pacient.cnp.isdigit():
        raise HTTPException(status_code=400, detail="CNP-ul trebuie să conțină exact 13 cifre!")

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
        # 1. Mai întâi ștergem contul asociat pacientului
        session.query(Conturi).filter(Conturi.pacient_id == id).delete(synchronize_session=False)

        # 2. Ștergem programările asociate pacientului
        session.query(Programari).filter(Programari.pacienti_id == id).delete(synchronize_session=False)

        # 3. La final, găsim și ștergem pacientul
        pacient = session.query(Pacienti).filter(Pacienti.id == id).first()
        if not pacient:
            raise HTTPException(status_code=404, detail="Pacientul nu exista")

        session.delete(pacient)
        session.commit()
        return {"mesaj": "Pacient și date asociate șterse cu succes!"}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        session.close()


@router.put("/{id_pacient}")
def update_pacient(id_pacient: int, req: PacientUpdate):
    # Validare CNP dacă se încearcă actualizarea lui
    if req.cnp and (len(req.cnp) != 13 or not req.cnp.isdigit()):
        raise HTTPException(status_code=400, detail="CNP-ul trebuie să conțină exact 13 cifre!")

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