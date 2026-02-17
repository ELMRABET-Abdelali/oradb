#!/bin/bash
############################################################
# TP06: Sécurité et Gestion des Accès
# Rocky Linux 8
############################################################

set -e
echo "============================================"
echo "  TP06: Sécurité et Accès"
echo "  $(date)"
echo "============================================"
echo ""

cat > /tmp/tp06_security.sql << 'EOSQL'
SET PAGESIZE 100 LINESIZE 150
SET SERVEROUTPUT ON

PROMPT ===== TP06.1: CRÉATION UTILISATEURS CDB =====

-- Utilisateurs communs (préfixe C##)
CREATE USER c##dba_admin IDENTIFIED BY Dba123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  CONTAINER=ALL;

GRANT DBA TO c##dba_admin CONTAINER=ALL;
PROMPT ✓ c##dba_admin créé avec rôle DBA

CREATE USER c##app_reader IDENTIFIED BY Reader123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  CONTAINER=ALL;

GRANT CONNECT TO c##app_reader CONTAINER=ALL;
PROMPT ✓ c##app_reader créé avec CONNECT

PROMPT
PROMPT ===== TP06.2: CRÉATION UTILISATEURS DANS PDB =====

ALTER SESSION SET CONTAINER=GDCPDB;

-- Utilisateurs locaux dans PDB
CREATE USER app_owner IDENTIFIED BY AppOwner123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON users;

GRANT CONNECT, RESOURCE TO app_owner;
PROMPT ✓ app_owner créé dans GDCPDB

CREATE USER app_user IDENTIFIED BY AppUser123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA 10M ON users;

GRANT CONNECT TO app_user;
PROMPT ✓ app_user créé dans GDCPDB

PROMPT
PROMPT ===== TP06.3: CRÉATION RÔLES PERSONNALISÉS =====

CREATE ROLE app_read_role;
GRANT SELECT ANY TABLE TO app_read_role;
PROMPT ✓ Rôle app_read_role créé

CREATE ROLE app_write_role;
GRANT app_read_role TO app_write_role;
GRANT INSERT ANY TABLE, UPDATE ANY TABLE, DELETE ANY TABLE TO app_write_role;
PROMPT ✓ Rôle app_write_role créé (hérite de app_read_role)

-- Affecter rôles
GRANT app_read_role TO app_user;
GRANT app_write_role TO app_owner;
PROMPT ✓ Rôles affectés aux utilisateurs

PROMPT
PROMPT ===== TP06.4: PROFILES DE RESSOURCES =====

-- Profile restrictif
CREATE PROFILE limited_profile LIMIT
  SESSIONS_PER_USER 2
  CPU_PER_SESSION UNLIMITED
  CPU_PER_CALL 3000
  CONNECT_TIME 480
  IDLE_TIME 30
  FAILED_LOGIN_ATTEMPTS 3
  PASSWORD_LIFE_TIME 90
  PASSWORD_REUSE_TIME 180
  PASSWORD_REUSE_MAX 5
  PASSWORD_LOCK_TIME 1
  PASSWORD_GRACE_TIME 7;

PROMPT ✓ Profile limited_profile créé

-- Affecter profile
ALTER USER app_user PROFILE limited_profile;
PROMPT ✓ Profile affecté à app_user

PROMPT
PROMPT ===== TP06.5: PRIVILEGES OBJET =====

-- Créer schéma de test dans app_owner
BEGIN
  EXECUTE IMMEDIATE 'CREATE TABLE app_owner.customers (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    email VARCHAR2(100),
    created_date DATE
  )';
  
  EXECUTE IMMEDIATE 'CREATE TABLE app_owner.orders (
    order_id NUMBER PRIMARY KEY,
    customer_id NUMBER,
    order_date DATE,
    amount NUMBER(10,2),
    FOREIGN KEY (customer_id) REFERENCES app_owner.customers(id)
  )';
  
  -- Insérer données
  FOR i IN 1..10 LOOP
    EXECUTE IMMEDIATE 'INSERT INTO app_owner.customers VALUES (:1, :2, :3, SYSDATE)'
      USING i, 'Customer ' || i, 'cust' || i || '@test.com';
  END LOOP;
  
  FOR i IN 1..20 LOOP
    EXECUTE IMMEDIATE 'INSERT INTO app_owner.orders VALUES (:1, :2, SYSDATE, :3)'
      USING i, MOD(i,10)+1, (i*100);
  END LOOP;
  
  COMMIT;
