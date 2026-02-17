# OraDB - Master Guide (Project Brain)

> **Purpose:** This file is the single source of truth for the entire project. It serves as a
> "memory document" so that any new conversation with an AI assistant can pick up exactly where
> the previous one left off. Read this file FIRST when starting a new session.

---

## 1. WHO, WHAT, WHY

**Author:** Abdelali ELMRABET (GitHub: `ELMRABET-Abdelali`)
**Repo:** `github.com/ELMRABET-Abdelali/oradb`
**Local workspace:** `c:\Users\DELL\Documents\GitHub\oradb\`
**License:** MIT

**What is OraDB?**

A Python CLI + Web GUI package that automates Oracle 19c DBA administration on Rocky Linux 8.
It replaces 15 TP (Travaux Pratiques) lab chapters with a single `oradba` command and a
browser-based dashboard. Think pgAdmin/phpMyAdmin for Oracle, or Proxmox GUI for VM management.

**The story in one sentence:**

> "Manual TP pages -> bash scripts -> CLI package -> Web GUI -> Multi-VM cluster management"

**The final goal:**

A fresh Rocky Linux 8 VM → `git clone` → `pip install` → `oradba install all` (30 min,
fully automated) → `oradba install gui` → open browser → see dashboard, manage databases,
run backups, monitor performance, run any TP from the GUI. Then repeat on more VMs,
link them, manage them all from one interface.

---

## 2. DEVELOPMENT WORKFLOW

This is the exact cycle we follow. Every session should continue this loop:

```
  LOCAL (Windows, VS Code)          GITHUB                    ROCKY 8 VM
  ========================          ======                    ============
  1. Edit Python/HTML/shell   -->   2. git push          -->  3. git pull
  4. Fix bugs found           <--   (GitHub Desktop)     <--  5. Test CLI + GUI
                                                              6. Document bugs
  Repeat until stable.
```

**Local machine:** Windows, VS Code, Python 3.13, no Oracle (can only syntax-check)
**Deploy target:** Rocky Linux 8 VM with 4GB+ RAM, internet access
**SSH key:** `./otherfiles/id_rsa` (included in repo, chmod 600 before use)

**How to push from Windows (no git CLI):**
- Use GitHub Desktop app: `Start-Process "C:\Users\DELL\AppData\Local\GitHubDesktop\GitHubDesktop.exe"`
- Or VS Code Source Control panel (Ctrl+Shift+G)

---

## 3. THE BIG PICTURE - Every TP Mapped

Each of the 15 TP chapters became a CLI command and a GUI page:

| TP | What It Does | CLI Command | GUI Page |
|----|-------------|-------------|----------|
| TP01 | System prep (users, groups, kernel params, RPMs) | `oradba install system` | Installation |
| TP02 | Download Oracle binaries (3GB zip) | `oradba install binaries` | Installation |
| TP03 | Install Oracle software + create database | `oradba install software` / `oradba install database` | Installation |
| TP04 | Multiplex controlfiles & redo logs | `oradba configure multiplexing` | Protection |
| TP05 | Tablespaces, datafiles, OMF | `oradba configure storage` | Storage |
| TP06 | Users, roles, privileges, TDE | `oradba configure users` | Security |
| TP07 | Flashback database & table | `oradba configure flashback` | Protection |
| TP08 | RMAN backup & recovery | `oradba configure backup` | Protection |
| TP09 | Data Guard (primary/standby) | `oradba configure dataguard` | Protection |
| TP10 | AWR, ADDM, SQL tuning | `oradba maintenance tune` | Dashboard |
| TP11 | OPatch, datapatch | `oradba maintenance patch` | Dashboard |
| TP12 | CDB/PDB management | `oradba advanced multitenant` | Databases |
| TP13 | AI/ML in-database features | `oradba advanced ai-ml` | Dashboard |
| TP14 | Data Pump export/import | `oradba advanced data-mobility` | Dashboard |
| TP15 | ASM + RAC cluster | `oradba advanced asm-rac` | Cluster |

**One command does it all:**
```bash
oradba install all   # Runs TP01 + TP02 + TP03 sequentially (30-45 min)
```

---

## 4. TECHNICAL ARCHITECTURE

### Package Structure

```
oradb/
  oracledba/                    # Main Python package (v1.0.0)
    __init__.py                 # Version: 1.0.0
    cli.py                      # Click CLI entry point (~1090 lines)
    web_server.py               # Flask GUI server (~2220 lines)
    setup_wizard.py             # Interactive wizard
    modules/                    # Business logic managers
      __init__.py
      install.py                # InstallManager - core installer (~545 lines)
      rman.py                   # RMANManager - backup/recovery
      dataguard.py              # DataGuardManager
      tuning.py                 # TuningManager - AWR/ADDM
      asm.py                    # ASMManager
      rac.py                    # RACManager
      pdb.py                    # PDBManager
      precheck.py               # PreInstallChecker - 50+ checks
      testing.py                # TestRunner - 11 test categories
      downloader.py             # OracleDownloader
      response_files.py         # Response file generator
    scripts/                    # 32 bash scripts (TP01-TP15 variants)
    configs/                    # YAML config templates
    utils/                      # logger.py, validators.py, config_loader.py
    web/
      templates/                # 14 Jinja2 HTML templates
        base.html               # Layout with sidebar navigation
        login.html              # Auth page (admin/admin123)
        dashboard.html          # System overview + Oracle metrics
        installation.html       # Auto-detect + install wizard
        databases.html          # CDB/PDB management
        storage.html            # Tablespaces & datafiles
        protection.html         # RMAN, flashback, Data Guard
        security.html           # Users, roles, audit
        cluster.html            # ASM, RAC, Grid
        labs.html               # Run any TP script
        terminal.html           # Execute DBA commands
        sample.html             # Sample schema management
        profile.html            # User profile
        change_password.html    # Password change
      static/                   # CSS, JS (minimal)
  pyproject.toml                # Build config + [gui] optional deps
  deploy-to-rocky8.sh           # Automated deploy script
  requirements.txt              # CLI deps: click, rich, pyyaml, psutil, requests
  requirements-gui.txt          # GUI deps: flask, flask-cors, jinja2
  tests/                        # pytest test suite
  guide/                        # Internal docs (17 files, .gitignored)
  docs/                         # Public docs (13 files, on GitHub)
