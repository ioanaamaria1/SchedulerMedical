from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import init_db
from routers import pacienti, programari, sloturi, lista_asteptare

app = FastAPI(title="Scheduler Medical API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "Scheduler Medical API functioneaza"}

app.include_router(pacienti.router, prefix="/pacienti", tags=["pacienti"])
app.include_router(programari.router, prefix="/programari", tags=["programari"])
app.include_router(sloturi.router, prefix="/sloturi", tags=["sloturi"])
app.include_router(lista_asteptare.router, prefix="/lista-asteptare", tags=["lista_asteptare"])