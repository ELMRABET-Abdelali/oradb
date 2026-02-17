# 🚀 Rocky 8 Remote Deployment Guide

## Overview
This script automates the deployment of the oradb package to a Rocky 8 server (178.128.10.67) using SSH.

## Prerequisites
- SSH key file at `./otherfiles/id_rsa`
- SSH access to the target server
- Target server running Rocky 8 with internet connection

## Quick Start

### Run the Deployment Script

From your Windows machine (Git Bash or WSL):

```bash
bash deploy-to-rocky8.sh
```

## What the Script Does

1. ✅ Tests SSH connection to server
2. ✅ Installs prerequisites (git, python39, pip)
3. ✅ Clones repository from GitHub
4. ✅ Installs oradb package via pip
5. ✅ Installs GUI dependencies
6. ✅ Creates `oradba` command in PATH
7. ✅ Displays next steps and available commands

## After Deployment

### Connect to the Server

```bash
ssh -i ./otherfiles/id_rsa root@178.128.10.67
```

### Available Commands on Server

#### View Help
```bash
oradba --help
```

#### Install Oracle Database 19c

**Option 1: One-Command Full Installation (Recommended)**
```bash
oradba install all
```

**Option 2: Step-by-Step Installation**
```bash
# Step 1: Prepare system
oradba install system

# Step 2: Download Oracle binaries
oradba install binaries

# Step 3: Install Oracle software
oradba install software

# Step 4: Create database
oradba install database
```

#### Start Web GUI
```bash
# Start on default port (5000)
oradba install gui

# Start on custom port
oradba install gui --port 8080

# Start with debug mode
oradba install gui --debug
```

Access the GUI at: `http://178.128.10.67:5000`

#### Run System Precheck
```bash
oradba precheck
```

#### View All Installation Commands
```bash
oradba install --help
```

## Installation Timeline

- **Package deployment**: 2-5 minutes
- **Oracle installation (`oradba install all`)**: 30-45 minutes
  - System prep: 5 minutes
  - Binary download: 10-15 minutes (3GB)
  - Software install: 10-15 minutes
  - Database creation: 10-15 minutes

## Troubleshooting

### SSH Connection Issues

```bash
# Test connection manually
ssh -i ./otherfiles/id_rsa root@178.128.10.67

# Check key permissions
chmod 600 ./otherfiles/id_rsa
```

### If oradba Command Not Found

```bash
# Use Python module directly
python3.9 -m oracledba.cli --version

# Or recreate symlink
cat > /usr/local/bin/oradba << 'EOF'
#!/bin/bash
python3.9 -m oracledba.cli "$@"
EOF
chmod +x /usr/local/bin/oradba
```

### GUI Dependencies Not Installed

```bash
cd /opt/oradb
python3.9 -m pip install -r requirements-gui.txt
```

## Documentation on Server

After deployment, documentation is available at:
- `/opt/oradb/guide/INSTALLATION_GUIDE.md` - Full installation guide
- `/opt/oradb/guide/QUICKSTART.md` - Quick start guide
- `/opt/oradb/guide/QUICK_INSTALL.md` - Quick installation
- `/opt/oradb/README.md` - Main README

## Notes

- The script uses `dnf` (preferred) and falls back to `yum` if needed
- Installation directory: `/opt/oradb`
- Python version: 3.9
- Package installed in editable mode (`pip install -e .`)

## Support

For issues or questions:
1. Check `/opt/oradb/guide/` documentation on the server
2. Run `oradba --help` for command reference
3. Use `oradba precheck` to validate system readiness
