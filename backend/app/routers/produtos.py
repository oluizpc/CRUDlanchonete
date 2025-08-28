from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from typing import List, Optional
from ..models import Produto, User
from ..schemas import ProdutoCreate, Produto as ProdutoSchema, ProdutoUpdate
from ..database import get_db
from .users import get_current_active_user

produtos_router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)

# Rota para listar produtos com filtros (pública)
@produtos_router.get("/", response_model=List[ProdutoSchema])
def listar_produtos(
    db: Session = Depends(get_db),
    descricao: str = Query(None),
    status_ativo: bool = Query(None, alias="status")
):
    query = db.query(Produto)
    
    if descricao:
        query = query.filter(Produto.descricao.ilike(f"%{descricao}%"))
        
    if status_ativo is not None:
        query = query.filter(Produto.status == status_ativo)
    
    return query.all()

# Rota para criar um novo produto (SEM AUTENTICAÇÃO - TEMPORÁRIO)
@produtos_router.post("/", response_model=ProdutoSchema, status_code=status.HTTP_201_CREATED)
def criar_produto(
    produto: ProdutoCreate,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_active_user)    # <-- COMENTADO
):
    try:
        # Converter dados e tratar o preço
        produto_data = produto.model_dump()
        
        # Converter float para Decimal para compatibilidade com banco
        if 'preco' in produto_data:
            produto_data['preco'] = Decimal(str(produto_data['preco']))
        
        # Garantir que status tenha valor padrão
        if 'status' not in produto_data or produto_data['status'] is None:
            produto_data['status'] = True
            
        print(f"DEBUG: Dados processados: {produto_data}")    # Para debug
        
        # Criar produto
        db_produto = Produto(**produto_data)
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        print(f"DEBUG: Produto criado com ID: {db_produto.idproduto}")    # Para debug
        
        return db_produto
        
    except IntegrityError as e:
        db.rollback()
        print(f"DEBUG: Erro de integridade: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um produto com esta descrição. Por favor, escolha outra."
        )
    except Exception as e:
        db.rollback()
        print(f"DEBUG: Erro interno: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Erro interno do servidor: {str(e)}"
        )

# Rota para atualizar um produto existente (SEM AUTENTICAÇÃO - TEMPORÁRIO)
@produtos_router.patch("/{id}", response_model=ProdutoSchema)
def atualizar_produto(
    id: int,
    produto_atualizado: ProdutoUpdate,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_active_user)    # <-- COMENTADO
):
    produto = db.query(Produto).filter(Produto.idproduto == id).first()

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = produto_atualizado.model_dump(exclude_unset=True)
    
    # Converter preço se estiver sendo atualizado
    if 'preco' in update_data and update_data['preco'] is not None:
        update_data['preco'] = Decimal(str(update_data['preco']))

    for key, value in update_data.items():
        setattr(produto, key, value)

    try:
        db.commit()
        db.refresh(produto)
        return produto
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um produto com esta descrição. Por favor, escolha outra."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")

# Rota para deletar um produto (SEM AUTENTICAÇÃO - TEMPORÁRIO)
@produtos_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_produto(
    id: int,
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.idproduto == id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # ✅ NOVO CÓDIGO: Verificar se o produto está em algum pedido
    # A tabela é 'pedido_produtos'. Importe o modelo PedidoProduto no início do arquivo.
    from ..models import PedidoProduto # <--- Adicione esta linha no topo do arquivo

    associacao_existente = db.query(PedidoProduto).filter(PedidoProduto.produto_id == id).first()
    if associacao_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este produto não pode ser excluído porque está associado a um pedido."
        )

    db.delete(produto)
    db.commit()
    return