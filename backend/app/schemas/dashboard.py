from decimal import Decimal
from pydantic import BaseModel


class MotivoRecusaItem(BaseModel):
    motivo: str
    quantidade: int


class DashboardGerencialOut(BaseModel):
    total_orcamentos: int
    total_orcado: Decimal
    total_aprovado: Decimal
    taxa_conversao_percent: float
    os_por_status: dict[str, int]
    valor_os_entregues: Decimal
    motivos_recusa: list[MotivoRecusaItem]
