# Schemas de Pydantic: validan lo que entra y lo que sale

from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field

# Valores permitidos
Estado = Literal["abierto", "en_proceso", "cerrado"]
Prioridad = Literal["bajo", "medio", "alto"]


# ---------- Usuarios ----------
class UserCreate(BaseModel):
    nombre: str
    email: EmailStr                            # valida que sea un correo
    password: str = Field(min_length=8)        # mínimo 8 caracteres
    rol: Literal["tecnico", "empleado"] = "empleado"


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str

    class Config:
        from_attributes = True


# ---------- Tickets ----------
class TicketCreate(BaseModel):
    titulo: str
    descripcion: str
    prioridad: Prioridad = "medio"
    fecha: Optional[date] = None   # si no se envía, se pone la fecha de hoy


class TicketUpdate(BaseModel):
    # Todo opcional porque es una actualización parcial (PATCH)
    estado: Optional[Estado] = None
    descripcion: Optional[str] = None
    prioridad: Optional[Prioridad] = None


class TicketResponse(BaseModel):
    id: int
    titulo: str
    descripcion: str
    estado: str
    prioridad: str
    owner_id: int
    fecha: Optional[date] = None

    class Config:
        from_attributes = True
