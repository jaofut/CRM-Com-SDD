from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.schemas.cliente import (
    ClienteCreate,
    ClienteDetalheOut,
    ClienteResumoOut,
    ClienteUpdate,
    ContatoCreate,
    ContatoOut,
    ContatoUpdate,
    MotoristaCreate,
    MotoristaOut,
    MotoristaUpdate,
)
from app.services import cliente_service

router = APIRouter(tags=["Clientes, Contatos e Motoristas"])


@router.get("/clientes", response_model=list[ClienteResumoOut])
def listar_clientes(
    ativo: bool | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.list_clientes(db, ativo=ativo, q=q)


@router.post("/clientes", response_model=ClienteResumoOut, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.create_cliente(db, payload)


@router.get("/clientes/{cliente_id}", response_model=ClienteDetalheOut)
def detalhar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.get_cliente_or_404(db, cliente_id)


@router.patch("/clientes/{cliente_id}", response_model=ClienteResumoOut)
def atualizar_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.update_cliente(db, cliente_id, payload)


@router.post("/clientes/{cliente_id}/contatos", response_model=ContatoOut, status_code=status.HTTP_201_CREATED)
def adicionar_contato(
    cliente_id: int,
    payload: ContatoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.add_contato(db, cliente_id, payload)


@router.patch("/contatos/{contato_id}", response_model=ContatoOut)
def atualizar_contato(
    contato_id: int,
    payload: ContatoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.update_contato(db, contato_id, payload)


@router.delete("/contatos/{contato_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_contato(
    contato_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    cliente_service.delete_contato(db, contato_id)


@router.post("/clientes/{cliente_id}/motoristas", response_model=MotoristaOut, status_code=status.HTTP_201_CREATED)
def adicionar_motorista(
    cliente_id: int,
    payload: MotoristaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.add_motorista(db, cliente_id, payload)


@router.patch("/motoristas/{motorista_id}", response_model=MotoristaOut)
def atualizar_motorista(
    motorista_id: int,
    payload: MotoristaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return cliente_service.update_motorista(db, motorista_id, payload)
