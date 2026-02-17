# OraDB Project - Current Status and Understanding

## 📅 Last Updated
February 17, 2026 — Session 4

## 🎯 Project Overview
**OraDB** - Complete Oracle Database 19c administration tool for Rocky Linux 8
- **Repository:** https://github.com/ELMRABET-Abdelali/oradb.git
- **Package Name:** oracledba v1.0.0
- **CLI Command:** `oradba`
- **Primary Language:** Python 3.9
- **Target Platform:** Rocky Linux 8
- **Latest Commit:** `b3770e1` — feat: single-command install with real-time output

## 🖥️ Deployment Information

### Active VM (NEW — Session 3)
- **IP Address:** 138.197.171.216
- **OS:** Rocky Linux 8.8 (7.5GB RAM, 2 CPUs, 156GB disk)
- **SSH Key:** `./otherfiles/id_rsa`
- **User:** root
- **Installation Path:** `/opt/oradb`
- **Oracle 19c:** FULLY INSTALLED AND RUNNING
- **GUI:** http://138.197.171.216:5000 (admin / admin123)

### Previous VM (Session 1-2, no longer active)
- **IP Address:** 178.128.10.67

### Local Development
- **Platform:** Windows
- **Working Directory:** `C:\Users\DELL\Documents\GitHub\oradb`
- **Git:** `C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe`

## ✅ What Has Been Accomplished (All Sessions Combined)

### Session 1-2: Initial Development
- ✅ CLI + Web GUI built and functional
- ✅ 26 CLI commands, 75 Flask routes, 14 HTML templates
- ✅ Deployed to old VM 178.128.10.67

### Session 3: Bug Fixes + New VM Deployment (Current)

#### Bug Fixes Applied
- ✅ **Critical:** Removed `shell=True` from 3 `subprocess.run()` calls in install.py (was silently breaking commands)
- ✅ **High:** Added shell metacharacter injection protection to `/api/terminal/execute` in web_server.py
- ✅ **Medium:** Changed 2 bare `except:` to `except AttributeError:` in web_server.py
- ✅ **Low:** Removed 7 dead module imports from cli.py
- ✅ **Low:** Removed duplicate `detector = SystemDetector()` in web_server.py

#### TP01 Script Fix
- ✅ Removed non-existent `libnsl2-devel` package from dnf install
- ✅ Added `--skip-broken` flag to dnf install for robustness
- ✅ Separated optional packages (compat-openssl10, python3-configshell) with fallback
- ✅ Made sysctl.conf idempotent (removes old Oracle params before re-adding)

#### TP03/DBCA Fix
- ✅ Added missing `-templateName General_Purpose.dbc` to dbca command
- ✅ Changed `-memoryPercentage 40` to `-totalMemory 2048` (works on low-RAM VMs)

#### Documentation
- ✅ DEPLOY_GUIDE.md completely rewritten as 13-section "Project Brain" document
- ✅ Audited all 30 doc files (guide/ + docs/), found 3 conflicting CLI syntaxes

#### Oracle 19c Installation on 138.197.171.216 — COMPLETED
- ✅ **TP01:** System readiness — users, groups, 50+ packages, kernel params, swap, /u01 structure
- ✅ **TP02:** Oracle binaries downloaded (3.06 GB in 46s), extracted (6.5 GB)
- ✅ **TP03 Software:** runInstaller succeeded, root scripts (orainstRoot.sh + root.sh) completed
- ✅ **TP03 Database:** DBCA created CDB GDCPROD + PDB GDCPDB, listener on port 1521
- ✅ **Verified:** `ora_pmon_GDCPROD` process running, database operational
- ✅ **GUI running:** http://138.197.171.216:5000 on 0.0.0.0:5000 (75 routes)

### Session 4: Single-Command Install + GUI Redesign (Current)

#### Core Architecture Change — `oradba install` = ONE command
- ✅ **install.py COMPLETE REWRITE (~684 lines):**
  - `_stream_cmd()` / `_stream_cmd_capture()` — every subprocess line streams to stdout + log simultaneously
  - No more `capture_output=True` anywhere — user sees EVERYTHING in real-time
  - `_step_header()` / `_step_result()` — visual step markers with per-step timing
  - `install_all(auto_yes=True)` — 4 steps: system → binaries → software → database
  - Success banner with connection info (SID, PDB, sqlplus commands)
  - Public `install_software()` method (was private `_install_oracle_software()`)
