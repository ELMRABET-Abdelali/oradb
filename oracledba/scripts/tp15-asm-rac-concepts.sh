#!/bin/bash
# TP15 - ASM et RAC Concepts
# Automatic Storage Management, Real Application Clusters
# Rocky Linux 8 - Oracle 19c

set -e

echo "================================================"
echo "  TP15: ASM et RAC Concepts"
echo "  Rocky Linux 8 - Oracle 19c"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/5] Vérification configuration cluster actuelle..."

# Check si environnement RAC
if [ -f "/etc/oracle/olr.loc" ]; then
    echo "✓ Configuration RAC détectée"
    cat /etc/oracle/olr.loc
else
    echo "ℹ Configuration Single Instance (non-RAC)"
fi

# Vérifier grid infrastructure
if [ -f "/etc/oracle/ocr.loc" ]; then
    echo "✓ Grid Infrastructure installé"
else
    echo "ℹ Grid Infrastructure non installé (optionnel en Single Instance)"
fi

echo ""
echo "[2/5] Simulation ASM architecture..."

cat << 'ASM_ARCHITECTURE' 
================================================
AUTOMATIC STORAGE MANAGEMENT (ASM)
================================================

Architecture ASM:
├── Grid Infrastructure (oracle user: grid)
│   ├── ASM Instance (RDBMS simplifié)
│   ├── Cluster Synchronization Services (CSS)
│   └── Event Manager (EVM)
│
├── Disk Groups (équivalent filesystem)
│   ├── DATA (données base)
│   │   ├── Datafiles
│   │   ├── Controlfiles
│   │   └── Tempfiles
│   ├── FRA (Fast Recovery Area)
│   │   ├── RMAN backups
│   │   ├── Archive logs
│   │   └── Flashback logs
│   └── GRID (OCR + Voting disks)
│       ├── OCR (Oracle Cluster Registry)
│       └── Voting disks
│
└── Redundancy Levels
    ├── EXTERNAL (no ASM mirroring - use RAID)
    ├── NORMAL (2-way mirroring)
    └── HIGH (3-way mirroring)

Commandes ASM:
--------------
# Se connecter à ASM
export ORACLE_SID=+ASM
sqlplus / as sysasm

# Lister disk groups
SELECT name, state, type, total_mb, free_mb 
FROM v$asm_diskgroup;

# Lister disks
SELECT group_number, disk_number, name, path, state 
FROM v$asm_disk;

# Créer disk group
CREATE DISKGROUP data01 
EXTERNAL REDUNDANCY
DISK '/dev/sdb1', '/dev/sdc1';

# Ajouter disk
ALTER DISKGROUP data01 ADD DISK '/dev/sdd1';

# Rebalance
ALTER DISKGROUP data01 REBALANCE POWER 8;

ASM_ARCHITECTURE

echo ""
echo "[3/5] Concepts RAC (Real Application Clusters)..."

cat << 'RAC_CONCEPTS'
================================================
REAL APPLICATION CLUSTERS (RAC)
================================================

Architecture RAC:
├── Shared Storage (ASM ou NFS)
│   ├── Database files (partagés entre tous noeuds)
│   ├── Controlfiles (multiplexés)
│   ├── Redo logs (thread par noeud)
│   └── Archive logs
│
├── Interconnect Privé (TCP/IP haute vitesse)
│   ├── Cache Fusion (transfer blocks entre instances)
│   └── Cluster communication
│
├── Noeuds (minimum 2)
│   ├── Node 1: Instance GDCPROD1
│   │   ├── SGA propre
│   │   ├── Background processes
│   │   └── Redo thread 1
│   │
│   └── Node 2: Instance GDCPROD2
│       ├── SGA propre
│       ├── Background processes
│       └── Redo thread 2
│
└── Grid Infrastructure
    ├── Clusterware (CRS)
    ├── ASM (storage management)
    ├── OCR (cluster configuration)
    ├── Voting Disk (cluster membership)
    └── SCAN (Single Client Access Name)

Processus spécifiques RAC:
--------------------------
LMSn  : Global Cache Service (Cache Fusion)
LMDn  : Lock Manager Daemon
LMON  : Global Enqueue Service Monitor
LCK0  : Lock Process
RMSn  : RAC Management Process
RSMN  : RAC management

Services RAC:
-------------
# Vérifier status cluster
crsctl status resource -t

# Vérifier tous les noeuds
olsnodes -n

# Status base RAC
srvctl status database -d GDCPROD

# Démarrer instance sur node spécifique
srvctl start instance -d GDCPROD -i GDCPROD1 -n node1

# Services pour load balancing
srvctl add service -d GDCPROD -s app_service \
  -preferred GDCPROD1 -available GDCPROD2

