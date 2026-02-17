# Prompt for AI — Paste This at the Start of Every New Session

> You are continuing work on the **OraDB** project. You have no memory of previous sessions. Read this entire prompt carefully — it IS your memory.

---

## Who You Are Working With
- **User:** Abdelali ELMRABET, Oracle DBA student
- **Platform:** Windows (VS Code + GitHub Copilot Chat)
- **Style:** User prefers action over discussion. Don't ask permission — just do it.

## The Project
**OraDB** (`oracledba` v1.0.0) — A Python tool that automates Oracle 19c Database installation and administration on Rocky Linux 8. It has:
- **CLI** (`oradba`) — 26 Click commands for install, backup, tuning, security, etc.
- **Web GUI** — Flask 3.1.2 on port 5000, 99+ routes, 15 HTML templates, login: admin/admin123
- **15 Training Practicals (TPs)** — Bash scripts that automate each DBA task

**Repository:** https://github.com/ELMRABET-Abdelali/oradb.git
**Local path:** `C:\Users\DELL\Documents\GitHub\oradb`

---

## Credentials & Access — EVERYTHING YOU NEED

### VM (Rocky Linux 8.8)
| Item | Value |
|------|-------|
| IP | `138.197.171.216` |
| User | `root` |
| SSH Key | `C:\Users\DELL\Documents\GitHub\oradb\otherfiles\id_rsa` |
| SSH Command | `ssh -i otherfiles/id_rsa root@138.197.171.216` |

### Oracle Database 19c (Running on VM)
| Item | Value |
|------|-------|
| ORACLE_HOME | `/u01/app/oracle/product/19.3.0/dbhome_1` |
| ORACLE_BASE | `/u01/app/oracle` |
| SID | `GDCPROD` |
| CDB Name | `GDCPROD` (status: OPEN, ACTIVE) |
| PDB: PDB$SEED | CON_ID=2, READ ONLY |
| PDB: GDCPDB | CON_ID=3, MOUNTED |
| PDB: PRODDB | CON_ID=4, READ WRITE |
| PDB: TESTDPL | CON_ID=5, READ WRITE (created via YAML deploy) |
| SYS password | `Oracle123` |
| SYSTEM password | `Oracle123` |
| Listener port | `1521` |
| FRA path | `/u01/app/oracle/fast_recovery_area` (12,732 MB configured, 440 MB used) |
| ARCHIVELOG | Enabled |
| Flashback | Enabled |

### Web GUI
| Item | Value |
|------|-------|
| URL | `http://138.197.171.216:5000` |
| Login | `admin` / `admin123` |
| Dashboard | `http://138.197.171.216:5000/dashboard` |
| Process | Started with `oradba install gui --host 0.0.0.0` |
| Log | `/tmp/gui.log` |

### Git (Windows — GitHub Desktop's bundled git)
```powershell
$g = "C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
& $g add -A
& $g commit -m "message"
& $g push origin main
```

### Deploy Workflow (Windows → VM)
```powershell
# 1. Commit and push locally
$g = "C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
& $g add -A; & $g commit -m "description"; & $g push origin main

# 2. Install on VM (pip from GitHub — forces reinstall)
$key = "C:\Users\DELL\Documents\GitHub\oradb\otherfiles\id_rsa"
ssh -i $key -o StrictHostKeyChecking=no root@138.197.171.216 "pip3.9 install --force-reinstall --no-cache-dir git+https://github.com/ELMRABET-Abdelali/oradb.git 2>&1 | tail -5"

# 3. Restart GUI (upload restart-gui.sh, run it)
scp -i $key -o StrictHostKeyChecking=no restart-gui.sh root@138.197.171.216:/tmp/restart-gui.sh
ssh -i $key -o StrictHostKeyChecking=no root@138.197.171.216 "bash /tmp/restart-gui.sh"

# 4. Test APIs (upload test-api.sh, run it)
scp -i $key -o StrictHostKeyChecking=no test-api.sh root@138.197.171.216:/tmp/test-api.sh
ssh -i $key -o StrictHostKeyChecking=no root@138.197.171.216 "bash /tmp/test-api.sh"
```

**Important:** When running multi-command SSH one-liners from PowerShell, semicolons get escaped. Always upload `.sh` scripts via `scp` and run them with `bash /tmp/script.sh`.

### Helper Scripts (already in repo root)
- `restart-gui.sh` — Kills old GUI, starts new one, waits, checks HTTP 200
- `test-api.sh` — Logs in with cookies, hits all API endpoints, prints JSON responses
- `test-infra.sh` — Tests infrastructure API endpoints (nodes, storage, configs, template)

---

## Current State (End of Session 6 — Feb 17, 2026)

### What's DONE and FULLY WORKING

#### Oracle 19c on VM (Sessions 1-4)
- CDB=GDCPROD with 2 PDBs, listener on 1521
- Single-command install: `oradba install --yes` (4 steps, ~18 min total)
- CLI 26 commands working

