# OracleDBA CLI - Quick Start Guide

## 🚀 One-Button Oracle Installation

The `oracledba` CLI now provides a **one-button installation** that automates the complete Oracle 19c setup on Rocky Linux 8.

## Prerequisites

- Rocky Linux 8 or compatible (CentOS Stream 8, AlmaLinux 8)
- Minimum 8GB RAM, 20GB disk space
- Root access
- Internet connection (for downloading Oracle binaries - 3GB)

## Installation Methods

### Method 1: Complete One-Button Install (Recommended)

```bash
# Install everything in one command (TP01 + TP02 + TP03)
sudo oradba install full
```

This will:
1. ✅ Configure system (users, groups, kernel params, packages)
2. ✅ Download Oracle 19c binaries from Google Drive (3GB)
3. ✅ Install Oracle software (runInstaller)
4. ✅ Create GDCPROD database with DBCA
5. ✅ Configure listener

**Time:** ~30-45 minutes

### Method 2: Step-by-Step Install

```bash
# Step 1: System preparation (TP01)
sudo oradba install system

# Step 2: Download binaries (TP02)
sudo su - oracle
oradba install binaries

# Step 3: Install Oracle software
oradba install software

# Step 4: Create database (TP03)
oradba install database
```

### Method 3: Skip Specific Steps

```bash
# Skip system setup (if already done)
sudo oradba install full --skip-system

# Skip binary download (if already downloaded)
sudo oradba install full --skip-binaries

# Only install software and create DB
sudo oradba install full --skip-system --skip-binaries
```

## Training Practicals (TPs)

The CLI includes all 15 Oracle DBA training practicals:

### List Available TPs

```bash
oradba tp list
```

Output:
```
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ TP   ┃ Name               ┃ Description                    ┃ Category    ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ TP01 │ System Readiness   │ User, groups, packages...      │ Installation│
│ TP02 │ Binary Install     │ Download Oracle 19c            │ Installation│
│ TP03 │ Database Creation  │ Create with DBCA               │ Installation│
│ TP04 │ Critical Files     │ Multiplex control files        │ Configuration│
│ TP05 │ Storage Management │ Tablespaces, datafiles         │ Configuration│
│ TP06 │ Security           │ Users, roles, profiles         │ Security    │
│ TP07 │ Flashback          │ Flashback technologies         │ Protection  │
│ TP08 │ RMAN Backup        │ Backup and recovery            │ Protection  │
│ TP09 │ Data Guard         │ High availability              │ HA          │
│ TP10 │ Performance Tuning │ AWR, SQL tuning                │ Performance │
│ TP11 │ Patching           │ Apply patches                  │ Maintenance │
│ TP12 │ Multitenant        │ CDB/PDB management             │ Architecture│
│ TP13 │ AI/ML              │ Machine Learning               │ Advanced    │
│ TP14 │ Data Mobility      │ Data Pump, export/import       │ Advanced    │
│ TP15 │ ASM/RAC            │ Clustering concepts            │ Advanced    │
└──────┴────────────────────┴────────────────────────────────┴─────────────┘
```

### Run Individual TP

```bash
# Run TP04 - Critical Files Multiplexing
oradba tp run 04

# Run TP07 - Flashback Technologies
oradba tp run 07

# Show real-time output
oradba tp run 08 --show-output
```

### Run All TPs

```bash
# Run complete training suite (TP01-TP15)
oradba tp run all

# Start from specific TP
oradba tp run-from 04    # Start from TP04
```

## Database Management

### Check Status

```bash
oradba status
```

### Start/Stop Database

```bash
oradba start
oradba stop
oradba restart
```

### Connect to SQL*Plus

```bash
# Connect as SYSDBA
oradba sqlplus --sysdba

# Connect to PDB
oradba sqlplus --pdb GDCPDB
```

## RMAN Backup

```bash
# Configure RMAN
oradba rman setup --retention 7 --compression

# Perform backup
oradba rman backup --type full
oradba rman backup --type incremental
oradba rman backup --type archive

# List backups
oradba rman list
```

## Data Guard Setup

