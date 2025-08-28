# app/routers/pedido_produtos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

pedido_produtos_router = APIRouter(
    prefix="/pedido_produtos", 
    tags=["Itens de Pedido"]
)

@pedido_produtos_router.post("/", response_model=schemas.PedidoProduto, status_code=status.HTTP_201_CREATED)
def criar_pedido_produto(item: schemas.PedidoProdutoCreate, db: Session = Depends(get_db)):
    # Verifica se o pedido existe e está aberto
    pedido = db.query(models.Pedido).filter(
        models.Pedido.idpedido == item.pedido_id,
        models.Pedido.status == 'aberto'
    ).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado ou não está aberto.")
    
    # Verifica se o produto existe
    produto = db.query(models.Produto).filter(models.Produto.idproduto == item.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    
    # Cria o novo item de pedido
    db_item = models.PedidoProduto(
        pedido_id=item.pedido_id,
        produto_id=item.produto_id,
        quantidade=item.quantidade,
        preco_unitario=produto.preco # Garante que o preço unitário vem do produto
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@pedido_produtos_router.get("/", response_model=list[schemas.PedidoProduto])
def listar_pedido_produtos(db: Session = Depends(get_db)):
    return db.query(models.PedidoProduto).all()

# --- NOVAS ROTAS ---

@pedido_produtos_router.delete("/{idpedido_produto}", status_code=status.HTTP_204_NO_CONTENT)
def remover_pedido_produto(idpedido_produto: int, db: Session = Depends(get_db)):
    item = db.query(models.PedidoProduto).filter(models.PedidoProduto.idpedido_produto == idpedido_produto).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item de pedido não encontrado.")
    
    db.delete(item)
    db.commit()
    return

@pedido_produtos_router.put("/{idpedido_produto}", response_model=schemas.PedidoProduto)
def atualizar_quantidade_pedido_produto(idpedido_produto: int, item_update: schemas.PedidoProdutoUpdate, db: Session = Depends(get_db)):
    item = db.query(models.PedidoProduto).filter(models.PedidoProduto.idpedido_produto == idpedido_produto).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item de pedido não encontrado.")
        
    if item_update.quantidade is not None:
        if item_update.quantidade <= 0:
            raise HTTPException(status_code=400, detail="A quantidade deve ser maior que zero. Use a rota DELETE para remover o item.")
        item.quantidade = item_update.quantidade

    db.commit()
    db.refresh(item)
    return item