#!/bin/bash
############################################################
# TP03b: Create GDCPROD Database using DBCA
# Rocky Linux 8 - Run as root
############################################################

set -e
echo "============================================"
echo "  TP03b: Database Creation with DBCA"
echo "  $(date)"
echo "============================================"
echo ""

# Create DBCA response file
echo "[1/3] Creating DBCA Response File..."
echo "-------------------------------------------"
cat > /tmp/dbca_create.rsp << 'EOF'
responseFileVersion=/oracle/assistants/rspfmt_dbca_response_schema_v19.0.0
gdbName=GDCPROD
sid=GDCPROD
databaseConfigType=SI
createAsContainerDatabase=true
numberOfPDBs=1
pdbName=GDCPDB
useLocalUndoForPDBs=true
pdbAdminPassword=Oracle123
templateName=General_Purpose.dbc
sysPassword=Oracle123
systemPassword=Oracle123
dbsnmpPassword=Oracle123
datafileDestination=/u01/app/oracle/oradata
recoveryAreaDestination=/u01/app/oracle/fast_recovery_area
storageType=FS
characterSet=AL32UTF8
nationalCharacterSet=AL16UTF16
memoryMgmtType=AUTO_SMP
totalMemory=4096
automaticMemoryManagement=FALSE
databaseType=MULTIPURPOSE
EOF

chown oracle:oinstall /tmp/dbca_create.rsp
echo "✓ DBCA response file created"
echo ""

# Create required directories
echo "[2/3] Creating Database Directories..."
echo "-------------------------------------------"
mkdir -p /u01/app/oracle/oradata
mkdir -p /u01/app/oracle/fast_recovery_area
mkdir -p /u01/app/oracle/admin/GDCPROD/adump
chown -R oracle:oinstall /u01/app/oracle/oradata /u01/app/oracle/fast_recovery_area /u01/app/oracle/admin
echo "✓ Directories created"
ls -ld /u01/app/oracle/oradata /u01/app/oracle/fast_recovery_area
echo ""

# Run DBCA
echo "[3/3] Creating GDCPROD Database (15-20 minutes)..."
echo "-------------------------------------------"
echo "Creating database: GDCPROD (CDB) with PDB: GDCPDB"
echo "This will take 15-20 minutes. Please be patient..."
echo ""

su - oracle -c "dbca -silent -createDatabase -responseFile /tmp/dbca_create.rsp" 2>&1 | tee /tmp/dbca_create.log

# Check database creation status
if grep -q "100% complete" /tmp/dbca_create.log; then
    echo ""
    echo "✓ Database created successfully"
else
    echo ""
    echo "✗ Database creation may have issues. Check log: /tmp/dbca_create.log"
    tail -50 /tmp/dbca_create.log
    exit 1
fi
echo ""

# Start listener if not running
echo "Starting Listener..."
echo "-------------------------------------------"
su - oracle -c "lsnrctl start LISTENER" 2>&1 || echo "Listener may already be running"
echo ""

# Add database to /etc/oratab
echo "Updating /etc/oratab..."
echo "-------------------------------------------"
sed -i '/^GDCPROD/d' /etc/oratab
echo "GDCPROD:/u01/app/oracle/product/19.0.0/dbhome_1:Y" >> /etc/oratab
echo "✓ /etc/oratab updated"
cat /etc/oratab | grep -v "^#\|^$"
echo ""

# Verify database
echo "Verifying Database..."
echo "-------------------------------------------"
su - oracle -c "sqlplus -s / as sysdba << EOSQL
SET PAGESIZE 0 FEEDBACK OFF VERIFY OFF HEADING OFF ECHO OFF
SELECT 'Database Name: ' || name FROM v\\\$database;
SELECT 'Database Status: ' || open_mode FROM v\\\$database;
SELECT 'CDB: ' || cdb FROM v\\\$database;
SELECT 'PDB Count: ' || COUNT(*) FROM dba_pdbs WHERE pdb_name != 'PDB\\\$SEED';
EOSQL"
echo ""

# Show PDBs
su - oracle -c "sqlplus -s / as sysdba << EOSQL
SET LINESIZE 150
COL pdb_name FORMAT A15
COL open_mode FORMAT A15
SELECT pdb_id, pdb_name, open_mode FROM dba_pdbs;
EXIT
EOSQL"
echo ""

echo "============================================"
echo "  TP03b COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Summary:"
echo "  • CDB Name: GDCPROD"
echo "  • PDB Name: GDCPDB"
echo "  • Character Set: AL32UTF8"
echo "  • Memory: 4GB SGA"
echo "  • Data Location: /u01/app/oracle/oradata"
echo "  • FRA Location: /u01/app/oracle/fast_recovery_area"
echo "  • Passwords: Oracle123 (SYS, SYSTEM, PDBADMIN)"
echo ""
echo "To connect:"
echo "  sqlplus / as sysdba"
echo "  sqlplus sys/Oracle123@localhost/GDCPROD as sysdba"
echo "  sqlplus system/Oracle123@localhost/GDCPDB"
