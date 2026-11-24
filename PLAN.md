# ReleasePad, new ISOCODELABS-specific portfolio project
24 November 2026. Original, AI-assisted synthetic software-release readiness workspace. Not affiliated with ISOCODELABS and not an employer assessment. New domain, schema and workflow, not a renamed vendor app or old ticket demo.

Role mapping: end-to-end TypeScript/React feature work, Python/FastAPI backend, SQL data, tests and deployment readiness. Focus: versioned immutable release snapshots with editable checklists and release comparison. User can create release candidate, track tests/docs/rollback criteria, compare candidates, save immutable readiness snapshot, and inspect why readiness changed. No real deployments triggered and no secrets/real code uploaded.

Data: workspaces, release candidates, checks, immutable snapshots. Release snapshots capture the complete checklist at that moment, remain stable after later edits, and show a digest. Frontend will use route-backed candidate selection and URL filters, optimistic-version updates, keyboard-accessible forms and small-screen stacked check rows. Backend must enforce isolation, versions, input sizes and snapshot gating.

Current: implementation in progress. NOT DEPLOYED. Fresh live verification remains required before any application. ISOCODE earliest start date remains unanswered; six-month willingness confirmed separately. No binding availability promise in this code or application prep.

Tests planned: isolation, create/read durability, validation, version conflicts, risk-free status transitions, snapshot immutability/digest, readiness gating, compare, cleanup and browser workflow. Must verify actual pixels before ready.
