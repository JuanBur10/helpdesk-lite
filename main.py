#donde tengo todos los endpoints
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from auth import hash_password, verify_password, create_token, get_current_user

app = FastAPI(title="HelpDesk Lite")


# ==================== AUTENTICACIÓN ====================

@app.post("/auth/register", response_model=schemas.UserResponse, status_code=201)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existe = db.query(models.User).filter(models.User.email == user.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    nuevo = models.User(
        nombre=user.nombre,
        email=user.email,
        password=hash_password(user.password),
        rol=user.rol,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # En "username" se escribe el correo
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if user is None or not verify_password(form.password, user.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    token = create_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


# ==================== TICKETS (protegidos) ====================

@app.post("/tickets/", response_model=schemas.TicketResponse, status_code=201)
def crear_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db),
                 user: models.User = Depends(get_current_user)):
    # El ticket queda asociado al usuario que está autenticado
    nuevo = models.Ticket(
        titulo=ticket.titulo,
        descripcion=ticket.descripcion,
        prioridad=ticket.prioridad,
        fecha=ticket.fecha or date.today(),   # si no envían fecha, queda la de hoy
        owner_id=user.id,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@app.get("/tickets/", response_model=List[schemas.TicketResponse])
def listar_tickets(estado: Optional[schemas.Estado] = None, skip: int = 0, limit: int = 10,
                   db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    consulta = db.query(models.Ticket)

    # Filtro opcional por estado
    if estado:
        consulta = consulta.filter(models.Ticket.estado == estado)

    # Paginación: skip = cuántos saltar, limit = cuántos traer
    return consulta.offset(skip).limit(limit).all()


@app.get("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def obtener_ticket(ticket_id: int, db: Session = Depends(get_db),
                   user: models.User = Depends(get_current_user)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return ticket


@app.patch("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def actualizar_ticket(ticket_id: int, datos: schemas.TicketUpdate, db: Session = Depends(get_db),
                      user: models.User = Depends(get_current_user)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Solo el creador puede modificarlo
    if ticket.owner_id != user.id:
        raise HTTPException(status_code=403, detail="No puedes modificar este ticket")

    # Solo se cambian los campos que se enviaron
    if datos.estado is not None:
        ticket.estado = datos.estado
    if datos.descripcion is not None:
        ticket.descripcion = datos.descripcion
    if datos.prioridad is not None:
        ticket.prioridad = datos.prioridad

    db.commit()
    db.refresh(ticket)
    return ticket


@app.delete("/tickets/{ticket_id}")
def eliminar_ticket(ticket_id: int, db: Session = Depends(get_db),
                    user: models.User = Depends(get_current_user)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    # Solo el propietario puede eliminarlo
    if ticket.owner_id != user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar este ticket")

    db.delete(ticket)
    db.commit()
    return {"mensaje": "Ticket eliminado"}
