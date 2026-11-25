from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.cliente import Cliente, Motorista
from app.models.orcamento import EtapaOrcamento, Orcamento
from app.models.ordem_servico import (
    OrdemServico,
    OrdemServicoHistorico,
    OrdemServicoItem,
    StatusOS,
)
from app.models.veiculo import Veiculo
from app.schemas.ordem_servico import (
    ConverterOrcamentoOSRequest,
    OSItemIn,
    OrdemServicoCreate,
    OrdemServicoStatusUpdate,
)


def _next_os_numero(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count = db.scalar(select(func.count(OrdemServico.id))) or 0
    return f"OS-{year}-{count + 1:04d}"


def _validar_km(veiculo: Veiculo, km_entrada: int, confirmar_km_menor: bool) -> None:
    if km_entrada < veiculo.km_atual and not confirmar_km_menor:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"KM de entrada ({km_entrada}) é menor que a última KM registrada ({veiculo.km_atual}). Confirme para prosseguir.",
        )
    if km_entrada > veiculo.km_atual:
        veiculo.km_atual = km_entrada


def _validar_motorista(db: Session, cliente_id: int, motorista_id: int | None) -> None:
    if motorista_id is None:
        return
    mot = db.get(Motorista, motorista_id)
    if not mot or mot.cliente_id != cliente_id:
        raise HTTPException(status_code=400, detail="Motorista inválido para este cliente")


def converter_orcamento_em_os(
    db: Session,
    orcamento_id: int,
    payload: ConverterOrcamentoOSRequest,
    usuario_id: int,
) -> OrdemServico:
    orc = db.scalar(
        select(Orcamento).options(selectinload(Orcamento.itens)).where(Orcamento.id == orcamento_id)
    )
    if not orc:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")
    if orc.etapa != EtapaOrcamento.APROVADO:
        raise HTTPException(status_code=400, detail="Apenas orçamentos APROVADOS podem ser convertidos em OS")

    existing_os = db.scalar(select(OrdemServico).where(OrdemServico.orcamento_id == orc.id))
    if existing_os:
        raise HTTPException(status_code=409, detail=f"Orçamento já convertido na OS {existing_os.numero}")

    veiculo = db.get(Veiculo, orc.veiculo_id)
    _validar_km(veiculo, payload.km_entrada, payload.confirmar_km_menor)
    _validar_motorista(db, orc.cliente_id, payload.motorista_entrada_id)

    itens_os = [
        OrdemServicoItem(
            tipo=item.tipo,
            descricao=item.descricao,
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            subtotal=item.subtotal,
        )
        for item in orc.itens
    ]

    os_obj = OrdemServico(
        numero=_next_os_numero(db),
        orcamento_id=orc.id,
        cliente_id=orc.cliente_id,
        veiculo_id=orc.veiculo_id,
        usuario_abertura_id=usuario_id,
        status=StatusOS.AGUARDANDO_PECA,
        km_entrada=payload.km_entrada,
        confirmar_km_menor=payload.confirmar_km_menor,
        motorista_entrada_id=payload.motorista_entrada_id,
        avarias_entrada=payload.avarias_entrada,
        valor_total=orc.valor_total,
        itens=itens_os,
        historico=[
            OrdemServicoHistorico(
                status_anterior=None,
                status_novo=StatusOS.AGUARDANDO_PECA.value,
                usuario_id=usuario_id,
                observacao=f"OS gerada a partir do orçamento {orc.numero}",
            )
        ],
    )
    db.add(os_obj)
    db.commit()
    return get_os_or_404(db, os_obj.id)


