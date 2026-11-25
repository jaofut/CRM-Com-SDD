from datetime import datetime
from pydantic import BaseModel, Field


class ContatoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    cargo: str = Field(min_length=1, max_length=80)
    telefone_whatsapp: str = Field(min_length=5, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    principal: bool = False


class ContatoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    cargo: str | None = Field(default=None, min_length=1, max_length=80)
    telefone_whatsapp: str | None = Field(default=None, min_length=5, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    principal: bool | None = None


class ContatoOut(BaseModel):
    id: int
    cliente_id: int
    nome: str
    cargo: str
    telefone_whatsapp: str
    email: str | None
    principal: bool

    model_config = {"from_attributes": True}


class MotoristaCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    telefone: str | None = Field(default=None, max_length=30)
    documento: str | None = Field(default=None, max_length=30)
    ativo: bool = True


class MotoristaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    telefone: str | None = Field(default=None, max_length=30)
    documento: str | None = Field(default=None, max_length=30)
    ativo: bool | None = None


class MotoristaOut(BaseModel):
    id: int
    cliente_id: int
    nome: str
    telefone: str | None
    documento: str | None
    ativo: bool

    model_config = {"from_attributes": True}


class ClienteCreate(BaseModel):
    razao_social: str = Field(min_length=1, max_length=180)
    nome_fantasia: str = Field(min_length=1, max_length=180)
    cnpj: str = Field(min_length=11, max_length=18)
    inscricao_estadual: str | None = Field(default=None, max_length=30)
    endereco: str | None = None
    condicoes_comerciais: str | None = None
    observacoes: str | None = None
    ativo: bool = True


class ClienteUpdate(BaseModel):
    razao_social: str | None = Field(default=None, min_length=1, max_length=180)
    nome_fantasia: str | None = Field(default=None, min_length=1, max_length=180)
    cnpj: str | None = Field(default=None, min_length=11, max_length=18)
    inscricao_estadual: str | None = Field(default=None, max_length=30)
    endereco: str | None = None
    condicoes_comerciais: str | None = None
    observacoes: str | None = None
    ativo: bool | None = None


class ClienteResumoOut(BaseModel):
    id: int
    razao_social: str
    nome_fantasia: str
    cnpj: str
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class VeiculoResumoOut(BaseModel):
    id: int
    cliente_id: int
    placa: str
    tipo: str
    marca_modelo: str
    ano: int | None
    chassi: str | None
    km_atual: int

    model_config = {"from_attributes": True}


class ClienteDetalheOut(BaseModel):
    id: int
    razao_social: str
    nome_fantasia: str
    cnpj: str
    inscricao_estadual: str | None
    endereco: str | None
    condicoes_comerciais: str | None
    observacoes: str | None
    ativo: bool
    created_at: datetime
    updated_at: datetime
    contatos: list[ContatoOut] = []
    motoristas: list[MotoristaOut] = []
    veiculos: list[VeiculoResumoOut] = []

    model_config = {"from_attributes": True}
