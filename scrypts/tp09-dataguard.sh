#!/bin/bash
# TP09: Data Guard (Simulation en Single Instance)
# Rocky Linux 8 - Oracle 19c
# Description: Configuration des archives logs et préparation Data Guard

echo "================================================"
echo "  TP09: Data Guard - Configuration"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/5] Activation ARCHIVELOG mode..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE OPEN;
ARCHIVE LOG LIST;
EXIT;
EOF"

echo ""
echo "[2/5] Configuration FORCE LOGGING..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER DATABASE FORCE LOGGING;
SELECT force_logging FROM v\$database;
EXIT;
EOF"

echo ""
echo "[3/5] Configuration Flashback Database..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SYSTEM SET db_recovery_file_dest_size=10G SCOPE=BOTH;
ALTER SYSTEM SET db_recovery_file_dest='/u01/app/oracle/fra' SCOPE=BOTH;
ALTER DATABASE FLASHBACK ON;
SELECT flashback_on FROM v\$database;
EXIT;
EOF"

echo ""
echo "[4/5] Configuration Standby Redo Logs..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER DATABASE ADD STANDBY LOGFILE THREAD 1 GROUP 10 '/u01/app/oracle/oradata/GDCPROD/standby_redo01.log' SIZE 50M;
ALTER DATABASE ADD STANDBY LOGFILE THREAD 1 GROUP 11 '/u01/app/oracle/oradata/GDCPROD/standby_redo02.log' SIZE 50M;
ALTER DATABASE ADD STANDBY LOGFILE THREAD 1 GROUP 12 '/u01/app/oracle/oradata/GDCPROD/standby_redo03.log' SIZE 50M;
ALTER DATABASE ADD STANDBY LOGFILE THREAD 1 GROUP 13 '/u01/app/oracle/oradata/GDCPROD/standby_redo04.log' SIZE 50M;
SELECT group#, thread#, bytes/1024/1024 AS size_mb, status FROM v\$standby_log;
EXIT;
EOF"

echo ""
echo "[5/5] Vérification configuration Data Guard..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SELECT name, log_mode, force_logging, flashback_on, protection_mode, protection_level 
FROM v\$database;
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP09 TERMINÉ"
echo "================================================"
echo "Configuration Data Guard Ready:"
echo "- Archive Log Mode: ENABLED"
echo "- Force Logging: YES"
echo "- Flashback Database: ON"
echo "- Standby Redo Logs: 4 groups créés"
echo ""
echo "Note: Pour Data Guard complet, standby database nécessaire"
