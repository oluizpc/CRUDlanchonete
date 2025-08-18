# app/routers/produtos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Produto, User
from ..schemas import ProdutoCreate, Produto as ProdutoSchema
from ..database import get_db
# Importe a dependência de autenticação
from .users import get_current_active_user

produtos_router = APIRouter(
    prefix="/produtos", # Adicionado um prefixo aqui
    tags=["Produtos"]
)

# Rota para listar todos os produtos
@produtos_router.get("/", response_model=list[ProdutoSchema])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(Produto).all()

# Rota para criar um novo produto - AGORA PROTEGIDA
@produtos_router.post("/", response_model=ProdutoSchema, status_code=status.HTTP_201_CREATED)
def criar_produto(
    produto: ProdutoCreate, 
    db: Session = Depends(get_db),
    # Adicione a dependência de autenticação
    current_user: User = Depends(get_current_active_user)
):
    try:
        db_produto = Produto(**produto.model_dump())
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        return db_produto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um produto com este nome. Por favor, escolha outro."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

# Rota para atualizar um produto existente (PATCH) - AGORA PROTEGIDA
@produtos_router.patch("/{id}", response_model=ProdutoSchema, status_code=status.HTTP_200_OK)
def update_produto(
    id: int,
    produto_atualizado: ProdutoCreate,
    db: Session = Depends(get_db),
    # Adicione a dependência de autenticação
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza um produto existente no banco de dados.
    - **id**: o ID do produto a ser atualizado.
    - **produto_atualizado**: Os dados de atualização do produto (nome, preco, etc.)
    """
    produto = db.query(Produto).filter(Produto.idproduto == id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = produto_atualizado.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(produto, key, value)

    db.commit()
    db.refresh(produto)
    return produto