from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.ordem_servico import StatusOS
from app.models.usuario import Usuario
from app.schemas.ordem_servico import (
    OSItemIn,
    OrdemServicoCreate,
    OrdemServicoOut,
    OrdemServicoStatusUpdate,
)
from app.services import os_service, pdf_service

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])


def to_os_out(os_obj) -> OrdemServicoOut:
    return OrdemServicoOut(
        id=os_obj.id,
        numero=os_obj.numero,
        orcamento_id=os_obj.orcamento_id,
        cliente_id=os_obj.cliente_id,
        veiculo_id=os_obj.veiculo_id,
        usuario_abertura_id=os_obj.usuario_abertura_id,
        status=os_obj.status,
        km_entrada=os_obj.km_entrada,
        confirmar_km_menor=os_obj.confirmar_km_menor,
        motorista_entrada_id=os_obj.motorista_entrada_id,
        avarias_entrada=os_obj.avarias_entrada,
        motorista_saida_id=os_obj.motorista_saida_id,
        observacoes_saida=os_obj.observacoes_saida,
        valor_total=os_obj.valor_total,
        data_entrada=os_obj.data_entrada,
        data_entrega=os_obj.data_entrega,
        cliente_nome=os_obj.cliente.nome_fantasia if os_obj.cliente else None,
        veiculo_placa=os_obj.veiculo.placa if os_obj.veiculo else None,
        motorista_entrada_nome=os_obj.motorista_entrada.nome if os_obj.motorista_entrada else None,
        motorista_saida_nome=os_obj.motorista_saida.nome if os_obj.motorista_saida else None,
        itens=os_obj.itens,
        historico=os_obj.historico,
    )


@router.get("", response_model=list[OrdemServicoOut])
def listar_os(
    status_filter: StatusOS | None = Query(default=None, alias="status"),
    cliente_id: int | None = Query(default=None),
    veiculo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return [to_os_out(o) for o in os_service.list_os(db, status_filter, cliente_id, veiculo_id)]


@router.post("", response_model=OrdemServicoOut, status_code=status.HTTP_201_CREATED)
def abrir_os_direta(
    payload: OrdemServicoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return to_os_out(os_service.create_os_direta(db, payload, current_user.id))


@router.get("/{os_id}", response_model=OrdemServicoOut)
def detalhar_os(
    os_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return to_os_out(os_service.get_os_or_404(db, os_id))


@router.patch("/{os_id}/status", response_model=OrdemServicoOut)
def atualizar_status_os(
    os_id: int,
    payload: OrdemServicoStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    from app.services.crm_service import registrar_preventiva_ao_entregar_os

    return to_os_out(
        os_service.update_status_os(
            db,
            os_id,
            payload,
            current_user.id,
            on_entregue_callback=registrar_preventiva_ao_entregar_os,
        )
    )


@router.post("/{os_id}/itens", response_model=OrdemServicoOut)
def adicionar_item_os(
    os_id: int,
    item: OSItemIn,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return to_os_out(os_service.add_item_os(db, os_id, item))


@router.get("/{os_id}/pdf")
def baixar_pdf_os(
    os_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    os_obj = os_service.get_os_or_404(db, os_id)
    pdf_bytes = pdf_service.gerar_pdf_os(os_obj)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{os_obj.numero}.pdf"'},
    )
