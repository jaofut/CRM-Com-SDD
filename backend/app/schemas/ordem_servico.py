from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.orcamento import TipoItem
from app.models.ordem_servico import StatusOS


class OSItemIn(BaseModel):
    tipo: TipoItem
    descricao: str = Field(min_length=1, max_length=200)
    quantidade: Decimal = Field(gt=0)
    valor_unitario: Decimal = Field(ge=0)


class OSItemOut(BaseModel):
    id: int
    tipo: TipoItem
    descricao: str
    quantidade: Decimal
    valor_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OSHistoricoOut(BaseModel):
    id: int
    status_anterior: str | None
    status_novo: str
    usuario_id: int
    observacao: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConverterOrcamentoOSRequest(BaseModel):
    km_entrada: int = Field(ge=0)
    confirmar_km_menor: bool = False
    motorista_entrada_id: int | None = None
    avarias_entrada: str | None = None


class OrdemServicoCreate(BaseModel):
    cliente_id: int
    veiculo_id: int
    km_entrada: int = Field(ge=0)
    confirmar_km_menor: bool = False
    motorista_entrada_id: int | None = None
    avarias_entrada: str | None = None
    itens: list[OSItemIn] = []


class OrdemServicoStatusUpdate(BaseModel):
    status: StatusOS
    observacao: str | None = None
    motorista_saida_id: int | None = None
    observacoes_saida: str | None = None
    preventiva_dias: int | None = Field(default=90, ge=1, le=730)
    km_previsto_proxima_revisao: int | None = Field(default=None, ge=0)


class OrdemServicoOut(BaseModel):
    id: int
    numero: str
    orcamento_id: int | None
    cliente_id: int
    veiculo_id: int
    usuario_abertura_id: int
    status: StatusOS
    km_entrada: int
    confirmar_km_menor: bool
    motorista_entrada_id: int | None
    avarias_entrada: str | None
    motorista_saida_id: int | None
    observacoes_saida: str | None
    valor_total: Decimal
    data_entrada: datetime
    data_entrega: datetime | None
    cliente_nome: str | None = None
    veiculo_placa: str | None = None
    motorista_entrada_nome: str | None = None
    motorista_saida_nome: str | None = None
    itens: list[OSItemOut] = []
    historico: list[OSHistoricoOut] = []

    model_config = {"from_attributes": True}
