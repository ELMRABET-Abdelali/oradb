# Oracle 19c Installation Guide

> **Complete Guide for Installing and Configuring Oracle Database 19c on Rocky Linux 8**

## 📋 Table of Contents

1. [Quick Start - One Command Installation](#quick-start)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Configuration Commands](#configuration-commands)
4. [Maintenance Commands](#maintenance-commands)
5. [Advanced Features](#advanced-features)
6. [Database Management](#database-management)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start - One Command Installation

Install everything with a single command:

```bash
sudo oradba install all
```

This command will:
- ✅ Configure system prerequisites (users, groups, kernel parameters, packages)
- ✅ Download Oracle 19c binaries (3GB from Google Drive)
- ✅ Extract and install Oracle software
- ✅ Create database with CDB and PDB
- ⏱️ **Total time: 30-45 minutes**

### Installation Options

**Full installation (with verbose output):**
```bash
sudo oradba install all --verbose
```

**Skip specific steps:**
```bash
# Skip system setup (if already done)
sudo oradba install all --skip-system

# Skip binary download (if already downloaded)
sudo oradba install all --skip-binaries

# Install only software, no database
sudo oradba install all --skip-db
```

---

## 📦 Step-by-Step Installation

If you prefer to run installation in stages:

### 1. System Preparation
```bash
sudo oradba install system
```

**What it does:**
- Creates `oracle` user and required groups
- Configures kernel parameters (shmmax, shmall, etc.)
- Installs required packages (bc, binutils, glibc-devel, ksh, etc.)
- Creates directories (/u01/app/oracle)
- Configures swap space

### 2. Download Oracle Binaries
```bash
sudo oradba install binaries
```

**What it does:**
- Downloads Oracle 19c from Google Drive (3GB)
- Extracts to ORACLE_HOME (6.5GB total)
- Configures Oracle environment variables

### 3. Install Oracle Software
```bash
sudo oradba install software
```

**What it does:**
- Runs Oracle installer (runInstaller)
- Installs Oracle Database 19c Enterprise Edition
- Executes root scripts automatically

### 4. Create Database
```bash
sudo oradba install database
```

**What it does:**
- Creates listener on port 1521
- Runs DBCA to create CDB (GDCPROD) and PDB (GDCPDB)
- Configures automatic memory management
- Sets up Fast Recovery Area

---

## ⚙️ Configuration Commands

After installation, configure additional database features:

### Multiplex Critical Files
```bash
sudo oradba configure multiplexing
```
- Multiplexes control files
- Adds redo log members
- Improves database reliability

### Storage Management
```bash
sudo oradba configure storage
```
- Creates tablespaces (TBS_DATA, TEMP_BIG, UNDOTBS2)
- Configures datafiles
- Sets up user quotas

### Security Configuration
```bash
sudo oradba configure users
```
- Creates database users and roles
- Configures profiles and resource limits
- Sets up privileges and grants

### Flashback Database
```bash
sudo oradba configure flashback
```
- Enables Flashback Database
- Configures Flashback Query
- Sets up Flashback Table and Drop

### RMAN Backup Configuration
```bash
sudo oradba configure backup
```
- Configures RMAN retention policy
- Sets up backup compression
- Configures controlfile autobackup
- Creates backup location

### Data Guard Setup
```bash
sudo oradba configure dataguard
```
- Enables ARCHIVELOG mode
- Configures FORCE LOGGING
- Creates standby redo logs
- Prepares for Data Guard configuration

### Run All Configuration Steps
```bash
sudo oradba configure all
```
Runs labs 04-09 sequentially.

---

## 🔧 Maintenance Commands

### Performance Tuning
```bash
sudo oradba maintenance tune
```
- Configures AWR snapshots
- Sets up SQL Plan Baselines
- Analyzes top SQL queries
- Configures memory (SGA/PGA)

### Apply Patches
```bash
sudo oradba maintenance patch
```
- Checks Oracle version
- Verifies OPatch
- Lists installed patches
- Shows component status

---

## 🚀 Advanced Features

### Multitenant Architecture
```bash
sudo oradba advanced multitenant
```
- Creates additional PDBs
- Manages PDB lifecycle
- Configures resource management
- Tests PDB cloning

### AI and Machine Learning
```bash
sudo oradba advanced ai-ml
```
- Configures Oracle Text
- Sets up machine learning tables
- Prepares for AI workloads

### Data Mobility
```bash
sudo oradba advanced data-mobility
```
- Configures Data Pump
- Sets up transportable tablespaces
- Tests data migration

### ASM and RAC Concepts
```bash
sudo oradba advanced asm-rac
```
- Reviews ASM architecture
- Explains RAC concepts
- Shows clustering preparation

---

## 💾 Database Management

### Check Database Status
```bash
oradba status
```

### Start Database
```bash
sudo oradba start
```

### Stop Database
```bash
sudo oradba stop
```

### Restart Database
```bash
sudo oradba restart
```

### Connect to SQL*Plus
```bash
# As SYSDBA
oradba sqlplus --sysdba

# Connect to PDB
oradba sqlplus --pdb GDCPDB
```

### View Logs
```bash
# Alert log (last 50 lines)
oradba logs alert

# Listener log
oradba logs listener

# Custom tail
oradba logs alert --tail 100
```

### Monitor Resources
```bash
# Tablespace usage
oradba monitor tablespaces

# Active sessions
oradba monitor sessions

# Only active sessions
oradba monitor sessions --active-only
```

---

## 📊 RMAN Backup Commands

### Configure RMAN
```bash
oradba rman setup --retention 7
```

### Full Backup
```bash
oradba rman backup --type full
```

### Incremental Backup
```bash
oradba rman backup --type incremental
```

### Archive Log Backup
```bash
oradba rman backup --type archive
```

### List Backups
```bash
oradba rman list --type backup
```

### Restore Database
```bash
oradba rman restore --point-in-time "2025-02-17 10:00:00"
```

---

## 📚 List All Available Labs

See complete list of all configuration labs:

```bash
oradba labs
```

**Output:**
```
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ #  ┃ Name                 ┃ Description                            ┃ Category     ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 01 │ System Readiness     │ User, groups, packages, kernel params  │ Installation │
│ 02 │ Binary Installation  │ Download and extract Oracle 19c        │ Installation │
│ 03 │ Database Creation    │ Create database with DBCA              │ Installation │
│ 04 │ Critical Files       │ Multiplex control files, redo logs     │ Configuration│
│ 05 │ Storage Management   │ Tablespaces, datafiles, OMF            │ Configuration│
│ 06 │ Security             │ Users, roles, profiles, privileges     │ Security     │
│ 07 │ Flashback            │ Flashback query, table, database       │ Protection   │
│ 08 │ RMAN Backup          │ Backup strategies and recovery         │ Protection   │
│ 09 │ Data Guard           │ High availability with standby         │ HA           │
│ 10 │ Performance Tuning   │ AWR, SQL tuning, optimization          │ Performance  │
│ 11 │ Patching             │ Apply patches and updates              │ Maintenance  │
│ 12 │ Multitenant          │ CDB/PDB management                     │ Architecture │
│ 13 │ AI/ML                │ Oracle Machine Learning                │ Advanced     │
│ 14 │ Data Mobility        │ Data Pump, transportable tablespaces   │ Advanced     │
│ 15 │ ASM/RAC              │ Clustering and ASM concepts            │ Advanced     │
└────┴──────────────────────┴────────────────────────────────────────┴──────────────┘
```

---

## 🔍 Troubleshooting

### Check Pre-Installation Requirements
```bash
oradba precheck
```

### Generate Fix Script
```bash
oradba precheck --fix
sudo bash fix-precheck-issues.sh
```

### View Installation Logs
All operations log to `/var/log/oracledba/`:
```bash
ls -lt /var/log/oracledba/
tail -100 /var/log/oracledba/tp01-system-readiness.sh.log
```

### Common Issues

#### 1. Insufficient Memory
**Error:** ORA-00845: MEMORY_TARGET not supported
**Solution:**
```bash
# Increase shared memory
sudo mount -o remount,size=4G /dev/shm
```

#### 2. Listener Not Starting
**Solution:**
```bash
# Check listener status
lsnrctl status

# Start manually
lsnrctl start
```

#### 3. Database Not Opening
**Solution:**
```bash
sqlplus / as sysdba
SQL> startup
SQL> select open_mode from v$database;
```

#### 4. Permission Issues
**Solution:**
```bash
# Fix Oracle file permissions
sudo chown -R oracle:oinstall /u01/app/oracle
sudo chmod -R 775 /u01/app/oracle
```

---

## 📝 Configuration File

Create a custom configuration file `config.yaml`:

```yaml
oracle:
  oracle_base: /u01/app/oracle
  oracle_home: /u01/app/oracle/product/19.3.0/dbhome_1
  oracle_sid: GDCPROD

database:
  db_name: GDCPROD
  sid: GDCPROD
  pdb_name: GDCPDB
  sys_password: YourSecurePassword123

google_drive:
  file_id: 1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns

backup:
  location: /u01/backup
  retention_days: 7
  compression: true
```

Use with any command:
```bash
sudo oradba install all --config config.yaml
```

---

## 🎯 Complete Workflow Example

**Fresh server to production-ready database:**

```bash
# 1. One-command installation (30-45 min)
sudo oradba install all --verbose

# 2. Configure additional features (10-15 min)
sudo oradba configure multiplexing
sudo oradba configure storage
sudo oradba configure backup

# 3. Setup RMAN backups
oradba rman setup --retention 7
oradba rman backup --type full

# 4. Check status
oradba status
oradba monitor tablespaces
oradba monitor sessions

# 5. Connect and test
oradba sqlplus --sysdba
SQL> SELECT name, open_mode FROM v$database;
SQL> SHOW pdbs;
```

**Total time: ~1 hour for complete production-ready database!**

---

## 📞 Support

- **Logs**: `/var/log/oracledba/`
- **Scripts**: Check `oracledba/scripts/` directory
- **Help**: `oradba --help`
- **Version**: `oradba --version`

---

## ✨ Features Overview

| Feature | Command | Category |
|---------|---------|----------|
| One-button install | `oradba install all` | Installation |
| System setup | `oradba install system` | Installation |
| File multiplexing | `oradba configure multiplexing` | Configuration |
| Storage mgmt | `oradba configure storage` | Configuration |
| User security | `oradba configure users` | Security |
| Flashback | `oradba configure flashback` | Protection |
| RMAN backup | `oradba configure backup` | Protection |
| Data Guard | `oradba configure dataguard` | HA |
| Performance tuning | `oradba maintenance tune` | Performance |
| Patching | `oradba maintenance patch` | Maintenance |
| Multitenant | `oradba advanced multitenant` | Advanced |
| AI/ML | `oradba advanced ai-ml` | Advanced |

---

## 🏆 Success Criteria

After running `oradba install all`, verify:

✅ **Oracle software installed:**
```bash
su - oracle -c 'echo $ORACLE_HOME'
su - oracle -c 'sqlplus -v'
```

✅ **Database running:**
```bash
oradba status
```

✅ **Listener active:**
```bash
lsnrctl status
```

✅ **PDB accessible:**
```bash
sqlplus sys/Oracle123@//localhost/GDCPDB as sysdba
```

✅ **All checks green:**
```bash
oradba test --report
```

---

**Happy Database Administration! 🎉**
