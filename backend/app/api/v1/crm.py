from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.crm import StatusLembrete, TipoLembrete
from app.models.usuario import Usuario
from app.schemas.crm import (
    InteracaoCreate,
    InteracaoOut,
    LembreteCreate,
    LembreteOut,
    LembreteUpdate,
)
from app.services import crm_service

router = APIRouter(tags=["CRM - Timeline e Lembretes"])


def _to_interacao_out(i) -> InteracaoOut:
    return InteracaoOut(
        id=i.id,
        cliente_id=i.cliente_id,
        usuario_id=i.usuario_id,
        usuario_nome=i.usuario.nome if i.usuario else None,
        tipo=i.tipo,
        resumo=i.resumo,
        created_at=i.created_at,
    )


def _to_lembrete_out(l) -> LembreteOut:
    return LembreteOut(
        id=l.id,
        cliente_id=l.cliente_id,
        veiculo_id=l.veiculo_id,
        os_origem_id=l.os_origem_id,
        usuario_responsavel_id=l.usuario_responsavel_id,
        tipo=l.tipo,
        titulo=l.titulo,
        data_prevista=l.data_prevista,
        km_previsto=l.km_previsto,
        status=l.status,
        observacoes=l.observacoes,
        created_at=l.created_at,
        cliente_nome=l.cliente.nome_fantasia if l.cliente else None,
        veiculo_placa=l.veiculo.placa if l.veiculo else None,
    )


@router.get("/clientes/{cliente_id}/interacoes", response_model=list[InteracaoOut])
def listar_interacoes(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return [_to_interacao_out(i) for i in crm_service.list_interacoes(db, cliente_id)]


@router.post("/clientes/{cliente_id}/interacoes", response_model=InteracaoOut, status_code=status.HTTP_201_CREATED)
def registrar_interacao(
    cliente_id: int,
    payload: InteracaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return _to_interacao_out(crm_service.create_interacao(db, cliente_id, current_user.id, payload))


@router.get("/lembretes", response_model=list[LembreteOut])
def listar_lembretes(
    status_filter: StatusLembrete | None = Query(default=None, alias="status"),
    ate_data: date | None = Query(default=None),
    tipo: TipoLembrete | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return [_to_lembrete_out(l) for l in crm_service.list_lembretes(db, status_filter, ate_data, tipo)]


@router.post("/lembretes", response_model=LembreteOut, status_code=status.HTTP_201_CREATED)
def criar_lembrete(
    payload: LembreteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return _to_lembrete_out(crm_service.create_lembrete(db, payload, current_user.id))


@router.patch("/lembretes/{lembrete_id}", response_model=LembreteOut)
def atualizar_lembrete(
    lembrete_id: int,
    payload: LembreteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return _to_lembrete_out(crm_service.update_lembrete(db, lembrete_id, payload))
