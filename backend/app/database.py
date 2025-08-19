from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# A string de conexão correta para o seu projeto no Supabase

# Cria o "motor" do SQLAlchemy com a sua DATABASE_URL
engine = create_engine(DATABASE_URL)

# Cria uma sessão local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependência para as rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
