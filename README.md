# OracleDBA — Complete Oracle 19c Installation & Administration

Single-command Oracle 19c installation and management tool for Rocky Linux 8/9.

## Quick Install (3 commands)

```bash
# 1. Install the package
pip3 install --upgrade pip && pip3 install git+https://github.com/ELMRABET-Abdelali/oradb.git

# 2. Install Oracle 19c (fully automated)
oradba install --yes

# 3. Launch Web GUI
oradba install gui
```

Then open **http://your-server-ip:5000** → click **Quick Install** → watch it run.

## What It Does

| Step | Description | Time |
|------|-------------|------|
| 1. System Readiness | Users, groups, kernel params, 50+ packages | ~3 min |
| 2. Download Binaries | 3 GB from Google Drive → extract to ORACLE_HOME | ~5 min |
| 3. Install Software | `runInstaller` (silent) + root scripts | ~8 min |
| 4. Create Database | Listener + DBCA → CDB + PDB | ~5 min |

Total: **~20 minutes** on a fresh Rocky Linux 8 VM.

## CLI Reference

```
oradba --help                  # All commands
oradba install --yes           # Full automated install
oradba install gui             # Web GUI on port 5000
oradba install system          # Just system prep
oradba install binaries        # Just download
oradba install software        # Just runInstaller
oradba install database        # Just DBCA
oradba install check           # Check what's installed
oradba status                  # Database status
oradba start / stop / restart  # Manage database
oradba rman backup full        # RMAN backup
```

## Requirements

- Rocky Linux 8.x or 9.x (or CentOS 8)
- 4 GB RAM minimum (8 GB recommended)
- 50 GB free disk space
- Python 3.8+
- Root access

## License

MIT
