#!/bin/bash
# TP04 - Multiplexage Fichiers Critiques
# Control Files, Redo Logs, Archive Logs
# Rocky Linux 8 - Oracle 19c

set -e

echo "================================================"
echo "  TP04: Multiplexage Fichiers Critiques"
echo "  Rocky Linux 8 - Oracle 19c"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/5] État actuel de la base..."

sqlplus -s / as sysdba << 'EOSQL'
SET LINESIZE 200
SELECT name, open_mode, log_mode FROM v$database;
SELECT group#, members, bytes/1024/1024 MB, status FROM v$log ORDER BY group#;
SELECT name FROM v$controlfile;
EOSQL

echo ""
echo "[2/5] Création répertoires pour multiplexage..."

mkdir -p /u01/app/oracle/oradata/GDCPROD/controlfile
mkdir -p /u01/app/oracle/fast_recovery_area/GDCPROD/controlfile
mkdir -p /u01/app/oracle/oradata/GDCPROD/onlinelog
mkdir -p /u01/app/oracle/fast_recovery_area/GDCPROD/onlinelog

echo "✓ Répertoires créés"

echo ""
echo "[3/5] Activation ARCHIVELOG..."

sqlplus / as sysdba << 'EOSQL'
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
ARCHIVE LOG LIST;
EXIT;
EOSQL

echo "✓ Mode ARCHIVELOG activé"

echo ""
echo "[4/5] Multiplexage Control Files..."

sqlplus / as sysdba << 'EOSQL' > /tmp/tp04_controlfile.log
-- État actuel
SELECT name FROM v$controlfile;

-- Arrêt et ajout membres
SHUTDOWN IMMEDIATE;
STARTUP NOMOUNT;

-- Modifier SPFILE pour 3 copies
ALTER SYSTEM SET control_files=
  '/u01/app/oracle/oradata/GDCPROD/control01.ctl',
  '/u01/app/oracle/oradata/GDCPROD/controlfile/control02.ctl',
  '/u01/app/oracle/fast_recovery_area/GDCPROD/controlfile/control03.ctl'
  SCOPE=SPFILE;

SHUTDOWN IMMEDIATE;
EXIT;
EOSQL

# Copier control file physiquement
cp /u01/app/oracle/oradata/GDCPROD/control01.ctl \
   /u01/app/oracle/oradata/GDCPROD/controlfile/control02.ctl

cp /u01/app/oracle/oradata/GDCPROD/control01.ctl \
   /u01/app/oracle/fast_recovery_area/GDCPROD/controlfile/control03.ctl

# Redémarrer
sqlplus / as sysdba << 'EOSQL'
STARTUP;
SELECT name FROM v$controlfile;
EXIT;
EOSQL

echo "✓ Control Files multiplexés (3 copies)"

echo ""
echo "[5/5] Multiplexage Redo Logs..."

sqlplus / as sysdba << 'EOSQL'
SET SERVEROUTPUT ON

-- Ajouter membres aux groupes existants
ALTER DATABASE ADD LOGFILE MEMBER
  '/u01/app/oracle/fast_recovery_area/GDCPROD/onlinelog/redo01b.log'
  TO GROUP 1;

ALTER DATABASE ADD LOGFILE MEMBER
  '/u01/app/oracle/fast_recovery_area/GDCPROD/onlinelog/redo02b.log'
  TO GROUP 2;

ALTER DATABASE ADD LOGFILE MEMBER
  '/u01/app/oracle/fast_recovery_area/GDCPROD/onlinelog/redo03b.log'
  TO GROUP 3;

-- Créer groupe 4 avec 2 membres
ALTER DATABASE ADD LOGFILE GROUP 4
  ('/u01/app/oracle/oradata/GDCPROD/onlinelog/redo04a.log',
   '/u01/app/oracle/fast_recovery_area/GDCPROD/onlinelog/redo04b.log')
  SIZE 200M;

-- Attendre synchronisation
EXEC DBMS_LOCK.SLEEP(2);

-- Vérifier
SELECT group#, member, status FROM v$logfile ORDER BY group#, member;

-- Forcer switch pour tester
ALTER SYSTEM SWITCH LOGFILE;
ALTER SYSTEM CHECKPOINT;

EXIT;
EOSQL

echo "✓ Redo Logs multiplexés (2 membres par groupe)"

echo ""
echo "================================================"
echo "  TP04 TERMINÉ - Fichiers Critiques Protégés"
echo "================================================"
echo ""

# Résumé final
sqlplus -s / as sysdba << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100
PROMPT === CONTROL FILES ===
SELECT name FROM v$controlfile;

PROMPT
PROMPT === REDO LOG GROUPS ===
SELECT group#, COUNT(*) members, bytes/1024/1024 MB, status 
FROM v$log 
GROUP BY group#, bytes, status 
ORDER BY group#;

PROMPT
PROMPT === REDO LOG MEMBERS ===
SELECT group#, member, status FROM v$logfile ORDER BY group#;

PROMPT
PROMPT === ARCHIVELOG STATUS ===
ARCHIVE LOG LIST;
EXIT;
EOSQL

echo ""
echo "Configuration finale:"
echo "- Control Files: 3 copies (oradata + fra)"
echo "- Redo Logs: 4 groups, 2 membres/group"
echo "- Archive Log: ENABLED"
echo ""
echo "Prochaine étape: TP05 - Gestion Stockage (Tablespaces)"
