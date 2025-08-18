# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .. import schemas, models, database
from ..utils.auth import get_password_hash
from ..utils.auth_token import verify_token

# Adiciona a dependência de segurança OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/login")

# Cria um APIRouter para as rotas de usuários
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Dependência para obter a sessão do banco de dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependência para verificar o token e obter o usuário logado
def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.username == username, models.User.is_active == True).first()
    if user is None:
        raise credentials_exception
    return user

# Rota para criar um novo usuário (POST) - NÃO precisa de proteção
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já registrado"
        )
    
    hashed_password = get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# Rota para obter todos os usuários (GET) - PROTEGIDA
@router.get("/", response_model=list[schemas.User])
def get_all_users(current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# Rota para obter um usuário pelo ID (GET) - PROTEGIDA
@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return user

# Rota para atualizar um usuário (PATCH) - PROTEGIDA
@router.patch("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password" and value:
            setattr(db_user, "hashed_password", get_password_hash(value))
        else:
            setattr(db_user, key, value)
            
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Rota para "deletar" um usuário (DELETE) - PROTEGIDA
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: models.User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    db_user.is_active = False  # Desativa o usuário em vez de deletar
    db.commit()
    # Retorna uma resposta vazia para o status 204
    return {}