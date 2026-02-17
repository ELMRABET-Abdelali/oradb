# OraDB - Deployment & Roadmap Guide

## What is OraDB?

OraDB is a complete Oracle 19c DBA automation package. It replaces manual TP lab work with a single CLI tool (`oradba`) and a Web GUI, similar to how:

- **pgAdmin** simplifies PostgreSQL management
- **phpMyAdmin** simplifies MySQL management
- **Proxmox GUI** replaces manual VM management
- **XenOrchestra** replaces XenServer CLI

### Evolution

```
Manual TPs (15 chapters)
    → Bash scripts (tp01-tp15 .sh files)
        → CLI package (oradba command)
            → Web GUI (Flask on port 5000)
                → Multi-VM cluster management (future)
```

Each TP became a **functionality** accessible via CLI commands and GUI buttons:

| TP | Functionality | CLI Command | GUI Page |
|----|--------------|-------------|----------|
| TP01 | System Readiness | `oradba install system` | Installation → Step 2 |
| TP02 | Binary Installation | `oradba install binaries` | Installation → Step 3 |
| TP03 | Database Creation | `oradba install database` | Installation → Step 4 |
| TP04 | Multiplexing | `oradba configure multiplexing` | Protection |
| TP05 | Storage Management | `oradba configure storage` | Storage |
| TP06 | Security & Access | `oradba configure users` | Security |
| TP07 | Flashback | `oradba configure flashback` | Protection |
| TP08 | RMAN Backup | `oradba configure backup` | Protection |
| TP09 | Data Guard | `oradba configure dataguard` | Protection |
| TP10 | Performance Tuning | `oradba maintenance tune` | Dashboard |
| TP11 | Patching | `oradba maintenance patch` | Dashboard |
| TP12 | Multitenant (CDB/PDB) | `oradba advanced multitenant` | Databases |
| TP13 | AI/ML Features | `oradba advanced ai-ml` | Dashboard |
| TP14 | Data Mobility | `oradba advanced data-mobility` | Dashboard |
| TP15 | ASM & RAC | `oradba advanced asm-rac` | Cluster |

---

## Final Goal

On a **fresh Rocky Linux 8** VM:

```bash
# 1. Clone and install
git clone https://github.com/ELMRABET-Abdelali/oradb.git /opt/oradb
cd /opt/oradb
python3.9 -m pip install -e ".[gui]"

# 2. One command installs everything
oradba install all
# → Watch all steps: system prep, download, software install, DB creation
# → 30-45 minutes, fully automated

# 3. Launch the GUI
oradba install gui
# → Open http://<server-ip>:5000
# → Login: admin / admin123
# → See dashboard, manage databases, run backups, monitor performance

# 4. Verify everything
oradba install check
# → Shows what's installed, what's running, what needs attention
```

Then repeat on additional VMs and link them:

```bash
# On VM2: Same install
oradba install all

# Link with NFS for shared storage
oradba nfs setup --server <nfs-ip> --export /u01/shared

# Add to cluster
oradba cluster add-node --ip <vm2-ip>

# Manage everything from one place
oradba install gui --port 8080
```

---

## Development Workflow

```
┌──────────────────────────────────────────────────────┐
│                  LOCAL (Windows)                      │
│                                                      │
│  1. Edit code in VS Code (c:\...\oradb\)            │
│  2. Test syntax: python -c "import oracledba.cli"   │
│  3. Git commit + push to GitHub                      │
└──────────────┬───────────────────────────────────────┘
               │ git push
               ▼
┌──────────────────────────────────────────────────────┐
│                  GITHUB                               │
│  github.com/ELMRABET-Abdelali/oradb                  │
└──────────────┬───────────────────────────────────────┘
               │ git pull (or deploy script)
               ▼
┌──────────────────────────────────────────────────────┐
│              ROCKY 8 VM (178.128.10.67)              │
│                                                      │
│  4. Pull latest:                                     │
│     cd /opt/oradb && git pull                        │
│  5. Reinstall: python3.9 -m pip install -e ".[gui]" │
│  6. Test CLI: oradba install check                   │
│  7. Test GUI: oradba install gui                     │
│  8. Visual test in browser                           │
└──────────────┬───────────────────────────────────────┘
               │ bugs found
               ▼
┌──────────────────────────────────────────────────────┐
│  9. Document bugs                                    │
│  10. Go back to step 1 (fix locally)                │
│  11. Repeat until stable                             │
└──────────────────────────────────────────────────────┘
```

