# Scheduler Inteligent pentru Programari Medicale

Aplicatie web pentru gestionarea programarilor medicale, construita cu FastAPI, Svelte si PostgreSQL.

## Tehnologii

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: Svelte, HTML, CSS
- **Baza de date**: PostgreSQL
- **Altele**: Uvicorn, Pydantic

## Structura proiectului
```
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── database/
│   │   ├── models.py
│   │   ├── db.py
│   │   └── dateslot.py
│   └── routers/
│       ├── pacienti.py
│       ├── programari.py
│       ├── sloturi.py
│       └── lista_asteptare.py
├── frontend/
│   ├── src/
│   │   ├── App.svelte
│   │   ├── lib/
│   │   │   ├── Calendar.svelte
│   │   │   ├── Sloturi.svelte
│   │   │   ├── DialogProgramare.svelte
│   │   │   └── ListaAsteptare.svelte
│   └── package.json
└── README.md
```

## Baza de date
```
pacienti          id, nume, cnp, phone, nastere
programari        id, pacienti_id, slot_id, type, stare
sloturi           id, date, start_time, duration_min
lista_asteptare   id, pacienti_id, data_preferata, type
notificari        id, programari_id, send_at, type
```

## Roadmap 12 Martie -> 30 Aprilie 2026
```
1. 12-23 Martie     github, db, sqlalchemy //reimplementam 
2. 24 Martie - 4 Aprilie   backend FastAPI: pacienti, sloturi, programari //reimplementam
3. 7-18 Aprilie     frontend Svelte: calendar, programari, lista asteptare
4. 21-30 Aprilie    testare, rezolvare probleme si deploy final
```

## Milestones
```
1. DB PostgreSQL + modele SQLAlchemy         23 Martie
2. API pacienti si sloturi functional        28 Martie
3. API programari functional                  4 Aprilie
4. Frontend calendar si sloturi             11 Aprilie
5. Frontend programari si lista asteptare   18 Aprilie
6. Notificari si statistici                 23 Aprilie
7. Testare si build final                   30 Aprilie
```
