from pydantic import BaseModel, EmailStr
from app.models.usuario import PerfilUsuario


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResumo(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    ativo: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResumo
