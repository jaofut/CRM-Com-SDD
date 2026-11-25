from datetime import date, datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cliente import Cliente
from app.models.crm import Interacao, Lembrete, StatusLembrete, TipoInteracao, TipoLembrete
from app.schemas.crm import InteracaoCreate, LembreteCreate, LembreteUpdate


def list_interacoes(db: Session, cliente_id: int) -> list[Interacao]:
    if not db.get(Cliente, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    stmt = (
        select(Interacao)
        .options(selectinload(Interacao.usuario))
        .where(Interacao.cliente_id == cliente_id)
        .order_by(Interacao.created_at.desc(), Interacao.id.desc())
    )
    return list(db.scalars(stmt).all())


def create_interacao(
    db: Session, cliente_id: int, usuario_id: int, payload: InteracaoCreate
) -> Interacao:
    if not db.get(Cliente, cliente_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    interacao = Interacao(
        cliente_id=cliente_id,
        usuario_id=usuario_id,
        tipo=payload.tipo,
        resumo=payload.resumo.strip(),
    )
    db.add(interacao)
    db.commit()
    db.refresh(interacao)
    return db.scalar(
        select(Interacao).options(selectinload(Interacao.usuario)).where(Interacao.id == interacao.id)
    )


def registrar_preventiva_ao_entregar_os(db: Session, os_obj, payload, usuario_id: int) -> None:
    dias = payload.preventiva_dias or 90
    data_prev = datetime.now(timezone.utc).date() + timedelta(days=dias)
    lembrete = Lembrete(
        cliente_id=os_obj.cliente_id,
        veiculo_id=os_obj.veiculo_id,
        os_origem_id=os_obj.id,
        usuario_responsavel_id=usuario_id,
        tipo=TipoLembrete.PREVENTIVA,
        titulo=f"Revisão preventiva pós-{os_obj.numero}",
        data_prevista=data_prev,
        km_previsto=payload.km_previsto_proxima_revisao,
        status=StatusLembrete.PENDENTE,
    )
    db.add(lembrete)
    db.add(
        Interacao(
            cliente_id=os_obj.cliente_id,
            usuario_id=usuario_id,
            tipo=TipoInteracao.SISTEMA,
            resumo=f"OS {os_obj.numero} entregue. Preventiva agendada para {data_prev.isoformat()}.",
        )
    )


def list_lembretes(
    db: Session,
    status_filter: StatusLembrete | None = None,
    ate_data: date | None = None,
    tipo: TipoLembrete | None = None,
) -> list[Lembrete]:
    stmt = (
        select(Lembrete)
        .options(selectinload(Lembrete.cliente), selectinload(Lembrete.veiculo))
        .order_by(Lembrete.data_prevista.asc(), Lembrete.id.asc())
    )
    if status_filter:
        stmt = stmt.where(Lembrete.status == status_filter)
    if ate_data:
        stmt = stmt.where(Lembrete.data_prevista <= ate_data)
    if tipo:
        stmt = stmt.where(Lembrete.tipo == tipo)
    return list(db.scalars(stmt).all())


def create_lembrete(db: Session, payload: LembreteCreate, usuario_id: int) -> Lembrete:
    if not db.get(Cliente, payload.cliente_id):
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    lemb = Lembrete(
        cliente_id=payload.cliente_id,
        veiculo_id=payload.veiculo_id,
        os_origem_id=payload.os_origem_id,
        usuario_responsavel_id=usuario_id,
        tipo=payload.tipo,
        titulo=payload.titulo.strip(),
        data_prevista=payload.data_prevista,
        km_previsto=payload.km_previsto,
        observacoes=payload.observacoes,
        status=StatusLembrete.PENDENTE,
    )
    db.add(lemb)
    db.commit()
    return db.scalar(
        select(Lembrete)
        .options(selectinload(Lembrete.cliente), selectinload(Lembrete.veiculo))
        .where(Lembrete.id == lemb.id)
    )


def update_lembrete(db: Session, lembrete_id: int, payload: LembreteUpdate) -> Lembrete:
    lemb = db.get(Lembrete, lembrete_id)
    if not lemb:
        raise HTTPException(status_code=404, detail="Lembrete não encontrado")
    lemb.status = payload.status
    if payload.data_prevista is not None:
        lemb.data_prevista = payload.data_prevista
    if payload.observacoes is not None:
        lemb.observacoes = payload.observacoes
    db.commit()
    return db.scalar(
        select(Lembrete)
        .options(selectinload(Lembrete.cliente), selectinload(Lembrete.veiculo))
        .where(Lembrete.id == lemb.id)
    )
