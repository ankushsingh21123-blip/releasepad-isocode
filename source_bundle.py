#!/usr/bin/env python3
"""Inspectable original ReleasePad source, not deployed. No network/execute during extraction."""
import pathlib,argparse
FILES = {'.dockerignore': 'node_modules\n'
                  'static\n'
                  '__pycache__\n'
                  '*.sqlite*\n'
                  '.env*\n'
                  '.git\n'
                  'evidence\n'
                  'test-results\n'
                  '*.zip\n'
                  'source_bundle.py\n',
 '.gitignore': 'node_modules/\nstatic/\n.env*\n*.sqlite*\n__pycache__/\n.pytest_cache/\ntest-results/\n',
 'Dockerfile': 'FROM node:22-alpine AS webbuild\n'
               'WORKDIR /build\n'
               'COPY package.json package-lock.json ./\n'
               'RUN npm ci --ignore-scripts\n'
               'COPY vite.config.ts ./\n'
               'COPY web ./web\n'
               'RUN npm run build\n'
               '\n'
               'FROM python:3.12-slim\n'
               'WORKDIR /app\n'
               'COPY requirements.txt ./\n'
               'RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 '
               'releasepad && mkdir /data && chown releasepad:releasepad /data\n'
               'COPY api ./api\n'
               'COPY run_server.py ./run_server.py\n'
               'COPY --from=webbuild /build/static ./static\n'
               'ENV RELEASEPAD_DB=/data/releasepad.sqlite\n'
               'ENV PORT=4182\n'
               'USER releasepad\n'
               'EXPOSE 4182\n'
               'HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import '
               'urllib.request;urllib.request.urlopen(\'http://127.0.0.1:\'+__import__(\'os\').environ.get(\'PORT\',\'4182\')+\'/api/health\',timeout=3)"\n'
               'CMD ["python", "run_server.py"]\n',
 'HOSTING_CHECKLIST.md': '# Hosting readiness, not a deployment\n'
                         '\n'
                         'No hosted ReleasePad service exists yet. The image definition is prepared for a '
                         'platform with a real persistent filesystem. A Docker build/run has not been tested '
                         'here. Do not claim a verified container until it has actually built and run.\n'
                         '\n'
                         '## Allowed shape to verify before committing\n'
                         '\n'
                         '- A dedicated new service and dedicated empty data volume, no existing customer '
                         'data or project repurposed.\n'
                         '- Actual provider plan verified free, no card/automatic paid overage, no terms or '
                         'obligations outside owner approval.\n'
                         '- The volume must be mounted at `/data`; set '
                         '`RELEASEPAD_DB=/data/releasepad.sqlite`.\n'
                         '- Single process/replica with SQLite. `run_server.py` respects provider `PORT` '
                         '(1–65535), and the container health check uses the same variable. Do not scale '
                         'across machines or put SQLite on ephemeral serverless `/tmp`.\n'
                         '- Public HTTPS frontend and API are same origin. Do not loosen cross-origin write '
                         'checks.\n'
                         '- Actual free-tier storage, inactivity, restart, retention and deletion rules must '
                         'be checked on the selected provider. No promise of uptime or permanence.\n'
                         '\n'
                         '## Required live acceptance\n'
                         '\n'
                         '1. Health returns actual storage type. No environment values, credentials or '
                         'detailed errors exposed.\n'
                         '2. Create workspace and candidate with synthetic data; complete required checks, '
                         'save snapshot and verify digest/readback.\n'
                         '3. Edit a check after the snapshot; show saved snapshot unchanged and current '
                         'readiness changed.\n'
                         '4. Reload and make a later independent request. Restart/redeploy then load the '
                         'same workspace/candidate/snapshot, proving the data volume survived.\n'
                         '5. Try another workspace token, invalid fields, stale version, critical waiver, '
                         'evidence-free pass and cross-origin writes. All rejected appropriately.\n'
                         '6. Verify compare, empty/error/offline/expired views and actual desktop/phone '
                         'pixels at the live URL.\n'
                         '7. Document observed URL/provider/plan, test time and caveats. Update resume from '
                         'those facts, not planned infrastructure.\n'
                         '\n'
                         "The current Cloudflare account's mailbox-verification gate is separate. This "
                         'container recipe neither bypasses that step nor makes FastAPI run unchanged in a '
                         "Worker. ReleasePad needs an appropriate verified runtime; the Certa project's "
                         "Worker adapter is not this application's backend.\n",
 'LICENSE': 'MIT License\n'
            '\n'
            'Copyright (c) 2026 Ankush Singh\n'
            '\n'
            'Permission is hereby granted, free of charge, to any person obtaining a copy of this software '
            'and associated documentation files (the "Software"), to deal in the Software without '
            'restriction, including without limitation the rights to use, copy, modify, merge, publish, '
            'distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the '
            'Software is furnished to do so, subject to the following conditions:\n'
            'The above copyright notice and this permission notice shall be included in all copies or '
            'substantial portions of the Software.\n'
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING '
            'BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND '
            'NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, '
            'DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, '
            'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n',
 'PLAN.md': '# ReleasePad, new ISOCODELABS-specific portfolio project\n'
            '24 November 2026. Original, AI-assisted synthetic software-release readiness workspace. Not '
            'affiliated with ISOCODELABS and not an employer assessment. New domain, schema and workflow, '
            'not a renamed vendor app or old ticket demo.\n'
            '\n'
            'Role mapping: end-to-end TypeScript/React feature work, Python/FastAPI backend, SQL data, tests '
            'and deployment readiness. Focus: versioned immutable release snapshots with editable checklists '
            'and release comparison. User can create release candidate, track tests/docs/rollback criteria, '
            'compare candidates, save immutable readiness snapshot, and inspect why readiness changed. No '
            'real deployments triggered and no secrets/real code uploaded.\n'
            '\n'
            'Data: workspaces, release candidates, checks, immutable snapshots. Release snapshots capture '
            'the complete checklist at that moment, remain stable after later edits, and show a digest. '
            'Frontend will use route-backed candidate selection and URL filters, optimistic-version updates, '
            'keyboard-accessible forms and small-screen stacked check rows. Backend must enforce isolation, '
            'versions, input sizes and snapshot gating.\n'
            '\n'
            'Current: implementation in progress. NOT DEPLOYED. Fresh live verification remains required '
            'before any application. ISOCODE earliest start date remains unanswered; six-month willingness '
            'confirmed separately. No binding availability promise in this code or application prep.\n'
            '\n'
            'Tests planned: isolation, create/read durability, validation, version conflicts, risk-free '
            'status transitions, snapshot immutability/digest, readiness gating, compare, cleanup and '
            'browser workflow. Must verify actual pixels before ready.\n',
 'README.md': '# ReleasePad\n'
              '\n'
              'Original AI-assisted synthetic release-readiness workspace prepared for an end-to-end '
              'software engineering portfolio. Not affiliated with ISOCODELABS, not an employer assessment, '
              'and not proof of unaided authorship.\n'
              '\n'
              '## Status\n'
              '\n'
              'Local implementation and tests pass. **Not deployed.** No remote persistence or production '
              'runtime claim. Do not use a serverless `/tmp` SQLite file as durable storage. Hosting and a '
              'fresh hosted browser verification remain required before using this project in an internship '
              'application.\n'
              '\n'
              '## What is new\n'
              '\n'
              'A release-candidate domain and SQL schema, not a renamed vendor or ticket demo. Each '
              'candidate has tests, rollback and documentation checks. Critical checks cannot be waived; '
              'passing checks need a synthetic evidence reference. Once ready, a snapshot records the '
              'complete checklist, version and a SHA-256 digest. Later edits do not rewrite it. Two '
              'candidates can be compared by check category/title and status.\n'
              '\n'
              'React/TypeScript frontend, Python/FastAPI API, SQLite database. Isolated random-bearer-token '
              'workspaces, optimistic version checks under database write transactions, prepared SQL, body '
              'limits, same-origin writes and seven-day cleanup. Demo capacities: 100 workspaces, 20 '
              'candidates per workspace, 40 checks and 20 snapshots per candidate. These are not production '
              'identity, security or compliance guarantees. Use synthetic information only.\n'
              '\n'
              '## Run\n'
              '\n'
              'Python 3.11+ and Node 22+ are recommended.\n'
              '\n'
              '```sh\n'
              'python -m pip install -r requirements.txt\n'
              'npm ci\n'
              'npm run build\n'
              '# Point to a persistent disk if hosting with SQLite.\n'
              'RELEASEPAD_DB=./releasepad.sqlite python -m uvicorn api.main:app --host 127.0.0.1 --port '
              '4182\n'
              '```\n'
              '\n'
              'Open http://127.0.0.1:4182. No actual release or deployment is triggered by any action.\n'
              '\n'
              '## Verify\n'
              '\n'
              '```sh\n'
              'python -m unittest test_api -v\n'
              'npm test\n'
              'npx playwright install chromium\n'
              'npx playwright test\n'
              '```\n'
              '\n'
              '15 FastAPI/SQLite tests, 6 actual React component tests and 3 browser scenarios pass locally. '
              'Browser checks cover evidence completion, readiness snapshot, digest readback, reload '
              'persistence, candidate comparison, expired-session and offline recovery, and screenshots/no '
              'overflow at 1280, 390 and 320 CSS pixels. Desktop/mobile actual pixels inspected. Build '
              'passes. The local API tests are not a substitute for hosted persistence/runtime tests.\n'
              '\n'
              '## Limits\n'
              '\n'
              'Anonymous demo tokens are stored in browser localStorage; anyone possessing a token can use '
              'that workspace. No real authentication, production audit signing, code scanning, CI '
              'connection or release automation is claimed. Snapshot digests detect changed serialized data, '
              'not who created it. Workspace cleanup runs on new workspace creation. Database backups and '
              'production concurrency testing are not implemented.\n'
              '\n'
              '## Container preparation\n'
              '\n'
              '`Dockerfile` and `HOSTING_CHECKLIST.md` describe a single-instance persistent-volume '
              'deployment shape. The single-process `run_server.py` entry point validates and respects '
              '`PORT`; its local stop/start persistence test passes. Container build/runtime has not been '
              'tested here and no hosting provider has been selected. Never describe an ephemeral `/tmp` '
              'file as durable.\n',
 'api/main.py': '"""Original AI-assisted synthetic release-readiness demo, no actual deployments."""\n'
                'import os,sqlite3,secrets,datetime,json,hashlib,re\n'
                'from contextlib import contextmanager\n'
                'from typing import Literal\n'
                'from urllib.parse import urlparse\n'
                'from fastapi import FastAPI,Header,HTTPException,Depends,Request\n'
                'from fastapi.responses import FileResponse,JSONResponse\n'
                'from pydantic import BaseModel,Field,ConfigDict\n'
                'from pathlib import Path\n'
                "app=FastAPI(title='ReleasePad synthetic portfolio')\n"
                "DB=os.environ.get('RELEASEPAD_DB','/tmp/releasepad.sqlite')\n"
                'def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()\n'
                '@contextmanager\n'
                'def db():\n'
                " c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute('PRAGMA "
                "foreign_keys=ON');c.execute('PRAGMA journal_mode=WAL')\n"
                ' try:yield c;c.commit()\n'
                ' except:c.rollback();raise\n'
                ' finally:c.close()\n'
                'def init():\n'
                " with db() as c:c.executescript('''CREATE TABLE IF NOT EXISTS workspaces(id TEXT PRIMARY "
                'KEY,created TEXT NOT NULL);\n'
                'CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,workspace TEXT NOT NULL '
                'REFERENCES workspaces(id),title TEXT NOT NULL,version INTEGER NOT NULL DEFAULT 1,created '
                'TEXT NOT NULL);\n'
                'CREATE TABLE IF NOT EXISTS checks(id TEXT PRIMARY KEY,candidate TEXT NOT NULL REFERENCES '
                'candidates(id),title TEXT NOT NULL,category TEXT NOT NULL,status TEXT NOT NULL,reference '
                "TEXT NOT NULL DEFAULT '',critical INTEGER NOT NULL,created TEXT NOT NULL);\n"
                'CREATE TABLE IF NOT EXISTS snapshots(id TEXT PRIMARY KEY,candidate TEXT NOT NULL REFERENCES '
                'candidates(id),payload TEXT NOT NULL,digest TEXT NOT NULL,created TEXT NOT NULL);\n'
                "CREATE INDEX IF NOT EXISTS candidate_workspace ON candidates(workspace);''')\n"
                'init()\n'
                "@app.middleware('http')\n"
                'async def safety(request:Request,call_next):\n'
                " if request.method in ['POST','PATCH','PUT','DELETE'] and "
                "request.url.path.startswith('/api/'):\n"
                "  origin=request.headers.get('origin')\n"
                '  if origin and urlparse(origin).netloc!=request.url.netloc:return '
                "JSONResponse({'detail':'Cross-origin writes rejected'},403)\n"
                "  if len(await request.body())>32768:return JSONResponse({'detail':'Request too "
                "large'},413)\n"
                ' response=await '
                "call_next(request);response.headers['Cache-Control']='no-store';response.headers['X-Content-Type-Options']='nosniff';return "
                'response\n'
                '\n'
                "def workspace(x_workspace:str=Header(default='')):\n"
                " if not re.fullmatch('[a-f0-9]{32}',x_workspace):raise HTTPException(401,'Start a new demo "
                "workspace')\n"
                ' with db() as c:\n'
                "  if not c.execute('SELECT id FROM workspaces WHERE id=?',(x_workspace,)).fetchone():raise "
                "HTTPException(401,'This workspace expired')\n"
                ' return x_workspace\n'
                'class CandidateIn(BaseModel):\n'
                " model_config=ConfigDict(extra='forbid')\n"
                ' title:str=Field(min_length=3,max_length=80)\n'
                'class CheckIn(BaseModel):\n'
                " model_config=ConfigDict(extra='forbid')\n"
                ' title:str=Field(min_length=3,max_length=100)\n'
                " category:Literal['tests','docs','rollback','security']\n"
                ' critical:bool=True\n'
                ' version:int=Field(ge=1)\n'
                'class UpdateIn(BaseModel):\n'
                " model_config=ConfigDict(extra='forbid')\n"
                " status:Literal['pending','pass','fail','waived']\n"
                " reference:str=Field(default='',max_length=180)\n"
                ' version:int=Field(ge=1)\n'
                'class VersionIn(BaseModel):\n'
                " model_config=ConfigDict(extra='forbid')\n"
                ' version:int=Field(ge=1)\n'
                'def owned(c,cid,w):\n'
                " row=c.execute('SELECT * FROM candidates WHERE id=? AND workspace=?',(cid,w)).fetchone()\n"
                " if not row:raise HTTPException(404,'Release candidate not found in this workspace')\n"
                ' return dict(row)\n'
                'def check_version(row,v):\n'
                " if row['version']!=v:raise HTTPException(409,'Another change was saved. Reload before "
                "editing.')\n"
                'def view(c,row):\n'
                " checks=[dict(x) for x in c.execute('SELECT * FROM checks WHERE candidate=? ORDER BY "
                "created,id',(row['id'],))]\n"
                " blockers=[x['title'] for x in checks if x['critical'] and x['status']!='pass']\n"
                " if not checks:blockers=['Add at least one release check']\n"
                " return {**row,'checks':checks,'ready':not "
                "blockers,'blockers':blockers,'snapshots':[dict(x) for x in c.execute('SELECT "
                "id,digest,created FROM snapshots WHERE candidate=? ORDER BY created DESC',(row['id'],))]}\n"
                "@app.get('/api/health')\n"
                'def health():\n'
                " with db() as c:c.execute('SELECT 1').fetchone()\n"
                " return {'ok':True,'storage':'sqlite','synthetic':True}\n"
                "@app.post('/api/workspaces',status_code=201)\n"
                'def create_workspace():\n'
                ' token=secrets.token_hex(16)\n'
                ' with db() as c:\n'
                '  '
                'cutoff=(datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=7)).isoformat()\n'
                "  for table in ['checks','snapshots']:c.execute(f'DELETE FROM {table} WHERE candidate IN "
                '(SELECT id FROM candidates WHERE workspace IN (SELECT id FROM workspaces WHERE '
                "created<?))',(cutoff,))\n"
                "  c.execute('DELETE FROM candidates WHERE workspace IN (SELECT id FROM workspaces WHERE "
                "created<?)',(cutoff,));c.execute('DELETE FROM workspaces WHERE created<?',(cutoff,))\n"
                "  if c.execute('SELECT count(*) FROM workspaces').fetchone()[0]>=100:raise "
                "HTTPException(503,'Demo capacity reached')\n"
                "  c.execute('INSERT INTO workspaces VALUES(?,?)',(token,now()))\n"
                " return {'workspace':token}\n"
                "@app.get('/api/candidates')\n"
                'def candidates(w=Depends(workspace)):\n'
                " with db() as c:return {'candidates':[view(c,dict(r)) for r in c.execute('SELECT * FROM "
                "candidates WHERE workspace=? ORDER BY created DESC',(w,))]}\n"
                "@app.post('/api/candidates',status_code=201)\n"
                'def add_candidate(d:CandidateIn,w=Depends(workspace)):\n'
                ' title=d.title.strip()\n'
                " if len(title)<3:raise HTTPException(422,'Enter a meaningful candidate title')\n"
                ' cid=secrets.token_hex(8)\n'
                ' with db() as c:\n'
                "  if c.execute('SELECT count(*) FROM candidates WHERE "
                "workspace=?',(w,)).fetchone()[0]>=20:raise HTTPException(429,'Demo limit: 20 candidates')\n"
                "  c.execute('INSERT INTO candidates VALUES(?,?,?,?,?)',(cid,w,title,1,now()))\n"
                "  for name,cat in [('Regression tests pass','tests'),('Rollback steps "
                "documented','rollback'),('Release notes reviewed','docs')]:c.execute('INSERT INTO checks "
                "VALUES(?,?,?,?,?,?,?,?)',(secrets.token_hex(8),cid,name,cat,'pending','',1,now()))\n"
                "  return {'candidate':view(c,owned(c,cid,w))}\n"
                "@app.get('/api/candidates/{cid}')\n"
                'def get_candidate(cid:str,w=Depends(workspace)):\n'
                " with db() as c:return {'candidate':view(c,owned(c,cid,w))}\n"
                "@app.post('/api/candidates/{cid}/checks',status_code=201)\n"
                'def add_check(cid:str,d:CheckIn,w=Depends(workspace)):\n'
                ' with db() as c:\n'
                "  c.execute('BEGIN IMMEDIATE');row=owned(c,cid,w);check_version(row,d.version)\n"
                "  if len(d.title.strip())<3:raise HTTPException(422,'Enter a meaningful check title')\n"
                "  if c.execute('SELECT count(*) FROM checks WHERE "
                "candidate=?',(cid,)).fetchone()[0]>=40:raise HTTPException(429,'Demo limit: 40 checks')\n"
                "  c.execute('INSERT INTO checks "
                "VALUES(?,?,?,?,?,?,?,?)',(secrets.token_hex(8),cid,d.title.strip(),d.category,'pending','',int(d.critical),now()));c.execute('UPDATE "
                "candidates SET version=version+1 WHERE id=?',(cid,));return "
                "{'candidate':view(c,owned(c,cid,w))}\n"
                "@app.patch('/api/candidates/{cid}/checks/{check_id}')\n"
                'def update_check(cid:str,check_id:str,d:UpdateIn,w=Depends(workspace)):\n'
                ' with db() as c:\n'
                "  c.execute('BEGIN IMMEDIATE');row=owned(c,cid,w);check_version(row,d.version)\n"
                "  check=c.execute('SELECT * FROM checks WHERE id=? AND "
                "candidate=?',(check_id,cid)).fetchone()\n"
                "  if not check:raise HTTPException(404,'Check not found')\n"
                "  if check['critical'] and d.status=='waived':raise HTTPException(422,'Critical checks "
                "cannot be waived')\n"
                "  if d.status in ['pass','waived'] and len(d.reference.strip())<5:raise "
                "HTTPException(422,'Add a synthetic evidence reference of at least 5 characters')\n"
                "  c.execute('UPDATE checks SET status=?,reference=? WHERE "
                "id=?',(d.status,d.reference.strip(),check_id));c.execute('UPDATE candidates SET "
                "version=version+1 WHERE id=?',(cid,));return {'candidate':view(c,owned(c,cid,w))}\n"
                "@app.post('/api/candidates/{cid}/snapshots',status_code=201)\n"
                'def snapshot(cid:str,d:VersionIn,w=Depends(workspace)):\n'
                ' with db() as c:\n'
                "  c.execute('BEGIN "
                "IMMEDIATE');row=owned(c,cid,w);check_version(row,d.version);current=view(c,row)\n"
                "  if not current['ready']:raise HTTPException(422,'Snapshot blocked: '+', "
                "'.join(current['blockers']))\n"
                "  if len(current['snapshots'])>=20:raise HTTPException(429,'Demo limit: 20 snapshots')\n"
                '  '
                "payload=json.dumps({'title':row['title'],'version':row['version'],'checks':current['checks']},sort_keys=True,separators=(',',':'));digest=hashlib.sha256(payload.encode()).hexdigest();sid=secrets.token_hex(8)\n"
                "  c.execute('INSERT INTO snapshots "
                "VALUES(?,?,?,?,?)',(sid,cid,payload,digest,now()));c.execute('UPDATE candidates SET "
                "version=version+1 WHERE id=?',(cid,));return "
                "{'snapshot':{'id':sid,'payload':json.loads(payload),'digest':digest}}\n"
                "@app.get('/api/candidates/{cid}/snapshots/{sid}')\n"
                'def get_snapshot(cid:str,sid:str,w=Depends(workspace)):\n'
                ' with db() as c:\n'
                "  owned(c,cid,w);r=c.execute('SELECT * FROM snapshots WHERE candidate=? AND "
                "id=?',(cid,sid)).fetchone()\n"
                "  if not r:raise HTTPException(404,'Snapshot not found')\n"
                "  r=dict(r);r['payload']=json.loads(r['payload']);return {'snapshot':r}\n"
                "@app.get('/api/compare')\n"
                'def compare(left:str,right:str,w=Depends(workspace)):\n'
                ' with db() as c:\n'
                '  a=view(c,owned(c,left,w));b=view(c,owned(c,right,w));key=lambda '
                "x:(x['category'],x['title'].lower());ma={key(x):x for x in a['checks']};mb={key(x):x for x "
                "in b['checks']}\n"
                "  changes=[{'category':k[0],'title':(mb.get(k) or "
                "ma[k])['title'],'before':ma.get(k,{}).get('status','absent'),'after':mb.get(k,{}).get('status','absent')} "
                'for k in sorted(ma.keys()|mb.keys()) if '
                "ma.get(k,{}).get('status')!=mb.get(k,{}).get('status')]\n"
                "  return {'left':a['title'],'right':b['title'],'changes':changes}\n"
                "@app.get('/{path:path}')\n"
                'def frontend(path:str):\n'
                " root=(Path(__file__).parent/'../static').resolve();target=(root/path).resolve()\n"
                " if not target.is_relative_to(root) or not target.is_file():target=root/'index.html'\n"
                " if not target.exists():raise HTTPException(404,'Frontend not built yet')\n"
                ' return FileResponse(target)\n',
 'browser.spec.ts': "import{test,expect}from'@playwright/test';\n"
                    "test('release evidence, immutable snapshot and candidate "
                    "comparison',async({page})=>{await page.goto('/');await "
                    "page.getByRole('button',{name:'Create demo workspace'}).click();await "
                    "page.getByLabel('New candidate title').fill('Search release 1.0');await "
                    "page.getByRole('button',{name:'+ Create candidate'}).click();await "
                    "expect(page.getByRole('heading',{name:'Search release "
                    "1.0',exact:true})).toBeVisible();for(const title of['Regression tests pass','Rollback "
                    "steps documented','Release notes reviewed']){const "
                    "form=page.locator('form.check').filter({has:page.getByRole('heading',{name:title,exact:true})});await "
                    "form.getByLabel(title+' status').selectOption('pass');await form.getByLabel(title+' "
                    "evidence').fill('Synthetic CI run #42');await form.getByRole('button',{name:'Save "
                    "check'}).click();await expect(form.locator('.state')).toHaveText('pass')}await "
                    "page.getByRole('button',{name:'Save readiness snapshot'}).click();await "
                    "expect(page.getByRole('heading',{name:'Saved "
                    "snapshot',exact:true})).toBeVisible();const digest=await page.locator('.snapshot "
                    "code').innerText();await page.reload();await expect(page.locator('.history "
                    "button')).toHaveCount(1);await page.locator('.history button').click();await "
                    "expect(page.locator('.snapshot code')).toHaveText(digest);await page.getByLabel('New "
                    "candidate title').fill('Search release 1.1');await page.getByRole('button',{name:'+ "
                    "Create candidate'}).click();await page.getByLabel('Compare with "
                    "candidate').selectOption({label:'Search release 1.0'});await "
                    "expect(page.locator('.compare')).toContainText('pending → pass')});\n"
                    "test('actual responsive screenshots no overflow',async({page})=>{await "
                    "page.goto('/');await page.getByRole('button',{name:'Create demo "
                    "workspace'}).click();await page.getByLabel('New candidate title').fill('Search release "
                    "2.0');await page.getByRole('button',{name:'+ Create candidate'}).click();await "
                    "expect(page.getByRole('heading',{name:'Search release "
                    "2.0',exact:true})).toBeVisible();for(const width of[1280,390,320]){await "
                    'page.setViewportSize({width,height:900});await '
                    'page.screenshot({path:`evidence/releasepad-${width}.png`,fullPage:true});expect(await '
                    'page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy()}});\n'
                    "test('expired session and offline recovery are visible',async({page,context})=>{await "
                    "page.goto('/');await "
                    "page.evaluate(()=>localStorage.setItem('releasepad-workspace','0'.repeat(32)));await "
                    "page.reload();await expect(page.getByRole('alert')).toContainText('expired');await "
                    "page.getByRole('button',{name:'Create demo workspace'}).click();await "
                    "page.getByLabel('New candidate title').fill('Offline candidate');await "
                    "context.setOffline(true);await page.getByRole('button',{name:'+ Create "
                    "candidate'}).click();await expect(page.getByRole('alert')).toBeVisible();await "
                    "context.setOffline(false);await page.getByRole('button',{name:'Reload "
                    "data'}).click();await page.getByRole('button',{name:'+ Create "
                    "candidate'}).click();await expect(page.getByRole('heading',{name:'Offline "
                    "candidate',exact:true})).toBeVisible()});\n",
 'package.json': '{\n'
                 '  "name": "releasepad-isocode",\n'
                 '  "private": true,\n'
                 '  "version": "1.0.0",\n'
                 '  "scripts": {\n'
                 '    "build": "vite build --outDir ../static",\n'
                 '    "test": "vitest run",\n'
                 '    "dev": "vite --host 127.0.0.1"\n'
                 '  },\n'
                 '  "dependencies": {\n'
                 '    "react": "^19.3.1",\n'
                 '    "react-dom": "^19.3.1",\n'
                 '    "react-router-dom": "^7.18.6"\n'
                 '  },\n'
                 '  "devDependencies": {\n'
                 '    "@playwright/test": "^1.65.1",\n'
                 '    "@testing-library/jest-dom": "6.9.1",\n'
                 '    "@testing-library/react": "16.3.0",\n'
                 '    "@types/react": "19.2.2",\n'
                 '    "@types/react-dom": "19.2.2",\n'
                 '    "jsdom": "26.1.0",\n'
                 '    "typescript": "5.9.3",\n'
                 '    "vite": "^8.3.8",\n'
                 '    "vitest": "^5.1.1"\n'
                 '  },\n'
                 '  "type": "module"\n'
                 '}\n',
 'playwright.config.ts': "import{defineConfig}from'@playwright/test';export default "
                         "defineConfig({testDir:'.',testMatch:'browser.spec.ts',workers:1,use:{baseURL:'http://127.0.0.1:4182',headless:true},webServer:{command:process.env.RELEASEPAD_TEST_SERVER||'python "
                         '-m uvicorn api.main:app --port '
                         "4182',url:'http://127.0.0.1:4182/api/health',reuseExistingServer:true}})\n",
 'requirements.txt': 'fastapi==0.135.1\nuvicorn==0.41.0\nhttpx==0.28.1\n',
 'run_server.py': '"""Dedicated single-process host entry point. No provider resources are created."""\n'
                  'import os\n'
                  'import uvicorn\n'
                  '\n'
                  '\n'
                  'def resolve_port(value):\n'
                  '    if not value.isascii() or not value.isdigit() or not 1 <= int(value) <= 65535:\n'
                  "        raise ValueError('PORT must be an integer from 1 to 65535')\n"
                  '    return int(value)\n'
                  '\n'
                  '\n'
                  "if __name__ == '__main__':\n"
                  "    uvicorn.run('api.main:app', host='0.0.0.0', port=resolve_port(os.environ.get('PORT', "
                  "'4182')), workers=1)\n",
 'test_api.py': 'import os,tempfile,unittest,json,hashlib\n'
                "os.environ['RELEASEPAD_DB']=tempfile.mktemp(suffix='.sqlite')\n"
                'from fastapi.testclient import TestClient\n'
                'from api.main import app\n'
                'class ReleaseTest(unittest.TestCase):\n'
                ' def setUp(self):\n'
                '  '
                "self.c=TestClient(app);self.w=self.c.post('/api/workspaces').json()['workspace'];self.h={'X-Workspace':self.w};self.v=self.c.post('/api/candidates',headers=self.h,json={'title':'Release "
                "1.0 candidate'}).json()['candidate']\n"
                " def update(self,check,status='pass',reference='Synthetic CI run 42',version=None):return "
                "self.c.patch('/api/candidates/'+self.v['id']+'/checks/'+check['id'],headers=self.h,json={'version':version "
                "or self.v['version'],'status':status,'reference':reference})\n"
                ' def ready(self):\n'
                "  for check in self.v['checks']:self.v=self.update(check).json()['candidate']\n"
                ' def '
                "test_requires_session(self):self.assertEqual(self.c.get('/api/candidates').status_code,401)\n"
                ' def '
                "test_creation_saved(self):self.assertEqual(self.c.get('/api/candidates/'+self.v['id'],headers=self.h).json()['candidate']['title'],'Release "
                "1.0 candidate')\n"
                ' def test_isolation(self):\n'
                '  '
                "w=self.c.post('/api/workspaces').json()['workspace'];self.assertEqual(self.c.get('/api/candidates/'+self.v['id'],headers={'X-Workspace':w}).status_code,404)\n"
                ' def '
                "test_validation(self):self.assertEqual(self.c.post('/api/candidates',headers=self.h,json={'title':'x'}).status_code,422)\n"
                ' def '
                "test_whitespace_title(self):self.assertEqual(self.c.post('/api/candidates',headers=self.h,json={'title':'   "
                "'}).status_code,422)\n"
                ' def '
                "test_critical_not_waivable(self):self.assertEqual(self.update(self.v['checks'][0],'waived').status_code,422)\n"
                ' def '
                "test_pass_needs_evidence(self):self.assertEqual(self.update(self.v['checks'][0],reference='').status_code,422)\n"
                ' def test_stale_version(self):\n'
                '  '
                "self.v=self.update(self.v['checks'][0]).json()['candidate'];self.assertEqual(self.update(self.v['checks'][1],version=1).status_code,409)\n"
                ' def '
                "test_snapshot_gate(self):self.assertEqual(self.c.post('/api/candidates/'+self.v['id']+'/snapshots',headers=self.h,json={'version':self.v['version']}).status_code,422)\n"
                ' def test_snapshot_immutable(self):\n'
                '  '
                "self.ready();r=self.c.post('/api/candidates/'+self.v['id']+'/snapshots',headers=self.h,json={'version':self.v['version']});self.assertEqual(r.status_code,201);snap=r.json()['snapshot'];self.v=self.c.get('/api/candidates/'+self.v['id'],headers=self.h).json()['candidate'];self.update(self.v['checks'][0],'fail','Synthetic "
                "failure');after=self.c.get('/api/candidates/'+self.v['id']+'/snapshots/'+snap['id'],headers=self.h).json()['snapshot'];self.assertEqual(after['payload'],snap['payload']);self.assertEqual(after['digest'],hashlib.sha256(json.dumps(after['payload'],sort_keys=True,separators=(',',':')).encode()).hexdigest())\n"
                ' def test_compare(self):\n'
                "  other=self.c.post('/api/candidates',headers=self.h,json={'title':'Release 1.1 "
                "candidate'}).json()['candidate'];self.v=self.update(self.v['checks'][0]).json()['candidate'];r=self.c.get('/api/compare',headers=self.h,params={'left':self.v['id'],'right':other['id']});self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['changes']),1)\n"
                ' def test_compare_isolation(self):\n'
                '  '
                "w=self.c.post('/api/workspaces').json()['workspace'];other=self.c.post('/api/candidates',headers={'X-Workspace':w},json={'title':'Other "
                "workspace'}).json()['candidate'];self.assertEqual(self.c.get('/api/compare',headers=self.h,params={'left':self.v['id'],'right':other['id']}).status_code,404)\n"
                ' def test_add_optional_check(self):\n'
                '  '
                "r=self.c.post('/api/candidates/'+self.v['id']+'/checks',headers=self.h,json={'title':'Optional "
                'copy '
                "review','category':'docs','critical':False,'version':self.v['version']});self.assertEqual(r.status_code,201);self.assertEqual(len(r.json()['candidate']['checks']),4)\n"
                ' def '
                "test_cross_origin(self):self.assertEqual(self.c.post('/api/workspaces',headers={'Origin':'https://other.test'}).status_code,403)\n"
                ' def '
                "test_body_limit(self):self.assertEqual(self.c.post('/api/candidates',headers=self.h,json={'title':'x'*34000}).status_code,413)\n"
                "if __name__=='__main__':unittest.main()\n",
 'test_container.py': '"""CI-only actual Docker image and disposable dedicated-volume persistence check."""\n'
                      'import subprocess, time, urllib.request, json, uuid\n'
                      'suffix=uuid.uuid4().hex[:10]\n'
                      "name='releasepad-test-'+suffix\n"
                      "volume=name+'-data'\n"
                      'port=4193\n'
                      '\n'
                      'def docker(*args):\n'
                      "    return subprocess.check_output(['docker',*args],text=True).strip()\n"
                      '\n'
                      "def request(path,method='GET',body=None,token=None):\n"
                      "    headers={'Content-Type':'application/json'}\n"
                      "    if token: headers['X-Workspace']=token\n"
                      '    with '
                      "urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=None "
                      'if body is None else '
                      'json.dumps(body).encode(),method=method,headers=headers),timeout=5) as response:\n'
                      '        return json.load(response)\n'
                      '\n'
                      'def start():\n'
                      '    '
                      "docker('run','-d','--name',name,'-p','127.0.0.1:'+str(port)+':'+str(port),'-e','PORT='+str(port),'-v',volume+':/data','releasepad-ci')\n"
                      '    for _ in range(100):\n'
                      '        try:\n'
                      "            assert request('/api/health')['storage']=='sqlite'\n"
                      '            return\n'
                      '        except Exception: time.sleep(.2)\n'
                      "    raise RuntimeError('Container did not become healthy')\n"
                      '\n'
                      'try:\n'
                      "    docker('volume','create',volume)\n"
                      '    start()\n'
                      "    token=request('/api/workspaces','POST')['workspace']\n"
                      "    candidate=request('/api/candidates','POST',{'title':'Container volume "
                      "test'},token)['candidate']\n"
                      "    for check in candidate['checks']:\n"
                      '        '
                      "candidate=request('/api/candidates/'+candidate['id']+'/checks/'+check['id'],'PATCH',{'version':candidate['version'],'status':'pass','reference':'Synthetic "
                      "container CI test'},token)['candidate']\n"
                      '    '
                      "snapshot=request('/api/candidates/'+candidate['id']+'/snapshots','POST',{'version':candidate['version']},token)['snapshot']\n"
                      "    with urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/') as response:\n"
                      "        assert b'<html' in response.read().lower()\n"
                      "    docker('rm','-f',name)\n"
                      '    start()\n'
                      "    restored=request('/api/candidates/'+candidate['id'],token=token)['candidate']\n"
                      '    '
                      "saved=request('/api/candidates/'+candidate['id']+'/snapshots/'+snapshot['id'],token=token)['snapshot']\n"
                      "    assert restored['ready'] and restored['title']==candidate['title']\n"
                      "    assert saved['digest']==snapshot['digest'] and "
                      "saved['payload']==snapshot['payload']\n"
                      "    print('PASS actual container build, non-default PORT, frontend, API, SQLite and "
                      'replacement-container dedicated-volume persistence. Not a hosting-provider '
                      "deployment.')\n"
                      'finally:\n'
                      "    subprocess.run(['docker','rm','-f',name],check=False)\n"
                      "    subprocess.run(['docker','volume','rm',volume],check=False)\n",
 'test_restart.py': '"""Local process-restart proof only, not hosted durability or container proof."""\n'
                    'import subprocess,tempfile,os,time,urllib.request,json,socket,sys\n'
                    'from pathlib import Path\n'
                    'root=Path(__file__).parent\n'
                    'with tempfile.TemporaryDirectory() as folder:\n'
                    ' with socket.socket() as probe:\n'
                    "  probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]\n"
                    " env={**os.environ,'RELEASEPAD_DB':folder+'/restart.sqlite','PORT':str(port)}\n"
                    ' def start():\n'
                    '  '
                    "p=subprocess.Popen([sys.executable,'run_server.py'],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)\n"
                    '  for _ in range(100):\n'
                    '   if p.poll() is not None:raise RuntimeError(p.stdout.read().decode())\n'
                    "   try:request('/api/health');return p\n"
                    '   except Exception:time.sleep(.05)\n'
                    "  p.terminate();p.wait();raise RuntimeError('Local server did not start')\n"
                    " def request(path,method='GET',body=None,token=None):\n"
                    "  headers={'Content-Type':'application/json'}\n"
                    "  if token:headers['X-Workspace']=token\n"
                    '  '
                    "r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(port)+path,data=None "
                    'if body is None else '
                    'json.dumps(body).encode(),method=method,headers=headers),timeout=4)\n'
                    '  return json.load(r)\n'
                    ' def stop(p):p.terminate();p.wait(timeout=5)\n'
                    ' p=start()\n'
                    ' try:\n'
                    '  '
                    "token=request('/api/workspaces','POST')['workspace'];v=request('/api/candidates','POST',{'title':'Restart "
                    "preservation'},token)['candidate']\n"
                    '  for c in '
                    "v['checks']:v=request('/api/candidates/'+v['id']+'/checks/'+c['id'],'PATCH',{'version':v['version'],'status':'pass','reference':'Synthetic "
                    "restart test'},token)['candidate']\n"
                    '  '
                    "snap=request('/api/candidates/'+v['id']+'/snapshots','POST',{'version':v['version']},token)['snapshot']\n"
                    ' finally:stop(p)\n'
                    ' p=start()\n'
                    ' try:\n'
                    '  '
                    "restored=request('/api/candidates/'+v['id'],token=token)['candidate'];saved=request('/api/candidates/'+v['id']+'/snapshots/'+snap['id'],token=token)['snapshot']\n"
                    "  assert restored['title']==v['title'] and restored['ready']\n"
                    "  assert saved['digest']==snap['digest'] and saved['payload']==snap['payload']\n"
                    "  print('PASS local process stop/start preserved workspace, candidate, evidence, "
                    "immutable snapshot and digest on dedicated SQLite file.')\n"
                    "  print('Not a hosted volume or container test.')\n"
                    ' finally:stop(p)\n',
 'vite.config.ts': "import{defineConfig}from'vite';export default "
                   "defineConfig({root:'web',server:{proxy:{'/api':'http://127.0.0.1:4182'}},test:{environment:'jsdom',include:['**/*.test.tsx']}})\n",
 'web/CheckRow.test.tsx': 'import React '
                          "from'react';import{describe,it,expect,vi,afterEach}from'vitest';import{render,screen,fireEvent,cleanup}from'@testing-library/react';import{CheckRow,Check}from'./CheckRow';\n"
                          "afterEach(cleanup);const base:Check={id:'test',title:'Regression "
                          "suite',category:'tests',status:'pending',reference:'',critical:1};\n"
                          "describe('actual release check component',()=>{it('renders required check and "
                          "accessible fields',()=>{render(<CheckRow check={base} busy={false} "
                          "update={()=>{}}/>);expect(screen.getByLabelText('Regression suite "
                          "status')).toBeTruthy();expect(screen.getByText('tests / "
                          "REQUIRED')).toBeTruthy()});it('critical check does not offer "
                          "waiver',()=>{render(<CheckRow check={base} busy={false} "
                          "update={()=>{}}/>);expect(screen.queryByRole('option',{name:'Waived'})).toBeNull()});it('optional "
                          "check offers waiver',()=>{render(<CheckRow check={{...base,critical:0}} "
                          'busy={false} '
                          "update={()=>{}}/>);expect(screen.getByRole('option',{name:'Waived'})).toBeTruthy()});it('submits "
                          "changed status and evidence',()=>{const update=vi.fn();render(<CheckRow "
                          'check={base} busy={false} '
                          "update={update}/>);fireEvent.change(screen.getByLabelText('Regression suite "
                          "status'),{target:{value:'pass'}});fireEvent.change(screen.getByLabelText('Regression "
                          "suite evidence'),{target:{value:'Synthetic CI "
                          "run'}});fireEvent.click(screen.getByRole('button',{name:'Save "
                          "check'}));expect(update).toHaveBeenCalledWith(base,'pass','Synthetic CI "
                          "run')});it('disables save while request is in flight',()=>{render(<CheckRow "
                          'check={base} busy={true} '
                          "update={()=>{}}/>);expect((screen.getByRole('button',{name:'Save check'})as "
                          "HTMLButtonElement).disabled).toBe(true)});it('retains stored "
                          "evidence',()=>{render(<CheckRow check={{...base,status:'pass',reference:'Saved "
                          "synthetic evidence'}} busy={false} "
                          "update={()=>{}}/>);expect((screen.getByLabelText('Regression suite evidence')as "
                          "HTMLInputElement).value).toBe('Saved synthetic evidence')})});\n",
 'web/CheckRow.tsx': "import React,{useState}from'react';\n"
                     'export type '
                     'Check={id:string;title:string;category:string;status:string;reference:string;critical:number};\n'
                     'export function '
                     'CheckRow({check,busy,update}:{check:Check;busy:boolean;update:(c:Check,s:string,r:string)=>void}){const[status,setStatus]=useState(check.status),[reference,setReference]=useState(check.reference);return '
                     '<form className="check" '
                     'onSubmit={e=>{e.preventDefault();update(check,status,reference)}}><div><span '
                     'className="category">{check.category} / '
                     "{check.critical?'REQUIRED':'OPTIONAL'}</span><h4>{check.title}</h4><span "
                     "className={'state '+check.status}>{check.status}</span></div><div "
                     'className="check-fields"><label>Status<select aria-label={check.title+\' status\'} '
                     'value={status} onChange={e=>setStatus(e.target.value)}><option '
                     'value="pending">Pending</option><option value="pass">Pass</option><option '
                     'value="fail">Fail</option>{!check.critical&&<option '
                     'value="waived">Waived</option>}</select></label><label>Synthetic evidence '
                     "reference<input aria-label={check.title+' evidence'} value={reference} "
                     'onChange={e=>setReference(e.target.value)} maxLength={180} placeholder="e.g. demo CI '
                     'run #42"/></label><button disabled={busy} className="save-check">Save '
                     'check</button></div></form>}\n',
 'web/index.html': '<!doctype html><html lang="en"><head><meta charset="UTF-8"/><meta name="viewport" '
                   'content="width=device-width,initial-scale=1.0"/><title>ReleasePad | Readiness, '
                   'recorded</title></head><body><div id="root"></div><script type="module" '
                   'src="/main.tsx"></script></body></html>\n',
 'web/main.tsx': "import{CheckRow}from'./CheckRow';\n"
                 'import '
                 "React,{useState,useEffect}from'react';import{createRoot}from'react-dom/client';import'./style.css';\n"
                 'type '
                 'Check={id:string;title:string;category:string;status:string;reference:string;critical:number};type '
                 'Candidate={id:string;title:string;version:number;checks:Check[];ready:boolean;blockers:string[];snapshots:{id:string;digest:string;created:string}[]};\n'
                 'function '
                 "App(){const[token,setToken]=useState(localStorage.getItem('releasepad-workspace')||'');const[items,setItems]=useState<Candidate[]>([]),[selected,setSelected]=useState(new "
                 "URLSearchParams(location.search).get('release')||''),[filter,setFilter]=useState('all'),[error,setError]=useState(''),[loading,setLoading]=useState(false),[busy,setBusy]=useState(false),[title,setTitle]=useState(''),[comparison,setComparison]=useState<any>(null),[snapshot,setSnapshot]=useState<any>(null);\n"
                 ' const current=items.find(v=>v.id===selected)||items[0];\n'
                 " async function api(path:string,method='GET',body?:any,t=token){const r=await "
                 "fetch('/api'+path,{method,headers:{'Content-Type':'application/json',...(t?{'X-Workspace':t}:{})},body:body===undefined?undefined:JSON.stringify(body)});const "
                 'd=await '
                 "r.json();if(!r.ok){if(r.status===401){setToken('');localStorage.removeItem('releasepad-workspace')}throw "
                 "new Error(typeof d.detail==='string'?d.detail:'Check the fields and try again.')}return "
                 'd}\n'
                 ' async function load(t=token){setLoading(true);try{const d=await '
                 "api('/candidates','GET',undefined,t);setItems(d.candidates)}catch(e:any){setError(e.message||'Connection "
                 "failed. Try again.')}finally{setLoading(false)}}\n"
                 ' useEffect(()=>{if(token)load()},[token]);\n'
                 ' function choose(id:string){setSelected(id);const url=new '
                 "URL(location.href);url.searchParams.set('release',id);history.replaceState({},'',url);setComparison(null);setSnapshot(null);setError('')}\n"
                 " async function act(fn:()=>Promise<void>){setBusy(true);setError('');try{await "
                 "fn()}catch(e:any){setError(e.message||'Connection failed. Try "
                 "again.')}finally{setBusy(false)}}\n"
                 ' const start=()=>act(async()=>{const d=await '
                 "api('/workspaces','POST');localStorage.setItem('releasepad-workspace',d.workspace);setToken(d.workspace)});\n"
                 ' const add=(e:React.FormEvent)=>{e.preventDefault();act(async()=>{const d=await '
                 "api('/candidates','POST',{title});setTitle('');await load();choose(d.candidate.id)})};\n"
                 ' const update=(check:Check,status:string,reference:string)=>act(async()=>{await '
                 "api('/candidates/'+current.id+'/checks/'+check.id,'PATCH',{version:current.version,status,reference});await "
                 'load()});\n'
                 ' const save=()=>act(async()=>{const d=await '
                 "api('/candidates/'+current.id+'/snapshots','POST',{version:current.version});setSnapshot(d.snapshot);await "
                 'load()});\n'
                 ' return <><header><a className="brand" href="/">▣ <b>ReleasePad</b></a><span>Readiness, '
                 'recorded.</span><div className="demo">SYNTHETIC WORKSPACE</div></header><main><div '
                 'className="intro"><div><p className="eyebrow">RELEASE OPERATIONS / PORTFOLIO '
                 'DEMO</p><h1>Ship with a clear record.</h1><p>Check the evidence. Freeze the decision. Keep '
                 'the history.</p></div><div className="stamp">No deployment actions<br/><strong>Just better '
                 'release decisions.</strong></div></div>{error&&<div className="error" role="alert">{error} '
                 '{token&&<button onClick={()=>load()}>Reload data</button>}</div>}{!token?<section '
                 'className="welcome"><span className="number">01</span><h2>A workspace of your '
                 'own.</h2><p>Create an isolated demo session, add a release candidate and check its '
                 'readiness.<br/>Use synthetic evidence only. No account or real deployment is '
                 "connected.</p><button disabled={busy} onClick={start}>{busy?'Creating…':'Create demo "
                 'workspace\'}</button></section>:<div className="layout"><aside><div '
                 'className="section-title"><h2>Candidates</h2><span>{items.length}</span></div><form '
                 'onSubmit={add}><label htmlFor="candidate-title">New candidate title</label><input '
                 'id="candidate-title" value={title} onChange={e=>setTitle(e.target.value)} minLength={3} '
                 'maxLength={80} placeholder="e.g. Search v1.2" required/><button disabled={busy}>+ Create '
                 'candidate</button></form><nav aria-label="Release candidates">{items.map(v=><button '
                 "key={v.id} className={current?.id===v.id?'selected':''} "
                 "onClick={()=>choose(v.id)}><strong>{v.title}</strong><small>{v.ready?'Ready to "
                 "snapshot':v.blockers.length+' pending blockers'} · v{v.version}</small></button>)}</nav><p "
                 'className="aside-note">Every candidate starts with tests, rollback and documentation '
                 'checks. Nothing deploys from here.</p></aside><section className="workbench">{loading?<div '
                 'className="empty" role="status">Loading saved release data…</div>:!current?<div '
                 'className="empty"><span className="number">02</span><h2>Give the next release a '
                 'name.</h2><p>Create your first candidate to see its readiness checklist.</p></div>:<><div '
                 'className="candidate-head"><div><p className="eyebrow">CANDIDATE / VERSION '
                 "{current.version}</p><h2>{current.title}</h2></div><span className={'badge "
                 "'+(current.ready?'ready':'pending')}>{current.ready?'Ready to snapshot':'Needs "
                 "review'}</span></div><div "
                 'className="metrics"><div><strong>{current.checks.filter(c=>c.status===\'pass\').length}<small> '
                 '/ {current.checks.length}</small></strong><span>Checks '
                 'passed</span></div><div><strong>{current.blockers.length}</strong><span>Release '
                 'blockers</span></div><div><strong>{current.snapshots.length}</strong><span>Immutable '
                 'snapshots</span></div></div><div className="toolbar"><h3>Readiness '
                 'checklist</h3><label>Show <select aria-label="Filter checks" value={filter} '
                 'onChange={e=>setFilter(e.target.value)}><option value="all">All checks</option><option '
                 'value="pending">Pending</option><option value="pass">Passed</option><option '
                 'value="fail">Failed</option></select></label></div><div '
                 'className="checks">{current.checks.filter(c=>filter===\'all\'||c.status===filter).map(c=><CheckRow '
                 "key={c.id+':'+c.status+':'+c.reference} check={c} busy={busy} "
                 'update={update}/>)}</div><div className="freeze"><div><h3>A decision you can point '
                 'to.</h3><p>Snapshots preserve this checklist, its evidence and a SHA-256 digest. Later '
                 'changes cannot rewrite the saved decision.</p></div><button '
                 'disabled={busy||!current.ready} onClick={save}>Save readiness '
                 'snapshot</button></div>{current.snapshots.length>0&&<section '
                 'className="history"><h3>Snapshot history</h3>{current.snapshots.map(s=><button key={s.id} '
                 'onClick={()=>act(async()=>setSnapshot((await '
                 "api('/candidates/'+current.id+'/snapshots/'+s.id)).snapshot))}><span>{new "
                 'Date(s.created).toLocaleString()}</span><code>{s.digest.slice(0,16)}…</code></button>)}</section>}{snapshot&&<section '
                 'className="snapshot"><h3>Saved snapshot</h3><p>Candidate version '
                 '{snapshot.payload.version}. {snapshot.payload.checks.length} recorded '
                 'checks.</p><code>{snapshot.digest}</code></section>}{items.length>1&&<section '
                 'className="compare"><h3>Compare candidate readiness</h3><select aria-label="Compare with '
                 'candidate" defaultValue="" onChange={e=>{const '
                 'id=e.target.value;if(id)act(async()=>setComparison(await '
                 'api(\'/compare?left=\'+current.id+\'&right=\'+id)))}}><option value="">Choose another '
                 'candidate</option>{items.filter(v=>v.id!==current.id).map(v=><option key={v.id} '
                 'value={v.id}>{v.title}</option>)}</select>{comparison&&<><p>{comparison.left} → '
                 '{comparison.right}</p>{comparison.changes.length?comparison.changes.map((v:any)=><p '
                 'key={v.category+v.title}><strong>{v.title}</strong>: {v.before} → {v.after}</p>):<p>No '
                 'status differences.</p>}</>}</section>}</>}</section></div>}<footer>Original AI-assisted '
                 'portfolio. Synthetic data only. Not affiliated with ISOCODELABS. No real release, '
                 'deployment or compliance guarantee. Demo workspaces expire after seven '
                 'days.</footer></main></>}\n'
                 "createRoot(document.getElementById('root')!).render(<App/>);\n",
 'web/style.css': '@import '
                  "url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');\n"
                  ":root{font-family:'DM "
                  "Sans',sans-serif;color:#20333f;background:#f4f6f8;font-synthesis:none}*{box-sizing:border-box}body{margin:0}button,input,select{font:inherit}button,a,input,select{outline-offset:4px}button{cursor:pointer;border:0;background:#255fd1;color:#fff;border-radius:6px;padding:12px "
                  '16px;font-size:12px;font-weight:700}button:hover{background:#194ba9}button:disabled{opacity:.5;cursor:not-allowed}header{background:#fff;border-bottom:1px '
                  'solid #dce4ea;padding:22px max(28px,calc((100vw - '
                  '1180px)/2));display:flex;align-items:center;gap:24px}.brand{font-family:Manrope,sans-serif;font-size:23px;color:#20333f;text-decoration:none;white-space:nowrap}.brand:first-letter{color:#255fd1}header>span{font-size:12px;color:#768590}.demo{margin-left:auto;font-size:9px;letter-spacing:1.3px;font-weight:700;color:#657d91;border:1px '
                  'solid #dae3eb;padding:7px 10px;border-radius:4px}main{max-width:1180px;margin:0 '
                  'auto;padding:42px 28px '
                  '20px}.intro{display:flex;justify-content:space-between;gap:32px;margin:10px 0 '
                  '38px;align-items:center}.eyebrow{font-size:10px;letter-spacing:1.8px;color:#6a8297;font-weight:700;margin:0 '
                  '0 '
                  '12px}h1{font-family:Manrope,sans-serif;letter-spacing:-1.5px;font-size:40px;font-weight:800;margin:0 '
                  '0 14px}.intro '
                  'p:not(.eyebrow){font-size:13px;color:#768590;margin:0}.stamp{font-size:11px;line-height:1.9;border-left:2px '
                  'solid #abc3ed;padding:10px 0 10px 20px;color:#7990a2}.stamp '
                  'strong{font-weight:500;color:#3c5367}.welcome,.empty{background:#fff;padding:50px;border:1px '
                  'solid '
                  '#e0e6ec;border-radius:10px}.number{font-size:11px;color:#255fd1;font-weight:700;letter-spacing:1px}.welcome '
                  'h2,.empty h2{font-family:Manrope;font-size:25px;letter-spacing:-.7px}.welcome p,.empty '
                  'p{font-size:13px;line-height:1.9;color:#718393}.welcome '
                  'button{margin-top:18px}.layout{display:grid;grid-template-columns:250px '
                  'minmax(0,1fr);gap:24px}aside{background:#eaf0f7;border:1px solid '
                  '#dde5ee;border-radius:10px;padding:22px '
                  '18px;align-self:start}.section-title{display:flex;align-items:center;justify-content:space-between}.section-title '
                  'h2{font-size:14px;margin:0 0 '
                  '20px}.section-title>span{font-size:11px;color:#718393;margin-bottom:20px}label{font-size:10px;color:#728495;display:block;font-weight:500}input,select{width:100%;border:1px '
                  'solid '
                  '#d5dfe8;background:#fff;border-radius:5px;padding:10px;color:#233b50;margin-top:7px;font-size:12px}aside '
                  'form button{margin:10px 0 20px;width:100%}aside nav{display:grid;gap:8px}aside nav '
                  'button{background:transparent;text-align:left;border:1px solid '
                  'transparent;padding:12px;color:#466076}aside nav '
                  'button.selected{background:#fff;border-color:#cbd8e7;box-shadow:0 2px 4px #1e3e6710}aside '
                  'nav strong{display:block;font-size:12px;overflow-wrap:anywhere}aside nav '
                  'small{display:block;margin-top:7px;font-size:10px;color:#7d8e9b;font-weight:400}.aside-note{font-size:10px;color:#8293a3;line-height:1.9;padding-top:20px;border-top:1px '
                  'solid #d9e2ed;margin-top:26px}.workbench{background:#fff;border:1px solid '
                  '#dde5ec;border-radius:10px;padding:28px;min-width:0}.candidate-head{display:flex;justify-content:space-between;gap:18px;align-items:center}.candidate-head '
                  'h2{font-family:Manrope;font-size:25px;letter-spacing:-.7px;margin:0;overflow-wrap:anywhere}.candidate-head '
                  '.eyebrow{font-size:9px;margin-bottom:10px}.badge{font-size:10px;border-radius:4px;padding:8px '
                  '10px;white-space:nowrap}.pending{color:#a27624;background:#fbf2df}.ready{color:#28755b;background:#e3f3eb}.metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:28px '
                  '0 32px;padding:22px 0;border-block:1px solid #e8edf1}.metrics '
                  'strong{font-family:Manrope;font-size:26px;display:block}.metrics '
                  'small{font-size:12px;color:#96a4af}.metrics '
                  'span{display:block;font-size:10px;color:#7a8f9f;margin-top:5px}.toolbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}.toolbar '
                  'h3,h3{font-size:13px}.toolbar label{display:flex;gap:10px;align-items:center}.toolbar '
                  'select{width:auto;margin:0;padding:7px}.checks{display:grid;gap:12px}.check{border:1px '
                  'solid '
                  '#e0e7ee;border-radius:7px;padding:17px;background:#fcfdfe}.category{font-size:8px;font-weight:700;text-transform:uppercase;letter-spacing:1.1px;color:#8597a5}.check '
                  'h4{font-size:13px;margin:8px '
                  '0}.check>div:first-child{position:relative;padding-right:65px}.state{position:absolute;right:0;top:14px;font-size:9px;padding:5px '
                  '8px;border-radius:3px;background:#edf1f5;color:#768d9f}.state.pass{color:#297358;background:#e6f3ec}.state.fail{color:#ad4f48;background:#fceae7}.check-fields{display:grid;grid-template-columns:95px '
                  'minmax(0,1fr) auto;gap:12px;align-items:end;margin-top:15px}.check input,.check '
                  'select{padding:9px;font-size:11px}.save-check{font-size:10px;background:#edf2f9;color:#456782;border:1px '
                  'solid '
                  '#d5e1ed;padding:10px}.freeze{display:flex;align-items:center;gap:24px;background:#f0f5fd;border:1px '
                  'solid #d9e4f6;padding:20px;margin-top:25px;border-radius:7px}.freeze '
                  'h3{margin-top:0}.freeze '
                  'p{font-size:11px;color:#7489a0;line-height:1.8;margin-bottom:0}.freeze '
                  'button{font-size:10px;white-space:nowrap}.history,.snapshot,.compare{border-top:1px solid '
                  '#e7ecf0;margin-top:24px;padding-top:12px}.history '
                  'button{display:flex;justify-content:space-between;gap:18px;width:100%;background:#f7f9fb;color:#657b8c;font-weight:400;text-align:left;margin:8px '
                  '0;font-size:10px}.snapshot{font-size:11px;line-height:1.8}.snapshot '
                  'code{display:block;overflow-wrap:anywhere;color:#466f99;background:#f0f5fb;padding:12px;border-radius:4px}.compare{font-size:11px}.compare '
                  'select{max-width:300px}footer{font-size:10px;line-height:1.8;color:#8a9ba8;padding:28px 0 '
                  '5px}.error{padding:14px 18px;background:#fff1ee;border:1px solid '
                  '#f3c2b7;border-radius:6px;font-size:12px;color:#a94d3b;margin:0 0 24px}.error '
                  'button{background:transparent;color:#a94d3b;text-decoration:underline;padding:0 '
                  '8px}@media(max-width:850px){.layout{grid-template-columns:210px '
                  'minmax(0,1fr)}.workbench{padding:20px}.check-fields{grid-template-columns:90px '
                  'minmax(0,1fr)}.save-check{grid-column:1/-1}.freeze{display:block}.freeze '
                  'button{margin-top:16px}.stamp{display:none}}@media(max-width:620px){header{padding:20px;gap:12px;flex-wrap:wrap}.brand{font-size:22px}header>span{display:none}.demo{font-size:7px;padding:6px;letter-spacing:.6px}main{padding:28px '
                  '18px 10px}.intro{margin:2px 0 28px}h1{font-size:29px;letter-spacing:-1.1px}.intro '
                  'p:not(.eyebrow){font-size:12px;line-height:1.8}.eyebrow{font-size:8px;letter-spacing:1.2px}.layout{grid-template-columns:1fr;gap:16px}aside{padding:18px}aside '
                  'nav{grid-template-columns:repeat(2,minmax(0,1fr))}.aside-note{display:none}aside '
                  'form{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:end}aside form '
                  'label{grid-column:1/-1}aside input{margin:0}aside form '
                  'button{margin:0;font-size:10px;white-space:nowrap}aside '
                  'nav{margin-top:18px}.section-title '
                  'h2,.section-title>span{margin-bottom:14px}.workbench{padding:20px '
                  '16px}.candidate-head{display:block}.candidate-head '
                  'h2{font-size:23px}.badge{display:inline-block;margin-top:13px}.metrics{gap:12px;margin:20px '
                  '0;padding:20px 0}.metrics strong{font-size:23px}.metrics '
                  'span{font-size:9px;line-height:1.6}.toolbar h3{font-size:12px}.toolbar '
                  'label{font-size:9px}.toolbar select{font-size:10px;padding:6px}.check{padding:15px '
                  '12px}.check-fields{gap:10px;grid-template-columns:80px minmax(0,1fr)}.check '
                  'h4{font-size:12px;line-height:1.7}.check-fields label{font-size:9px}.check '
                  'input{min-width:0}.freeze{padding:18px}.welcome,.empty{padding:30px 20px}.welcome '
                  'h2,.empty h2{font-size:22px}.history button{flex-direction:column;gap:6px}}\n'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--extract',required=True);args=p.parse_args();root=pathlib.Path(args.extract)
 if root.exists() and any(root.iterdir()):raise SystemExit('Refusing nonempty destination')
 root.mkdir(parents=True,exist_ok=True)
 for name,content in FILES.items():
  path=root/name
  if root.resolve() not in path.resolve().parents:raise SystemExit('Invalid path')
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
 print('Extracted',len(FILES),'original source files')