---

## Deployment

### Prerequisites

- SSH key at `./otherfiles/id_rsa`
- Target: Rocky Linux 8 with internet access
- Server IP: 178.128.10.67 (or update in script)

### Option 1: Automated Deploy Script

From your Windows machine (Git Bash or WSL):

```bash
bash deploy-to-rocky8.sh
```

This script:
1. Tests SSH connection
2. Installs git, python3.9, pip on the server
3. Clones the repo to `/opt/oradb`
4. Installs the package with `pip install -e ".[gui]"`
5. Creates the `oradba` command in PATH
6. Verifies installation

### Option 2: Manual Deploy

```bash
# Connect to server
ssh -i ./otherfiles/id_rsa root@178.128.10.67

# Install prerequisites
dnf install -y git python39 python39-pip python39-devel gcc make
python3.9 -m pip install --upgrade pip

# Clone and install
cd /opt
git clone https://github.com/ELMRABET-Abdelali/oradb.git
cd oradb
python3.9 -m pip install -e ".[gui]"

# Create oradba shortcut
cat > /usr/local/bin/oradba << 'EOF'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
EOF
chmod +x /usr/local/bin/oradba

# Verify
oradba --version
oradba --help
```

### Option 3: Update Existing Installation

```bash
ssh -i ./otherfiles/id_rsa root@178.128.10.67
cd /opt/oradb
git pull
python3.9 -m pip install -e ".[gui]"
oradba --version
```

---

## After Deployment

### Install Oracle 19c

**One-command (recommended):**
```bash
oradba install all
```

**Step-by-step:**
```bash
oradba install system      # TP01: System prep (users, groups, kernel)
oradba install binaries    # TP02: Download Oracle binaries (3GB)
oradba install software    # TP03a: Install Oracle software
oradba install database    # TP03b: Create database with DBCA
```

**Check what's installed:**
```bash
oradba install check
```

### Start the Web GUI

```bash
oradba install gui                 # Default: 0.0.0.0:5000
oradba install gui --port 8080     # Custom port
oradba install gui --debug         # Debug mode
```

Access: `http://<server-ip>:5000`
Login: `admin` / `admin123`

### GUI Pages

| Page | Purpose |
|------|---------|
| Dashboard | System overview, Oracle metrics, quick status |
| Installation | Auto-detect what's installed, run install steps |
| Databases | Manage CDB/PDB, start/stop instances |
| Storage | Tablespaces, datafiles, OMF management |
| Protection | RMAN backup, flashback, Data Guard |
| Security | Users, roles, privileges, profiles |
| Cluster | ASM, RAC, Grid Infrastructure |
| Labs | Run any TP script directly |
| Terminal | Execute DBA commands (sqlplus, lsnrctl, rman...) |
| Sample DB | Create/verify/remove sample schemas |

### CLI Commands Reference

```bash
# Installation
oradba install all|system|binaries|software|database|gui|check

# Configuration (TP04-09)
oradba configure multiplexing|storage|users|flashback|backup|dataguard|all

# Maintenance (TP10-11)
oradba maintenance tune|patch

# Advanced (TP12-14)
oradba advanced multitenant|ai-ml|data-mobility|asm-rac

# Database Management
oradba start|stop|restart|status
oradba sqlplus
oradba monitor

# Specific Tools
oradba rman backup|restore|validate|list|configure|crosscheck
oradba dataguard status|setup|switchover|failover
oradba pdb list|create|open|close|clone|unplug
oradba flashback enable|disable|status|restore
oradba security audit|users|roles|profiles|tde
oradba asm diskgroup|disk|status|balance
oradba rac node|service|status|relocate

# Utilities
oradba precheck
oradba logs view|tail|search
oradba download oracle
oradba genrsp software|dbca|netca
```

