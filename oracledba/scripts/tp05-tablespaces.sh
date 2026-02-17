#!/bin/bash
############################################################
# TP05: Gestion du Stockage - Tablespaces
# Rocky Linux 8
############################################################

set -e
echo "============================================"
echo "  TP05: Gestion du Stockage"
echo "  $(date)"
echo "============================================"
echo ""

cat > /tmp/tp05_tablespaces.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
SET SERVEROUTPUT ON

PROMPT ===== CONFIGURATION ACTUELLE TABLESPACES =====
COL tablespace_name FORMAT A20
COL file_name FORMAT A60
COL size_mb FORMAT 999,999
SELECT tablespace_name, status, contents 
FROM dba_tablespaces 
ORDER BY tablespace_name;

PROMPT
PROMPT === Fichiers de données ===
SELECT tablespace_name, file_name, bytes/1024/1024 as size_mb, autoextensible
FROM dba_data_files
ORDER BY tablespace_name;

PROMPT
PROMPT ===== TP05.1: CRÉATION TABLESPACES =====

-- Créer répertoire pour les tablespaces
!mkdir -p /u01/app/oracle/oradata/GDCPROD/tbs

-- Tablespace PERMANENT pour données applicatives
CREATE TABLESPACE TBS_DATA
  DATAFILE '/u01/app/oracle/oradata/GDCPROD/tbs/tbs_data01.dbf' SIZE 100M
  AUTOEXTEND ON NEXT 10M MAXSIZE 500M
  EXTENT MANAGEMENT LOCAL AUTOALLOCATE
  SEGMENT SPACE MANAGEMENT AUTO;

PROMPT ✓ TBS_DATA créé

-- Tablespace TEMPORARY
CREATE TEMPORARY TABLESPACE TEMP_BIG
  TEMPFILE '/u01/app/oracle/oradata/GDCPROD/tbs/temp_big01.tmp' SIZE 50M
  AUTOEXTEND ON NEXT 10M MAXSIZE 200M;

PROMPT ✓ TEMP_BIG créé

-- Tablespace UNDO
CREATE UNDO TABLESPACE UNDOTBS2
  DATAFILE '/u01/app/oracle/oradata/GDCPROD/tbs/undotbs2_01.dbf' SIZE 100M
  AUTOEXTEND ON NEXT 10M MAXSIZE 500M;

PROMPT ✓ UNDOTBS2 créé

PROMPT
PROMPT ===== TP05.2: MODIFICATION TABLESPACES =====

-- Ajouter fichier à tablespace existant
ALTER TABLESPACE TBS_DATA ADD DATAFILE 
  '/u01/app/oracle/oradata/GDCPROD/tbs/tbs_data02.dbf' SIZE 50M;

PROMPT ✓ Fichier ajouté à TBS_DATA

-- Redimensionner un fichier
ALTER DATABASE DATAFILE '/u01/app/oracle/oradata/GDCPROD/tbs/tbs_data02.dbf' 
  RESIZE 75M;

PROMPT ✓ Fichier redimensionné

-- Mettre tablespace en OFFLINE/ONLINE
ALTER TABLESPACE TBS_DATA OFFLINE;
ALTER TABLESPACE TBS_DATA ONLINE;

PROMPT ✓ Tablespace TBS_DATA testé OFFLINE/ONLINE

PROMPT
PROMPT ===== TP05.3: GESTION QUOTAS UTILISATEURS =====

-- Créer utilisateur de test
CREATE USER app_user IDENTIFIED BY App123
  DEFAULT TABLESPACE TBS_DATA
  TEMPORARY TABLESPACE TEMP_BIG
  QUOTA 50M ON TBS_DATA;

GRANT CONNECT, RESOURCE TO app_user;

PROMPT ✓ Utilisateur app_user créé avec quota 50M

-- Créer table pour tester l'espace
CREATE TABLE app_user.test_quota (
  id NUMBER,
  data VARCHAR2(4000)
);

-- Insérer données pour consommer espace
BEGIN
  FOR i IN 1..1000 LOOP
    INSERT INTO app_user.test_quota VALUES (i, RPAD('X', 4000, 'X'));
  END LOOP;
  COMMIT;
END;
/

PROMPT ✓ Table test créée avec 1000 lignes

PROMPT
PROMPT ===== TP05.4: MONITORING ESPACE =====

PROMPT === Utilisation par tablespace ===
COL tablespace FORMAT A20
SELECT 
  tablespace_name as tablespace,
  ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
  COUNT(*) as files
FROM dba_data_files
GROUP BY tablespace_name
UNION ALL
SELECT 
  tablespace_name,
  ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
  COUNT(*)
FROM dba_temp_files
GROUP BY tablespace_name
ORDER BY 1;

PROMPT
PROMPT === Espace libre ===
SELECT 
  tablespace_name,
  ROUND(SUM(bytes)/1024/1024, 2) as free_mb
FROM dba_free_space
GROUP BY tablespace_name
ORDER BY tablespace_name;

PROMPT
PROMPT === Quotas utilisateurs ===
COL username FORMAT A20
COL tablespace_name FORMAT A20
SELECT username, tablespace_name, 
       bytes/1024/1024 as used_mb,
       max_bytes/1024/1024 as quota_mb
FROM dba_ts_quotas
WHERE username = 'APP_USER';

PROMPT
PROMPT ===== TP05.5: TABLESPACES EN READ ONLY =====

-- Mettre TBS_DATA en read only
ALTER TABLESPACE TBS_DATA READ ONLY;
PROMPT ✓ TBS_DATA en READ ONLY

-- Vérifier statut
SELECT tablespace_name, status FROM dba_tablespaces 
WHERE tablespace_name = 'TBS_DATA';

-- Remettre en READ WRITE
ALTER TABLESPACE TBS_DATA READ WRITE;
PROMPT ✓ TBS_DATA remis en READ WRITE

PROMPT
PROMPT ===== RÉSUMÉ TP05 =====
SELECT 'Tablespaces permanents: ' || COUNT(*) as info 
FROM dba_tablespaces WHERE contents = 'PERMANENT'
UNION ALL
SELECT 'Tablespaces temporaires: ' || COUNT(*) 
FROM dba_tablespaces WHERE contents = 'TEMPORARY'
UNION ALL
SELECT 'Tablespaces UNDO: ' || COUNT(*) 
FROM dba_tablespaces WHERE contents = 'UNDO'
UNION ALL
SELECT 'Total fichiers de données: ' || COUNT(*) 
FROM dba_data_files
UNION ALL
SELECT 'Utilisateurs avec quotas: ' || COUNT(DISTINCT username) 
FROM dba_ts_quotas;

EXIT
EOSQL

echo "[1/1] Exécution TP05 - Gestion Tablespaces..."
su - oracle -c "sqlplus / as sysdba @/tmp/tp05_tablespaces.sql" 2>&1 | tee /tmp/tp05_output.log

echo ""
echo "============================================"
echo "  TP05 TERMINÉ"
echo "============================================"
echo "Logs: /tmp/tp05_output.log"
