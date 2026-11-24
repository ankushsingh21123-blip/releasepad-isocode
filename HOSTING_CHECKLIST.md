# Hosting readiness, not a deployment

No hosted ReleasePad service exists yet. The image definition is prepared for a platform with a real persistent filesystem. A Docker build/run has not been tested here. Do not claim a verified container until it has actually built and run.

## Allowed shape to verify before committing

- A dedicated new service and dedicated empty data volume, no existing customer data or project repurposed.
- Actual provider plan verified free, no card/automatic paid overage, no terms or obligations outside owner approval.
- The volume must be mounted at `/data`; set `RELEASEPAD_DB=/data/releasepad.sqlite`.
- Single process/replica with SQLite. `run_server.py` respects provider `PORT` (1–65535), and the container health check uses the same variable. Do not scale across machines or put SQLite on ephemeral serverless `/tmp`.
- Public HTTPS frontend and API are same origin. Do not loosen cross-origin write checks.
- Actual free-tier storage, inactivity, restart, retention and deletion rules must be checked on the selected provider. No promise of uptime or permanence.

## Required live acceptance

1. Health returns actual storage type. No environment values, credentials or detailed errors exposed.
2. Create workspace and candidate with synthetic data; complete required checks, save snapshot and verify digest/readback.
3. Edit a check after the snapshot; show saved snapshot unchanged and current readiness changed.
4. Reload and make a later independent request. Restart/redeploy then load the same workspace/candidate/snapshot, proving the data volume survived.
5. Try another workspace token, invalid fields, stale version, critical waiver, evidence-free pass and cross-origin writes. All rejected appropriately.
6. Verify compare, empty/error/offline/expired views and actual desktop/phone pixels at the live URL.
7. Document observed URL/provider/plan, test time and caveats. Update resume from those facts, not planned infrastructure.

The current Cloudflare account's mailbox-verification gate is separate. This container recipe neither bypasses that step nor makes FastAPI run unchanged in a Worker. ReleasePad needs an appropriate verified runtime; the Certa project's Worker adapter is not this application's backend.