END;
/

PROMPT ✓ Tables customers et orders créées avec données

-- Donner accès SELECT à app_user
GRANT SELECT ON app_owner.customers TO app_user;
GRANT SELECT ON app_owner.orders TO app_user;
PROMPT ✓ SELECT accordé à app_user sur tables

PROMPT
PROMPT ===== TP06.6: AUDIT =====

-- Activer audit unifié
ALTER SESSION SET CONTAINER=CDB$ROOT;
AUDIT POLICY ORA_SECURECONFIG;
AUDIT POLICY ORA_ACCOUNT_MGMT;
PROMPT ✓ Politiques d'audit activées

ALTER SESSION SET CONTAINER=GDCPDB;

-- Auditer actions spécifiques
AUDIT SELECT ON app_owner.customers BY ACCESS;
AUDIT INSERT, UPDATE, DELETE ON app_owner.orders BY ACCESS;
PROMPT ✓ Audit configuré sur tables sensibles

PROMPT
PROMPT ===== VÉRIFICATIONS =====

PROMPT === Utilisateurs dans PDB ===
COL username FORMAT A20
COL account_status FORMAT A20
COL profile FORMAT A20
SELECT username, account_status, profile, created
FROM dba_users
WHERE username IN ('APP_OWNER', 'APP_USER', 'C##DBA_ADMIN', 'C##APP_READER')
ORDER BY username;

PROMPT
PROMPT === Rôles créés ===
COL role FORMAT A20
SELECT role FROM dba_roles 
WHERE role LIKE 'APP%' 
ORDER BY role;

PROMPT
PROMPT === Privileges de rôle app_write_role ===
COL grantee FORMAT A20
COL privilege FORMAT A25
SELECT grantee, privilege 
FROM dba_sys_privs 
WHERE grantee = 'APP_WRITE_ROLE'
ORDER BY privilege;

PROMPT
PROMPT === Profiles ===
COL profile FORMAT A20
COL resource_name FORMAT A30
COL limit FORMAT A20
SELECT profile, resource_name, limit
FROM dba_profiles
WHERE profile = 'LIMITED_PROFILE'
AND resource_type = 'PASSWORD'
ORDER BY resource_name;

PROMPT
PROMPT === Objets app_owner ===
COL object_name FORMAT A20
COL object_type FORMAT A20
SELECT object_name, object_type, status
FROM dba_objects
WHERE owner = 'APP_OWNER'
ORDER BY object_type, object_name;

PROMPT
PROMPT ===== RÉSUMÉ TP06 =====
ALTER SESSION SET CONTAINER=CDB$ROOT;
SELECT 'Utilisateurs communs: ' || COUNT(*) as info
FROM dba_users
WHERE username LIKE 'C##%'
UNION ALL
SELECT 'Rôles personnalisés: ' || COUNT(*)
FROM dba_roles
WHERE role LIKE 'APP%';

ALTER SESSION SET CONTAINER=GDCPDB;
SELECT 'Utilisateurs PDB: ' || COUNT(*) as info
FROM dba_users
WHERE username IN ('APP_OWNER', 'APP_USER')
UNION ALL
SELECT 'Tables app_owner: ' || COUNT(*)
FROM dba_tables
WHERE owner = 'APP_OWNER'
UNION ALL
SELECT 'Enregistrements customers: ' || COUNT(*)
FROM app_owner.customers
UNION ALL
SELECT 'Enregistrements orders: ' || COUNT(*)
FROM app_owner.orders;

EXIT
EOSQL

echo "[1/1] Exécution TP06 - Sécurité..."
su - oracle -c "sqlplus / as sysdba @/tmp/tp06_security.sql" 2>&1 | tee /tmp/tp06_output.log

echo ""
echo "============================================"
echo "  TP06 TERMINÉ"
echo "============================================"
echo "Logs: /tmp/tp06_output.log"
