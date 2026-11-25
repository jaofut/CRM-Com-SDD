from datetime import datetime, timezone
from decimal import Decimal
import enum
from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EtapaOrcamento(str, enum.Enum):
    RASCUNHO = "RASCUNHO"
    ENVIADO = "ENVIADO"
    EM_NEGOCIACAO = "EM_NEGOCIACAO"
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"


class TipoItem(str, enum.Enum):
    PECA = "PECA"
    SERVICO = "SERVICO"


class Orcamento(Base):
    __tablename__ = "orcamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    contato_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("contatos.id", ondelete="RESTRICT"), nullable=False
    )
    veiculo_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("veiculos.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    etapa: Mapped[EtapaOrcamento] = mapped_column(
        SAEnum(EtapaOrcamento, native_enum=False), nullable=False, default=EtapaOrcamento.RASCUNHO
    )
    validade_dias: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    desconto_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    po_aprovacao: Mapped[str | None] = mapped_column(String(60), nullable=True)
    motivo_recusa: Mapped[str | None] = mapped_column(String(200), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    itens = relationship("OrcamentoItem", back_populates="orcamento", cascade="all, delete-orphan")
    cliente = relationship("Cliente")
    contato = relationship("Contato")
    veiculo = relationship("Veiculo")


class OrcamentoItem(Base):
    __tablename__ = "orcamento_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    orcamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orcamentos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tipo: Mapped[TipoItem] = mapped_column(SAEnum(TipoItem, native_enum=False), nullable=False)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    valor_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    orcamento = relationship("Orcamento", back_populates="itens")
