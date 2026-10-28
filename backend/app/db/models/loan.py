import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedUUIDModel
from app.db.models.shg import InterestType


class LoanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISBURSED = "DISBURSED"
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    CLOSED = "CLOSED"
    WRITTEN_OFF = "WRITTEN_OFF"


class InstallmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class PaymentMode(str, enum.Enum):
    CASH = "CASH"
    UPI = "UPI"
    BANK = "BANK"


class Loan(TimestampedUUIDModel):
    __tablename__ = "loans"

    shg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shgs.id", ondelete="RESTRICT"), nullable=False, index=True)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False, index=True)
    loan_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    purpose: Mapped[str] = mapped_column(String(255), nullable=False)
    principal: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(6, 3), nullable=False)
    interest_type: Mapped[InterestType] = mapped_column(Enum(InterestType, name="loan_interest_type_enum"), nullable=False)
    tenure_months: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_fee: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[LoanStatus] = mapped_column(Enum(LoanStatus, name="loan_status_enum"), default=LoanStatus.DRAFT, nullable=False, index=True)

    applied_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    disbursed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # Optimistic locking

    shg: Mapped["SHG"] = relationship("SHG", back_populates="loans")
    member: Mapped["Member"] = relationship("Member", back_populates="loans")
    schedule: Mapped[list["LoanSchedule"]] = relationship("LoanSchedule", back_populates="loan", cascade="all, delete-orphan", order_by="LoanSchedule.installment_no")
    history: Mapped[list["LoanStatusHistory"]] = relationship("LoanStatusHistory", back_populates="loan", cascade="all, delete-orphan")
    repayments: Mapped[list["Repayment"]] = relationship("Repayment", back_populates="loan", cascade="all, delete-orphan")


class LoanSchedule(TimestampedUUIDModel):
    __tablename__ = "loan_schedule"

    loan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False, index=True)
    installment_no: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    principal_due: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    interest_due: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_due: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    principal_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    interest_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    penalty_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[InstallmentStatus] = mapped_column(Enum(InstallmentStatus, name="installment_status_enum"), default=InstallmentStatus.PENDING, nullable=False)

    loan: Mapped["Loan"] = relationship("Loan", back_populates="schedule")


class LoanStatusHistory(TimestampedUUIDModel):
    __tablename__ = "loan_status_history"

    loan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status: Mapped[LoanStatus | None] = mapped_column(Enum(LoanStatus, name="loan_status_hist_from_enum"), nullable=True)
    to_status: Mapped[LoanStatus] = mapped_column(Enum(LoanStatus, name="loan_status_hist_to_enum"), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    loan: Mapped["Loan"] = relationship("Loan", back_populates="history")


class Repayment(TimestampedUUIDModel):
    __tablename__ = "repayments"

    loan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="RESTRICT"), nullable=False, index=True)
    meeting_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="SET NULL"), nullable=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    principal_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    interest_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    penalty_component: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    paid_on: Mapped[date] = mapped_column(Date, nullable=False)
    mode: Mapped[PaymentMode] = mapped_column(Enum(PaymentMode, name="payment_mode_enum"), default=PaymentMode.CASH, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("journal_entries.id", ondelete="RESTRICT"), nullable=True)

    loan: Mapped["Loan"] = relationship("Loan", back_populates="repayments")
    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="repayments")
    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry")

