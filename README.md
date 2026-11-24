# ReleasePad

Original AI-assisted synthetic release-readiness workspace prepared for an end-to-end software engineering portfolio. Not affiliated with ISOCODELABS, not an employer assessment, and not proof of unaided authorship.

## Status

Local implementation and tests pass. **Not deployed.** No remote persistence or production runtime claim. Do not use a serverless `/tmp` SQLite file as durable storage. Hosting and a fresh hosted browser verification remain required before using this project in an internship application.

## What is new

A release-candidate domain and SQL schema, not a renamed vendor or ticket demo. Each candidate has tests, rollback and documentation checks. Critical checks cannot be waived; passing checks need a synthetic evidence reference. Once ready, a snapshot records the complete checklist, version and a SHA-256 digest. Later edits do not rewrite it. Two candidates can be compared by check category/title and status.

React/TypeScript frontend, Python/FastAPI API, SQLite database. Isolated random-bearer-token workspaces, optimistic version checks under database write transactions, prepared SQL, body limits, same-origin writes and seven-day cleanup. Demo capacities: 100 workspaces, 20 candidates per workspace, 40 checks and 20 snapshots per candidate. These are not production identity, security or compliance guarantees. Use synthetic information only.

## Run

Python 3.11+ and Node 22+ are recommended.

```sh
python -m pip install -r requirements.txt
npm ci
npm run build
# Point to a persistent disk if hosting with SQLite.
RELEASEPAD_DB=./releasepad.sqlite python -m uvicorn api.main:app --host 127.0.0.1 --port 4182
```

Open http://127.0.0.1:4182. No actual release or deployment is triggered by any action.

## Verify

```sh
python -m unittest test_api -v
npm test
npx playwright install chromium
npx playwright test
```

15 FastAPI/SQLite tests, 6 actual React component tests and 3 browser scenarios pass locally. Browser checks cover evidence completion, readiness snapshot, digest readback, reload persistence, candidate comparison, expired-session and offline recovery, and screenshots/no overflow at 1280, 390 and 320 CSS pixels. Desktop/mobile actual pixels inspected. Build passes. The local API tests are not a substitute for hosted persistence/runtime tests.

## Limits

Anonymous demo tokens are stored in browser localStorage; anyone possessing a token can use that workspace. No real authentication, production audit signing, code scanning, CI connection or release automation is claimed. Snapshot digests detect changed serialized data, not who created it. Workspace cleanup runs on new workspace creation. Database backups and production concurrency testing are not implemented.
