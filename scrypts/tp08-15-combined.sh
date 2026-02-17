#!/bin/bash
###########################################################
# TP08-15: TPs Avancés Combinés
############################################################
set -e
echo "================================================"
echo "  Exécution TPs 08-15 (Advanced Topics)"
echo "  $(date)"
echo "================================================"

# TP08: RMAN Backup/Recovery
cat > /tmp/tp08_rman.sh << 'EOSQL'
echo "===== TP08: RMAN BACKUP ====="
su - oracle << 'EOF'
rman target / << 'RMANSCRIPT'
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE DEVICE TYPE DISK PARALLELISM 2;
SHOW ALL;

BACKUP DATABASE PLUS ARCHIVELOG;
LIST BACKUP SUMMARY;
EXIT
RMANSCRIPT
EOF
echo "✓ TP08 RMAN Backup terminé"
EOSQL

# TP09: Data Guard Concepts (théorique - pas de vrai standby)
cat > /tmp/tp09_dataguard.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
PROMPT ===== TP09: DATA GUARD SETUP (Simulation) =====
-- Activer Force Logging
ALTER DATABASE FORCE LOGGING;
PROMPT ✓ Force Logging activé

-- Vérifier configuration Data Guard
SELECT name, value FROM v$parameter WHERE name LIKE '%log_archive%';

-- Créer standby controlfile
ALTER DATABASE CREATE STANDBY CONTROLFILE AS '/tmp/standby_control.ctl';
PROMPT ✓ Standby controlfile créé

SELECT 'Data Guard Ready (simulation)' as status FROM dual;
EXIT
EOSQL

# TP10: Performance Tuning
cat > /tmp/tp10_tuning.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
ALTER SESSION SET CONTAINER=GDCPDB;

PROMPT ===== TP10: PERFORMANCE TUNING =====
-- Créer table de test
CREATE TABLE app_owner.perf_test AS 
SELECT LEVEL as id, DBMS_RANDOM.STRING('A', 100) as data 
FROM dual CONNECT BY LEVEL <= 10000;

PROMPT ✓ Table perf_test créée (10000 lignes)

-- Sans index
SET TIMING ON
SELECT COUNT(*) FROM app_owner.perf_test WHERE id = 5000;
SET TIMING OFF

-- Créer index
CREATE INDEX app_owner.idx_perf_id ON app_owner.perf_test(id);
PROMPT ✓ Index créé

-- Avec index
SET TIMING ON
SELECT COUNT(*) FROM app_owner.perf_test WHERE id = 5000;
SET TIMING OFF

-- Statistiques
EXEC DBMS_STATS.GATHER_TABLE_STATS('APP_OWNER', 'PERF_TEST');
PROMPT ✓ Statistiques collectées

-- AWR Snapshot
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT();
PROMPT ✓ AWR Snapshot créé

SELECT 'Tuning concepts demonstrated' FROM dual;
EXIT
EOSQL

# TP11: Patching (concepts)
cat > /tmp/tp11_patching.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
PROMPT ===== TP11: PATCHING =====
COL action_time FORMAT A20
COL action FORMAT A30
COL version FORMAT A20

-- Historique des patches
SELECT action_time, action, version, comments 
FROM dba_registry_sqlpatch 
ORDER BY action_time DESC
FETCH FIRST 10 ROWS ONLY;

-- Version actuelle
SELECT banner FROM v$version;

SELECT 'Patch history reviewed' FROM dual;
EXIT
EOSQL

# TP12: Multitenant
cat > /tmp/tp12_multitenant.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
PROMPT ===== TP12: MULTITENANT =====

-- Lister PDBs
SHOW PDBS;

-- Créer nouveau PDB
CREATE PLUGGABLE DATABASE testpdb ADMIN USER pdbadmin IDENTIFIED BY Pdb123
  FILE_NAME_CONVERT=('/GDCPDB/','/TESTPDB/');
  
ALTER PLUGGABLE DATABASE testpdb OPEN;
ALTER PLUGGABLE DATABASE testpdb SAVE STATE;
PROMPT ✓ PDB TESTPDB créé

