#!/bin/bash
# TP15: ASM et RAC Concepts
# Rocky Linux 8 - Oracle 19c
# Description: Concepts ASM, RAC, Grid Infrastructure

echo "================================================"
echo "  TP15: ASM et RAC - Concepts et Préparation"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/6] Vérification Single Instance actuelle..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SELECT 
    instance_name,
    host_name,
    version,
    instance_role,
    database_role,
    parallel
FROM v\$instance;

SELECT name, value FROM v\$parameter WHERE name IN ('cluster_database', 'cluster_database_instances');
EXIT;
EOF"

echo ""
echo "[2/6] Configuration actuelle du stockage..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200 PAGESIZE 100

-- Fichiers de données
SELECT 
    file_name,
    tablespace_name,
    ROUND(bytes/1024/1024/1024,2) AS size_gb,
    status
FROM dba_data_files
ORDER BY tablespace_name;

-- Fichiers de contrôle
SELECT name FROM v\$controlfile;

-- Redo logs
SELECT 
    group#,
    thread#,
    sequence#,
    ROUND(bytes/1024/1024,2) AS size_mb,
    members,
    status
FROM v\$log;
EXIT;
EOF"

echo ""
echo "[3/6] Vérification infrastructure RAC disponible..."
echo "Nœuds RAC configurés:"
ping -c 2 rac1 2>/dev/null && echo "  ✓ rac1: Accessible" || echo "  ✗ rac1: Non accessible"
ping -c 2 rac2 2>/dev/null && echo "  ✓ rac2: Accessible" || echo "  ✗ rac2: Non accessible"

echo ""
echo "Stockage partagé NFS:"
df -h | grep oracledata | awk '{print "  " $1 " -> " $6 " (" $2 ")"}'

echo ""
echo "[4/6] Vérification utilisateur grid..."
if id grid > /dev/null 2>&1; then
    echo "✓ Utilisateur grid existe"
    id grid
    echo ""
    echo "SSH Equivalence:"
    su - grid -c "ssh rac2 hostname" 2>/dev/null && echo "  ✓ rac1 -> rac2: OK" || echo "  ✗ rac1 -> rac2: NOK"
else
    echo "✗ Utilisateur grid n'existe pas"
fi

echo ""
echo "[5/6] Concepts ASM (Automatic Storage Management)..."
cat << 'EOF'

ASM - Automatic Storage Management:
─────────────────────────────────────────
• Volume Manager et Filesystem pour Oracle
• Striping et Mirroring automatiques
• Rééquilibrage dynamique des données
• Allocation/libération automatique de l'espace

Composants ASM:
├── ASM Instance: Instance légère pour gérer le stockage
├── ASM Disk Groups: Groupes de disques logiques
│   ├── +DATA: Données de base (NORMAL/HIGH redundancy)
│   ├── +FRA: Fast Recovery Area
│   └── +OCR: OCR et Voting disks (RAC)
└── ASM Files: Fichiers abstraits (+DATA/db_name/datafile/...)

Types de Redundancy:
• EXTERNAL: Pas de mirroring ASM (RAID matériel)
• NORMAL: Mirroring 2-way (2 copies)
• HIGH: Mirroring 3-way (3 copies)

Commandes ASM:
• asmcmd: CLI pour naviguer filesystem ASM
• crsctl: Contrôle Cluster Ready Services
• srvctl: Gestion services Oracle (database, instance, listener)

EOF

echo ""
echo "[6/6] Concepts RAC (Real Application Clusters)..."
cat << 'EOF'

RAC - Real Application Clusters:
─────────────────────────────────────────
• Plusieurs instances Oracle accèdent à une seule base de données
• Haute disponibilité et scalabilité horizontale
• Load balancing automatique
• Failover transparent

Architecture RAC:
┌──────────────────┐     ┌──────────────────┐
│   Node 1 (rac1)  │     │   Node 2 (rac2)  │
│  ┌────────────┐  │     │  ┌────────────┐  │
│  │ Instance 1 │  │     │  │ Instance 2 │  │
│  └─────┬──────┘  │     │  └─────┬──────┘  │
│        │         │     │        │         │
│  ┌─────┴──────┐  │     │  ┌─────┴──────┐  │
│  │    SGA     │  │     │  │    SGA     │  │
│  └────────────┘  │     │  └────────────┘  │
└────────┬─────────┘     └─────────┬────────┘
         │                         │
         │  ┌───────────────────┐  │
         └──┤ Shared Storage    ├──┘
            │ (ASM Disk Groups) │
            │  +DATA  +FRA      │
            └───────────────────┘

Composants RAC:
├── Grid Infrastructure
│   ├── Oracle Clusterware (CRS)
│   ├── ASM (Automatic Storage Management)
│   └── Oracle Networking (SCAN, VIP)
├── Cache Fusion
│   └── Transfert de blocs entre instances via interconnect
├── Voting Disks
│   └── Détection split-brain, membership
└── OCR (Oracle Cluster Registry)
    └── Configuration cluster

Addresses Réseau:
• Public IP: Communication client-database
• Private IP (Interconnect): Communication inter-nœuds
• VIP (Virtual IP): Failover rapide
• SCAN (Single Client Access Name): Point d'entrée unique

Services RAC:
• Listener: Un par nœud + SCAN listener
• Database Service: Load balancing politique
• Failover: TAF (Transparent Application Failover)

Commandes RAC utiles:
• crsctl check crs: Statut services CRS
• srvctl status database -d <db_name>: Statut database
• srvctl start instance -d <db_name> -i <instance>
• olsnrctl status: Statut listener
• asmcmd lsdg: Liste disk groups ASM

EOF

echo ""
echo "Infrastructure RAC actuelle:"
echo "─────────────────────────────"
echo "• Node 1: $(hostname) (rac1)"
echo "• Node 2: rac2"
echo "• NFS Server: nfs-dba (165.22.168.219)"
echo "• Shared Storage: 4 x 236GB (grid, ocr, data, fra)"
echo "• Grid User: Configuré avec SSH equivalence"
echo ""
echo "Prochaines étapes pour RAC complet:"
echo "1. Installer Grid Infrastructure 19c"
echo "2. Créer ASM disk groups (+DATA, +FRA, +OCR)"
echo "3. Installer Oracle RAC Database 19c"
echo "4. Créer RAC Database avec DBCA"
echo "5. Configurer Services et Load Balancing"

echo ""
echo "================================================"
echo "  TP15 TERMINÉ"
echo "================================================"
echo "Concepts ASM et RAC:"
echo "- Infrastructure RAC: Préparée (2 nœuds + NFS)"
echo "- Stockage partagé: 4 montages NFS actifs"
echo "- Grid user: Configuré avec SSH sans mot de passe"
echo "- Documentation: Concepts ASM et RAC détaillés"
echo ""
echo "Pour installation Grid Infrastructure:"
echo "./gridSetup.sh -silent -responseFile /path/to/grid.rsp"
