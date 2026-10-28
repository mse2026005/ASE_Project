from typing import Any
from fastapi import HTTPException, status


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required", details: dict[str, Any] | None = None):
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Permission denied", details: dict[str, Any] | None = None):
        super().__init__(
            code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ConflictError(AppError):
    def __init__(self, code: str = "CONFLICT", message: str = "Resource conflict", details: dict[str, Any] | None = None):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class LoanInvalidTransitionError(AppError):
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code="LOAN_INVALID_TRANSITION",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class MakerCheckerViolationError(AppError):
    def __init__(self, message: str = "The applicant or creator cannot approve this loan application.", details: dict[str, Any] | None = None):
        super().__init__(
            code="MAKER_CHECKER_VIOLATION",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class LedgerImbalanceError(AppError):
    def __init__(self, message: str = "Debit and credit totals must balance exactly.", details: dict[str, Any] | None = None):
        super().__init__(
            code="LEDGER_IMBALANCE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class IdempotencyConflictError(AppError):
    def __init__(self, message: str = "Idempotency key was previously used with a different request payload.", details: dict[str, Any] | None = None):
        super().__init__(
            code="IDEMPOTENCY_CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )

