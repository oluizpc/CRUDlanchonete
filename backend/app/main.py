from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from app.routers import (
    users, 
    auth, 
    produtos_router, 
    mesas_router, 
    clientes_router, 
    pedidos_router, 
    pagamentos_router,
    situacao_mesas_router, # Adicionado
    pedido_produtos_router # Adicionado
)

app = FastAPI(title="Restaurante API", description="API para gerenciamento de restaurante", version="1.0.0")

# Lista de origens permitidas (localhost:3000 para o seu frontend)
origins = [
    "http://localhost",
    "http://localhost:3000",
]

# Adicione o middleware CORS à sua aplicação
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    print("Tentando criar tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
except Exception as e:
    print("\nERRO GRAVE: Falha na conexão ou na criação das tabelas!")
    print(f"Detalhes do erro: {e}")

# Inclua os routers
app.include_router(produtos_router)
app.include_router(mesas_router)
app.include_router(clientes_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)
app.include_router(users.router) 
app.include_router(auth.router)
app.include_router(situacao_mesas_router)
app.include_router(pedido_produtos_router)