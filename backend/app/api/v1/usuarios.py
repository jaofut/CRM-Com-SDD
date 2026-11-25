from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, require_role
from app.models.usuario import PerfilUsuario, Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuários (ADMIN)"])


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role([PerfilUsuario.ADMIN])),
):
    return list(db.scalars(select(Usuario).order_by(Usuario.nome.asc())).all())


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role([PerfilUsuario.ADMIN])),
):
    existing = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if existing:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")
    user = Usuario(
        nome=payload.nome.strip(),
        email=payload.email,
        senha_hash=hash_password(payload.senha),
        perfil=payload.perfil,
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role([PerfilUsuario.ADMIN])),
):
    user = db.get(Usuario, usuario_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "senha" in data and data["senha"]:
        user.senha_hash = hash_password(data.pop("senha"))
    for key, val in data.items():
        setattr(user, key, val)
    db.commit()
    db.refresh(user)
    return user