- ✅ **cli.py updated:**
  - `oradba install` (no subcommand) runs full install via `invoke_without_command=True`
  - `--yes` / `-y` flag skips confirmation prompt
  - `oradba install --yes` = fully automated, zero interaction
- ✅ **tp03-creation-instance.sh fixed for automation:**
  - Removed `read -p` interactive prompt (was blocking automated execution)
  - Auto-runs root scripts (orainstRoot.sh + root.sh) with error tolerance
  - Fixed DBCA params: `-gdbName` case fix, `-totalMemory 2048`, `-recoveryAreaDestination`
  - Idempotent `/etc/oratab` update with grep check

#### GUI Redesign — Installation Page
- ✅ **web_server.py API routes updated:**
  - Quick install now runs `oradba install --yes` (same code path as CLI)
  - Logs API parses "Step X/Y" markers from install.py output for progress tracking
  - Detects `oradba install` process (not old shell script)
- ✅ **installation.html completely rewritten:**
  - Visual stepper: 4 circles with connecting lines (gray → blue pulse → green check)
  - Prominent "One-Click Installation" button at top
  - 500px terminal panel showing real-time log content
  - Step progress updates from server-parsed markers
  - Individual steps collapsed under "debugging" section
  - Default SID changed from ORCL to GDCPROD

#### VM Rebuild — Fresh Test Pending
- 🔄 VM 138.197.171.216 rebuilt (fresh Rocky 8 image)
- ⏳ Testing `oradba install --yes` on clean VM (the real proof)

## 🏗️ Architecture Understanding

### CLI Commands Structure
The package provides a comprehensive CLI through `oracledba.cli`:

```bash
oradba install [command]
```

**Available commands:**
- `all` / `full` - Complete Oracle 19c installation (TP01+TP02+TP03)
- `system` - TP01: System preparation (users, groups, kernel params, packages)
- `binaries` - TP02: Download Oracle binaries (3GB from Google Drive)
- `software` - Install Oracle software (runInstaller)
- `database` - TP03: Create database (DBCA)
- `gui` - Start Web GUI server

### Training Practicals (TPs)
The system is organized around 15 training practicals:

1. **TP01** - System Readiness (users, groups, packages)
2. **TP02** - Binary Installation (download Oracle 19c)
3. **TP03** - Database Creation (DBCA)
4. **TP04** - Critical Files (multiplexing)
5. **TP05** - Storage Management (tablespaces)
6. **TP06** - Security (users, roles, profiles)
7. **TP07** - Flashback Technologies
8. **TP08** - RMAN Backup
9. **TP09** - Data Guard
10. **TP10** - Performance Tuning
11. **TP11** - Patching
12. **TP12** - Multitenant (CDB/PDB)
13. **TP13** - AI/ML Integration
14. **TP14** - Data Mobility
15. **TP15** - ASM/RAC Clustering

### Web GUI Structure
```
oracledba/
├── web_server.py          # Flask application with all routes
├── web/
│   ├── templates/         # HTML templates
│   └── static/           # CSS, JS, images
├── cli.py                # Click CLI commands
├── modules/              # Core functionality modules
│   ├── install.py        # Installation manager
│   ├── database.py       # Database operations
│   ├── rman.py          # RMAN operations
│   ├── dataguard.py     # Data Guard
│   ├── tuning.py        # Performance tuning
│   ├── security.py      # Security management
│   ├── flashback.py     # Flashback operations
│   ├── pdb.py           # PDB management
│   ├── asm.py           # ASM operations
│   └── rac.py           # RAC operations
└── utils/               # Utility functions
```

## 🔧 Current Running Services

### On Active VM (138.197.171.216)

1. **Oracle Database 19c**
   - CDB: GDCPROD (open, read-write)
   - PDB: GDCPDB
   - SID: GDCPROD
   - Listener: port 1521
   - Passwords: SYS=Oracle123, SYSTEM=Oracle123, PDB Admin=Oracle123
   - Status: ✅ Running (`ora_pmon_GDCPROD` confirmed)

