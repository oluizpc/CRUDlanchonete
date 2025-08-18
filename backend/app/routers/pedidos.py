# app/routers/pedidos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from .. import models, schemas
from ..database import get_db

pedidos_router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@pedidos_router.get("/", response_model=list[schemas.Pedido])
def listar_pedidos(db: Session = Depends(get_db)):
    return db.query(models.Pedido).options(joinedload(models.Pedido.itens)).all()

@pedidos_router.get("/{id}", response_model=schemas.Pedido)
def obter_pedido(id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).options(joinedload(models.Pedido.itens)).filter(models.Pedido.idpedido == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    return pedido

@pedidos_router.post("/", response_model=schemas.Pedido, status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    pedido_data = pedido.model_dump(exclude={"itens"})
    itens_data = pedido.itens

    novo_pedido = models.Pedido(**pedido_data)

    for item in itens_data:
        produto = db.query(models.Produto).filter(models.Produto.idproduto == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto com ID {item.produto_id} não encontrado.")

        novo_item_pedido = models.PedidoProduto(
            produto_id=item.produto_id,
            quantidade=item.quantidade,
            preco_unitario=produto.preco
        )
        novo_pedido.itens.append(novo_item_pedido)

    db.add(novo_pedido)
    try:
        db.commit()
        db.refresh(novo_pedido)
        return novo_pedido
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade ao criar pedido.")

@pedidos_router.put("/{id}", response_model=schemas.Pedido)
def atualizar_pedido(id: int, pedido_atualizado: schemas.PedidoUpdate, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.idpedido == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    
    update_data = pedido_atualizado.model_dump(exclude={"itens"}, exclude_unset=True)
    for key, value in update_data.items():
        setattr(pedido, key, value)

    if pedido_atualizado.itens is not None:
        itens_existentes = {item.idpedido_produto: item for item in pedido.itens}
        ids_na_requisicao = {item.idpedido_produto for item in pedido_atualizado.itens if item.idpedido_produto is not None}

        for item_data in pedido_atualizado.itens:
            if item_data.idpedido_produto in itens_existentes:
                item_existente = itens_existentes[item_data.idpedido_produto]
                if item_data.produto_id is not None:
                    item_existente.produto_id = item_data.produto_id
                if item_data.quantidade is not None:
                    item_existente.quantidade = item_data.quantidade
            elif item_data.idpedido_produto is None:
                if item_data.produto_id is not None and item_data.quantidade is not None:
                    produto = db.query(models.Produto).filter(models.Produto.idproduto == item_data.produto_id).first()
                    if not produto:
                        raise HTTPException(status_code=404, detail=f"Produto com ID {item_data.produto_id} não encontrado.")
                    
                    novo_item = models.PedidoProduto(
                        pedido_id=pedido.idpedido,
                        produto_id=item_data.produto_id,
                        quantidade=item_data.quantidade,
                        preco_unitario=produto.preco
                    )
                    db.add(novo_item)

        for id_item, item_existente in itens_existentes.items():
            if id_item not in ids_na_requisicao:
                db.delete(item_existente)

    db.commit()
    db.refresh(pedido)
    return pedido

@pedidos_router.delete("/{id_pedido}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pedido(id_pedido: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(models.Pedido.idpedido == id_pedido).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    
    for item in pedido.itens:
        db.delete(item)

    db.delete(pedido)
    db.commit()

@pedidos_router.delete("/{id_pedido}/itens/{id_item}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_item_do_pedido(id_pedido: int, id_item: int, db: Session = Depends(get_db)):
    item = db.query(models.PedidoProduto).filter(
        models.PedidoProduto.idpedido_produto == id_item,
        models.PedidoProduto.pedido_id == id_pedido
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item de pedido não encontrado.")

    db.delete(item)
    db.commit()