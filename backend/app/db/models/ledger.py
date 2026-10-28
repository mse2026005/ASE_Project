import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedUUIDModel


class AccountType(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class JournalSourceType(str, enum.Enum):
    SAVINGS = "SAVINGS"
    DISBURSAL = "DISBURSAL"
    REPAYMENT = "REPAYMENT"
    FINE = "FINE"
    FEE = "FEE"
    REVERSAL = "REVERSAL"
    ADJUSTMENT = "ADJUSTMENT"


class Account(TimestampedUUIDModel):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("shg_id", "code", "member_id", name="uq_shg_account_code_member"),
    )

    shg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shgs.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 1000, 1010, 1100, 2000, etc.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType, name="account_type_enum"), nullable=False)
    member_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=True, index=True)

    shg: Mapped["SHG"] = relationship("SHG", back_populates="accounts")
    member: Mapped["Member"] = relationship("Member")
    lines: Mapped[list["JournalLine"]] = relationship("JournalLine", back_populates="account")


class JournalEntry(TimestampedUUIDModel):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("shg_id", "idempotency_key", name="uq_shg_idempotency_key"),
    )

    shg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shgs.id", ondelete="RESTRICT"), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[JournalSourceType] = mapped_column(Enum(JournalSourceType, name="journal_source_type_enum"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reverses_entry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="RESTRICT"), unique=True, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    posted_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    shg: Mapped["SHG"] = relationship("SHG")
    lines: Mapped[list["JournalLine"]] = relationship("JournalLine", back_populates="entry", cascade="all, delete-orphan")
    reversed_entry: Mapped["JournalEntry | None"] = relationship("JournalEntry", remote_side="JournalEntry.id")


class JournalLine(TimestampedUUIDModel):
    __tablename__ = "journal_lines"
    __table_args__ = (
        CheckConstraint("(debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0)", name="check_debit_xor_credit"),
        CheckConstraint("debit >= 0 AND credit >= 0", name="check_positive_amounts"),
    )

    entry_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="RESTRICT"), nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)

    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["Account"] = relationship("Account", back_populates="lines")

