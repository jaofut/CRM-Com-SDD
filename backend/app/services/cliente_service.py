import re
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.cliente import Cliente, Contato, Motorista
from app.schemas.cliente import (
    ClienteCreate,
    ClienteUpdate,
    ContatoCreate,
    ContatoUpdate,
    MotoristaCreate,
    MotoristaUpdate,
)


def normalize_cnpj(cnpj: str) -> str:
    digits = re.sub(r"\D", "", cnpj)
    return digits or cnpj.strip()


def list_clientes(db: Session, ativo: bool | None = None, q: str | None = None) -> list[Cliente]:
    stmt = select(Cliente)
    if ativo is not None:
        stmt = stmt.where(Cliente.ativo == ativo)
    if q and q.strip():
        term = f"%{q.strip()}%"
        norm_q = f"%{normalize_cnpj(q)}%"
        stmt = stmt.where(
            or_(
                Cliente.razao_social.ilike(term),
                Cliente.nome_fantasia.ilike(term),
                Cliente.cnpj.ilike(term),
                Cliente.cnpj.ilike(norm_q),
            )
        )
    stmt = stmt.order_by(Cliente.nome_fantasia.asc())
    return list(db.scalars(stmt).all())


def create_cliente(db: Session, payload: ClienteCreate) -> Cliente:
    cnpj_norm = normalize_cnpj(payload.cnpj)
    existing = db.scalar(select(Cliente).where(Cliente.cnpj == cnpj_norm))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "CNPJ já cadastrado",
                "cliente_id": existing.id,
                "nome_fantasia": existing.nome_fantasia,
            },
        )
    cliente = Cliente(
        razao_social=payload.razao_social.strip(),
        nome_fantasia=payload.nome_fantasia.strip(),
        cnpj=cnpj_norm,
        inscricao_estadual=payload.inscricao_estadual,
        endereco=payload.endereco,
        condicoes_comerciais=payload.condicoes_comerciais,
        observacoes=payload.observacoes,
        ativo=payload.ativo,
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def get_cliente_or_404(db: Session, cliente_id: int) -> Cliente:
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente


def update_cliente(db: Session, cliente_id: int, payload: ClienteUpdate) -> Cliente:
    cliente = get_cliente_or_404(db, cliente_id)
    data = payload.model_dump(exclude_unset=True)
    if "cnpj" in data and data["cnpj"] is not None:
        cnpj_norm = normalize_cnpj(data["cnpj"])
        existing = db.scalar(
            select(Cliente).where(Cliente.cnpj == cnpj_norm, Cliente.id != cliente_id)
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "CNPJ já cadastrado em outro cliente", "cliente_id": existing.id},
            )
        data["cnpj"] = cnpj_norm

    for key, val in data.items():
        setattr(cliente, key, val)
    db.commit()
    db.refresh(cliente)
    return cliente


def add_contato(db: Session, cliente_id: int, payload: ContatoCreate) -> Contato:
    get_cliente_or_404(db, cliente_id)
    if payload.principal:
        for c in db.scalars(select(Contato).where(Contato.cliente_id == cliente_id)).all():
            c.principal = False
    contato = Contato(cliente_id=cliente_id, **payload.model_dump())
    db.add(contato)
    db.commit()
    db.refresh(contato)
    return contato


def update_contato(db: Session, contato_id: int, payload: ContatoUpdate) -> Contato:
    contato = db.get(Contato, contato_id)
    if not contato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contato não encontrado")
    data = payload.model_dump(exclude_unset=True)
    if data.get("principal"):
        for c in db.scalars(
            select(Contato).where(Contato.cliente_id == contato.cliente_id, Contato.id != contato_id)
        ).all():
            c.principal = False
    for key, val in data.items():
        setattr(contato, key, val)
    db.commit()
    db.refresh(contato)
    return contato


def delete_contato(db: Session, contato_id: int) -> None:
    contato = db.get(Contato, contato_id)
    if not contato:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contato não encontrado")
    db.delete(contato)
    db.commit()


def add_motorista(db: Session, cliente_id: int, payload: MotoristaCreate) -> Motorista:
    get_cliente_or_404(db, cliente_id)
    motorista = Motorista(cliente_id=cliente_id, **payload.model_dump())
    db.add(motorista)
    db.commit()
    db.refresh(motorista)
    return motorista


def update_motorista(db: Session, motorista_id: int, payload: MotoristaUpdate) -> Motorista:
    motorista = db.get(Motorista, motorista_id)
    if not motorista:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Motorista não encontrado")
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(motorista, key, val)
    db.commit()
    db.refresh(motorista)
    return motorista