```

### Entry Points

| What | How | Details |
|------|-----|---------|
| CLI | `oradba` | Entry point in pyproject.toml: `oracledba.cli:main` |
| GUI | `oradba install gui` | Flask app on port 5000, auth required |
| Direct Python | `python3.9 -m oracledba.cli` | Fallback if entry point not created |
| GUI import | `from oracledba.web_server import app` | For programmatic use |

### Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `InstallManager` | modules/install.py | Runs TP scripts, creates DB, installs Oracle |
| `SystemDetector` | web_server.py | Detects Oracle env, running processes, metrics |
| `GUIConfig` | web_server.py | Manages ~/.oracledba/ config + user database |
| `PreInstallChecker` | modules/precheck.py | 50+ pre-installation checks |

### Oracle Defaults

| Setting | Default Value |
|---------|--------------|
| ORACLE_HOME | `/u01/app/oracle/product/19.3.0/dbhome_1` |
| ORACLE_BASE | `/u01/app/oracle` |
| ORACLE_SID | `GDCPROD` |
| PDB name | `GDCPDB` |
| SYS password | `Oracle123` |
| Listener port | 1521 |
| GUI port | 5000 |
| GUI login | admin / admin123 |

---

## 5. COMPLETE CLI REFERENCE (Current/Authoritative)

**IMPORTANT:** Many doc files in guide/ and docs/ use OUTDATED syntax.
The ONLY correct syntax is the one below (post-refactoring):

```bash
# === INSTALLATION ===
oradba install all          # Full automated install (TP01+TP02+TP03)
oradba install system       # TP01: System readiness
oradba install binaries     # TP02: Download Oracle zip
oradba install software     # TP03a: runInstaller
oradba install database     # TP03b: DBCA + listener
oradba install gui          # Launch Flask web GUI
oradba install check        # Show what's installed/running

# === CONFIGURATION (TP04-TP09) ===
oradba configure multiplexing   # TP04
oradba configure storage        # TP05
oradba configure users          # TP06
oradba configure flashback      # TP07
oradba configure backup         # TP08
oradba configure dataguard      # TP09
oradba configure all            # All of the above

# === MAINTENANCE (TP10-TP11) ===
oradba maintenance tune         # TP10
oradba maintenance patch        # TP11

