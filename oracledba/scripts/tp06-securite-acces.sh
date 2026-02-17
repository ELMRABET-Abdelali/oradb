#!/bin/bash
# TP06 - Sécurité et Gestion des Accès
# Users, Roles, Privileges, Profiles
# Rocky Linux 8 - Oracle 19c

set -e

echo "================================================"
echo "  TP06: Sécurité et Gestion des Accès"
echo "  Rocky Linux 8 - Oracle 19c"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/7] Ouverture PDB GDCPDB..."

sqlplus / as sysdba << 'EOSQL'
ALTER PLUGGABLE DATABASE gdcpdb OPEN;
SHOW PDBS;
EXIT;
EOSQL

echo ""
echo "[2/7] Création utilisateurs métier dans PDB..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Utilisateur développeur
CREATE USER dev_user IDENTIFIED BY DevPass123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA 100M ON users;

-- Utilisateur applicatif  
CREATE USER app_user IDENTIFIED BY AppPass123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA 500M ON users;

-- Utilisateur lecture seule
CREATE USER readonly_user IDENTIFIED BY ReadPass123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA 0 ON users;

-- Vérifier
SELECT username, default_tablespace, temporary_tablespace, account_status
FROM dba_users
WHERE username IN ('DEV_USER', 'APP_USER', 'READONLY_USER');

EXIT;
EOSQL

echo "✓ Utilisateurs créés: dev_user, app_user, readonly_user"

echo ""
echo "[3/7] Création rôles personnalisés..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Rôle développeur
CREATE ROLE dev_role;
GRANT CREATE SESSION TO dev_role;
GRANT CREATE TABLE TO dev_role;
GRANT CREATE VIEW TO dev_role;
GRANT CREATE PROCEDURE TO dev_role;
GRANT CREATE SEQUENCE TO dev_role;

-- Rôle applicatif
CREATE ROLE app_role;
GRANT CREATE SESSION TO app_role;
GRANT CREATE TABLE TO app_role;
GRANT CREATE PROCEDURE TO app_role;

-- Rôle lecture seule
CREATE ROLE readonly_role;
GRANT CREATE SESSION TO readonly_role;
GRANT SELECT ANY TABLE TO readonly_role;

-- Assigner rôles aux utilisateurs
GRANT dev_role TO dev_user;
GRANT app_role TO app_user;
GRANT readonly_role TO readonly_user;

-- Vérifier
SELECT grantee, granted_role FROM dba_role_privs
WHERE grantee IN ('DEV_USER', 'APP_USER', 'READONLY_USER');

EXIT;
EOSQL

echo "✓ Rôles créés et assignés"

echo ""
echo "[4/7] Configuration profiles de sécurité..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Profile développeurs (plus flexible)
CREATE PROFILE dev_profile LIMIT
  SESSIONS_PER_USER 3
  CPU_PER_SESSION UNLIMITED
  CONNECT_TIME UNLIMITED
  IDLE_TIME 60
  FAILED_LOGIN_ATTEMPTS 5
  PASSWORD_LIFE_TIME 90
  PASSWORD_REUSE_TIME 365
  PASSWORD_GRACE_TIME 7;

-- Profile applicatif (restrictif)
CREATE PROFILE app_profile LIMIT
  SESSIONS_PER_USER 10
  CPU_PER_SESSION UNLIMITED
  CONNECT_TIME UNLIMITED
  IDLE_TIME 30
  FAILED_LOGIN_ATTEMPTS 3
  PASSWORD_LIFE_TIME 60
  PASSWORD_REUSE_TIME 180
  PASSWORD_GRACE_TIME 3;

-- Assigner profiles
ALTER USER dev_user PROFILE dev_profile;
ALTER USER app_user PROFILE app_profile;
ALTER USER readonly_user PROFILE dev_profile;

-- Vérifier
SELECT username, profile, account_status FROM dba_users
WHERE username IN ('DEV_USER', 'APP_USER', 'READONLY_USER');

EXIT;
EOSQL

echo "✓ Profiles configurés"

echo ""
echo "[5/7] Test connexions et privilèges..."

# Test dev_user
echo "Test connexion dev_user..."
sqlplus -s dev_user/DevPass123@localhost:1521/gdcpdb << 'EOSQL'
-- Créer table de test
CREATE TABLE test_dev (id NUMBER, name VARCHAR2(50));
INSERT INTO test_dev VALUES (1, 'Test');
COMMIT;
SELECT * FROM test_dev;
DROP TABLE test_dev;
EXIT;
EOSQL

echo "✓ dev_user: CREATE TABLE OK"

# Test readonly_user
echo "Test connexion readonly_user..."
sqlplus -s readonly_user/ReadPass123@localhost:1521/gdcpdb << 'EOSQL'
-- Vérifier accès lecture seule
SELECT COUNT(*) FROM dba_tables WHERE rownum = 1;
EXIT;
EOSQL

echo "✓ readonly_user: SELECT OK"

echo ""
echo "[6/7] Configuration audit de sécurité..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Activer audit unifié
ALTER SYSTEM SET audit_trail=DB,EXTENDED SCOPE=SPFILE;

-- Policies d'audit
AUDIT CREATE TABLE BY dev_user;
AUDIT DROP TABLE BY dev_user;
AUDIT SELECT TABLE BY readonly_user;

-- Vérifier configuration
SELECT user_name, audit_option, success, failure 
FROM dba_stmt_audit_opts;

EXIT;
EOSQL

echo "✓ Audit configuré (redémarrage requis pour activation complète)"

echo ""
echo "[7/7] Configuration tnsnames.ora pour connexions..."

cat > $ORACLE_HOME/network/admin/tnsnames.ora << 'EOF'
GDCPROD =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = localhost)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = GDCPROD)
    )
  )

GDCPDB =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = localhost)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = gdcpdb)
    )
  )
EOF

# Test tnsping
tnsping GDCPDB 3

echo "✓ tnsnames.ora configuré"

echo ""
echo "================================================"
echo "  TP06 TERMINÉ - Sécurité Configurée"
echo "================================================"
echo ""

# Rapport final
sqlplus -s / as sysdba << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100
ALTER SESSION SET CONTAINER=gdcpdb;

PROMPT === UTILISATEURS CRÉÉS ===
SELECT username, account_status, profile, default_tablespace
FROM dba_users
WHERE username IN ('DEV_USER', 'APP_USER', 'READONLY_USER');

PROMPT
PROMPT === RÔLES ASSIGNÉS ===
SELECT grantee, granted_role FROM dba_role_privs
WHERE grantee IN ('DEV_USER', 'APP_USER', 'READONLY_USER')
ORDER BY grantee;

PROMPT
PROMPT === PROFILES LIMITES ===
SELECT profile, resource_name, limit
FROM dba_profiles
WHERE profile IN ('DEV_PROFILE', 'APP_PROFILE')
  AND resource_name IN ('SESSIONS_PER_USER', 'IDLE_TIME', 'FAILED_LOGIN_ATTEMPTS')
ORDER BY profile, resource_name;

EXIT;
EOSQL

echo ""
echo "Comptes créés:"
echo "- dev_user/DevPass123 (dev_role, dev_profile)"
echo "- app_user/AppPass123 (app_role, app_profile)"
echo "- readonly_user/ReadPass123 (readonly_role)"
echo ""
echo "Connexion exemple:"
echo "  sqlplus dev_user/DevPass123@localhost:1521/gdcpdb"
echo ""
echo "Prochaine étape: TP07 - Flashback Technologies"