#### Session 5: SQL Engine Fixed + All API Routes Returning Real Data
- **V$ Shell Expansion Bug:** `_run_sql()` and `run_sqlplus()` use `subprocess.Popen` + `stdin=PIPE`
- **v\\$ Escaping Bug:** All 10 instances fixed to plain `v$`
- **LINESIZE 1000 + TRIMSPOOL + TRIMOUT** — prevents column wrapping
- **COLUMN FORMAT** directives for NAME, MEMBER, COMPONENT columns
- **parse_sql_rows()** — robust: finds header by first `|` line, skips non-pipe lines

#### API Routes Tested and Working (Session 5)
| Route | Status | Sample Response |
|-------|--------|-----------------|
| `GET /api/databases/list` | ✅ | CDB GDCPROD (OPEN/ACTIVE) + 3 PDBs |
| `GET /api/storage/tablespaces` | ✅ | 5 tablespaces with size/usage (DATA, SYSAUX, SYSTEM, UNDOTBS1, USERS) |
| `GET /api/storage/controlfile/list` | ✅ | 3 control files (control01.ctl, control02.ctl, control03.ctl) |
| `GET /api/storage/redolog/list` | ✅ | 4 groups × 2 members = 8 redo logs (200 MB each) |
| `GET /api/protection/archivelog/status` | ✅ | `{log_mode: "ARCHIVELOG", flashback_on: "YES"}` |
| `GET /api/protection/fra/status` | ✅ | `{configured: true, name: "/u01/app/.../fast_recovery_area", size_mb: 12732, used_mb: 440}` |
| `GET /api/security/users` | ✅ | 35 users (SYS=OPEN, SYSTEM=OPEN, rest=LOCKED) |
| `GET /api/security/audit/view` | ✅ | `{records: []}` (works, empty because no recent audit) |
| `GET /dashboard` | ✅ | HTTP 200, SGA/PGA/tablespace metrics rendering |
| PDB actions | ✅ | `POST /api/databases/pdb/<name>/open\|close\|drop` |
| User actions | ✅ | `POST /api/security/user/<name>/lock\|unlock\|drop` |
| Storage actions | ✅ | Tablespace drop, redo log add |

#### Templates Redesigned (Session 5)
- **databases.html** — CDB info card + PDB table with Open/Close/Drop buttons
- **storage.html** — Tablespace table with progress bars (color-coded) + control file table + redo log table with Add/Multiplex
- **protection.html** — Proper JSON field checks (not string matching), status badges
- **security.html** — User table with status badges (green=OPEN, red=LOCKED) + Lock/Unlock/Drop

#### Session 6: Infrastructure Management Platform
New `/infrastructure` page making OraDB a real database platform:
- **Node Management** — Auto-detects local node (hostname, public IP, Oracle status). Add remote VMs via SSH credentials stored in `~/.oracledba/ssh-keys/`
- **Storage Pools** — Scans configured paths for datafiles, disk usage bars, expandable tablespace lists with "+N more" UI
- **NFS Management** — Add NFS servers, mount remote shares, manage pool lifecycle
- **YAML Provisioning** — Dark-themed YAML editor. Save/load/delete configs. 5-step deployment: PDB → tablespaces → users → protection → verify
- **17 new API routes** under `/api/infrastructure/` (nodes, storage, configs, deploy, template)
- **New files:** `infrastructure.html` (~500 lines), `examples/db-config-production.yml`, `examples/db-config-dev.yml`
- **Data storage:** `~/.oracledba/nodes.json` (node registry), `~/.oracledba/db-configs/*.yml` (saved configs), `~/.oracledba/ssh-keys/*.pem` (SSH keys)
- **Deployed & verified:** PDB TESTDPL created via YAML deploy, 5 tablespaces detected, local node auto-detected

### Latest Commits
```
f5e80e5 (HEAD) fix: storage pool tablespace listing - use 2-column query for pipe parsing
b59cefe fix: infinite recursion in _save_nodes_data
16c8d06 feat: infrastructure management system - nodes, storage pools, NFS, YAML provisioning
6c2b5f9 fix: LINESIZE 1000 + COLUMN FORMAT + robust parse_sql_rows + show all users
ebbd232 v6 — stdin PIPE for sqlplus, structured JSON APIs, proper UI tables
```

---

## WHAT NEEDS TO BE BUILT — Session 7 Goals

### 1. Database Detail Page (`/databases/<pdb_name>`)
Each PDB gets a detail page showing everything attached to it:
- **Status:** open mode, con_id, creation date
- **Tablespaces:** which tablespaces belong to this PDB, their sizes, usage progress bars
- **Users:** users in this PDB, their roles, privileges, lock status
- **Protection:** archivelog, FRA, flashback status for this PDB

### 2. Multi-Node Operations
- Test "Add Node" flow with a real remote VM
- Run SQL on remote nodes via SSH tunnel
- Show cluster-wide status on Infrastructure page

