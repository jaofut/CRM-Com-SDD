from app.models.usuario import PerfilUsuario, Usuario
from app.models.cliente import Cliente, Contato, Motorista
from app.models.veiculo import TipoVeiculo, Veiculo
from app.models.orcamento import EtapaOrcamento, Orcamento, OrcamentoItem, TipoItem
from app.models.ordem_servico import (
    OrdemServico,
    OrdemServicoHistorico,
    OrdemServicoItem,
    StatusOS,
)
from app.models.crm import (
    Interacao,
    Lembrete,
    StatusLembrete,
    TipoInteracao,
    TipoLembrete,
)

__all__ = [
    "PerfilUsuario",
    "Usuario",
    "Cliente",
    "Contato",
    "Motorista",
    "TipoVeiculo",
    "Veiculo",
    "EtapaOrcamento",
    "Orcamento",
    "OrcamentoItem",
    "TipoItem",
    "OrdemServico",
    "OrdemServicoItem",
    "OrdemServicoHistorico",
    "StatusOS",
    "Interacao",
    "Lembrete",
    "TipoInteracao",
    "TipoLembrete",
    "StatusLembrete",
]
