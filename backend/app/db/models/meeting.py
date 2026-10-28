import enum
import uuid
from datetime import date
from decimal import Decimal
from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimestampedUUIDModel


class MeetingStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    HELD = "HELD"
    CANCELLED = "CANCELLED"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    EXCUSED = "EXCUSED"


class DueStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    OVERDUE = "OVERDUE"


class Meeting(TimestampedUUIDModel):
    __tablename__ = "meetings"

    shg_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shgs.id", ondelete="RESTRICT"), nullable=False, index=True)
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[MeetingStatus] = mapped_column(Enum(MeetingStatus, name="meeting_status_enum"), default=MeetingStatus.SCHEDULED, nullable=False)
    agenda: Mapped[str | None] = mapped_column(String(500), nullable=True)
    minutes: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    shg: Mapped["SHG"] = relationship("SHG", back_populates="meetings")
    attendance: Mapped[list["Attendance"]] = relationship("Attendance", back_populates="meeting", cascade="all, delete-orphan")
    repayments: Mapped[list["Repayment"]] = relationship("Repayment", back_populates="meeting")


class Attendance(TimestampedUUIDModel):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("meeting_id", "member_id", name="uq_meeting_member_attendance"),
    )

    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus, name="attendance_status_enum"), default=AttendanceStatus.PRESENT, nullable=False)

    meeting: Mapped["Meeting"] = relationship("Meeting", back_populates="attendance")
    member: Mapped["Member"] = relationship("Member", back_populates="attendance")


class SavingsDue(TimestampedUUIDModel):
    __tablename__ = "savings_dues"
    __table_args__ = (
        UniqueConstraint("member_id", "period", name="uq_member_period_savings_due"),
    )

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id", ondelete="RESTRICT"), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(7), nullable=False, index=True)  # YYYY-MM
    amount_due: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    status: Mapped[DueStatus] = mapped_column(Enum(DueStatus, name="due_status_enum"), default=DueStatus.PENDING, nullable=False)

    member: Mapped["Member"] = relationship("Member", back_populates="savings_dues")

