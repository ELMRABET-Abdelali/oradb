# OraDB Project — Current Status

## Last Updated: February 17, 2026 — End of Session 5

## Project Overview
| Item | Value |
|------|-------|
| Name | OraDB (`oracledba` v1.0.0) |
| Purpose | Oracle 19c installation + administration tool |
| Repository | https://github.com/ELMRABET-Abdelali/oradb.git |
| CLI Command | `oradba` |
| Language | Python 3.9 |
| Target OS | Rocky Linux 8 |
| Latest Commit | `6c2b5f9` |

## VM & Oracle Status

### VM: 138.197.171.216 (Rocky Linux 8.8)
- 7.5 GB RAM, 2 CPUs, 156 GB disk
- SSH: `ssh -i otherfiles/id_rsa root@138.197.171.216`
- Oracle 19c: **FULLY INSTALLED AND RUNNING**

### Oracle Database
| Component | Status |
|-----------|--------|
| CDB: GDCPROD | OPEN, ACTIVE |
| PDB: PDB$SEED | READ ONLY (con_id=2) |
| PDB: GDCPDB | MOUNTED (con_id=3) |
| PDB: PRODDB | READ WRITE (con_id=4) |
| Listener | Running on port 1521 |
| ARCHIVELOG | Enabled |
| Flashback | Enabled |
| FRA | `/u01/app/oracle/fast_recovery_area` — 12,732 MB (440 MB used) |
| SYS/SYSTEM password | `Oracle123` |

### Web GUI
| Item | Value |
|------|-------|
| URL | http://138.197.171.216:5000 |
| Credentials | admin / admin123 |
| Routes | 82 |
| Templates | 14 |
| Status | Running |

## Session History

### Sessions 1-3: Foundation
- Built CLI (26 commands) + Web GUI (Flask, 14 templates)
- Oracle 19c installed on VM: system prep → download 3GB binaries → runInstaller → DBCA
- Multiple bug fixes (shell=True, command injection, DBCA params, etc.)

### Session 4: Single-Command Install
- `install.py` completely rewritten with live-streaming `_stream_cmd()`
- `oradba install --yes` = fully automated 4-step install (~18 min)
- GUI installation page: visual stepper with one-click button
- tp03 fixed for automation (removed `read -p`, auto root scripts)

### Session 5: SQL Engine + API + UI Overhaul (Current)

#### Root Cause Fixes
| Bug | What Was Wrong | How Fixed |
|-----|---------------|-----------|
| V$ Shell Expansion | `echo "$sql" \| sqlplus` made Bash treat `$INSTANCE` as empty variable | `subprocess.Popen` + `stdin=PIPE` — SQL never touches shell |
| v\\$ Python Escape | SQL strings had `v\\$` which wrote literal `\` to Oracle | Changed all 10 instances to `v$` |
| Column Wrapping | Oracle's 513-char default width wrapped output across lines | `LINESIZE 1000` + `TRIMSPOOL ON` + `COLUMN FORMAT A100` |
| Bad Parse Logic | `parse_sql_rows` assumed first line = headers | Rewritten: find first line with `\|` separator |
| Empty Users List | `WHERE oracle_maintained = 'N'` returned 0 rows | Removed filter, shows all 35 users |

#### New/Fixed API Routes
All routes now return structured JSON (tested on VM):
- **Databases:** CDB info + PDB list + PDB open/close/drop actions
- **Storage:** Tablespaces (with size/usage), control files (3), redo logs (4 groups × 2 members), drop/add actions
- **Protection:** ARCHIVELOG status, FRA status (name/size/used), flashback status
- **Security:** 35 users with status badges, lock/unlock/drop + audit view
- **Dashboard:** HTTP 200, SGA/PGA/tablespace metrics working

#### Redesigned Templates
- `databases.html` — CDB card + PDB table with action buttons
- `storage.html` — Tablespace progress bars + controlfile table + redo log table
- `protection.html` — JSON-based status detection (not string matching)
- `security.html` — User table with color-coded status, action buttons

## What Needs to Be Built Next (Session 6)

### Priority 1: Database Detail Page + Creation Wizard
- Each PDB gets a detail page (`/databases/<name>`) showing: tablespaces, users, roles, backups, datafiles, protection status
- PDB creation = full wizard: name → tablespace → admin user → protection → RMAN schedule

### Priority 2: Dashboard Non-Blocking Refresh
- Current: reloads every 3s, blocks interaction
- Fix: background AJAX fetch updating DOM in-place, refresh toggle

### Priority 3: Terminal → SQL Console (phpMyAdmin Style)
- Top: SQL input area, Bottom: HTML table results
- Sidebar: pre-built queries (monitoring, storage, security, performance, logs)
- Export as CSV, query history

### Priority 4: Protection Actions + Demo
- RMAN: configure, run backup, view sets, test restore
- Flashback: create restore point, demo recovery
- Full test: create table → insert → break → recover → verify

### Priority 5: Logs Management
- View/download/delete Oracle alert log, listener log, GUI logs
- Filter by date/severity

---

## Quick Reference

### Commit & Deploy Workflow
```powershell
# Git
$g = "C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
& $g add -A; & $g commit -m "msg"; & $g push origin main

# Deploy
$key = "C:\Users\DELL\Documents\GitHub\oradb\otherfiles\id_rsa"
ssh -i $key root@138.197.171.216 "pip3.9 install --force-reinstall --no-cache-dir git+https://github.com/ELMRABET-Abdelali/oradb.git 2>&1 | tail -5"

# Restart + Test (use scp + bash for multi-command)
scp -i $key restart-gui.sh root@138.197.171.216:/tmp/
ssh -i $key root@138.197.171.216 "bash /tmp/restart-gui.sh"
```

### SQL Pattern in Code
```python
result = run_sqlplus('COL "NAME" FORMAT A80\nSELECT name AS "NAME" FROM v$tablespace;')
rows = parse_sql_rows(result)  # → [{'NAME': 'SYSTEM'}, {'NAME': 'SYSAUX'}, ...]
```

### Key Files
| File | Lines | Purpose |
|------|-------|---------|
| `oracledba/web_server.py` | ~2620 | Flask app, 82 routes, all API logic |
| `oracledba/cli.py` | ~300 | Click CLI entry point |
| `oracledba/modules/install.py` | ~684 | InstallManager with live streaming |
| `oracledba/web/templates/*.html` | 14 files | Bootstrap 5 templates |
| `restart-gui.sh` | helper | Kill + restart GUI on VM |
| `test-api.sh` | helper | Login + test all API endpoints |
| `prompt-for-ai.md` | | Full context for new AI sessions |

---

*For complete credentials and technical context, see `prompt-for-ai.md`*
