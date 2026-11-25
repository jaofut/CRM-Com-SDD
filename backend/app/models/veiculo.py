from datetime import datetime, timezone
import enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoVeiculo(str, enum.Enum):
    CAVALO_MECANICO = "CAVALO_MECANICO"
    CARRETA = "CARRETA"
    TRUCK = "TRUCK"
    TOCO = "TOCO"
    ONIBUS = "ONIBUS"
    UTILITARIO_PESADO = "UTILITARIO_PESADO"
    OUTRO = "OUTRO"


class Veiculo(Base):
    __tablename__ = "veiculos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    placa: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    tipo: Mapped[TipoVeiculo] = mapped_column(
        SAEnum(TipoVeiculo, native_enum=False), nullable=False
    )
    marca_modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chassi: Mapped[str | None] = mapped_column(String(30), nullable=True)
    km_atual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    cliente = relationship("Cliente", back_populates="veiculos")
