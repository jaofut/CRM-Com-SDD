from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    razao_social: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    nome_fantasia: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, index=True, nullable=False)
    inscricao_estadual: Mapped[str | None] = mapped_column(String(30), nullable=True)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    condicoes_comerciais: Mapped[str | None] = mapped_column(Text, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    contatos = relationship("Contato", back_populates="cliente", cascade="all, delete-orphan")
    motoristas = relationship("Motorista", back_populates="cliente", cascade="all, delete-orphan")
    veiculos = relationship("Veiculo", back_populates="cliente")


class Contato(Base):
    __tablename__ = "contatos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    cargo: Mapped[str] = mapped_column(String(80), nullable=False)
    telefone_whatsapp: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    cliente = relationship("Cliente", back_populates="contatos")


class Motorista(Base):
    __tablename__ = "motoristas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    documento: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    cliente = relationship("Cliente", back_populates="motoristas")
