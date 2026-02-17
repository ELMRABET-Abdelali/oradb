#!/bin/bash
# TP14 - Mobilité des Données et Gestion Concurrence
# Data Pump, Transportable Tablespaces, Locking
# Rocky Linux 8 - Oracle 19c

set -e

echo "================================================"
echo "  TP14: Mobilité et Concurrence"
echo "  Rocky Linux 8 - Oracle 19c"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/7] Configuration Data Pump (expdp/impdp)..."

# Créer directory pour Data Pump
sqlplus / as sysdba << 'EOSQL'
-- Créer directory object
CREATE OR REPLACE DIRECTORY dp_dir AS '/u01/app/oracle/admin/datapump';

-- Vérifier
SELECT directory_name, directory_path FROM dba_directories 
WHERE directory_name = 'DP_DIR';

-- Grant aux utilisateurs
ALTER SESSION SET CONTAINER=gdcpdb;
GRANT READ, WRITE ON DIRECTORY dp_dir TO dev_user;
GRANT READ, WRITE ON DIRECTORY dp_dir TO mluser;

EXIT;
EOSQL

# Créer répertoire physique
mkdir -p /u01/app/oracle/admin/datapump
chmod 755 /u01/app/oracle/admin/datapump

echo "✓ Data Pump directory configuré"

echo ""
echo "[2/7] Export schema complet avec Data Pump..."

echo "Export du schéma MLUSER..."

expdp mluser/MlPass123@localhost:1521/gdcpdb \
  DIRECTORY=dp_dir \
  DUMPFILE=mluser_export_%U.dmp \
  LOGFILE=mluser_export.log \
  SCHEMAS=mluser \
  PARALLEL=2 \
  COMPRESSION=ALL \
  FILESIZE=100M

echo "✓ Export terminé"
ls -lh /u01/app/oracle/admin/datapump/mluser_export*

echo ""
echo "[3/7] Import Data Pump dans autre PDB..."

sqlplus / as sysdba << 'EOSQL'
-- Préparer PDB2 pour import
ALTER SESSION SET CONTAINER=pdb2;

-- Créer utilisateur destination
CREATE USER mluser_copy IDENTIFIED BY MlCopy123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON users;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW TO mluser_copy;

-- Grant directory
GRANT READ, WRITE ON DIRECTORY dp_dir TO mluser_copy;

EXIT;
EOSQL

echo "Import dans PDB2..."

impdp system/SystemOracle123@localhost:1521/pdb2 \
  DIRECTORY=dp_dir \
  DUMPFILE=mluser_export_%U.dmp \
  LOGFILE=mluser_import_pdb2.log \
  REMAP_SCHEMA=mluser:mluser_copy \
  PARALLEL=2

echo "✓ Import terminé dans PDB2"

echo ""
echo "[4/7] Export/Import table individuelle (NETWORK_LINK)..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=pdb2;

-- Créer database link vers GDCPDB
CREATE PUBLIC DATABASE LINK gdcpdb_link
  CONNECT TO mluser IDENTIFIED BY MlPass123
  USING '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SERVICE_NAME=gdcpdb)))';

-- Test link
SELECT COUNT(*) FROM customer_data@gdcpdb_link;

-- Import direct via network
-- Note: Nécessite expdp avec NETWORK_LINK
EXIT;
EOSQL

echo "✓ Database link créé"

echo ""
echo "[5/7] Transportable Tablespaces (TTS)..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Créer tablespace à transporter
CREATE TABLESPACE tts_test
  DATAFILE '/u01/app/oracle/oradata/GDCPROD/tts_test01.dbf'
  SIZE 50M
  AUTOEXTEND ON;

-- Créer table dans ce tablespace
CREATE TABLE transport_test (
    id NUMBER PRIMARY KEY,
    data VARCHAR2(100)
) TABLESPACE tts_test;

INSERT INTO transport_test 
SELECT LEVEL, 'Data ' || LEVEL 
FROM dual CONNECT BY LEVEL <= 1000;
COMMIT;

-- Mettre tablespace en READ ONLY
ALTER TABLESPACE tts_test READ ONLY;

-- Vérifier compatibilité transport
EXEC DBMS_TTS.TRANSPORT_SET_CHECK('TTS_TEST', TRUE);

-- Voir violations
SELECT * FROM transport_set_violations;

EXIT;
EOSQL

echo "✓ Tablespace préparé pour transport"

echo ""
echo "[6/7] Tests de Concurrence et Locking..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Créer table de test concurrence
CREATE TABLE lock_test (
    id NUMBER PRIMARY KEY,
    value NUMBER,
    updated_by VARCHAR2(50),
    update_time TIMESTAMP
);