2. **Web GUI**
   - URL: http://138.197.171.216:5000
   - Credentials: admin / admin123
   - Log: `/var/log/oradba-gui.log`
   - Status: ✅ Running (75 routes, 0.0.0.0:5000)

## 🐛 Known Issues Fixed This Session

### Issue 1: subprocess.run shell=True with list args (FIXED — Critical)
- 3 calls in install.py were passing list + `shell=True`, dropping all args
- Removed `shell=True` from listener_cmd, dbca_cmd, verify_cmd

### Issue 2: Terminal Command Injection (FIXED — High)
- `/api/terminal/execute` was only whitelist-checking but not rejecting shell metacharacters
- Added rejection of `;`, `&&`, `||`, `|`, `$()`, backticks, `>`, `<`

### Issue 3: DBCA Missing templateName (FIXED — Session 3)
- `dbca -silent -createDatabase` requires `-templateName` alongside `-gdbName`
- Added `-templateName General_Purpose.dbc`
- Changed `-memoryPercentage 40` → `-totalMemory 2048` for low-RAM VMs

### Issue 4: TP01 Package Failures (FIXED — Session 3)
- `libnsl2-devel` doesn't exist on Rocky 8
- Added `--skip-broken`, separated optional packages with fallback

## 🎯 Next Steps (For Next AI Session)

### Immediate Priority — Verify on Fresh VM
1. **Run `oradba install --yes` on rebuilt VM** — the single-command test
2. **Launch GUI with `oradba install gui`** — verify installation page works
3. **Fix any bugs found** during fresh VM testing

### Medium Priority
- Test all 15 TPs via GUI (TP04-TP15 configuration labs)
- Security hardening (change default passwords, HTTPS)
- Complete dashboard integration with real Oracle metrics
- `oradba install-all` for TP04-TP15 (post-install configuration labs)

## 📂 Important File Locations

### On Remote Server
- **Package:** `/opt/oradb/`
- **Config:** `~/.oracledba/`
- **GUI Config:** `~/.oracledba/gui_config.json`
- **GUI Users:** `~/.oracledba/gui_users.json`
- **Installation Log:** `/tmp/install.log`
- **GUI Log:** `/tmp/gui.log`
- **Oracle Installation Log:** `/tmp/oracle-install.log`
- **Oracle Home (planned):** `/u01/app/oracle/product/19.3.0/dbhome_1`
- **Oracle Base (planned):** `/u01/app/oracle`

### On Local Machine
- **SSH Key:** `C:\Users\DELL\Documents\GitHub\oradb\otherfiles\id_rsa`
- **Deployment Script:** `C:\Users\DELL\Documents\GitHub\oradb\deploy-to-rocky8.sh`

### Documentation
- **Main README:** `guide/README.md`
- **Installation Guide:** `guide/INSTALLATION_GUIDE.md`
- **Quick Start:** `guide/QUICKSTART.md`
- **Quick Install:** `guide/QUICK_INSTALL.md`
- **Deployment Guide:** `DEPLOY_GUIDE.md`

## 🔑 Important Commands

### Connect to Server
```bash
ssh -i otherfiles/id_rsa root@138.197.171.216
```

### CLI Commands (on VM)
```bash
oradba --version            # v1.0.0
oradba --help               # 26 commands
oradba precheck             # System check with Rich table
oradba install system       # TP01
oradba install binaries     # TP02
oradba install software     # runInstaller
oradba install database     # DBCA
oradba install gui          # Start web GUI
```

### Start GUI
```bash
ssh -i otherfiles/id_rsa root@138.197.171.216 "cd /opt/oradb && nohup python3.9 -m oracledba.web_server > /var/log/oradba-gui.log 2>&1 &"
```

### Update Code from GitHub
```bash
ssh -i otherfiles/id_rsa root@138.197.171.216 "cd /opt/oradb && git pull origin main"
```

### Git commit+push from Windows
```powershell
$git = "C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe"
& $git add -A
& $git commit -m "message"
& $git push origin main
```

### Create files on VM via SSH (avoiding escaping issues)
```powershell
# Use base64 to avoid PowerShell → SSH escaping problems
# Example: echo BASE64STRING | base64 -d > /path/to/file
```

## 💡 Technical Notes

