#!/bin/bash
# TP08: RMAN Backup and Recovery
# Rocky Linux 8 - Oracle 19c
# Description: Configuration RMAN et sauvegarde complète

echo "================================================"
echo "  TP08: RMAN - Backup et Recovery"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/6] Vérification configuration RMAN..."
su - oracle -c "rman target / << 'EOF'
SHOW ALL;
EXIT;
EOF"

echo ""
echo "[2/6] Configuration RMAN..."
su - oracle -c "rman target / << 'EOF'
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO '/u01/app/oracle/backup/%F';
CONFIGURE DEVICE TYPE DISK PARALLELISM 2 BACKUP TYPE TO BACKUPSET;
CONFIGURE BACKUP OPTIMIZATION ON;
SHOW ALL;
EXIT;
EOF"

echo ""
echo "[3/6] Création répertoire backup..."
mkdir -p /u01/app/oracle/backup
chown -R oracle:oinstall /u01/app/oracle/backup
chmod -R 775 /u01/app/oracle/backup

echo ""
echo "[4/6] Backup complet de la base..."
su - oracle -c "rman target / << 'EOF'
BACKUP DATABASE PLUS ARCHIVELOG;
LIST BACKUP SUMMARY;
EXIT;
EOF"

echo ""
echo "[5/6] Backup des fichiers de contrôle..."
su - oracle -c "rman target / << 'EOF'
BACKUP CURRENT CONTROLFILE;
LIST BACKUP OF CONTROLFILE;
EXIT;
EOF"

echo ""
echo "[6/6] Test de restauration Validate..."
su - oracle -c "rman target / << 'EOF'
RESTORE DATABASE VALIDATE;
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP08 TERMINÉ"
echo "================================================"
echo "RMAN configuré:"
echo "- Retention Policy: 7 jours"
echo "- Controlfile Autobackup: ON"
echo "- Backup Location: /u01/app/oracle/backup"
echo "- Full Database Backup: Completed"
echo ""
du -sh /u01/app/oracle/backup
