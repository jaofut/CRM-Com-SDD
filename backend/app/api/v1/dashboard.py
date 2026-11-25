from datetime import date, datetime, time, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.models.orcamento import EtapaOrcamento, Orcamento
from app.models.ordem_servico import OrdemServico, StatusOS
from app.models.usuario import PerfilUsuario, Usuario
from app.schemas.dashboard import DashboardGerencialOut, MotivoRecusaItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard Gerencial (ADMIN)"])


@router.get("/gerencial", response_model=DashboardGerencialOut)
def dashboard_gerencial(
    inicio: date | None = Query(default=None),
    fim: date | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_role([PerfilUsuario.ADMIN])),
):
    orc_stmt = select(Orcamento)
    os_stmt = select(OrdemServico)
    if inicio:
        dt_ini = datetime.combine(inicio, time.min, tzinfo=timezone.utc)
        orc_stmt = orc_stmt.where(Orcamento.created_at >= dt_ini)
        os_stmt = os_stmt.where(OrdemServico.data_entrada >= dt_ini)
    if fim:
        dt_fim = datetime.combine(fim, time.max, tzinfo=timezone.utc)
        orc_stmt = orc_stmt.where(Orcamento.created_at <= dt_fim)
        os_stmt = os_stmt.where(OrdemServico.data_entrada <= dt_fim)

    orcs = list(db.scalars(orc_stmt).all())
    ordens = list(db.scalars(os_stmt).all())

    total_orcamentos = len(orcs)
    total_orcado = sum((o.valor_total for o in orcs), Decimal("0.00"))
    aprovados = [o for o in orcs if o.etapa == EtapaOrcamento.APROVADO]
    total_aprovado = sum((o.valor_total for o in aprovados), Decimal("0.00"))
    taxa = round((len(aprovados) / total_orcamentos) * 100, 2) if total_orcamentos > 0 else 0.0

    os_por_status = {s.value: 0 for s in StatusOS}
    valor_entregues = Decimal("0.00")
    for os_obj in ordens:
        os_por_status[os_obj.status.value] = os_por_status.get(os_obj.status.value, 0) + 1
        if os_obj.status == StatusOS.ENTREGUE:
            valor_entregues += os_obj.valor_total

    recusa_counts: dict[str, int] = {}
    for o in orcs:
        if o.etapa == EtapaOrcamento.RECUSADO and o.motivo_recusa:
            recusa_counts[o.motivo_recusa] = recusa_counts.get(o.motivo_recusa, 0) + 1
    motivos = [
        MotivoRecusaItem(motivo=m, quantidade=q)
        for m, q in sorted(recusa_counts.items(), key=lambda x: -x[1])
    ]

    return DashboardGerencialOut(
        total_orcamentos=total_orcamentos,
        total_orcado=total_orcado,
        total_aprovado=total_aprovado,
        taxa_conversao_percent=taxa,
        os_por_status=os_por_status,
        valor_os_entregues=valor_entregues,
        motivos_recusa=motivos,
    )
