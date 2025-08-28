from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, database
from ..utils.auth import verify_password
from ..utils.auth_token import create_access_token

router = APIRouter(
    prefix="/token",
    tags=["Auth"]
)

# A dependência para o banco de dados pode ser reutilizada
def get_db():
    db = database.SessionLocal()
    try: 
        yield db
    finally:
        db.close()

# Endpoint para login e geração de token JWT
@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha ou usuário incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}