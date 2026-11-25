from datetime import datetime, timezone
from decimal import Decimal
import enum
from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.orcamento import TipoItem


class StatusOS(str, enum.Enum):
    AGUARDANDO_PECA = "AGUARDANDO_PECA"
    EM_EXECUCAO = "EM_EXECUCAO"
    EM_TESTE = "EM_TESTE"
    PRONTA = "PRONTA"
    ENTREGUE = "ENTREGUE"


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    orcamento_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("orcamentos.id", ondelete="SET NULL"), nullable=True
    )
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    veiculo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("veiculos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    usuario_abertura_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[StatusOS] = mapped_column(
        SAEnum(StatusOS, native_enum=False), nullable=False, default=StatusOS.AGUARDANDO_PECA
    )
    km_entrada: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmar_km_menor: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    motorista_entrada_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("motoristas.id", ondelete="SET NULL"), nullable=True
    )
    avarias_entrada: Mapped[str | None] = mapped_column(Text, nullable=True)
    motorista_saida_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("motoristas.id", ondelete="SET NULL"), nullable=True
    )
    observacoes_saida: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    data_entrada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    data_entrega: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    itens = relationship("OrdemServicoItem", back_populates="ordem_servico", cascade="all, delete-orphan")
    historico = relationship(
        "OrdemServicoHistorico", back_populates="ordem_servico", cascade="all, delete-orphan"
    )
    cliente = relationship("Cliente")
    veiculo = relationship("Veiculo")
    motorista_entrada = relationship("Motorista", foreign_keys=[motorista_entrada_id])
    motorista_saida = relationship("Motorista", foreign_keys=[motorista_saida_id])


class OrdemServicoItem(Base):
    __tablename__ = "ordem_servico_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    os_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ordens_servico.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[TipoItem] = mapped_column(SAEnum(TipoItem, native_enum=False), nullable=False)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    ordem_servico = relationship("OrdemServico", back_populates="itens")


class OrdemServicoHistorico(Base):
    __tablename__ = "ordem_servico_historico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    os_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ordens_servico.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status_anterior: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status_novo: Mapped[str] = mapped_column(String(30), nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    ordem_servico = relationship("OrdemServico", back_populates="historico")
