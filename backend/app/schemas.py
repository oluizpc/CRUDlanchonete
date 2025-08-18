# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List 
from datetime import datetime, date 

# --- Schemas para Produtos ---
class ProdutoBase(BaseModel):
    nome: str
    preco: float
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    status: Optional[bool] = None

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    idproduto: int
    data_criacao: datetime
    data_alteracao: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    status: Optional[bool] = None

# --- Schemas para Clientes ---
class ClienteCreate(BaseModel):
    nome: str
    email: Optional[str] = None 
    apelido: Optional[str] = None
    telefone: Optional[str] = None

class Cliente(ClienteCreate):
    idcliente: int
    data_criacao: datetime
    data_alteracao: datetime

    class Config:
        from_attributes = True

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    apelido: Optional[str] = None
    telefone: Optional[str] = None

# --- Schemas para Mesas ---
class MesaCreate(BaseModel):
    numero: int
    id_situacao_fk: int

class Mesa(MesaCreate):
    idmesa: int
    data_criacao: datetime
    data_alteracao: Optional[datetime] = None 

    class Config:
        from_attributes = True

# --- Schemas para Pedidos ---
class PedidoProdutoCreate(BaseModel):
    produto_id: int
    quantidade: int

class PedidoCreate(BaseModel):
    cliente_id: int
    mesa_id: int
    itens: List[PedidoProdutoCreate]

class PedidoProduto(PedidoProdutoCreate):
    idpedido_produto: int
    preco_unitario: float

    class Config:
        from_attributes = True

class Pedido(BaseModel):
    idpedido: int
    cliente_id: int
    mesa_id: int
    data_pedido: datetime
    status: str
    itens: List[PedidoProduto]

    class Config:
        from_attributes = True

class PedidoProdutoUpdate(BaseModel):
    idpedido_produto: Optional[int] = None
    produto_id: Optional[int] = None
    quantidade: Optional[int] = None

class PedidoUpdate(BaseModel):
    cliente_id: Optional[int] = None
    mesa_id: Optional[int] = None
    status: Optional[str] = None
    itens: Optional[List[PedidoProdutoUpdate]] = None

# --- Schemas para Auth e Users ---
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str
    is_active: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None