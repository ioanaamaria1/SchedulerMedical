from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import get_session
from database.models import Conturi, Pacienti
from passlib.context import CryptContext
import jwt
import datetime
import random

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = "cheia-noastra-super-secreta-medicala"

EMAIL_DOCTOR = "doctor@clinica.ro"


class AuthRequest(BaseModel):
    email: str
    parola: str


@router.post("/login")
def login(req: AuthRequest):
    session = get_session()
    try:
        cont = session.query(Conturi).filter(Conturi.email == req.email).first()
        if not cont or not pwd_context.verify(req.parola.encode('utf-8'), cont.parola_hash):
            raise HTTPException(status_code=401, detail="Email sau parola incorecta")

        expira_la = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        token_data = {
            "sub": cont.email,
            "rol": cont.rol,
            "pacient_id": cont.pacient_id,
            "exp": expira_la.timestamp()
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")

        return {"access_token": token, "rol": cont.rol, "pacient_id": cont.pacient_id}
    finally:
        session.close()


@router.post("/register")
def register(req: AuthRequest):
    session = get_session()
    try:
        existent = session.query(Conturi).filter(Conturi.email == req.email).first()
        if existent:
            raise HTTPException(status_code=400, detail="Acest email este deja inregistrat!")

        rol_ales = "doctor" if req.email == EMAIL_DOCTOR else "pacient"

        pacient_id_nou = None
        if rol_ales == "pacient":
            nume_provizoriu = req.email.split('@')[0].capitalize()

            # Generam un CNP si un Telefon temporar unic pentru a respecta regula UNIQUE din baza de date
            cnp_temporar = f"T-{random.randint(1000000000, 9999999999)}"
            tel_temporar = f"07{random.randint(10000000, 99999999)}"

            nou_pacient = Pacienti(nume=nume_provizoriu, cnp=cnp_temporar, phone=tel_temporar)

            session.add(nou_pacient)
            session.flush()
            pacient_id_nou = nou_pacient.id

        hash_parola = pwd_context.hash(req.parola.encode('utf-8'))
        nou_cont = Conturi(email=req.email, parola_hash=hash_parola, rol=rol_ales, pacient_id=pacient_id_nou)

        session.add(nou_cont)
        session.commit()
        return {"mesaj": f"Cont creat cu succes ca {rol_ales}!"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()