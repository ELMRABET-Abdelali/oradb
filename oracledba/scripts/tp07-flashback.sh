#!/bin/bash
###########################################################
# TP07: Flashback Technologies
############################################################
set -e
echo "============================================"
echo "  TP07: Flashback Technologies"
echo "  $(date)"
echo "============================================"

cat > /tmp/tp07_flashback.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
ALTER SESSION SET CONTAINER=GDCPDB;

PROMPT ===== TP07.1: FLASHBACK QUERY (AS OF) =====
-- Créer table de test
CREATE TABLE app_owner.employees (
  emp_id NUMBER PRIMARY KEY,
  name VARCHAR2(50),
  salary NUMBER,
  updated_at TIMESTAMP DEFAULT SYSTIMESTAMP
);

INSERT INTO app_owner.employees VALUES (1, 'Alice', 50000, SYSTIMESTAMP);
INSERT INTO app_owner.employees VALUES (2, 'Bob', 60000, SYSTIMESTAMP);
INSERT INTO app_owner.employees VALUES (3, 'Charlie', 55000, SYSTIMESTAMP);
COMMIT;

-- Capturer SCN et timestamp
VARIABLE v_scn NUMBER
VARIABLE v_time TIMESTAMP
BEGIN
  SELECT current_scn INTO :v_scn FROM v$database;
  :v_time := SYSTIMESTAMP;
  DBMS_OUTPUT.PUT_LINE('SCN actuel: ' || :v_scn);
END;
/

-- Modifier données
UPDATE app_owner.employees SET salary = salary * 1.1 WHERE emp_id = 1;
DELETE FROM app_owner.employees WHERE emp_id = 3;
COMMIT;
PROMPT ✓ Données modifi\u00e9es (UPDATE + DELETE)

-- Flashback Query
PROMPT === Données actuelles ===
SELECT * FROM app_owner.employees ORDER BY emp_id;

PROMPT
PROMPT === Données avant modification (Flashback AS OF SCN) ===
SELECT * FROM app_owner.employees AS OF SCN :v_scn ORDER BY emp_id;

PROMPT
PROMPT ===== TP07.2: FLASHBACK VERSION QUERY =====
SELECT versions_startscn, versions_endscn, versions_operation, emp_id, name, salary
FROM app_owner.employees 
VERSIONS BETWEEN SCN MINVALUE AND MAXVALUE
WHERE emp_id = 1
ORDER BY versions_startscn NULLS FIRST;

PROMPT
PROMPT ===== TP07.3: FLASHBACK TABLE =====
-- Activer row movement
ALTER TABLE app_owner.employees ENABLE ROW MOVEMENT;
PROMPT ✓ ROW MOVEMENT activé

-- Flashback table à l'ancien SCN
FLASHBACK TABLE app_owner.employees TO SCN :v_scn;
PROMPT ✓ Table restaurée via FLASHBACK TABLE

PROMPT === Données après FLASHBACK TABLE ===
SELECT * FROM app_owner.employees ORDER BY emp_id;

PROMPT
PROMPT ===== TP07.4: FLASHBACK DROP (RECYCLE BIN) =====
-- Supprimer table
DROP TABLE app_owner.employees;
PROMPT ✓ Table supprimée

-- Vérifier recycle bin
PROMPT === Recycle Bin ===
COL object_name FORMAT A30
COL original_name FORMAT A20
SELECT object_name, original_name, type, droptime 
FROM dba_recyclebin 
WHERE owner = 'APP_OWNER';

-- Restaurer depuis recycle bin
FLASHBACK TABLE app_owner.employees TO BEFORE DROP;
PROMPT ✓ Table restaurée depuis RECYCLE BIN

SELECT COUNT(*) as row_count FROM app_owner.employees;

PROMPT
PROMPT ===== TP07.5: FLASHBACK DATABASE =====
ALTER SESSION SET CONTAINER=CDB\$ROOT;

-- Vérifier si Flashback Database est activé
PROMPT === Statut Flashback Database ===
SELECT flashback_on, log_mode FROM v\$database;

-- Activer Flashback Database (si pas déjà fait)
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE FLASHBACK ON;
ALTER DATABASE OPEN;
PROMPT ✓ Flashback Database activé

-- Vérifier point de restauration le plus ancien
SELECT oldest_flashback_scn, oldest_flashback_time 
FROM v\$flashback_database_log;

PROMPT
PROMPT ===== TP07.6: GUARANTEED RESTORE POINT =====
CREATE RESTORE POINT before_changes GUARANTEE FLASHBACK DATABASE;
PROMPT ✓ Restore Point créé

-- Lister restore points
COL name FORMAT A30
SELECT name, scn, time, guarantee_flashback_database, storage_size
FROM v\$restore_point;

PROMPT
PROMPT ===== RÉSUMÉ TP07 =====
ALTER SESSION SET CONTAINER=GDCPDB;
SELECT 'Tables app_owner: ' || COUNT(*) as info FROM dba_tables WHERE owner = 'APP_OWNER'
UNION ALL
SELECT 'Objects in recycle bin: ' || COUNT(*) FROM dba_recyclebin WHERE owner = 'APP_OWNER';

ALTER SESSION SET CONTAINER=CDB\$ROOT;
SELECT 'Flashback Database: ' || flashback_on FROM v\$database
UNION ALL
SELECT 'Archive Log Mode: ' || log_mode FROM v\$database
UNION ALL
SELECT 'Restore Points: ' || COUNT(*) FROM v\$restore_point;

EXIT
EOSQL

echo "[1/1] Exécution TP07..."
su - oracle -c "sqlplus / as sysdba @/tmp/tp07_flashback.sql" 2>&1 | tee /tmp/tp07_output.log

echo ""
echo "============================================"
echo "  TP07 TERMINÉ"
echo "============================================"
