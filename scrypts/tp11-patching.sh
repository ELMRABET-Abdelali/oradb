#!/bin/bash
# TP11: Patching et Maintenance
# Rocky Linux 8 - Oracle 19c
# Description: Vérification version, patches et opatch

echo "================================================"
echo "  TP11: Patching et Maintenance"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/5] Version Oracle actuelle..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SELECT * FROM v\$version;
SELECT * FROM v\$instance;
EXIT;
EOF"

echo ""
echo "[2/5] Vérification OPatch..."
su - oracle -c "cd \$ORACLE_HOME/OPatch && ./opatch version"

echo ""
echo "[3/5] Liste patches installés..."
su - oracle -c "cd \$ORACLE_HOME/OPatch && ./opatch lsinventory"

echo ""
echo "[4/5] Vérification des composants..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200 PAGESIZE 100
SELECT comp_name, version, status FROM dba_registry ORDER BY comp_name;
EXIT;
EOF"

echo ""
echo "[5/5] Informations système et database..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200
SELECT 
    instance_name,
    host_name,
    version,
    startup_time,
    status,
    database_status
FROM v\$instance;

SELECT 
    name,
    dbid,
    created,
    log_mode,
    open_mode
FROM v\$database;

SELECT 
    tablespace_name,
    ROUND(SUM(bytes)/1024/1024/1024,2) AS size_gb
FROM dba_data_files
GROUP BY tablespace_name
ORDER BY 2 DESC;
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP11 TERMINÉ"
echo "================================================"
echo "Informations système:"
echo "- Oracle Database 19c Enterprise Edition"
echo "- Rocky Linux 8.8"
echo "- OPatch version vérifié"
echo ""
echo "Pour appliquer patches:"
echo "1. Télécharger patch depuis My Oracle Support"
echo "2. Arrêter base: shutdown immediate"
echo "3. Appliquer: opatch apply"
echo "4. Redémarrer: startup"
echo "5. Post-patch: @?\rdbms\admin\catbundle.sql psu apply"
