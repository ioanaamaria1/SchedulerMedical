from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Enum, DateTime
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class StareProgramare(enum.Enum):
    programat = "programat"
    anulat = "anulat"
    finalizat = "finalizat"
    urgent = "urgent"

class Pacienti(Base):
    __tablename__ = "pacienti"
    id = Column(Integer, primary_key=True)
    nume = Column(String(100), nullable=False)
    cnp = Column(String(13), unique=True, nullable=False)
    phone = Column(String(15))
    nastere = Column(Date)
    programari = relationship("Programari", back_populates="pacient")
    lista_asteptare = relationship("ListaAsteptare", back_populates="pacient")

class Sloturi(Base):
    __tablename__ = "sloturi"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    duration_min = Column(Integer, default=30)
    programari = relationship("Programari", back_populates="slot")

class Programari(Base):
    __tablename__ = "programari"
    id = Column(Integer, primary_key=True)
    pacienti_id = Column(Integer, ForeignKey("pacienti.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("sloturi.id"), nullable=False)
    type = Column(String(50))
    stare = Column(Enum(StareProgramare), default=StareProgramare.programat)
    pacient = relationship("Pacienti", back_populates="programari")
    slot = relationship("Sloturi", back_populates="programari")
    notificari = relationship("Notificari", back_populates="programare")

class ListaAsteptare(Base):
    __tablename__ = "lista_asteptare"
    id = Column(Integer, primary_key=True)
    pacienti_id = Column(Integer, ForeignKey("pacienti.id"), nullable=False)
    data_preferata = Column(Date)
    type = Column(String(50))
    pacient = relationship("Pacienti", back_populates="lista_asteptare")

class Notificari(Base):
    __tablename__ = "notificari"
    id = Column(Integer, primary_key=True)
    programari_id = Column(Integer, ForeignKey("programari.id"), nullable=False)
    send_at = Column(DateTime)
    type = Column(String(50))
    programare = relationship("Programari", back_populates="notificari")