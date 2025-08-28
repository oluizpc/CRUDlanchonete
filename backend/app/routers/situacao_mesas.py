# app/routers/situacao_mesas.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import SituacaoMesa as SituacaoMesaModel
from ..schemas import SituacaoMesa as SituacaoMesaSchema

situacao_mesas_router = APIRouter(
    prefix="/situacoes_mesas",
    tags=["Situação das Mesas"]
)

@situacao_mesas_router.get("/", response_model=list[SituacaoMesaSchema])
def listar_situacoes_mesa(db: Session = Depends(get_db)):
    return db.query(SituacaoMesaModel).all()