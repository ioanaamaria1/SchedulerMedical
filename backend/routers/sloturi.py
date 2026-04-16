from fastapi import APIRouter, HTTPException
from datetime import date
from database.db import get_session
from database.models import Sloturi, Programari
from database.dateslot import genereaza_sloturi_zi, get_sloturi_zi

router = APIRouter()
@router.get("/libere/{data}")
def get_sloturi_libere(data: date):
    genereaza_sloturi_zi(data)
    sloturi = get_sloturi_zi(data)
    return [s for s in sloturi if not s["ocupat"]]

@router.get("/{data}")
def get_sloturi(data: date):
    genereaza_sloturi_zi(data)
    return get_sloturi_zi(data)