# === ADVANCED (TP12-TP15) ===
oradba advanced multitenant     # TP12
oradba advanced ai-ml           # TP13
oradba advanced data-mobility   # TP14
oradba advanced asm-rac         # TP15

# === STANDALONE TOOLS ===
oradba rman backup|restore|validate|list|configure|crosscheck|setup
oradba dataguard status|setup|switchover|failover
oradba tuning analyze|awr|addm|sql-trace
oradba pdb list|create|open|close|clone|unplug
oradba flashback enable|disable|status|restore
oradba security audit|users|roles|profiles|tde
oradba asm setup|status|diskgroup|disk|balance
oradba rac setup|status|node|service|relocate

# === DATABASE ===
oradba start|stop|restart|status
oradba sqlplus
oradba monitor

# === UTILITIES ===
oradba precheck [--fix]
oradba logs view|tail|search
oradba download oracle
oradba genrsp software|dbca|netca
oradba nfs setup|export|mount|status

# === META ===
oradba --version
oradba --help
oradba labs                     # List all available TP scripts
```

**WARNING - Outdated syntax found in old docs:**
- `oradba install --full` (OLD, wrong) -> `oradba install all` (CORRECT)
- `oradba tp run 01` (OLD, removed) -> `oradba labs` (CORRECT)
- `oradba rman --backup full` (OLD) -> `oradba rman backup` (CORRECT)
- `oradba install --system` (OLD) -> `oradba install system` (CORRECT)

---

## 6. WEB GUI - 75 ROUTES

The Flask app registers 75 routes. Key pages:

| Page | URL | Purpose |
|------|-----|---------|
| Login | `/login` | PBKDF2-SHA256 auth |
| Dashboard | `/` | System overview + Oracle metrics |
| Installation | `/installation` | Auto-detect + install wizard (10 checks) |
| Databases | `/databases` | CDB/PDB management |
| Storage | `/storage` | Tablespaces & datafiles |
| Protection | `/protection` | RMAN, flashback, Data Guard |
| Security | `/security` | Users, roles, audit, TDE |
| Cluster | `/cluster` | ASM, RAC, NFS, Grid |
| Labs | `/labs` | Run TP scripts, view logs |
| Terminal | `/terminal` | sqlplus, lsnrctl, rman, basic shell |
| Sample | `/sample` | Sample schema tools |
| Profile | `/profile` | User profile settings |

**Key API endpoints:**
- `POST /api/terminal/execute` - Run whitelisted DBA commands
- `GET /api/installation/detect` - 10-point detection (OS, users, kernel, RPMs, dirs, zipfile, ORACLE_HOME, listener, DB, PDB)
- `GET /api/oracle-metrics` - Live Oracle metrics
- `POST /api/labs/run` - Execute TP scripts
- `POST /api/rman/backup` - RMAN backup
- `POST /api/databases/create` - Create PDB

**Security:** Terminal commands are whitelisted (no arbitrary shell). Shell metacharacters
(`;`, `&&`, `||`, `|`, `$()`, backticks, `>`, `<`) are blocked except in pre-approved exact commands.

---

## 7. DEPLOY TO A NEW VM

### Current Deploy Targets

| VM | IP | Status | Purpose |
|----|-----|--------|---------|
| VM1 (old) | 178.128.10.67 | Previous testing | First test server |
| VM2 (new) | 138.197.171.216 | Current target | Fresh Rocky 8 deploy |

### Step-by-Step Manual Deploy (Recommended)

```bash
# 1. Connect from Windows (PowerShell or Git Bash)
ssh -i ./otherfiles/id_rsa root@138.197.171.216

# 2. Install prerequisites
dnf install -y git python39 python39-pip python39-devel gcc make
python3.9 -m pip install --upgrade pip

# 3. Clone the repo
cd /opt
git clone https://github.com/ELMRABET-Abdelali/oradb.git
cd oradb

# 4. Install the package (editable mode + GUI deps)
python3.9 -m pip install -e ".[gui]"

# 5. Create oradba command in PATH
cat > /usr/local/bin/oradba << 'SCRIPT'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
SCRIPT
chmod +x /usr/local/bin/oradba

# 6. Verify
oradba --version            # Should show 1.0.0
oradba --help               # Should show all command groups
oradba install check        # Should show detection results

# 7. Install Oracle (30-45 min)
oradba install all

