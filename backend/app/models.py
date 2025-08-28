# app/models.py
from typing import Optional
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Produto(Base):
    __tablename__ = 'produtos'
    idproduto = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String, nullable=False, unique=True)
    preco = Column(Numeric(10,2), nullable=False)
    categoria = Column(String(50), nullable=True)
    status = Column(Boolean, default=True)
    data_criacao = Column(DateTime, server_default=func.now())
    data_alteracao = Column(DateTime, onupdate=func.now())
    pedido_produtos = relationship("PedidoProduto", back_populates="produto")

class SituacaoMesa(Base):
    __tablename__ = 'situacao_mesa'
    id_situacao = Column(Integer, primary_key=True, autoincrement=True)
    situacao_descricao = Column(String(50), nullable=False, unique=True)
    
    mesas = relationship("Mesa", back_populates="situacao")

class Mesa(Base):
    __tablename__ = 'mesas'
    idmesa = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(Integer, nullable=False, unique=True)
    id_situacao_fk = Column(Integer, ForeignKey('situacao_mesa.id_situacao'), nullable=False)
    id_cliente_fk = Column(Integer, ForeignKey('clientes.idcliente'), nullable=True) # Adicionado
    data_criacao = Column(DateTime, server_default=func.now())
    data_alteracao = Column(DateTime, onupdate=func.now())
    
    situacao = relationship("SituacaoMesa", back_populates="mesas")
    cliente = relationship("Cliente", back_populates="mesas")
    pedidos = relationship("Pedido", back_populates="mesa")

class Cliente(Base):
    __tablename__ = 'clientes'
    idcliente = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    apelido = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True, unique=True) # ✅ LINHA A SER ALTERADA
    telefone = Column(String(20), nullable=True)
    data_criacao = Column(DateTime, server_default=func.now())
    data_alteracao = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    pedidos = relationship("Pedido", back_populates="cliente")
    mesas = relationship("Mesa", back_populates="cliente")

class Pedido(Base):
    __tablename__ = 'pedidos'
    idpedido = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(Integer, ForeignKey('clientes.idcliente'), nullable=False)
    mesa_id = Column(Integer, ForeignKey('mesas.idmesa'), nullable=False)
    data_pedido = Column(DateTime, server_default=func.now())
    status = Column(String(20), default='Pendente')
    
    cliente = relationship("Cliente", back_populates="pedidos")
    mesa = relationship("Mesa", back_populates="pedidos")
    itens = relationship("PedidoProduto", back_populates="pedido")
    pagamento = relationship("Pagamento", back_populates="pedido", uselist=False)

class PedidoProduto(Base):
    __tablename__ = 'pedido_produtos' 
    idpedido_produto = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.idpedido'), nullable=False)
    produto_id = Column(Integer, ForeignKey('produtos.idproduto'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Numeric(10,2), nullable=False)
    data_criacao = Column(DateTime, server_default=func.now())
    data_alteracao = Column(DateTime, onupdate=func.now())
    
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")

class Pagamento(Base):
    __tablename__ = 'pagamentos'
    idpagamento = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.idpedido'), nullable=False)
    valor = Column(Numeric(10,2), nullable=False)
    data_pagamento = Column(DateTime, server_default=func.now())
    metodo_pagamento = Column(String(50), nullable=False)
    
    pedido = relationship("Pedido", back_populates="pagamento")

class TipoPagamento(Base):
    __tablename__ = "tipo_pagamentos"
    idtipopagamento = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(200))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, onupdate=func.now())