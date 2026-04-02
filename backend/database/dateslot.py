from datetime import date, time, timedelta
from database.db import get_session
from database.models import Sloturi, Programari

def genereaza_sloturi_zi(data: date, ora_start: time = time(8, 0),
                          ora_end: time = time(17, 0), durata_min: int = 30):
    session = get_session()
    try:
        existente = session.query(Sloturi).filter(Sloturi.date == data).count()
        if existente > 0:
            return

        start = timedelta(hours=ora_start.hour, minutes=ora_start.minute)
        end = timedelta(hours=ora_end.hour, minutes=ora_end.minute)
        current = start
        while current + timedelta(minutes=durata_min) <= end:
            h, m = divmod(int(current.total_seconds()) // 60, 60)
            slot = Sloturi(date=data, start_time=time(h, m), duration_min=durata_min)
            session.add(slot)
            current += timedelta(minutes=durata_min)
        session.commit()
    finally:
        session.close()

def get_sloturi_zi(data: date):

    session = get_session()
    try:
        sloturi = session.query(Sloturi).filter(Sloturi.date == data).all()
        rezultat = []
        for slot in sloturi:
            ocupat = session.query(Programari).filter(
                Programari.slot_id == slot.id
            ).first() is not None
            rezultat.append({
                "id": slot.id,
                "ora": slot.start_time.strftime("%H:%M"),
                "durata": slot.duration_min,
                "ocupat": ocupat
            })
        return rezultat
    finally:
        session.close()