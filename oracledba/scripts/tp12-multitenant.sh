#!/bin/bash
# TP12: Multitenant Architecture
# Rocky Linux 8 - Oracle 19c
# Description: Gestion CDB et PDB

echo "================================================"
echo "  TP12: Multitenant - CDB et PDB"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/8] Vérification architecture Multitenant..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SELECT name, cdb, con_id FROM v\$database;
SELECT name, open_mode, con_id FROM v\$pdbs;
EXIT;
EOF"

echo ""
echo "[2/8] Création nouvelle PDB: PDB2..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
CREATE PLUGGABLE DATABASE pdb2 
ADMIN USER pdb2admin IDENTIFIED BY Oracle123
FILE_NAME_CONVERT=('/u01/app/oracle/oradata/GDCPROD/GDCPDB/', '/u01/app/oracle/oradata/GDCPROD/pdb2/');
ALTER PLUGGABLE DATABASE pdb2 OPEN;
ALTER PLUGGABLE DATABASE pdb2 SAVE STATE;
SELECT name, open_mode FROM v\$pdbs;
EXIT;
EOF"

echo ""
echo "[3/8] Connexion à PDB2 et création utilisateur..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=pdb2;
CREATE USER pdb2_user IDENTIFIED BY User123;
GRANT CONNECT, RESOURCE TO pdb2_user;
ALTER USER pdb2_user QUOTA 100M ON USERS;
SELECT username, account_status FROM dba_users WHERE username='PDB2_USER';
EXIT;
EOF"

echo ""
echo "[4/8] Test données dans PDB2..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=pdb2;
CREATE TABLE pdb2_user.test_pdb2 (
    id NUMBER PRIMARY KEY,
    description VARCHAR2(100),
    created_date DATE DEFAULT SYSDATE
);
INSERT INTO pdb2_user.test_pdb2 VALUES (1, 'Test in PDB2', SYSDATE);
INSERT INTO pdb2_user.test_pdb2 VALUES (2, 'Multitenant Test', SYSDATE);
COMMIT;
SELECT * FROM pdb2_user.test_pdb2;
EXIT;
EOF"

echo ""
echo "[5/8] Clone PDB: Création PDB3 depuis PDB2..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER PLUGGABLE DATABASE pdb2 CLOSE;
ALTER PLUGGABLE DATABASE pdb2 OPEN READ ONLY;
CREATE PLUGGABLE DATABASE pdb3 FROM pdb2 
FILE_NAME_CONVERT=('/u01/app/oracle/oradata/GDCPROD/pdb2/', '/u01/app/oracle/oradata/GDCPROD/pdb3/');
ALTER PLUGGABLE DATABASE pdb2 CLOSE;
ALTER PLUGGABLE DATABASE pdb2 OPEN;
ALTER PLUGGABLE DATABASE pdb3 OPEN;
ALTER PLUGGABLE DATABASE pdb3 SAVE STATE;
SELECT name, open_mode FROM v\$pdbs ORDER BY name;
EXIT;
EOF"

echo ""
echo "[6/8] Vérification ressources PDB..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SELECT 
    p.name,
    p.open_mode,
    p.restricted,
    p.total_size/1024/1024 AS size_mb
FROM v\$pdbs p
ORDER BY p.name;
EXIT;
EOF"

echo ""
echo "[7/8] Configuration Resource Manager pour PDB..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
BEGIN
    DBMS_RESOURCE_MANAGER.create_pending_area();
    
    -- Créer plan CDB
    DBMS_RESOURCE_MANAGER.create_cdb_plan(
        plan => 'cdb_plan',
        comment => 'CDB Resource Plan'
    );
    
    -- Directives pour PDBs
    DBMS_RESOURCE_MANAGER.create_cdb_plan_directive(
        plan => 'cdb_plan',
        pluggable_database => 'GDCPDB',
        shares => 3,
        utilization_limit => 100
    );
    
    DBMS_RESOURCE_MANAGER.create_cdb_plan_directive(
        plan => 'cdb_plan',
        pluggable_database => 'pdb2',
        shares => 2,
        utilization_limit => 80
    );
    
    DBMS_RESOURCE_MANAGER.create_cdb_plan_directive(
        plan => 'cdb_plan',
        pluggable_database => 'pdb3',
        shares => 1,
        utilization_limit => 50
    );
    
    DBMS_RESOURCE_MANAGER.validate_pending_area();
    DBMS_RESOURCE_MANAGER.submit_pending_area();
END;
/

-- Activer le plan
ALTER SYSTEM SET resource_manager_plan='cdb_plan' SCOPE=BOTH;
SELECT name, is_top_plan FROM v\$rsrc_plan WHERE is_top_plan='TRUE';
EXIT;
EOF"

echo ""
echo "[8/8] Résumé architecture Multitenant..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200 PAGESIZE 100
SELECT 
    p.con_id,
    p.name AS pdb_name,
    p.open_mode,
    p.restricted,
    TO_CHAR(p.open_time, 'YYYY-MM-DD HH24:MI:SS') AS open_time,
    d.status
FROM v\$pdbs p
LEFT JOIN cdb_pdbs d ON p.name = d.pdb_name
ORDER BY p.con_id;

SELECT 
    COUNT(*) AS total_pdbs,
    SUM(CASE WHEN open_mode='READ WRITE' THEN 1 ELSE 0 END) AS read_write_pdbs,
    SUM(CASE WHEN open_mode='READ ONLY' THEN 1 ELSE 0 END) AS read_only_pdbs
FROM v\$pdbs
WHERE name != 'PDB\$SEED';
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP12 TERMINÉ"
echo "================================================"
echo "Architecture Multitenant configurée:"
echo "- CDB: GDCPROD"
echo "- PDB1: GDCPDB (original)"
echo "- PDB2: pdb2 (nouveau)"
echo "- PDB3: pdb3 (clone de pdb2)"
echo "- Resource Manager: cdb_plan activé"
echo ""
echo "Commandes utiles:"
echo "- Show PDBs: SHOW PDBS"
echo "- Switch PDB: ALTER SESSION SET CONTAINER=pdb_name"
echo "- Close PDB: ALTER PLUGGABLE DATABASE pdb_name CLOSE"
echo "- Open PDB: ALTER PLUGGABLE DATABASE pdb_name OPEN"
echo "- Drop PDB: DROP PLUGGABLE DATABASE pdb_name INCLUDING DATAFILES"
