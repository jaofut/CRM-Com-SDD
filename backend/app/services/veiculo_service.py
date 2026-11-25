import re
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.veiculo import Veiculo
from app.schemas.veiculo import (
    BuscaClienteItem,
    BuscaGlobalResponse,
    BuscaVeiculoItem,
    VeiculoCreate,
    VeiculoUpdate,
)
from app.services.cliente_service import get_cliente_or_404, normalize_cnpj


def normalize_placa(placa: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", placa).upper()


def create_veiculo(db: Session, cliente_id: int, payload: VeiculoCreate) -> Veiculo:
    get_cliente_or_404(db, cliente_id)
    placa_norm = normalize_placa(payload.placa)
    existing = db.scalar(select(Veiculo).where(Veiculo.placa == placa_norm))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Placa já cadastrada",
                "veiculo_id": existing.id,
                "cliente_id": existing.cliente_id,
            },
        )
    veiculo = Veiculo(
        cliente_id=cliente_id,
        placa=placa_norm,
        tipo=payload.tipo,
        marca_modelo=payload.marca_modelo.strip(),
        ano=payload.ano,
        chassi=payload.chassi,
        km_atual=payload.km_atual,
    )
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    return veiculo


def update_veiculo(db: Session, veiculo_id: int, payload: VeiculoUpdate) -> Veiculo:
    veiculo = db.get(Veiculo, veiculo_id)
    if not veiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado")

    data = payload.model_dump(exclude_unset=True)
    if "cliente_id" in data and data["cliente_id"] is not None:
        get_cliente_or_404(db, data["cliente_id"])
    if "placa" in data and data["placa"] is not None:
        placa_norm = normalize_placa(data["placa"])
        existing = db.scalar(
            select(Veiculo).where(Veiculo.placa == placa_norm, Veiculo.id != veiculo_id)
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Placa já cadastrada em outro veículo", "veiculo_id": existing.id},
            )
        data["placa"] = placa_norm

    for key, val in data.items():
        setattr(veiculo, key, val)
    db.commit()
    db.refresh(veiculo)
    return veiculo


def busca_global(db: Session, q: str) -> BuscaGlobalResponse:
    term = q.strip()
    if not term:
        return BuscaGlobalResponse(clientes=[], veiculos=[])

    like_term = f"%{term}%"
    cnpj_like = f"%{normalize_cnpj(term)}%"
    placa_like = f"%{normalize_placa(term)}%"

    clientes = db.scalars(
        select(Cliente)
        .where(
            or_(
                Cliente.razao_social.ilike(like_term),
                Cliente.nome_fantasia.ilike(like_term),
                Cliente.cnpj.ilike(cnpj_like),
            )
        )
        .order_by(Cliente.nome_fantasia.asc())
        .limit(10)
    ).all()

    veiculos = db.execute(
        select(Veiculo, Cliente.nome_fantasia)
        .join(Cliente, Veiculo.cliente_id == Cliente.id)
        .where(
            or_(
                Veiculo.placa.ilike(placa_like),
                Veiculo.marca_modelo.ilike(like_term),
            )
        )
        .order_by(Veiculo.placa.asc())
        .limit(10)
    ).all()

    return BuscaGlobalResponse(
        clientes=[
            BuscaClienteItem(
                id=c.id,
                nome_fantasia=c.nome_fantasia,
                razao_social=c.razao_social,
                cnpj=c.cnpj,
            )
            for c in clientes
        ],
        veiculos=[
            BuscaVeiculoItem(
                id=v.id,
                placa=v.placa,
                marca_modelo=v.marca_modelo,
                cliente_id=v.cliente_id,
                cliente_nome=cliente_nome,
            )
            for v, cliente_nome in veiculos
        ],
    )
