#!/bin/bash
# TP10: Performance Tuning
# Rocky Linux 8 - Oracle 19c
# Description: Tuning SQL et analyse AWR

echo "================================================"
echo "  TP10: Performance Tuning"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/7] Configuration AWR (Automatic Workload Repository)..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
EXEC DBMS_WORKLOAD_REPOSITORY.modify_snapshot_settings(interval => 30, retention => 10080);
SELECT snap_interval, retention FROM dba_hist_wr_control;
EXIT;
EOF"

echo ""
echo "[2/7] Création snapshot AWR manuel..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
EXEC DBMS_WORKLOAD_REPOSITORY.create_snapshot();
SELECT MAX(snap_id) AS latest_snapshot FROM dba_hist_snapshot;
EXIT;
EOF"

echo ""
echo "[3/7] Configuration SQL Plan Baseline..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SYSTEM SET optimizer_capture_sql_plan_baselines=TRUE SCOPE=BOTH;
SHOW PARAMETER optimizer_capture_sql_plan_baselines;
EXIT;
EOF"

echo ""
echo "[4/7] Génération de charge SQL pour test..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;
CREATE TABLE IF NOT EXISTS perf_test AS SELECT * FROM all_objects;
SELECT COUNT(*) FROM perf_test;
CREATE INDEX idx_perf_test_owner ON perf_test(owner);
CREATE INDEX idx_perf_test_object_name ON perf_test(object_name);
EXEC DBMS_STATS.gather_table_stats(USER, 'PERF_TEST');
EXIT;
EOF"

echo ""
echo "[5/7] Analyse Top SQL..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200 PAGESIZE 100
SELECT sql_id, 
       executions,
       ROUND(elapsed_time/1000000,2) AS elapsed_sec,
       ROUND(cpu_time/1000000,2) AS cpu_sec,
       buffer_gets,
       disk_reads,
       SUBSTR(sql_text, 1, 80) AS sql_text
FROM v\$sql
WHERE executions > 0
ORDER BY elapsed_time DESC
FETCH FIRST 10 ROWS ONLY;
EXIT;
EOF"

echo ""
echo "[6/7] Vérification SGA et PGA..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SHOW PARAMETER sga_target;
SHOW PARAMETER pga_aggregate_target;
SELECT ROUND(SUM(value)/1024/1024/1024,2) AS sga_gb FROM v\$sga;
SELECT name, ROUND(value/1024/1024,2) AS size_mb FROM v\$pgastat WHERE name IN ('total PGA allocated', 'maximum PGA allocated');
EXIT;
EOF"

echo ""
echo "[7/7] Configuration Advisor..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
-- Enable SQL Tuning Advisor
ALTER SYSTEM SET statistics_level=TYPICAL SCOPE=BOTH;
SHOW PARAMETER statistics_level;
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP10 TERMINÉ"
echo "================================================"
echo "Performance Tuning configuré:"
echo "- AWR Snapshots: 30 minutes interval, 7 days retention"
echo "- SQL Plan Baselines: ENABLED"
echo "- Statistics Level: TYPICAL"
echo "- Test table created with indexes"
echo ""
echo "Commandes utiles:"
echo "- Rapport AWR: @\$ORACLE_HOME/rdbms/admin/awrrpt.sql"
echo "- Rapport ADDM: @\$ORACLE_HOME/rdbms/admin/addmrpt.sql"
