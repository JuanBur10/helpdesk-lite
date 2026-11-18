# Tablas de la base de datos
from datetime import date
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)   # se guarda con hash, no en texto plano
    rol = Column(String, default="empleado")     # tecnico o empleado

    # Un usuario tiene muchos tickets (1:N)
    tickets = relationship("Ticket", back_populates="owner")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    estado = Column(String, default="abierto")
    prioridad = Column(String, default="medio")
    fecha = Column(Date, default=date.today)  # se agregó en la migración 3

    # Cada ticket pertenece a un usuario
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tickets")