### 3. Terminal → SQL Console (phpMyAdmin Style)
Replace the raw terminal page with a structured SQL workspace:
- **Top panel:** SQL input `<textarea>` with Run button
- **Bottom panel:** Results as HTML table (not raw text)
- **Sidebar:** Pre-built queries (monitoring, storage, security, performance, logs)
- **Export:** download results as CSV
- **History:** recently executed queries with re-run button

### 4. RMAN Backup + Restore
- Configure retention policy, run backup now, view backup sets, test restore
- Flashback demo: create restore point → make change → flashback → verify recovery

### 5. Logs Management & Dashboard Refresh
- View/download/delete Oracle alert log, listener log, GUI logs
- Dashboard: background AJAX fetch, refresh toggle

---

## Key Technical Patterns

### How SQL Queries Work
```python
# Standalone function — used by most API routes
result = run_sqlplus(sql)          # Returns raw sqlplus stdout
rows = parse_sql_rows(result)      # Parses pipe-delimited → list of dicts

# Class method — used by dashboard metrics (SystemDetector)
output = self._run_sql(sql)
rows = self._parse_sql_rows(output)
```

Both use `subprocess.Popen` + `stdin=PIPE`. SQL auto-prefixed with:
```sql
SET PAGESIZE 1000
SET LINESIZE 1000
SET FEEDBACK OFF
SET HEADING ON
SET COLSEP '|'
SET TRIMSPOOL ON
SET TRIMOUT ON
```
For long columns, add `COL "COLNAME" FORMAT A100` before SELECT.

### To Query a Specific PDB
Add `ALTER SESSION SET CONTAINER = pdb_name;` before the SELECT in the SQL string. Consider adding `pdb` parameter to `run_sqlplus()`.

### Template Pattern (Session 5 Standard)
1. API route returns `jsonify({'success': True, 'data': [...]})` 
2. Template JavaScript calls `fetch('/api/...')` 
3. Parse JSON, build HTML table rows dynamically
4. Action buttons call POST endpoints, then refresh data

### File Structure
```
oracledba/
├── web_server.py              # Flask app (~3300 lines, 99+ routes)
├── cli.py                     # Click CLI (26 commands)
├── modules/install.py         # InstallManager (rewritten session 4)
├── scripts/tp01..tp15*.sh     # Bash scripts for each TP
├── web/templates/             # 14 HTML templates
│   ├── base.html              # Layout: Bootstrap 5 + sidebar nav (Infrastructure link added)
│   ├── dashboard.html         # Server-side Jinja2 (591 lines)
│   ├── databases.html         # PDB management (redesigned session 5)
│   ├── storage.html           # Tablespaces + controlfiles + redo logs (session 5)
│   ├── protection.html        # ARCHIVELOG/FRA/Flashback/RMAN (session 5)
│   ├── security.html          # Users + audit (session 5)
│   ├── infrastructure.html    # Infrastructure dashboard: nodes + storage + YAML (session 6)
│   ├── installation.html      # One-click installer wizard (session 4)
│   ├── terminal.html          # Raw SQL terminal
│   ├── sample.html            # Sample schema operations
│   ├── labs.html              # TP execution runner
│   ├── cluster.html           # RAC/ASM (placeholder)
│   └── login.html, profile.html, change_password.html
└── utils/
```

---

## Bugs Already Fixed (Sessions 1-5) — Don't Re-Fix
1. `subprocess.run(list, shell=True)` → removed `shell=True` (install.py)
2. Terminal command injection → metacharacter rejection
3. Bare `except:` → `except AttributeError:` (2 locations)
4. Dead imports removed from cli.py
5. Duplicate `SystemDetector()` removed
6. `libnsl2-devel` removed from tp01, `--skip-broken` added
7. DBCA: `-templateName`, `-gdbName` case, `-totalMemory 2048`, `-recoveryAreaDestination`
8. tp03: removed `read -p` blocking prompt
9. install.py: `capture_output=True` → `_stream_cmd()` live streaming
10. CLI `oradba install` → `invoke_without_command=True`
11. `echo "$sql" | sqlplus` → `subprocess.Popen` + `stdin=PIPE`
12. `v\\$` → `v$` (10 instances)
13. `change_password` None guard
14. `parse_sql_rows` header detection (first `|` line, not line 0)
15. `LINESIZE 300` → `1000` + `TRIMSPOOL ON` + `TRIMOUT ON`
16. `COL FORMAT` for NAME/MEMBER/COMPONENT columns
17. Users query: removed `WHERE oracle_maintained = 'N'` filter
18. Infinite recursion: `_save_nodes_data()` → `_ensure_infra_files()` → `_save_nodes_data()` loop — removed circular call
19. Empty tablespace list: single-column `SELECT` has no pipe separator for `parse_sql_rows()` — changed to 2-column query

---

*Last updated: February 17, 2026 — End of Session 6*
*Latest commit: `f5e80e5`*
