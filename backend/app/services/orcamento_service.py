from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.cliente import Cliente, Contato
from app.models.orcamento import EtapaOrcamento, Orcamento, OrcamentoItem
from app.models.veiculo import Veiculo
from app.schemas.orcamento import OrcamentoCreate, OrcamentoEtapaUpdate, OrcamentoItemIn, OrcamentoUpdate


def _next_orcamento_numero(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.scalar(select(func.count(Orcamento.id))) or 0
    return f"ORC-{year}-{count + 1:04d}"


def _build_itens_e_total(
    itens_in: list[OrcamentoItemIn], desconto_total: Decimal
) -> tuple[list[OrcamentoItem], Decimal]:
    itens: list[OrcamentoItem] = []
    soma = Decimal("0.00")
    for item in itens_in:
        subtotal = (item.quantidade * item.valor_unitario).quantize(Decimal("0.01"))
        soma += subtotal
        itens.append(
            OrcamentoItem(
                tipo=item.tipo,
                descricao=item.descricao.strip(),
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                subtotal=subtotal,
            )
        )
    total = max(Decimal("0.00"), soma - desconto_total).quantize(Decimal("0.01"))
    return itens, total


def create_orcamento(db: Session, payload: OrcamentoCreate, usuario_id: int) -> Orcamento:
    cliente = db.get(Cliente, payload.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    contato = db.get(Contato, payload.contato_id)
    if not contato or contato.cliente_id != payload.cliente_id:
        raise HTTPException(status_code=400, detail="Contato inválido para este cliente")
    veiculo = db.get(Veiculo, payload.veiculo_id)
    if not veiculo or veiculo.cliente_id != payload.cliente_id:
        raise HTTPException(status_code=400, detail="Veículo inválido para este cliente")

    itens, total = _build_itens_e_total(payload.itens, payload.desconto_total)
    orc = Orcamento(
        numero=_next_orcamento_numero(db),
        cliente_id=payload.cliente_id,
        contato_id=payload.contato_id,
        veiculo_id=payload.veiculo_id,
        usuario_id=usuario_id,
        etapa=EtapaOrcamento.RASCUNHO,
        validade_dias=payload.validade_dias,
        desconto_total=payload.desconto_total,
        valor_total=total,
        observacoes=payload.observacoes,
        itens=itens,
    )
    db.add(orc)
    db.commit()
    return get_orcamento_or_404(db, orc.id)


def list_orcamentos(
    db: Session,
    etapa: EtapaOrcamento | None = None,
    cliente_id: int | None = None,
    veiculo_id: int | None = None,
) -> list[Orcamento]:
    stmt = (
        select(Orcamento)
        .options(
            selectinload(Orcamento.itens),
            selectinload(Orcamento.cliente),
            selectinload(Orcamento.veiculo),
            selectinload(Orcamento.contato),
        )
        .order_by(Orcamento.id.desc())
    )
    if etapa:
        stmt = stmt.where(Orcamento.etapa == etapa)
    if cliente_id:
        stmt = stmt.where(Orcamento.cliente_id == cliente_id)
    if veiculo_id:
        stmt = stmt.where(Orcamento.veiculo_id == veiculo_id)
    return list(db.scalars(stmt).all())


def get_orcamento_or_404(db: Session, orcamento_id: int) -> Orcamento:
    stmt = (
        select(Orcamento)
        .options(
            selectinload(Orcamento.itens),
            selectinload(Orcamento.cliente),
            selectinload(Orcamento.veiculo),
            selectinload(Orcamento.contato),
        )
        .where(Orcamento.id == orcamento_id)
    )
    orc = db.scalar(stmt)
    if not orc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado")
    return orc


def update_orcamento(db: Session, orcamento_id: int, payload: OrcamentoUpdate) -> Orcamento:
    orc = get_orcamento_or_404(db, orcamento_id)
    if orc.etapa == EtapaOrcamento.APROVADO:
        raise HTTPException(status_code=400, detail="Orçamento aprovado não pode ser editado")

    if payload.validade_dias is not None:
        orc.validade_dias = payload.validade_dias
    if payload.observacoes is not None:
        orc.observacoes = payload.observacoes
    if payload.desconto_total is not None:
        orc.desconto_total = payload.desconto_total

    if payload.itens is not None:
        orc.itens.clear()
        itens, total = _build_itens_e_total(payload.itens, orc.desconto_total)
        orc.itens.extend(itens)
        orc.valor_total = total
    elif payload.desconto_total is not None:
        soma = sum((i.subtotal for i in orc.itens), Decimal("0.00"))
        orc.valor_total = max(Decimal("0.00"), soma - orc.desconto_total).quantize(Decimal("0.01"))

    db.commit()
    return get_orcamento_or_404(db, orc.id)


def update_etapa_orcamento(
    db: Session, orcamento_id: int, payload: OrcamentoEtapaUpdate
) -> Orcamento:
    orc = get_orcamento_or_404(db, orcamento_id)
    if payload.etapa == EtapaOrcamento.RECUSADO:
        if not payload.motivo_recusa or not payload.motivo_recusa.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="motivo_recusa é obrigatório quando o orçamento é recusado",
            )
        orc.motivo_recusa = payload.motivo_recusa.strip()
    if payload.po_aprovacao is not None:
        orc.po_aprovacao = payload.po_aprovacao.strip() or None
    orc.etapa = payload.etapa
    db.commit()
    return get_orcamento_or_404(db, orc.id)