```bash
# On primary server
oradba dataguard setup-primary --standby-host 192.168.1.20

# On standby server
oradba dataguard setup-standby --primary-host 192.168.1.10

# Check status
oradba dataguard status
```

## Flashback Operations

```bash
# Enable flashback
oradba flashback enable

# Create restore point
oradba flashback create-restore-point --name BEFORE_UPDATE

# Flashback database
oradba flashback database --to-restore-point BEFORE_UPDATE

# Flashback table
oradba flashback table EMPLOYEES --to-timestamp "2026-02-17 10:00:00"
```

## Performance Tuning

```bash
# Run performance report
oradba tuning awr-report --hours 24

# SQL tuning advisor
oradba tuning sql-advisor --sql-id abcd1234

# Check tablespace usage
oradba monitor tablespaces

# Monitor sessions
oradba monitor sessions --active-only
```

## PDB Management

```bash
# Create PDB
oradba pdb create --name TESTPDB

# Open PDB
oradba pdb open --name TESTPDB

# Close PDB
oradba pdb close --name TESTPDB

# Drop PDB
oradba pdb drop --name TESTPDB
```

## Security Management

```bash
# Create user
oradba security user --create APP_USER

# Drop user
oradba security user --drop APP_USER

# List users
oradba security user --list
```

## Monitoring

### View Logs

```bash
# Alert log (last 50 lines)
oradba logs alert

# Listener log
oradba logs listener

# Custom tail count
oradba logs alert --tail 100
```

### Monitor Resources

```bash
# Tablespace usage
oradba monitor tablespaces

# Active sessions
oradba monitor sessions --active-only
```

## Pre-Installation Check

```bash
# Check system requirements
oradba precheck

# Generate fix script
oradba precheck --fix
sudo bash fix-precheck-issues.sh
```

## Configuration

### Custom Configuration File

Create `oracle-config.yaml`:

```yaml
oracle:
  oracle_base: /u01/app/oracle
  oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
  oracle_sid: PRODDB

database:
  db_name: PRODDB
  sid: PRODDB
  pdb_name: PDB1
  sys_password: YourSecurePassword123

google_drive:
  file_id: 1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns
```

Use with:

```bash
oradba install full --config oracle-config.yaml
```

## Logs and Troubleshooting

All operations are logged to `/var/log/oracledba/`:

```bash
# View recent logs
ls -lh /var/log/oracledba/

# Check specific TP log
cat /var/log/oracledba/tp01-system-readiness.sh.log

# Follow installation log in real-time
tail -f /var/log/oracledba/tp03-creation-instance.sh.log
```

## Quick Reference

### Essential Commands

```bash
# Complete installation
sudo oradba install full

# List training labs
oradba tp list

# Run specific lab
oradba tp run 07

# Check database status
oradba status

# Connect to database
oradba sqlplus --sysdba

# Backup database
oradba rman backup --type full

# View alert log
oradba logs alert
```

### Database Connection Info

After successful installation:

- **CDB Name:** GDCPROD
- **PDB Name:** GDCPDB
- **SYS Password:** Oracle123 (default)
- **Listener Port:** 1521
- **ORACLE_HOME:** /u01/app/oracle/product/19.3.0/dbhome_1

Connect:
```bash
sqlplus sys/Oracle123@//localhost/GDCPROD as sysdba
sqlplus sys/Oracle123@//localhost/GDCPDB as sysdba
```

## SSH Remote Installation

For remote server installation:

```bash
# From your local machine
ssh -i your-key.pem root@your-server-ip

# Then run installation
oradba install full
```

## Help

```bash
# General help
oradba --help

# Command-specific help
oradba install --help
oradba tp --help
oradba rman --help
```

## Support

- **Documentation:** Check individual TP markdown files in `dba-story-tps/`
- **Logs:** `/var/log/oracledba/`
- **Script Location:** Check scripts in package under `oracledba/scripts/`

## Next Steps

After installation:

1. ✅ Verify database: `oradba status`
2. ✅ Run TP04-TP15 for complete training
3. ✅ Configure backups: `oradba rman setup`
4. ✅ Set up monitoring: `oradba monitor tablespaces`
5. ✅ Create application users: `oradba security user --create`

---

**Enjoy your Oracle 19c database!** 🎉