---

## Installation Timeline

| Step | Duration | What happens |
|------|----------|-------------|
| Package deploy | 2-5 min | git clone + pip install |
| System prep (TP01) | 5 min | Users, groups, kernel params, packages |
| Binary download (TP02) | 10-15 min | 3GB Oracle zip from Google Drive |
| Software install (TP03a) | 10-15 min | runInstaller in silent mode |
| Database creation (TP03b) | 10-15 min | DBCA creates CDB + PDB |
| **Total** | **30-45 min** | Full Oracle 19c with database |

---

## Roadmap

### Phase 1: Single VM (Current)
- [x] CLI package with all TP functionalities
- [x] Web GUI with dashboard, installation, management pages
- [x] Auto-detection of installed components
- [x] Terminal with DBA commands (sqlplus, rman, lsnrctl...)
- [x] One-click automated installation
- [x] Deploy script for Rocky 8
- [ ] Full end-to-end test on fresh Rocky 8 VM
- [ ] Fix all bugs found during testing
- [ ] Ensure all GUI pages work with live Oracle data

### Phase 2: Multi-VM
- [ ] NFS server setup via CLI (`oradba nfs setup`)
- [ ] Node linking (`oradba cluster add-node --ip <ip>`)
- [ ] Manage multiple VMs from one GUI
- [ ] Data Guard between primary and standby VMs

### Phase 3: Packaging & Distribution
- [ ] Build as a proper Python package (`pip install oracledba`)
- [ ] Docker container for the management tool
- [ ] Ansible playbooks for fleet deployment
- [ ] High availability database cluster managed via single interface

### Phase 4: Production Ready
- [ ] HTTPS/TLS for GUI
- [ ] Role-based access control in GUI
- [ ] Monitoring alerts and notifications
- [ ] Automated backup scheduling via GUI
- [ ] Performance dashboards with real-time charts

---

## Troubleshooting

### SSH Connection Issues

```bash
ssh -i ./otherfiles/id_rsa root@178.128.10.67
# If permission denied:
chmod 600 ./otherfiles/id_rsa
```

### oradba Command Not Found

```bash
# Direct Python module call
python3.9 -m oracledba.cli --version

# Recreate symlink
cat > /usr/local/bin/oradba << 'EOF'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
EOF
chmod +x /usr/local/bin/oradba
```

### GUI Won't Start

```bash
# Check Flask is installed
python3.9 -m pip install flask flask-cors

# Or install all GUI deps
cd /opt/oradb
python3.9 -m pip install -e ".[gui]"

# Test import
python3.9 -c "from oracledba.web_server import start_gui_server; print('OK')"
```

### Package Import Errors

```bash
cd /opt/oradb
python3.9 -m pip install -e ".[gui]" --force-reinstall
```

---

## Project Structure

```
oradb/
├── oracledba/              # Main Python package
│   ├── cli.py              # CLI entry point (oradba command)
│   ├── web_server.py       # Flask web GUI server
│   ├── setup_wizard.py     # Interactive setup wizard
│   ├── modules/            # Business logic (install, rman, dg...)
│   ├── scripts/            # 32 TP shell scripts
│   ├── configs/            # YAML configuration templates
│   ├── utils/              # Helper utilities
│   └── web/templates/      # 14 HTML templates for GUI
├── deploy-to-rocky8.sh     # Automated deployment script
├── pyproject.toml          # Package build configuration
├── requirements.txt        # CLI dependencies
├── requirements-gui.txt    # GUI dependencies
├── guide/                  # Documentation
└── tests/                  # Test suite
```

---

## Notes

- **Python**: 3.9 on Rocky 8 (`python3.9`)
- **Install dir**: `/opt/oradb` (editable install)
- **Oracle Home**: `/u01/app/oracle/product/19.3.0/dbhome_1`
- **Oracle SID**: `GDCPROD` (default), PDB: `GDCPDB`
- **GUI port**: 5000 (default), configurable with `--port`
- **GUI auth**: admin / admin123 (change after first login)
