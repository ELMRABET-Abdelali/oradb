#!/bin/bash
# TP05 - Gestion du Stockage
# Tablespaces, Datafiles, OMF
# Rocky Linux 8 - Oracle 19c

set -e

echo "================================================"
echo "  TP05: Gestion du Stockage"
echo "  Tablespaces et Datafiles"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/6] État actuel des tablespaces..."

sqlplus -s / as sysdba << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100
SELECT tablespace_name, status, contents, extent_management 
FROM dba_tablespaces 
ORDER BY tablespace_name;

SELECT tablespace_name, file_name, bytes/1024/1024 MB, autoextensible 
FROM dba_data_files 
ORDER BY tablespace_name;
EOSQL

echo ""
echo "[2/6] Création tablespace GDCDATA pour données métier..."

sqlplus / as sysdba << 'EOSQL'
CREATE TABLESPACE gdcdata
  DATAFILE '/u01/app/oracle/oradata/GDCPROD/gdcdata01.dbf' 
  SIZE 100M
  AUTOEXTEND ON NEXT 10M MAXSIZE 1G
  EXTENT MANAGEMENT LOCAL
  SEGMENT SPACE MANAGEMENT AUTO;

-- Vérifier
SELECT tablespace_name, file_name, bytes/1024/1024 MB, maxbytes/1024/1024 MAX_MB
FROM dba_data_files 
WHERE tablespace_name = 'GDCDATA';
EXIT;
EOSQL

echo "✓ Tablespace GDCDATA créé (100MB, autoextend 1GB)"

echo ""
echo "[3/6] Ajout datafile supplémentaire à GDCDATA..."

sqlplus / as sysdba << 'EOSQL'
ALTER TABLESPACE gdcdata
  ADD DATAFILE '/u01/app/oracle/oradata/GDCPROD/gdcdata02.dbf'
  SIZE 50M
  AUTOEXTEND ON NEXT 5M MAXSIZE 500M;

-- Vérifier
SELECT file_name, bytes/1024/1024 MB FROM dba_data_files 
WHERE tablespace_name = 'GDCDATA'
ORDER BY file_name;
EXIT;
EOSQL

echo "✓ Second datafile ajouté (50MB, autoextend 500MB)"

echo ""
echo "[4/6] Création TEMP tablespace supplémentaire..."

sqlplus / as sysdba << 'EOSQL'
CREATE TEMPORARY TABLESPACE temp2
  TEMPFILE '/u01/app/oracle/oradata/GDCPROD/temp02.dbf'
  SIZE 50M
  AUTOEXTEND ON NEXT 10M MAXSIZE 500M;

-- Vérifier
SELECT tablespace_name, file_name, bytes/1024/1024 MB 
FROM dba_temp_files
ORDER BY tablespace_name;
EXIT;
EOSQL

echo "✓ Tablespace temporaire TEMP2 créé"

echo ""
echo "[5/6] Configuration OMF (Oracle Managed Files)..."

sqlplus / as sysdba << 'EOSQL'
-- Définir emplacements par défaut
ALTER SYSTEM SET db_create_file_dest='/u01/app/oracle/oradata' SCOPE=BOTH;
ALTER SYSTEM SET db_recovery_file_dest='/u01/app/oracle/fast_recovery_area' SCOPE=BOTH;
ALTER SYSTEM SET db_recovery_file_dest_size=10G SCOPE=BOTH;

-- Créer tablespace avec OMF (sans spécifier datafile)
CREATE TABLESPACE omf_test;

-- Vérifier localisation automatique
SELECT file_name FROM dba_data_files WHERE tablespace_name = 'OMF_TEST';

SHOW PARAMETER db_create_file_dest;
SHOW PARAMETER db_recovery_file_dest;

EXIT;
EOSQL

echo "✓ OMF configuré et testé"

echo ""
echo "[6/6] Simulation croissance et resize..."

sqlplus / as sysdba << 'EOSQL'
-- Créer table dans GDCDATA pour forcer croissance
CREATE TABLE test_growth (
    id NUMBER,
    data VARCHAR2(4000)
) TABLESPACE gdcdata;

-- Insérer données
BEGIN
    FOR i IN 1..10000 LOOP
        INSERT INTO test_growth VALUES (i, RPAD('X', 4000, 'X'));
    END LOOP;
    COMMIT;
END;
/

-- Vérifier utilisation
SELECT 
    tablespace_name,
    ROUND(SUM(bytes)/1024/1024, 2) AS used_mb
FROM dba_segments
WHERE tablespace_name = 'GDCDATA'
GROUP BY tablespace_name;

-- Resize manuel d'un datafile
ALTER DATABASE DATAFILE '/u01/app/oracle/oradata/GDCPROD/gdcdata01.dbf' 
RESIZE 150M;

-- Vérifier nouvelle taille
SELECT file_name, bytes/1024/1024 MB FROM dba_data_files
WHERE tablespace_name = 'GDCDATA'
ORDER BY file_name;

-- Nettoyer table test
DROP TABLE test_growth PURGE;

EXIT;
EOSQL

echo "✓ Test croissance et resize réussi"

echo ""
echo "================================================"
echo "  TP05 TERMINÉ - Stockage Configuré"
echo "================================================"
echo ""

# Rapport final
sqlplus -s / as sysdba << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100

PROMPT === ESPACE UTILISE PAR TABLESPACE ===
SELECT 
    t.tablespace_name,
    ROUND(SUM(d.bytes)/1024/1024, 2) AS total_mb,
    ROUND(SUM(CASE WHEN d.autoextensible = 'YES' 
              THEN d.maxbytes ELSE d.bytes END)/1024/1024, 2) AS max_mb,
    COUNT(d.file_id) AS files
FROM dba_tablespaces t
LEFT JOIN dba_data_files d ON t.tablespace_name = d.tablespace_name
WHERE t.contents = 'PERMANENT'
GROUP BY t.tablespace_name
ORDER BY 1;

PROMPT
PROMPT === TEMP TABLESPACES ===
SELECT tablespace_name, file_name, bytes/1024/1024 MB
FROM dba_temp_files
ORDER BY tablespace_name;

PROMPT
PROMPT === OMF CONFIGURATION ===
SHOW PARAMETER db_create_file_dest
SHOW PARAMETER db_recovery_file_dest

EXIT;
EOSQL

echo ""
echo "Configuration stockage:"
echo "- Tablespace données: GDCDATA (2 datafiles)"
echo "- Tablespace temp: TEMP, TEMP2"
echo "- OMF: Activé"
echo "- FRA: 10GB"
echo ""
echo "Prochaine étape: TP06 - Sécurité et Accès"
