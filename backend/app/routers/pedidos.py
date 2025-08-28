# app/routers/pedidos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from .. import models, schemas
from ..database import get_db

pedidos_router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@pedidos_router.get("/mesa/{mesa_id}", response_model=schemas.Pedido)
def buscar_pedido_por_mesa(mesa_id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.mesa_id == mesa_id,
        models.Pedido.status == 'aberto'
    ).options(
        joinedload(models.Pedido.itens).joinedload(models.PedidoProduto.produto)
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Nenhum pedido aberto encontrado para esta mesa.")
    
    return pedido

# Rota adicionada para buscar um pedido por seu ID (requisitada pelo frontend)
@pedidos_router.get("/{pedido_id}", response_model=schemas.Pedido)
def buscar_pedido_por_id(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.idpedido == pedido_id
    ).options(
        joinedload(models.Pedido.itens).joinedload(models.PedidoProduto.produto)
    ).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    
    return pedido


@pedidos_router.post("/mesa/{mesa_id}", response_model=schemas.Pedido, status_code=status.HTTP_201_CREATED)
def criar_pedido_para_mesa(mesa_id: int, cliente_id: int, db: Session = Depends(get_db)):
    # Verifica se já existe um pedido aberto para esta mesa
    existing_pedido = db.query(models.Pedido).filter(
        models.Pedido.mesa_id == mesa_id,
        models.Pedido.status == 'aberto'
    ).first()
    
    if existing_pedido:
        raise HTTPException(status_code=400, detail="Já existe um pedido aberto para esta mesa.")
        
    novo_pedido = models.Pedido(mesa_id=mesa_id, cliente_id=cliente_id, status='aberto')
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido

@pedidos_router.post("/", response_model=schemas.Pedido, status_code=status.HTTP_201_CREATED)
def criar_pedido_com_itens(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    novo_pedido = models.Pedido(cliente_id=pedido.cliente_id, mesa_id=pedido.mesa_id, status=pedido.status)
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    for item_data in pedido.itens:
        produto = db.query(models.Produto).filter(models.Produto.idproduto == item_data.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto com ID {item_data.produto_id} não encontrado.")

        novo_item = models.PedidoProduto(
            pedido_id=novo_pedido.idpedido,
            produto_id=item_data.produto_id,
            quantidade=item_data.quantidade,
            preco_unitario=produto.preco
        )
        db.add(novo_item)
    
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
    
    
