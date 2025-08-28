# app/routers/mesas.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

mesas_router = APIRouter(prefix="/mesas", tags=["Mesas"])

@mesas_router.get("/", response_model=list[schemas.Mesa])
def listar_mesas(db: Session = Depends(get_db)):
    return db.query(models.Mesa).order_by(models.Mesa.numero).all()

@mesas_router.get("/{id}", response_model=schemas.Mesa)
def obter_mesa(id: int, db: Session = Depends(get_db)):
    mesa = db.query(models.Mesa).filter(models.Mesa.idmesa == id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    return mesa

@mesas_router.post("/", response_model=schemas.Mesa, status_code=status.HTTP_201_CREATED)
def criar_mesa(mesa: schemas.MesaCreate, db: Session = Depends(get_db)):
    # ✅ NOVO: Adicione uma verificação para evitar números duplicados no banco de dados.
    db_mesa_existente = db.query(models.Mesa).filter(models.Mesa.numero == mesa.numero).first()
    if db_mesa_existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe uma mesa com este número.")

    db_mesa = models.Mesa(**mesa.model_dump())
    db.add(db_mesa)
    db.commit()
    db.refresh(db_mesa)
    return db_mesa

@mesas_router.put("/{id}", response_model=schemas.Mesa)
def atualizar_mesa(id: int, mesa: schemas.MesaUpdate, db: Session = Depends(get_db)):
    db_mesa = db.query(models.Mesa).filter(models.Mesa.idmesa == id).first()
    if not db_mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")

    for key, value in mesa.model_dump(exclude_unset=True).items():
        setattr(db_mesa, key, value)
    
    db.commit()
    db.refresh(db_mesa)
    return db_mesa

@mesas_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_mesa(id: int, db: Session = Depends(get_db)):
    mesa = db.query(models.Mesa).filter(models.Mesa.idmesa == id).first()
    if not mesa:
        raise HTTPException(status_code=404, detail="Mesa não encontrada.")
    db.delete(mesa)
    db.commit()