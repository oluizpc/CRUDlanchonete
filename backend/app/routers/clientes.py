from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Cliente
from ..schemas import ClienteCreate, ClienteUpdate, Cliente
from ..database import get_db

clientes_router = APIRouter(prefix="/clientes", tags=["Clientes"])

@clientes_router.get("/", response_model=list[Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).filter(Cliente.is_active == True).all()

@clientes_router.post("/", response_model=Cliente, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    try:
        db_cliente = Cliente(**cliente_data.model_dump())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um cliente com este nome ou e-mail. Por favor, escolha outro."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {e}")

@clientes_router.put("/{id}", response_model=Cliente)
def atualizar_cliente(id: int, cliente_atualizado: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.idcliente == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    update_data = cliente_atualizado.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cliente, key, value)

    db.commit()
    db.refresh(cliente)
    return cliente

@clientes_router.patch("/{id}", response_model=Cliente)
def desativar_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.idcliente == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    cliente.is_active = False
    db.commit()
    db.refresh(cliente)
    return cliente