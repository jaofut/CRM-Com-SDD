from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.orcamento import EtapaOrcamento
from app.models.usuario import Usuario
from app.schemas.orcamento import (
    OrcamentoCreate,
    OrcamentoEtapaUpdate,
    OrcamentoOut,
    OrcamentoUpdate,
)
from app.schemas.ordem_servico import ConverterOrcamentoOSRequest, OrdemServicoOut
from app.services import orcamento_service, os_service, pdf_service
from app.api.v1.ordens_servico import to_os_out

router = APIRouter(prefix="/orcamentos", tags=["Orçamentos"])


def _to_out(orc) -> OrcamentoOut:
    return OrcamentoOut(
        id=orc.id,
        numero=orc.numero,
        cliente_id=orc.cliente_id,
        contato_id=orc.contato_id,
        veiculo_id=orc.veiculo_id,
        usuario_id=orc.usuario_id,
        etapa=orc.etapa,
        validade_dias=orc.validade_dias,
        desconto_total=orc.desconto_total,
        valor_total=orc.valor_total,
        po_aprovacao=orc.po_aprovacao,
        motivo_recusa=orc.motivo_recusa,
        observacoes=orc.observacoes,
        created_at=orc.created_at,
        updated_at=orc.updated_at,
        cliente_nome=orc.cliente.nome_fantasia if orc.cliente else None,
        veiculo_placa=orc.veiculo.placa if orc.veiculo else None,
        contato_nome=orc.contato.nome if orc.contato else None,
        contato_whatsapp=orc.contato.telefone_whatsapp if orc.contato else None,
        itens=orc.itens,
    )


@router.get("", response_model=list[OrcamentoOut])
def listar_orcamentos(
    etapa: EtapaOrcamento | None = Query(default=None),
    cliente_id: int | None = Query(default=None),
    veiculo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return [_to_out(o) for o in orcamento_service.list_orcamentos(db, etapa, cliente_id, veiculo_id)]


@router.post("", response_model=OrcamentoOut, status_code=status.HTTP_201_CREATED)
def criar_orcamento(
    payload: OrcamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orc = orcamento_service.create_orcamento(db, payload, current_user.id)
    return _to_out(orc)


@router.get("/{orcamento_id}", response_model=OrcamentoOut)
def detalhar_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return _to_out(orcamento_service.get_orcamento_or_404(db, orcamento_id))


@router.put("/{orcamento_id}", response_model=OrcamentoOut)
def atualizar_orcamento(
    orcamento_id: int,
    payload: OrcamentoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return _to_out(orcamento_service.update_orcamento(db, orcamento_id, payload))


@router.patch("/{orcamento_id}/etapa", response_model=OrcamentoOut)
def mover_etapa_orcamento(
    orcamento_id: int,
    payload: OrcamentoEtapaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return _to_out(orcamento_service.update_etapa_orcamento(db, orcamento_id, payload))


@router.get("/{orcamento_id}/pdf")
def baixar_pdf_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    orc = orcamento_service.get_orcamento_or_404(db, orcamento_id)
    pdf_bytes = pdf_service.gerar_pdf_orcamento(orc)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{orc.numero}.pdf"'},
    )


@router.post("/{orcamento_id}/converter-os", response_model=OrdemServicoOut, status_code=status.HTTP_201_CREATED)
def converter_em_os(
    orcamento_id: int,
    payload: ConverterOrcamentoOSRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    os_obj = os_service.converter_orcamento_em_os(db, orcamento_id, payload, current_user.id)
    return to_os_out(os_obj)