# 8. Launch GUI
oradba install gui
# Open http://138.197.171.216:5000
# Login: admin / admin123
```

### Automated Deploy Script

```bash
# Fresh install
bash deploy-to-rocky8.sh

# Update existing install (after git push from local)
bash deploy-to-rocky8.sh update
```

The script handles: SSH connection test, prerequisites, git clone/pull,
pip install, symlink creation, verification.

### Update Cycle (After Fixing Bugs Locally)

```bash
# On the VM:
cd /opt/oradb
git pull
python3.9 -m pip install -e ".[gui]"
oradba install check
```

---

## 8. KNOWN ISSUES & DECISIONS

### Bugs Fixed (This Session)

| Bug | File | Fix Applied |
|-----|------|-------------|
| `subprocess.run(list, shell=True)` silently broke DB creation | install.py L344,374,386 | Removed `shell=True` (use `shell=False` with list args) |
| Terminal command injection via `;` and `&&` | web_server.py L886 | Added metacharacter rejection before whitelist check |
| Bare `except:` masking errors | web_server.py L1452,L1557 | Changed to `except AttributeError:` |
| `os.geteuid()` crash on Windows | install.py L77 | Wrapped in `try/except AttributeError` |
| Log dir `/var/log/oracledba` fails on non-root | install.py | Fallback to `/tmp/oracledba-logs` |
| Package-data missing HTML templates | pyproject.toml | Added `web/templates/*.html` and `web/static/**/*` |
| Dead module imports shadowed by Click groups | cli.py L19-25 | Removed 7 unused imports |
| Duplicate `detector = SystemDetector()` | web_server.py L195 | Removed duplicate instantiation |

### Documentation Inconsistencies

The `guide/` (17 files) and `docs/` (13 files) folders contain OUTDATED and CONTRADICTORY
information. Key issues:

1. **3 different CLI syntaxes** across files: `--flag` style (oldest), `subcommand` style (middle), current `group subcommand` style
2. **`tp run` commands** referenced in old docs were REMOVED in CLI refactoring
3. **GitHub repo URL** is sometimes `oracledba` (wrong) vs `oradb` (correct)
4. **GUI status** - some old docs say "not implemented" but GUI now works (75 routes, 14 templates)
5. **Test files** referenced in guide/TESTING.md don't exist yet
6. **Language** - ~7 files French, ~10 English, no standard

**The DEPLOY_GUIDE.md (this file) is the AUTHORITATIVE reference.** When in doubt, trust this file over anything in `guide/` or `docs/`.

### Architectural Decisions

- **Editable install** (`pip install -e .`): Code executes from `/opt/oradb/` directly. Changes via `git pull` take effect immediately without reinstalling. But `pip install -e ".[gui]"` must be re-run if dependencies change in pyproject.toml.
- **Flask relative template path**: `template_folder='web/templates'` resolves relative to the package's `__init__.py` directory. Works correctly in both editable and regular installs.
- **Script execution**: `InstallManager._run_script()` uses `Path(__file__).parent.parent / "scripts"` to find scripts. Works because scripts are inside the package directory.
- **Auth**: PBKDF2-SHA256 with 100k iterations. Default admin/admin123 with `must_change_password` flag.

---

## 9. INSTALLATION TIMELINE

| Step | Duration | What Happens |
|------|----------|-------------|
| Package deploy | 2-5 min | git clone + pip install |
| System prep (TP01) | 5 min | `groupadd oinstall/dba/oper`, `useradd oracle`, kernel params, RPM packages |
| Binary download (TP02) | 10-15 min | Download 3GB Oracle zip (Google Drive ID: `1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns`) |
| Software install (TP03a) | 10-15 min | `runInstaller -silent` with response file |
| Database creation (TP03b) | 10-15 min | `dbca -silent -createDatabase`, listener config |
| **Total** | **30-45 min** | Full Oracle 19c EE with CDB (GDCPROD) + PDB (GDCPDB) |

---

## 10. ROADMAP

### Phase 1: Single VM -- CURRENT
- [x] CLI package with all 15 TP functionalities
- [x] Web GUI: 14 pages, 75 routes, auth, terminal
- [x] Auto-detection of installed components (10 checks)
- [x] Terminal with whitelisted DBA commands
- [x] One-command automated install (`oradba install all`)
- [x] Deploy script for Rocky 8 (fresh + update modes)
- [x] Bug fixes: subprocess, injection, Windows compat
- [ ] Full end-to-end test on fresh Rocky 8 VM
- [ ] Fix all bugs found during VM testing
- [ ] Ensure all GUI pages show live Oracle data

### Phase 2: Multi-VM & Cluster
- [ ] NFS server setup (`oradba nfs setup --server <ip>`)
- [ ] Node linking (`oradba cluster add-node --ip <ip>`)
- [ ] Manage multiple VMs from one GUI
- [ ] Data Guard between primary and standby VMs

### Phase 3: Packaging & Distribution
- [ ] Publish to PyPI (`pip install oracledba`)
- [ ] Docker container for management tool
- [ ] Ansible playbooks for fleet deployment

### Phase 4: Production Ready
- [ ] HTTPS/TLS for GUI
- [ ] Role-based access control
- [ ] Monitoring alerts & notifications
- [ ] Automated backup scheduling via GUI
- [ ] Performance dashboards with real-time charts

---

## 11. TROUBLESHOOTING

### SSH Connection

```bash
# Fix key permissions (required on Linux/Mac)
chmod 600 ./otherfiles/id_rsa

