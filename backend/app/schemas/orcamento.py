from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.models.orcamento import EtapaOrcamento, TipoItem


class OrcamentoItemIn(BaseModel):
    tipo: TipoItem
    descricao: str = Field(min_length=1, max_length=200)
    quantidade: Decimal = Field(gt=0)
    valor_unitario: Decimal = Field(ge=0)


class OrcamentoItemOut(BaseModel):
    id: int
    tipo: TipoItem
    descricao: str
    quantidade: Decimal
    valor_unitario: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrcamentoCreate(BaseModel):
    cliente_id: int
    contato_id: int
    veiculo_id: int
    validade_dias: int = Field(default=15, ge=1, le=365)
    desconto_total: Decimal = Field(default=Decimal("0.00"), ge=0)
    observacoes: str | None = None
    itens: list[OrcamentoItemIn] = Field(min_length=1)


class OrcamentoUpdate(BaseModel):
    validade_dias: int | None = Field(default=None, ge=1, le=365)
    desconto_total: Decimal | None = Field(default=None, ge=0)
    observacoes: str | None = None
    itens: list[OrcamentoItemIn] | None = None


class OrcamentoEtapaUpdate(BaseModel):
    etapa: EtapaOrcamento
    po_aprovacao: str | None = Field(default=None, max_length=60)
    motivo_recusa: str | None = Field(default=None, max_length=200)


class OrcamentoOut(BaseModel):
    id: int
    numero: str
    cliente_id: int
    contato_id: int
    veiculo_id: int
    usuario_id: int
    etapa: EtapaOrcamento
    validade_dias: int
    desconto_total: Decimal
    valor_total: Decimal
    po_aprovacao: str | None
    motivo_recusa: str | None
    observacoes: str | None
    created_at: datetime
    updated_at: datetime
    cliente_nome: str | None = None
    veiculo_placa: str | None = None
    contato_nome: str | None = None
    contato_whatsapp: str | None = None
    itens: list[OrcamentoItemOut] = []

    model_config = {"from_attributes": True}