### Oracle Installation on VM (Actual Timings)
- TP01 System Readiness: ~2 minutes (packages, kernel, swap, users)
- TP02 Binary Download: ~1 minute (3.06 GB at ~65MB/s from Google Drive)
- TP02 Extraction: ~2 minutes (6.5 GB extracted)
- TP03 runInstaller: ~3 minutes
- TP03 DBCA: ~10-12 minutes
- **Total: ~18 minutes** (NOT 30-45 as documentation says)

## 🔍 Architecture Quick Reference

### CLI (26 commands via Click)
```
oradba install [all|full|system|binaries|software|database|gui|check]
oradba [rman|dataguard|tuning|asm|rac|pdb|flashback|security|nfs|logs|monitor]
oradba [configure|maintenance|advanced]
oradba [start|stop|restart|status|sqlplus|exec|precheck|test|vm-init|download|genrsp|labs]
```

### Web GUI (75 routes, Flask 3.1.2)
- Auth: PBKDF2-SHA256, admin/admin123
- Templates: 14 HTML (dashboard, installation, rman, dataguard, etc.)
- API: `/api/installation/*`, `/api/terminal/*`, `/api/dashboard/*`

### Key Scripts (French-named, in oracledba/scripts/)
- `tp01-system-readiness.sh` (root) — System prep
- `tp02-installation-binaire.sh` (oracle) — Download + extract
- `tp03-creation-instance.sh` (oracle) — runInstaller + DBCA

### Oracle Defaults
- ORACLE_HOME: `/u01/app/oracle/product/19.3.0/dbhome_1`
- ORACLE_BASE: `/u01/app/oracle`
- SID: GDCPROD, PDB: GDCPDB
- Listener: port 1521
- Google Drive File ID: `1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns`

## 📞 Quick Reference

### Access URLs
- GUI: http://138.197.171.216:5000
- Dashboard: http://138.197.171.216:5000/dashboard
- Installation: http://138.197.171.216:5000/installation

### Key Files Modified This Session (Session 4)
- `oracledba/modules/install.py` — COMPLETE REWRITE: _stream_cmd(), step headers, install_all()
- `oracledba/cli.py` — invoke_without_command, --yes flag, public install_software()
- `oracledba/scripts/tp03-creation-instance.sh` — Removed read -p, auto root scripts, fixed DBCA
- `oracledba/web_server.py` — Quick install uses `oradba install --yes`, step parsing in logs API
- `oracledba/web/templates/installation.html` — Visual stepper, one-click button, terminal panel
- `PROJECT_STATUS.md` — This file (updated for session 4)
- `prompt-for-ai.md` — Updated for session 4 continuation

### Commits This Session (Session 4)
- `b3770e1` — feat: single-command install with real-time output (oradba install --yes)

### Common Issues
- **PowerShell → SSH escaping:** Use base64 encoding for complex commands
- **"Module not found"** → Run `pip3.9 install -e .` in `/opt/oradb`
- **GUI not accessible** → Check `ss -tlnp | grep 5000` and firewall
- **DBCA fails** → Ensure `-templateName General_Purpose.dbc` is present

## 🚨 Critical Notes for Next AI Session

1. **VM is 138.197.171.216** (not 178.128.10.67 — old VM)
2. **Oracle 19c is FULLY INSTALLED** — GDCPROD running, GDCPDB available
3. **SSH key:** `./otherfiles/id_rsa`
4. **Git executable on Windows:** `C:\Users\DELL\AppData\Local\GitHubDesktop\app-3.5.4\resources\app\git\cmd\git.exe`
5. **Read DEPLOY_GUIDE.md first** — It's the comprehensive project brain document
6. **Python 3.9** is required (not 3.8 or 3.10)
7. **oradba wrapper** at `/usr/local/bin/oradba` (runs `python3.9 -m oracledba.cli "$@"`)
8. **User's top priority for next session:** Fix the GUI installation page UX (step-by-step flow, no sync popups, visual progress like a normal installer)
9. **Workflow:** Edit locally on Windows → push to GitHub → pull on VM → test
10. **Flask runs on 0.0.0.0:5000** — accessible externally, no firewall blocking

---

**Status:** ✅ Single-command install ready (`oradba install --yes`) | ✅ GUI redesigned with stepper | 🔄 Testing on fresh VM
