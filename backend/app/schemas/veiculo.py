from datetime import datetime
from pydantic import BaseModel, Field
from app.models.veiculo import TipoVeiculo


class VeiculoCreate(BaseModel):
    placa: str = Field(min_length=7, max_length=10)
    tipo: TipoVeiculo
    marca_modelo: str = Field(min_length=1, max_length=120)
    ano: int | None = None
    chassi: str | None = Field(default=None, max_length=30)
    km_atual: int = Field(default=0, ge=0)


class VeiculoUpdate(BaseModel):
    cliente_id: int | None = None
    placa: str | None = Field(default=None, min_length=7, max_length=10)
    tipo: TipoVeiculo | None = None
    marca_modelo: str | None = Field(default=None, min_length=1, max_length=120)
    ano: int | None = None
    chassi: str | None = Field(default=None, max_length=30)
    km_atual: int | None = Field(default=None, ge=0)


class VeiculoOut(BaseModel):
    id: int
    cliente_id: int
    placa: str
    tipo: TipoVeiculo
    marca_modelo: str
    ano: int | None
    chassi: str | None
    km_atual: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class BuscaClienteItem(BaseModel):
    id: int
    nome_fantasia: str
    razao_social: str
    cnpj: str


class BuscaVeiculoItem(BaseModel):
    id: int
    placa: str
    marca_modelo: str
    cliente_id: int
    cliente_nome: str


class BuscaGlobalResponse(BaseModel):
    clientes: list[BuscaClienteItem]
    veiculos: list[BuscaVeiculoItem]
