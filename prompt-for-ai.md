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

## Current State (as of Feb 17, 2026 — End of Session 4)

### What's DONE and WORKING
- ✅ Oracle 19c was FULLY INSTALLED on VM 138.197.171.216 (Rocky 8.8) in Session 3
- ✅ **Single-command install: `oradba install --yes`** — runs all 4 steps automatically with real-time terminal output
- ✅ **install.py completely rewritten** — `_stream_cmd()` streams every line to stdout+log, step headers with timing, success banner
- ✅ **CLI updated** — `oradba install` (no subcommand) runs full install via `invoke_without_command=True`, `--yes` skips confirmation
- ✅ **tp03 fixed for automation** — removed `read -p` blocking prompt, auto root scripts, fixed DBCA params
- ✅ **GUI installation page redesigned** — visual stepper (4 circles), one-click button, real-time terminal panel
- ✅ **GUI quick install uses same code path as CLI** — `oradba install --yes` (not separate shell scripts)
- ✅ CLI (`oradba`) works: `--version`, `--help`, `precheck`, `install system/binaries/software/database`
- ✅ TP01 (system prep), TP02 (download 3GB binaries), TP03 (runInstaller + DBCA) all pass via CLI
- ✅ Multiple bug fixes applied across sessions 1-4

### What NEEDS WORK (User's Priority)
**#1 — Test on fresh VM.** The VM was rebuilt with a fresh image. Need to:
1. Clone repo, install package (`pip3.9 install -e .`)
2. Run `oradba install --yes` and verify it completes all 4 steps
3. Launch GUI with `oradba install gui` and verify installation page works
4. Fix any bugs found during testing

**#2 — Post-install labs.** Once install works:
- `oradba install-all` for TP04-TP15 configuration labs
- Test labs via GUI

## Critical Technical Details

### SSH Access
```bash
ssh -i C:\Users\DELL\Documents\GitHub\oradb\otherfiles\id_rsa root@138.197.171.216
```
**Note:** VM was rebuilt — first connection will need to accept new host key.

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

### VM Setup (Fresh Image — Do This First)
```bash
# 1. Install Python 3.9 + git
dnf install -y python39 python39-pip git

# 2. Clone repo
git clone https://github.com/ELMRABET-Abdelali/oradb.git /opt/oradb

# 3. Install package
cd /opt/oradb
pip3.9 install -e .

# 4. Create oradba wrapper
cat > /usr/local/bin/oradba << 'EOF'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
EOF
chmod +x /usr/local/bin/oradba

# 5. Run full install
oradba install --yes

# 6. Start GUI
oradba install gui --host 0.0.0.0
```

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
| `oracledba/modules/install.py` | InstallManager class — REWRITTEN session 4 |
| `oracledba/scripts/tp01-system-readiness.sh` | System prep (root) |
| `oracledba/scripts/tp02-installation-binaire.sh` | Download Oracle (oracle user) |
| `oracledba/scripts/tp03-creation-instance.sh` | runInstaller + DBCA — FIXED session 4 |
| `oracledba/web/templates/installation.html` | Installation page — REDESIGNED session 4 |
| `DEPLOY_GUIDE.md` | 13-section master reference |
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
9. tp03 `read -p` interactive prompt → removed (was blocking automation)
10. tp03 DBCA `-gdbname` → `-gdbName` (case fix)
11. tp03 missing `-recoveryAreaDestination` → added
12. install.py `capture_output=True` everywhere → replaced with `_stream_cmd()` live streaming
13. CLI `oradba install` with no subcommand did nothing → now runs `install_all()` via `invoke_without_command=True`

## Session 4 Architecture Changes (Important)

### install.py Key Methods
```python
class InstallManager:
    _out(text)              # Write to stdout + log file simultaneously
    _stream_cmd(cmd)        # Popen + stream every line through _out()
    _stream_cmd_capture(cmd) # Same but also captures output for post-checking
    _step_header(n, total, title)  # "Step 2/4 — Download & Extract"
    _step_result(n, success, secs) # "✓ Step 2 complete (3m 45s)"
    
    install_all(auto_yes=False)  # Main entry: 4 steps with timing
    install_system()             # Just TP01
    install_binaries()           # Just TP02
    install_software()           # Just runInstaller + root scripts
    create_database()            # Just listener + DBCA
```

### GUI Quick Install Flow
1. User clicks "Start Installation" button
2. Frontend POST `/api/installation/quick`
3. Backend runs `nohup oradba install --yes > /tmp/oracle-install-all.log 2>&1 &`
4. Frontend polls `/api/installation/logs/quick` every 1s
5. Backend parses log for "Step X/Y" markers → returns `current_step`, `step_statuses`
6. Frontend updates stepper circles (gray → blue pulse → green check)

## Documentation Warning
There are 30+ doc files in `guide/` and `docs/` folders. **Many are outdated and contradict each other.** Three different CLI syntaxes exist across them. **DEPLOY_GUIDE.md is the AUTHORITATIVE reference.**

## How to Start
1. Read `PROJECT_STATUS.md` for current state
2. Read `DEPLOY_GUIDE.md` for full project context
3. Check what the user asks for
4. Start working — don't ask unnecessary questions

---

*Last updated: February 17, 2026 — End of Session 4*
*Latest commit: `b3770e1` — feat: single-command install with real-time output*
