# app/routers/__init__.py

from .clientes import clientes_router
from .mesas import mesas_router
from .produtos import produtos_router
from .pedidos import pedidos_router
from .pagamentos import pagamentos_router
from .situacao_mesas import situacao_mesas_router
from .pedido_produtos import pedido_produtos_router
from . import users
from . import auth