-- Informations CDB/PDB
COL name FORMAT A20
COL open_mode FORMAT A15
SELECT con_id, name, open_mode, total_size/1024/1024 as size_mb 
FROM v$containers ORDER BY con_id;

SELECT 'Multitenant architecture demonstrated' FROM dual;
EXIT
EOSQL

# TP13: AI Foundations (concepts)
cat > /tmp/tp13_ai.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
ALTER SESSION SET CONTAINER=GDCPDB;

PROMPT ===== TP13: AI FOUNDATIONS =====
-- Activer AI Vector Search features (19c bases)
CREATE TABLE app_owner.documents (
  doc_id NUMBER PRIMARY KEY,
  title VARCHAR2(200),
  content CLOB,
  embedding VARCHAR2(4000),
  created_date DATE
);

INSERT INTO app_owner.documents VALUES 
  (1, 'Oracle Database', 'Enterprise database system', NULL, SYSDATE);
INSERT INTO app_owner.documents VALUES 
  (2, 'AI and ML', 'Artificial Intelligence concepts', NULL, SYSDATE);
COMMIT;

PROMPT ✓ AI document structure créée

-- Text indexing simulation
CREATE INDEX app_owner.idx_doc_content ON app_owner.documents(content) 
  INDEXTYPE IS CTXSYS.CONTEXT;
PROMPT ✓ Text index créé

SELECT 'AI foundations ready' FROM dual;
EXIT
EOSQL

# TP14: Concurrency & Locking
cat > /tmp/tp14_concurrency.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
ALTER SESSION SET CONTAINER=GDCPDB;

PROMPT ===== TP14: CONCURRENCY AND LOCKING =====
-- Afficher locks actuels
COL object_name FORMAT A30
SELECT sess.sid, sess.serial#, lo.oracle_username, 
       ao.object_name, lo.locked_mode
FROM v$locked_object lo, dba_objects ao, v$session sess
WHERE ao.object_id = lo.object_id
AND lo.session_id = sess.sid
AND ROWNUM <= 5;

-- Deadlock detection
SELECT name, value FROM v$sysstat 
WHERE name LIKE '%deadlock%';

-- Transaction info
SELECT addr, start_time, status FROM v$transaction;

SELECT 'Concurrency mechanisms reviewed' FROM dual;
EXIT
EOSQL

# TP15: ASM & RAC Concepts
cat > /tmp/tp15_asm.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
PROMPT ===== TP15: ASM & RAC CONCEPTS =====

-- Vérifier si ASM est utilisé
SELECT name, value FROM v$parameter 
WHERE name IN ('asm_diskgroups', 'asm_diskstring', 'cluster_database');

-- Afficher filesystem actuel
SELECT tablespace_name, file_name 
FROM dba_data_files 
WHERE ROWNUM <= 3;

PROMPT
PROMPT === Storage Architecture ===
SELECT SUM(bytes)/1024/1024/1024 as total_gb 
FROM dba_data_files;

PROMPT
PROMPT Note: Cette installation utilise filesystem standard.
PROMPT ASM/RAC nécessiterait une installation cluster.
SELECT 'ASM/RAC concepts reviewed' FROM dual;
EXIT
EOSQL

# Exécution séquentielle
echo ""
bash /tmp/tp08_rman.sh 2>&1 | tee /tmp/tp08_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp09_dataguard.sql" 2>&1 | tee /tmp/tp09_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp10_tuning.sql" 2>&1 | tee /tmp/tp10_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp11_patching.sql" 2>&1 | tee /tmp/tp11_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp12_multitenant.sql" 2>&1 | tee /tmp/tp12_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp13_ai.sql" 2>&1 | tee /tmp/tp13_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp14_concurrency.sql" 2>&1 | tee /tmp/tp14_output.log
echo ""
su - oracle -c "sqlplus / as sysdba @/tmp/tp15_asm.sql" 2>&1 | tee /tmp/tp15_output.log

echo ""
echo "================================================"
echo "  TOUS LES TPs TERMINÉS (TP08-TP15)"
echo "================================================"
echo "Logs disponibles: /tmp/tp0[8-15]_output.log"