INSERT INTO lock_test VALUES (1, 100, 'INITIAL', SYSTIMESTAMP);
INSERT INTO lock_test VALUES (2, 200, 'INITIAL', SYSTIMESTAMP);
INSERT INTO lock_test VALUES (3, 300, 'INITIAL', SYSTIMESTAMP);
COMMIT;

-- Simuler lock (SELECT FOR UPDATE)
DECLARE
    v_value NUMBER;
BEGIN
    -- Session 1: Lock row
    SELECT value INTO v_value FROM lock_test 
    WHERE id = 1 FOR UPDATE;
    
    DBMS_OUTPUT.PUT_LINE('Row locked, value: ' || v_value);
    
    -- Attendre (simuler long processing)
    DBMS_LOCK.SLEEP(2);
    
    -- Update
    UPDATE lock_test 
    SET value = value + 50, 
        updated_by = 'Session1',
        update_time = SYSTIMESTAMP
    WHERE id = 1;
    
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Update committed');
END;
/

-- Vérifier locks actuels
SELECT 
    s.sid,
    s.serial#,
    s.username,
    s.status,
    s.schemaname,
    l.type,
    l.lmode,
    l.request,
    l.ctime
FROM v$session s
JOIN v$lock l ON s.sid = l.sid
WHERE s.username IS NOT NULL
  AND s.username != 'SYS'
ORDER BY s.username, l.ctime DESC;

-- Test NOWAIT
DECLARE
    v_value NUMBER;
BEGIN
    SELECT value INTO v_value 
    FROM lock_test 
    WHERE id = 2 
    FOR UPDATE NOWAIT;
    
    UPDATE lock_test SET value = value + 100 WHERE id = 2;
    COMMIT;
    DBMS_OUTPUT.PUT_LINE('NOWAIT succeeded');
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Lock conflict: ' || SQLERRM);
END;
/

EXIT;
EOSQL

echo "✓ Tests concurrence exécutés"

echo ""
echo "[7/7] Monitoring des locks et sessions..."

sqlplus -s / as sysdba << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100
ALTER SESSION SET CONTAINER=gdcpdb;

PROMPT === SESSIONS ACTIVES ===
SELECT sid, serial#, username, status, schemaname, 
       osuser, machine, program,
       logon_time
FROM v$session
WHERE username IS NOT NULL
  AND username NOT IN ('SYS', 'SYSTEM')
ORDER BY logon_time DESC;

PROMPT
PROMPT === LOCKS ACTIFS ===
SELECT 
    l.sid,
    s.username,
    s.osuser,
    l.type AS lock_type,
    DECODE(l.lmode,
        0, 'None',
        1, 'Null',
        2, 'Row-S',
        3, 'Row-X',
        4, 'Share',
        5, 'S/Row-X',
        6, 'Exclusive',
        l.lmode) AS lock_mode,
    DECODE(l.request,
        0, 'None',
        1, 'Null',
        2, 'Row-S',
        3, 'Row-X',
        4, 'Share',
        5, 'S/Row-X',
        6, 'Exclusive',
        l.request) AS lock_request,
    l.ctime AS time_held
FROM v$lock l
JOIN v$session s ON l.sid = s.sid
WHERE s.username IS NOT NULL
ORDER BY l.ctime DESC;

PROMPT
PROMPT === BLOCKING SESSIONS (si existe) ===
SELECT 
    s1.sid AS blocking_sid,
    s1.username AS blocking_user,
    s2.sid AS blocked_sid,
    s2.username AS blocked_user,
    s1.status AS blocker_status,
    s2.status AS blocked_status
FROM v$session s1
JOIN v$session s2 ON s1.sid = s2.blocking_session
WHERE s2.blocking_session IS NOT NULL;

EXIT;
EOSQL

echo ""
echo "================================================"
echo "  TP14 TERMINÉ - Mobilité et Concurrence OK"
echo "================================================"
echo ""

echo "Opérations de mobilité:"
echo "- Data Pump: Export/Import schéma complet"
echo "- Network Link: Import direct entre PDBs"
echo "- TTS: Tablespace transportable préparé"
echo ""
ls -lh /u01/app/oracle/admin/datapump/*.dmp 2>/dev/null | tail -5

echo ""
echo "Gestion concurrence:"
echo "- Locks: SELECT FOR UPDATE testé"
echo "- NOWAIT: Handling immediate lock conflicts"
echo "- Monitoring: v\$lock, v\$session queries"
echo ""
echo "Vues utiles:"
echo "  - v\$session: Sessions actives"
echo "  - v\$lock: Locks actuels"
echo "  - dba_blockers: Sessions bloquantes"
echo "  - dba_waiters: Sessions en attente"
echo ""
echo "Prochaine étape: TP15 - ASM et RAC Concepts"
