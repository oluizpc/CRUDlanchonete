# app/routers/pagamentos.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db

pagamentos_router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])

# Rotas de CRUD para pagamentos devem ser implementadas aqui
@pagamentos_router.get("/")
def listar_pagamentos(db: Session = Depends(get_db)):
    return {"mensagem": "Implementar lógica para listar pagamentos"}