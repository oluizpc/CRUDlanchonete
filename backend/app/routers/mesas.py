# app/routers/mesas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Mesa
from ..schemas import MesaCreate, Mesa as MesaSchema

mesas_router = APIRouter(prefix="/mesas", tags=["Mesas"])

@mesas_router.get("/", response_model=list[MesaSchema])
def listar_mesas(db: Session = Depends(get_db)):
    return db.query(Mesa).all()

@mesas_router.post("/", response_model=MesaSchema, status_code=status.HTTP_201_CREATED)
def criar_mesa(mesa: MesaCreate, db: Session = Depends(get_db)):
    nova_mesa = Mesa(**mesa.model_dump())
    db.add(nova_mesa)
    try:
        db.commit()
        db.refresh(nova_mesa)
        return nova_mesa
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mesa já existe")