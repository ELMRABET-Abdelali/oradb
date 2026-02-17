#!/bin/bash
############################################################
# TP04: Multiplexage Control Files & Redo Logs
# Rocky Linux 8
############################################################

set -e
echo "============================================"
echo "  TP04: Multiplexage Fichiers Critiques"
echo "  $(date)"
echo "============================================"
echo ""

# Create SQL script for multiplexing
cat > /tmp/tp04_multiplex.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
SET SERVEROUTPUT ON

-- Afficher configuration actuelle
PROMPT ===== CONFIGURATION ACTUELLE =====
PROMPT
PROMPT === Control Files ===
SELECT name FROM v$controlfile;

PROMPT
PROMPT === Redo Log Groups ===
SELECT group#, thread#, sequence#, bytes/1024/1024 as size_mb, members, status 
FROM v$log ORDER BY group#;

PROMPT
PROMPT === Redo Log Members ===
SELECT group#, member FROM v$logfile ORDER BY group#, member;

-- Créer répertoires pour stockage multiplexé
!mkdir -p /u01/app/oracle/oradata/GDCPROD/control
!mkdir -p /u01/app/oracle/oradata/GDCPROD/redo1
!mkdir -p /u01/app/oracle/oradata/GDCPROD/redo2

PROMPT
PROMPT ===== MULTIPLEXAGE CONTROL FILES =====

-- Shutdown et copie des control files
SHUTDOWN IMMEDIATE;
!cp /u01/app/oracle/oradata/GDCPROD/control01.ctl /u01/app/oracle/oradata/GDCPROD/control/control02.ctl
!cp /u01/app/oracle/oradata/GDCPROD/control01.ctl /u01/app/oracle/oradata/GDCPROD/control/control03.ctl

STARTUP NOMOUNT;

-- Modifier le SPFILE pour ajouter les control files
ALTER SYSTEM SET control_files='/u01/app/oracle/oradata/GDCPROD/control01.ctl',
                                '/u01/app/oracle/oradata/GDCPROD/control/control02.ctl',
                                '/u01/app/oracle/oradata/GDCPROD/control/control03.ctl' 
SCOPE=SPFILE;

SHUTDOWN IMMEDIATE;
STARTUP;

PROMPT
PROMPT === Control Files Multiplexés ===
SELECT name FROM v$controlfile;

PROMPT
PROMPT ===== MULTIPLEXAGE REDO LOGS =====

-- Ajouter membres aux groupes existants
ALTER DATABASE ADD LOGFILE MEMBER '/u01/app/oracle/oradata/GDCPROD/redo1/redo01b.log' TO GROUP 1;
ALTER DATABASE ADD LOGFILE MEMBER '/u01/app/oracle/oradata/GDCPROD/redo1/redo02b.log' TO GROUP 2;
ALTER DATABASE ADD LOGFILE MEMBER '/u01/app/oracle/oradata/GDCPROD/redo1/redo03b.log' TO GROUP 3;

-- Ajouter un 4ème groupe avec 2 membres
ALTER DATABASE ADD LOGFILE GROUP 4 
  ('/u01/app/oracle/oradata/GDCPROD/redo2/redo04a.log',
   '/u01/app/oracle/oradata/GDCPROD/redo2/redo04b.log') SIZE 200M;

-- Forcer log switches pour tester
ALTER SYSTEM SWITCH LOGFILE;
ALTER SYSTEM CHECKPOINT;

PROMPT
PROMPT === Configuration Finale Redo Logs ===
SELECT group#, thread#, bytes/1024/1024 as size_mb, members, status 
FROM v$log ORDER BY group#;

PROMPT
PROMPT === Membres Redo Logs ===
COL member FORMAT A70
SELECT group#, member, status FROM v$logfile ORDER BY group#, member;

PROMPT
PROMPT ===== VERIFICATION ARCHIVE LOG MODE =====
ARCHIVE LOG LIST;

PROMPT
PROMPT ===== RESUME TP04 =====
SELECT 'Control Files: ' || COUNT(*) || ' copies' as info FROM v$controlfile
UNION ALL
SELECT 'Redo Log Groups: ' || COUNT(*) || ' groupes' FROM v$log
UNION ALL
SELECT 'Redo Log Members: ' || COUNT(*) || ' membres' FROM v$logfile;

EXIT
EOSQL

echo "[1/2] Exécution du multiplexage..."
su - oracle -c "sqlplus / as sysdba @/tmp/tp04_multiplex.sql" 2>&1 | tee /tmp/tp04_output.log

# Vérification
echo ""
echo "[2/2] Vérification finale..."
su - oracle -c "sqlplus -s / as sysdba << EOF
SET PAGESIZE 0 FEEDBACK OFF
SELECT 'TP04 STATUS: COMPLETE' FROM dual;
SELECT '✓ Control files: ' || COUNT(*) FROM v\$controlfile HAVING COUNT(*) >= 3;
SELECT '✓ Redo log groups: ' || COUNT(*) FROM v\$log HAVING COUNT(*) >= 4;
SELECT '✓ Redo log members total: ' || COUNT(*) FROM v\$logfile HAVING COUNT(*) >= 7;
EXIT
EOF"

echo ""
echo "============================================"
echo "  TP04 TERMINÉ"
echo "============================================"
echo "Logs: /tmp/tp04_output.log"
