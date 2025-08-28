from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import Cliente as ClienteModel
from ..schemas import ClienteCreate, ClienteUpdate, Cliente as ClienteSchema
from ..database import get_db

clientes_router = APIRouter(prefix="/clientes", tags=["Clientes"])

@clientes_router.get("/", response_model=List[ClienteSchema])
def listar_clientes(
    db: Session = Depends(get_db),
    nomeRazaoSocial: Optional[str] = Query(None),
    apelidoNomeFantasia: Optional[str] = Query(None),
    cidade: Optional[str] = Query(None),
    situacao: Optional[str] = Query(None),
    celularTelefone: Optional[str] = Query(None),
    cpf: Optional[str] = Query(None)
):
    """
    Lista todos os clientes e permite filtrar por diversos campos.
    """
    query = db.query(ClienteModel)
    if nomeRazaoSocial:
        query = query.filter(ClienteModel.nome.ilike(f"%{nomeRazaoSocial}%"))
    if apelidoNomeFantasia:
        query = query.filter(ClienteModel.apelido.ilike(f"%{apelidoNomeFantasia}%"))
    if cidade:
        query = query.filter(ClienteModel.cidade.ilike(f"%{cidade}%"))
    if situacao == "ativos":
        query = query.filter(ClienteModel.is_active == True)
    elif situacao == "inativos":
        query = query.filter(ClienteModel.is_active == False)
    if celularTelefone:
        query = query.filter(ClienteModel.telefone.ilike(f"%{celularTelefone}%"))
    if cpf:
        query = query.filter(ClienteModel.cpf.ilike(f"%{cpf}%"))
    
    return query.all()

@clientes_router.post("/", response_model=ClienteSchema, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = ClienteModel(**cliente_data.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

@clientes_router.put("/{id}", response_model=ClienteSchema)
def atualizar_cliente(id: int, cliente_atualizado: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.idcliente == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    update_data = cliente_atualizado.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente

@clientes_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_cliente(id: int, db: Session = Depends(get_db)):
    """
    Exclui um cliente pelo ID.
    """
    cliente = db.query(ClienteModel).filter(ClienteModel.idcliente == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(cliente)
    db.commit()
    return None

@clientes_router.patch("/{id}", response_model=ClienteSchema)
def desativar_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.idcliente == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cliente.is_active = False
    db.commit()
    db.refresh(cliente)
    return cliente