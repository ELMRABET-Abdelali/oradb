# Prompt for AI — Paste This at the Start of Every New Session

> You are continuing work on the **OraDB** project. You have no memory of previous sessions. Read this entire prompt carefully — it IS your memory.

---

## Who You Are Working With
- **User:** Abdelali ELMRABET, Oracle DBA student
- **Platform:** Windows (VS Code + GitHub Copilot Chat)
- **Language:** User writes in English (sometimes with typos), code comments mix French/English
- **Style:** User prefers action over discussion. Don't ask permission — just do it. User says "do it" not "can you do it"

## The Project
**OraDB** (`oracledba` v1.0.0) — A Python tool that automates Oracle 19c Database installation and administration on Rocky Linux 8. It has:
- **CLI** (`oradba`) — 26 Click commands for install, backup, tuning, security, etc.
- **Web GUI** — Flask 3.1.2 on port 5000, 75 routes, 14 HTML templates, login: admin/admin123
- **15 Training Practicals (TPs)** — Bash scripts that automate each DBA task

**Repository:** https://github.com/ELMRABET-Abdelali/oradb.git
**Local path:** `C:\Users\DELL\Documents\GitHub\oradb`

## Current State (as of Feb 17, 2026)

### What's DONE and WORKING
- ✅ Oracle 19c FULLY INSTALLED on VM 138.197.171.216 (Rocky 8.8, 7.5GB RAM, 2 CPUs)
- ✅ Database running: CDB=GDCPROD, PDB=GDCPDB, Listener on port 1521
- ✅ CLI (`oradba`) works: `--version`, `--help`, `precheck`, `install system/binaries/software/database`
- ✅ GUI runs at http://138.197.171.216:5000 (75 routes load, login works)
- ✅ TP01 (system prep), TP02 (download 3GB binaries), TP03 (runInstaller + DBCA) all pass via CLI
- ✅ Multiple bug fixes applied (see below)
- ✅ DEPLOY_GUIDE.md is the comprehensive "project brain" document — READ IT for full details
- ✅ PROJECT_STATUS.md has current state summary

### What NEEDS WORK (User's Priority)
**#1 — Fix the GUI Installation Page UX.** The user said:
> "The sync element that shows each 2 or 3 seconds is not good — just put the synced element in the header. For installation I want to see the steps running like a normal logiciel would do — step one, then step two, etc. Not a log dump. Like a normal installer on my local PC."

Specifically:
1. Remove the sync/polling popup that appears every few seconds → move sync indicator to header only
2. Redesign `/installation` page to show step-by-step progress (Step 1 ✅ → Step 2 🔄 → Step 3 ⏳)
3. Show commands being executed in real-time, not just a log file viewer
4. No log file list/dropdown — just flowing installation progress

## Critical Technical Details

### SSH Access
```bash
ssh -i C:\Users\DELL\Documents\GitHub\oradb\otherfiles\id_rsa root@138.197.171.216
```

### Git (Windows — GitHub Desktop's bundled git)
```powershell
$git = "C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
& $git add -A
& $git commit -m "message"
& $git push origin main
```

### Development Workflow
1. Edit code locally on Windows in VS Code
2. Commit + push to GitHub
3. SSH to VM: `cd /opt/oradb && git pull origin main`
4. Test CLI: `oradba <command>`
5. Test GUI: restart Flask, check browser at http://138.197.171.216:5000
6. Find bugs → fix locally → repeat

### PowerShell → SSH Escaping Problem
When creating files on the VM via SSH, **use base64 encoding** to avoid escaping hell:
```powershell
# Encode in PowerShell, decode on VM
ssh ... "echo BASE64_STRING | base64 -d > /path/to/file"
```

### Key Files
| File | Purpose |
|------|---------|
| `oracledba/cli.py` | Click CLI entry point (26 commands) |
| `oracledba/web_server.py` | Flask app (~2220 lines, 75 routes) |
| `oracledba/modules/install.py` | InstallManager class (TP orchestration) |
| `oracledba/scripts/tp01-system-readiness.sh` | System prep (root) |
| `oracledba/scripts/tp02-installation-binaire.sh` | Download Oracle (oracle user) |
| `oracledba/scripts/tp03-creation-instance.sh` | runInstaller + DBCA (oracle user) |
| `oracledba/web/templates/installation.html` | Installation page template |
| `DEPLOY_GUIDE.md` | **READ THIS** — 13-section master reference |
| `PROJECT_STATUS.md` | Current state summary |

### Oracle Defaults
- ORACLE_HOME: `/u01/app/oracle/product/19.3.0/dbhome_1`
- ORACLE_BASE: `/u01/app/oracle`
- SID: `GDCPROD`, PDB: `GDCPDB`
- Passwords: SYS=`Oracle123`, SYSTEM=`Oracle123`
- Listener: port 1521
- Google Drive File ID (Oracle ZIP): `1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns`

### The oradba wrapper on VM
Located at `/usr/local/bin/oradba`, contains:
```bash
#!/bin/bash
python3.9 -m oracledba.cli "$@"
```

## Bugs Already Fixed (Don't Re-Fix These)
1. `subprocess.run(list, shell=True)` in install.py → removed `shell=True` (3 locations)
2. Terminal command injection in web_server.py → added metacharacter rejection
3. Bare `except:` → `except AttributeError:` in web_server.py (2 locations)
4. 7 dead imports removed from cli.py
5. Duplicate `SystemDetector()` removed from web_server.py
6. `libnsl2-devel` removed from tp01 (doesn't exist on Rocky 8), added `--skip-broken`
7. DBCA missing `-templateName General_Purpose.dbc` → added
8. DBCA `-memoryPercentage 40` → changed to `-totalMemory 2048`

## Documentation Warning
There are 30+ doc files in `guide/` and `docs/` folders. **Many are outdated and contradict each other.** Three different CLI syntaxes exist across them. **DEPLOY_GUIDE.md is the AUTHORITATIVE reference** — it was rewritten in session 3 as the single source of truth.

## How to Start
1. Read `DEPLOY_GUIDE.md` for full project context
2. Read `PROJECT_STATUS.md` for current state
3. Check what the user asks for
4. Start working — don't ask unnecessary questions

---

*Last updated: February 17, 2026 — End of Session 3*
*Latest commit: `0456101` — update PROJECT_STATUS with session 3 state*