Haute Disponibilité:
--------------------
- Automatic failover: Si node1 down, connexions → node2
- Load balancing: Distribution connexions
- Connection pooling: FCF (Fast Connection Failover)
- TAF (Transparent Application Failover)
- Services prioritized/preferred

RAC_CONCEPTS

echo ""
echo "[4/5] Configuration Single Instance avec NFS (simulation RAC storage)..."

# Vérifier NFS mounts si disponibles
echo "Vérification NFS mounts..."
df -h | grep nfs || echo "Aucun mount NFS actif"

# Configuration pour RAC-ready
sqlplus / as sysdba << 'EOSQL'
-- Paramètres pour environnement RAC
ALTER SYSTEM SET cluster_database=FALSE SCOPE=SPFILE;
ALTER SYSTEM SET cluster_database_instances=1 SCOPE=SPFILE;

-- Si conversion vers RAC (future)
-- ALTER SYSTEM SET cluster_database=TRUE SCOPE=SPFILE;
-- ALTER SYSTEM SET cluster_database_instances=2 SCOPE=SPFILE;
-- ALTER SYSTEM SET instance_number=1 SCOPE=SPFILE;
-- ALTER SYSTEM SET thread=1 SCOPE=SPFILE;

-- Vérifier configuration
SHOW PARAMETER cluster_database;
SHOW PARAMETER thread;
SHOW PARAMETER instance_number;

-- GCS/GES Statistics (vides en single instance)
SELECT * FROM gv$instance;

EXIT;
EOSQL

echo ""
echo "[5/5] Vérification Redo Threads (RAC preparation)..."

sqlplus / as sysdba << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100

-- Threads actuels
SELECT thread#, status, enabled, groups, instance 
FROM v$thread;

-- Online Redo Logs par thread
SELECT thread#, group#, bytes/1024/1024 AS mb, members, status 
FROM v$log
ORDER BY thread#, group#;

-- Pour RAC: Créer thread 2 (exemple)
-- ALTER DATABASE ADD LOGFILE THREAD 2 
--   GROUP 21 ('/shared/redo/redo21a.log', '/shared/redo/redo21b.log') SIZE 200M,
--   GROUP 22 ('/shared/redo/redo22a.log', '/shared/redo/redo22b.log') SIZE 200M;
-- ALTER DATABASE ENABLE PUBLIC THREAD 2;

-- Standby Redo Logs (déjà créés en TP09)
SELECT thread#, group#, bytes/1024/1024 AS mb, members, status 
FROM v$standby_log
ORDER BY thread#, group#;

-- Vérifier DRM (Dynamic Resource Mastering) - RAC only
SELECT * FROM gv$gcshvmaster_info WHERE ROWNUM <= 10;

EXIT;
EOSQL

echo ""
echo "================================================"
echo "  TP15 TERMINÉ - ASM/RAC Concepts Explorés"
echo "================================================"
echo ""

echo "Concepts couverts:"
echo ""
echo "1. ASM (Automatic Storage Management):"
echo "   - Disk Groups (DATA, FRA, GRID)"
echo "   - Redundancy (EXTERNAL, NORMAL, HIGH)"
echo "   - ASMCMD utility"
echo "   - +ASM instance"
echo ""
echo "2. RAC (Real Application Clusters):"
echo "   - Multi-instance architecture"
echo "   - Cache Fusion (memory-to-memory)"
echo "   - Interconnect privé"
echo "   - Services load balancing"
echo "   - Automatic failover"
echo ""
echo "3. Grid Infrastructure:"
echo "   - Clusterware (CRS)"
echo "   - OCR (Oracle Cluster Registry)"
echo "   - Voting Disks"
echo "   - SCAN (Single Client Access Name)"
echo ""
echo "État actuel:"
sqlplus -s / as sysdba << 'EOSQL'
SET PAGESIZE 20
SELECT name AS database_name, 
       cdb, 
       open_mode,
       'Single Instance' AS architecture
FROM v$database;

SELECT instance_name, version, status, 
       host_name, 
       startup_time
FROM v$instance;
EXIT;
EOSQL

echo ""
echo "Pour convertir vers RAC (avancé):"
echo "1. Installer Grid Infrastructure sur tous noeuds"
echo "2. Configurer ASM disk groups partagés"
echo "3. Convertir database vers shared storage"
echo "4. Activer cluster_database=TRUE"
echo "5. Créer instances sur chaque noeud"
echo "6. Configurer services et load balancing"
echo ""
echo "Documentation:"
echo "- ASM Admin Guide: Doc ID 1531487.1"
echo "- RAC Admin Guide: https://docs.oracle.com/en/database/oracle/oracle-database/19/racad/"
echo "- Grid Infrastructure: Doc ID 1962984.1"
echo ""
echo "================================================"
echo "  FORMATION COMPLÈTE - 15 TPs TERMINÉS !"
echo "================================================"
