# PROMPT: Build "SHG Credit Manager"

> Paste this file into Antigravity as the task prompt. Keep `spec.md` in the project root; it is the source of truth for the data model, rules, API, and design system.

---

## Role

You are a senior full-stack engineer and product designer. Build a production-quality **Micro-lending / Self-Help Group (SHG) Credit Management System**.

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL
- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS (with custom design tokens)

Read `spec.md` fully before writing any code. If this prompt and `spec.md` disagree, `spec.md` wins. If something is ambiguous, make the most reasonable decision, write it down in `docs/decisions.md`, and keep moving.

## What this product is

SHGs are small community groups (10 to 20 members) that pool monthly savings and lend to each other, and sometimes receive bank-linkage loans. Most track everything in paper notebooks. This product replaces the notebook with a trustworthy digital ledger used by group leaders (often on a phone, in the field), members, NGO/bank admins, and auditors.

**Priorities, in order:** financial accuracy, security, authorization, auditability. These are hard requirements, not polish.

## Non-negotiable engineering rules

1. **Money is `Decimal` in Python and `NUMERIC(14,2)` in Postgres. Never `float`.** Rounding is `ROUND_HALF_UP` to 2 dp, defined in one module and used everywhere.
2. **The ledger is append-only and double-entry.** Every money movement creates balanced journal entries. No `UPDATE` or `DELETE` on ledger rows; corrections are reversing entries.
3. **Every money-moving endpoint is idempotent** (`Idempotency-Key` header) and runs in a single DB transaction with row-level locking.
4. **Authorization is enforced on the server**, at role level and at object level (a leader can only touch their own group; a member can only read their own data). The UI hiding a button is not security.
5. **Loan state transitions live in exactly one place** (a state machine module) and invalid transitions raise a typed error.
6. **Maker-checker:** the person who creates a loan application cannot approve it.
7. **No secrets in code.** Config from environment only. PII is masked in API responses and logs. Never store full Aadhaar numbers.
8. **Strict typing:** mypy strict on the backend, TypeScript strict with no `any` on the frontend.

## Design direction (equally important as the code)

The UI must feel like a thoughtfully designed fintech/ledger product made by a human design team, **not** like an AI-generated template. Warm, calm, trustworthy, editorial: an accounting notebook meets a modern banking app.

**Do not do any of the following:**

- Purple/indigo/blue gradients, gradient text, glassmorphism, glowing orbs, neon
- A centered-headline-plus-two-buttons hero section
- Emoji as icons or decoration
- Rows of identical `rounded-2xl` soft-shadow cards in a uniform grid repeated down the page
- Inter/Roboto/system-default typography
- Filler copy ("Welcome back, John!", "Unlock your financial potential"), lorem ipsum, or fake round-number charts (10k, 20k, 30k)
- Bouncy or pulsing animation, or an icon next to every heading
- Raw Tailwind palette classes in components (use semantic tokens only)

**Do this instead:**

- Define design tokens first (see `spec.md`, section 12), then build a `/styleguide` page, then build screens
- A serif for page titles and key figures, a clean humanist sans for UI, `tabular-nums` on every money column
- Hairline 1px borders and surface tints for hierarchy; almost no shadows
- Varied layout rhythm: ledgers, ruled tables, split panes, timelines
- Indian digit grouping for currency (₹1,25,000.00), right-aligned in tables
- Status shown by color **and** text, never color alone
- Real loading, error, and empty states with plain, helpful copy
- WCAG AA contrast, visible focus rings, full keyboard navigation, usable at 360px width

## Execution plan

Work in phases. After each phase: run the code, run the tests, fix failures, and post a short summary of what was built, what was decided, and what is next.

| Phase | Scope | Gate |
|---|---|---|
| 1 | Monorepo scaffold, docker-compose (Postgres), config, DB models, Alembic migration, base error handling, Mermaid ER diagram | **Stop for approval** |
| 2 | Auth (JWT + refresh rotation), RBAC, object-level authorization, audit logging, tests | |
| 3 | Ledger engine, savings, loans, state machine, schedule calculator, idempotency, concurrency tests | **Stop for approval** |
| 4 | Reports, CSV/PDF exports, seed script with realistic data | |
| 5 | Design tokens, fonts, component library, `/styleguide` page | **Stop for approval** |
| 6 | Feature screens wired to the real API through a typed client generated from OpenAPI | |
| 7 | Polish: accessibility audit, responsive checks, empty/error states, performance, README, screenshots | |

Do not start building feature screens (Phase 6) until the style guide (Phase 5) is approved.

## Seed data

Realistic, not placeholder: 2 SHGs, about 12 members each, 6 months of savings, and a mix of active, closed, and overdue loans. Use realistic Indian names and village/ward names. Never "John Doe".

## Definition of done

- `docker compose up` plus two documented commands starts everything
- All tests pass, and the ledger balance invariant holds on the seed data
- No console errors or warnings in the browser
- `ruff`, `mypy`, `eslint`, and `prettier` are configured and clean
- README covers setup, env vars, running tests, and the demo logins for each role
- Finally, review the finished UI against the "do not" list above, list any deviations, and fix them

## Output style

Be concise in your progress updates. Do not paste large code blocks into chat; write them to files. When you make a judgment call, record it in `docs/decisions.md` in one or two lines.
