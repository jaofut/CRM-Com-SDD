from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.crm import StatusLembrete, TipoInteracao, TipoLembrete


class InteracaoCreate(BaseModel):
    tipo: TipoInteracao
    resumo: str = Field(min_length=1)


class InteracaoOut(BaseModel):
    id: int
    cliente_id: int
    usuario_id: int
    usuario_nome: str | None = None
    tipo: TipoInteracao
    resumo: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LembreteCreate(BaseModel):
    cliente_id: int
    veiculo_id: int | None = None
    os_origem_id: int | None = None
    tipo: TipoLembrete = TipoLembrete.FOLLOW_UP
    titulo: str = Field(min_length=1, max_length=160)
    data_prevista: date
    km_previsto: int | None = Field(default=None, ge=0)
    observacoes: str | None = None


class LembreteUpdate(BaseModel):
    status: StatusLembrete
    data_prevista: date | None = None
    observacoes: str | None = None


class LembreteOut(BaseModel):
    id: int
    cliente_id: int
    veiculo_id: int | None
    os_origem_id: int | None
    usuario_responsavel_id: int
    tipo: TipoLembrete
    titulo: str
    data_prevista: date
    km_previsto: int | None
    status: StatusLembrete
    observacoes: str | None
    created_at: datetime
    cliente_nome: str | None = None
    veiculo_placa: str | None = None

    model_config = {"from_attributes": True}
