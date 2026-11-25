from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, verify_password
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioResumo

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if not user or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário desativado",
        )
    token = create_access_token(user.id, user.perfil)
    return TokenResponse(access_token=token, usuario=UsuarioResumo.model_validate(user))


@router.get("/me", response_model=UsuarioResumo)
def me(current_user: Usuario = Depends(get_current_user)):
    return UsuarioResumo.model_validate(current_user)
