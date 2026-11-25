from datetime import date, datetime, timezone
import enum
from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TipoInteracao(str, enum.Enum):
    LIGACAO = "LIGACAO"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    PRESENCIAL = "PRESENCIAL"
    SISTEMA = "SISTEMA"


class TipoLembrete(str, enum.Enum):
    FOLLOW_UP = "FOLLOW_UP"
    PREVENTIVA = "PREVENTIVA"


class StatusLembrete(str, enum.Enum):
    PENDENTE = "PENDENTE"
    CONCLUIDO = "CONCLUIDO"
    REAGENDADO = "REAGENDADO"


class Interacao(Base):
    __tablename__ = "interacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    tipo: Mapped[TipoInteracao] = mapped_column(
        SAEnum(TipoInteracao, native_enum=False), nullable=False
    )
    resumo: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    usuario = relationship("Usuario")


class Lembrete(Base):
    __tablename__ = "lembretes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    veiculo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("veiculos.id", ondelete="SET NULL"), nullable=True
    )
    os_origem_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ordens_servico.id", ondelete="SET NULL"), nullable=True
    )
    usuario_responsavel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    tipo: Mapped[TipoLembrete] = mapped_column(
        SAEnum(TipoLembrete, native_enum=False), nullable=False
    )
    titulo: Mapped[str] = mapped_column(String(160), nullable=False)
    data_prevista: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    km_previsto: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[StatusLembrete] = mapped_column(
        SAEnum(StatusLembrete, native_enum=False), nullable=False, default=StatusLembrete.PENDENTE
    )
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    cliente = relationship("Cliente")
    veiculo = relationship("Veiculo")
