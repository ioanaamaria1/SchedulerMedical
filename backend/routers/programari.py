from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
from database.models import Programari, Sloturi
from sqlalchemy.orm import joinedload

router = APIRouter()

class ProgramareRequest(BaseModel):
    pacienti_id: int
    slot_id: int
    type: str

# 1. OBȚINE TOATE PROGRAMĂRILE (ACUM TRAGE PERFECT DATELE DIN TABEL)
@router.get("/")
def get_programari():
    session = get_session()
    try:
        # Aducem programările cu tot cu slotul lor atașat
        programari_db = session.query(Programari).options(joinedload(Programari.slot)).all()

        lista_finala = []
        for p in programari_db:
            # Folosim numele EXACȚI din models.py: .date și .start_time
            ziua = str(p.slot.date) if p.slot and p.slot.date else "0000-00-00"
            ora = str(p.slot.start_time)[:5] if p.slot and p.slot.start_time else "--:--"

            lista_finala.append({
                "id": p.id,
                "pacienti_id": p.pacienti_id,
                "slot_id": p.slot_id,
                "type": p.type,
                "data": ziua,
                "ora": ora
            })

        return lista_finala
    finally:
        session.close()

# 2. CREEAZĂ O NOUĂ PROGRAMARE
@router.post("/")
def create_programare(prog: ProgramareRequest):
    session = get_session()
    try:
        # REGULA ANTI-SPAM: Maxim 3 programari active per pacient
        numar_programari = session.query(Programari).filter(Programari.pacienti_id == prog.pacienti_id).count()

        if numar_programari >= 3:
            raise HTTPException(
                status_code=400,
                detail="Ai atins limita maximă de programări active (3). Te rugăm să anulezi din ele sau să contactezi clinica."
            )

        # Verificăm dacă slotul există
        slot = session.query(Sloturi).filter(Sloturi.id == prog.slot_id).first()
        if not slot:
            raise HTTPException(status_code=404, detail="Slotul nu a fost găsit.")

        # Verificăm dacă slotul e deja ocupat
        programare_existenta = session.query(Programari).filter(Programari.slot_id == prog.slot_id).first()
        if programare_existenta:
            raise HTTPException(status_code=400, detail="Acest slot este deja ocupat.")

        noua_prog = Programari(
            pacienti_id=prog.pacienti_id,
            slot_id=prog.slot_id,
            type=prog.type
        )

        session.add(noua_prog)
        session.commit()
        return {"mesaj": "Programare creată!"}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

# 3. ȘTERGE (ANULEAZĂ) O PROGRAMARE
@router.delete("/{id}")
def delete_programare(id: int):
    session = get_session()
    try:
        prog = session.query(Programari).filter(Programari.id == id).first()
        if not prog:
            raise HTTPException(status_code=404, detail="Programarea nu a fost găsită")

        session.delete(prog)
        session.commit()
        return {"mesaj": "Programare anulată!"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()