def create_os_direta(db: Session, payload: OrdemServicoCreate, usuario_id: int) -> OrdemServico:
    cliente = db.get(Cliente, payload.cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    veiculo = db.get(Veiculo, payload.veiculo_id)
    if not veiculo or veiculo.cliente_id != payload.cliente_id:
        raise HTTPException(status_code=400, detail="Veículo inválido para este cliente")

    _validar_km(veiculo, payload.km_entrada, payload.confirmar_km_menor)
    _validar_motorista(db, payload.cliente_id, payload.motorista_entrada_id)

    itens_os: list[OrdemServicoItem] = []
    total = Decimal("0.00")
    for item in payload.itens:
        sub = (item.quantidade * item.valor_unitario).quantize(Decimal("0.01"))
        total += sub
        itens_os.append(
            OrdemServicoItem(
                tipo=item.tipo,
                descricao=item.descricao.strip(),
                quantidade=item.quantidade,
                valor_unitario=item.valor_unitario,
                subtotal=sub,
            )
        )

    os_obj = OrdemServico(
        numero=_next_os_numero(db),
        cliente_id=payload.cliente_id,
        veiculo_id=payload.veiculo_id,
        usuario_abertura_id=usuario_id,
        status=StatusOS.AGUARDANDO_PECA,
        km_entrada=payload.km_entrada,
        confirmar_km_menor=payload.confirmar_km_menor,
        motorista_entrada_id=payload.motorista_entrada_id,
        avarias_entrada=payload.avarias_entrada,
        valor_total=total,
        itens=itens_os,
        historico=[
            OrdemServicoHistorico(
                status_anterior=None,
                status_novo=StatusOS.AGUARDANDO_PECA.value,
                usuario_id=usuario_id,
                observacao="Abertura direta de OS",
            )
        ],
    )
    db.add(os_obj)
    db.commit()
    return get_os_or_404(db, os_obj.id)


def list_os(
    db: Session,
    status_filter: StatusOS | None = None,
    cliente_id: int | None = None,
    veiculo_id: int | None = None,
) -> list[OrdemServico]:
    stmt = (
        select(OrdemServico)
        .options(
            selectinload(OrdemServico.itens),
            selectinload(OrdemServico.historico),
            selectinload(OrdemServico.cliente),
            selectinload(OrdemServico.veiculo),
            selectinload(OrdemServico.motorista_entrada),
            selectinload(OrdemServico.motorista_saida),
        )
        .order_by(OrdemServico.id.desc())
    )
    if status_filter:
        stmt = stmt.where(OrdemServico.status == status_filter)
    if cliente_id:
        stmt = stmt.where(OrdemServico.cliente_id == cliente_id)
    if veiculo_id:
        stmt = stmt.where(OrdemServico.veiculo_id == veiculo_id)
    return list(db.scalars(stmt).all())


def get_os_or_404(db: Session, os_id: int) -> OrdemServico:
    stmt = (
        select(OrdemServico)
        .options(
            selectinload(OrdemServico.itens),
            selectinload(OrdemServico.historico),
            selectinload(OrdemServico.cliente),
            selectinload(OrdemServico.veiculo),
            selectinload(OrdemServico.motorista_entrada),
            selectinload(OrdemServico.motorista_saida),
        )
        .where(OrdemServico.id == os_id)
    )
    os_obj = db.scalar(stmt)
    if not os_obj:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
    return os_obj


def update_status_os(
    db: Session,
    os_id: int,
    payload: OrdemServicoStatusUpdate,
    usuario_id: int,
    on_entregue_callback=None,
) -> OrdemServico:
    os_obj = get_os_or_404(db, os_id)
    if payload.status == StatusOS.ENTREGUE:
        if not payload.motorista_saida_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="motorista_saida_id é obrigatório para concluir a entrega da OS",
            )
        _validar_motorista(db, os_obj.cliente_id, payload.motorista_saida_id)
        os_obj.motorista_saida_id = payload.motorista_saida_id
        os_obj.observacoes_saida = payload.observacoes_saida
        os_obj.data_entrega = datetime.now(timezone.utc)

    status_ant = os_obj.status.value
    os_obj.status = payload.status
    os_obj.historico.append(
        OrdemServicoHistorico(
            status_anterior=status_ant,
            status_novo=payload.status.value,
            usuario_id=usuario_id,
            observacao=payload.observacao,
        )
    )

    if payload.status == StatusOS.ENTREGUE and on_entregue_callback is not None:
        on_entregue_callback(db, os_obj, payload, usuario_id)

    db.commit()
    return get_os_or_404(db, os_obj.id)


def add_item_os(db: Session, os_id: int, item: OSItemIn) -> OrdemServico:
    os_obj = get_os_or_404(db, os_id)
    if os_obj.status == StatusOS.ENTREGUE:
        raise HTTPException(status_code=400, detail="OS já entregue não aceita novos itens")
    sub = (item.quantidade * item.valor_unitario).quantize(Decimal("0.01"))
    os_obj.itens.append(
        OrdemServicoItem(
            tipo=item.tipo,
            descricao=item.descricao.strip(),
            quantidade=item.quantidade,
            valor_unitario=item.valor_unitario,
            subtotal=sub,
        )
    )
    os_obj.valor_total = (os_obj.valor_total + sub).quantize(Decimal("0.01"))
    db.commit()
    return get_os_or_404(db, os_obj.id)
