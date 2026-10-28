# Architecture Decisions & Assumptions

This document records the architectural and design decisions made for the SHG Credit Management System as required by `spec.md` and `prompt.md`.

## 1. Prepayment Behavior
- **Decision:** When an overpayment occurs beyond the current due installment, the default behavior is **reduce tenure** (apply excess to the principal of subsequent installments from oldest to newest).
- **Rationale:** Aligns with standard SHG practices and minimizes total interest burden on rural micro-borrowers.

## 2. Interest Recognition
- **Decision:** Interest is recognized **per installment** upon schedule generation and due dates, and posted to the ledger upon repayment collection.
- **Rationale:** Consistent with group meeting schedules where collections and interest accrual happen periodically (monthly/meeting-wise) rather than continuous daily accrual. Daily accrual is reserved strictly for overdue penalties.

## 3. PDF Generation Library
- **Decision:** Use **ReportLab** for PDF generation.
- **Rationale:** ReportLab is a pure-Python library with zero native system dependencies (unlike WeasyPrint which requires cairo, pango, and gdk-pixbuf libraries that often cause installation failure on Windows/minimal Docker images).

## 4. Daily Overdue & Penalty Scheduler
- **Decision:** Implement both a standalone management CLI command (`python -m app.jobs.daily_accrual`) and an optional integrated **APScheduler** background service enabled via config flag (`ENABLE_IN_PROCESS_SCHEDULER=true`).
- **Rationale:** Supports both containerized cron jobs (12-factor production deployment) and single-process local development/testing without requiring an external cron daemon.

## 5. Ledger Balance Invariant & Immutability
- **Decision:** Ledger journal entries and journal lines are strictly append-only. No `UPDATE` or `DELETE` endpoints exist. Reversals create explicit offsetting mirror journal entries referencing `reverses_entry_id`.
- **Rationale:** Enforces complete double-entry integrity, immutable accounting trails, and regulatory compliance.

## 6. Authentication & Refresh Token Rotation
- **Decision:** Access token stored in memory/Authorization header (15m expiry). Refresh token stored in `httpOnly`, `Secure`, `SameSite=Strict` cookie (7d expiry) with automatic token rotation, family-id tracking, and breach/reuse detection (revoking the entire token family if a compromised token is reused).
- **Rationale:** Meets stringent banking security standards against XSS and token exfiltration.

