from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.usuario import Usuario
from app.schemas.veiculo import BuscaGlobalResponse, VeiculoCreate, VeiculoOut, VeiculoUpdate
from app.services import veiculo_service

router = APIRouter(tags=["Veículos e Busca"])


@router.get("/busca", response_model=BuscaGlobalResponse)
def busca_global(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return veiculo_service.busca_global(db, q)


@router.post("/clientes/{cliente_id}/veiculos", response_model=VeiculoOut, status_code=status.HTTP_201_CREATED)
def adicionar_veiculo(
    cliente_id: int,
    payload: VeiculoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return veiculo_service.create_veiculo(db, cliente_id, payload)


@router.patch("/veiculos/{veiculo_id}", response_model=VeiculoOut)
def atualizar_veiculo(
    veiculo_id: int,
    payload: VeiculoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return veiculo_service.update_veiculo(db, veiculo_id, payload)
