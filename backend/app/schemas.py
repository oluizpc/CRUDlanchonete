# app/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# --- Schemas para Produto ---
class ProdutoBase(BaseModel):
    descricao: str
    preco: float
    categoria: Optional[str] = None
    status: bool = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    descricao: Optional[str] = None
    preco: Optional[float] = None
    categoria: Optional[str] = None
    status: Optional[bool] = None

class Produto(ProdutoBase):
    idproduto: int
    data_criacao: Optional[datetime] = None
    data_alteracao: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# NOVO: Esquema simplificado para o Produto
class ProdutoNome(BaseModel):
    idproduto: int
    descricao: str
    model_config = ConfigDict(from_attributes=True)

# --- Schemas para Clientes ---
class ClienteBase(BaseModel):
    nome: str
    email: Optional[str] = None
    apelido: Optional[str] = None
    telefone: Optional[str] = None

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    idcliente: int
    data_criacao: datetime
    data_alteracao: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    apelido: Optional[str] = None
    telefone: Optional[str] = None

# --- Schemas para Mesas ---
# --- Schemas para Mesas ---
class SituacaoMesa(BaseModel):
    id_situacao: int
    situacao_descricao: str
    model_config = ConfigDict(from_attributes=True)

class Cliente_Nome(BaseModel):
    idcliente: int
    nome: str
    model_config = ConfigDict(from_attributes=True)

class MesaBase(BaseModel):
    # ✅ NOVO: Adicione o campo `numero` à base
    numero: int
    id_situacao_fk: int

class MesaCreate(MesaBase):
    pass

class Mesa(MesaBase):
    idmesa: int
    id_cliente_fk: Optional[int] = None
    cliente: Optional[Cliente_Nome] = None
    situacao: SituacaoMesa
    model_config = ConfigDict(from_attributes=True)

class MesaUpdate(BaseModel):
    id_situacao_fk: Optional[int] = None
    id_cliente_fk: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
    
    
# --- Schemas para Pedidos ---
# Schema para criar um item de pedido (usado na rota de lançamento individual)
class PedidoProdutoCreate(BaseModel):
    pedido_id: int
    produto_id: int
    quantidade: int
    preco_unitario: float
    model_config = ConfigDict(from_attributes=True)

# Schema para a criação de um pedido completo com itens
class PedidoCreate(BaseModel):
    cliente_id: int
    mesa_id: int
    itens: List[PedidoProdutoCreate]

# Schema para o retorno de um item de pedido
class PedidoProduto(PedidoProdutoCreate):
    idpedido_produto: int
    # NOVO: Inclui o relacionamento com o Produto para que o frontend possa acessar os dados aninhados.
    produto: Optional[ProdutoNome] = None
    model_config = ConfigDict(from_attributes=True)

# Schema para o retorno de um pedido completo
class Pedido(BaseModel):
    idpedido: int
    cliente_id: int
    mesa_id: int
    data_pedido: datetime
    status: str
    # NOVO: Garante que a lista de itens do pedido usa o novo esquema
    itens: List[PedidoProduto]
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None