# Connect
ssh -i ./otherfiles/id_rsa root@138.197.171.216

# If "Host key verification failed"
ssh-keygen -R 138.197.171.216
```

### oradba Command Not Found

```bash
# Fallback: call Python directly
python3.9 -m oracledba.cli --version

# Recreate the symlink
cat > /usr/local/bin/oradba << 'SCRIPT'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
SCRIPT
chmod +x /usr/local/bin/oradba
```

### GUI Won't Start

```bash
# Check Flask is installed
python3.9 -c "import flask; print(flask.__version__)"

# Install GUI deps
cd /opt/oradb
python3.9 -m pip install -e ".[gui]"

# Test import
python3.9 -c "from oracledba.web_server import app; print('OK,', len(list(app.url_map.iter_rules())), 'routes')"
```

### Package Import Errors

```bash
cd /opt/oradb
python3.9 -m pip install -e ".[gui]" --force-reinstall
```

### Oracle Environment Not Set

```bash
# Add to oracle user's .bash_profile:
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export ORACLE_BASE=/u01/app/oracle
export PATH=$ORACLE_HOME/bin:$PATH
```

---

## 12. QUICK REFERENCE FOR NEW AI SESSIONS

When starting a new conversation, tell the AI:

> "Read DEPLOY_GUIDE.md first -- it's the project brain. Then continue where we left off."

**Key facts the AI needs:**
- Package: `oracledba` v1.0.0, entry point `oradba`
- Framework: Click (CLI) + Flask (GUI)
- Target: Rocky Linux 8, Oracle 19c EE
- Repo: `github.com/ELMRABET-Abdelali/oradb`
- Local: `c:\Users\DELL\Documents\GitHub\oradb\`
- Deploy VM: 138.197.171.216 (SSH key: `./otherfiles/id_rsa`)
- Workflow: edit locally -> GitHub Desktop push -> git pull on VM -> test -> fix -> repeat
- All Python compiles OK, 75 routes, 14 templates load, CLI imports clean
- `guide/` and `docs/` contain OUTDATED info. Trust THIS file only.
- The `--flag` style commands in old docs are WRONG. Current syntax uses `group subcommand`.

---

## 13. FILES MODIFIED IN RECENT SESSIONS

| File | What Changed |
|------|-------------|
| `DEPLOY_GUIDE.md` | Complete rewrite as project brain document |
| `deploy-to-rocky8.sh` | Added update mode, fixed pip install method, cleaned emoji |
| `oracledba/cli.py` | Added `install check` command, removed dead imports, added `import subprocess` |
| `oracledba/web_server.py` | Terminal expansion (DBA commands), `/api/installation/detect` endpoint, command injection fix, duplicate detector removal, `except AttributeError` fixes |
| `oracledba/web/templates/terminal.html` | DBA quick commands (3-column layout) |
| `oracledba/web/templates/installation.html` | Detection summary panel with 10 auto-checks |
| `oracledba/modules/install.py` | Fixed `os.geteuid()` Windows crash, log_dir fallback, removed `shell=True` from subprocess calls |
| `pyproject.toml` | Added `[gui]` optional deps, fixed package-data for HTML templates |
