#!/bin/bash
############################################################
# TP03: Oracle 19c Software Installation
# Rocky Linux 8 - Run as root
############################################################

set -e
echo "============================================"
echo "  TP03: Oracle 19c Software Installation"
echo "  $(date)"
echo "============================================"
echo ""

# Create response file for silent installation
echo "[1/3] Creating Response File for Silent Installation..."
echo "-------------------------------------------"
cat > /tmp/db_install.rsp << 'EOF'
oracle.install.option=INSTALL_DB_SWONLY
UNIX_GROUP_NAME=oinstall
INVENTORY_LOCATION=/u01/app/oraInventory
ORACLE_HOME=/u01/app/oracle/product/19.0.0/dbhome_1
ORACLE_BASE=/u01/app/oracle
oracle.install.db.InstallEdition=EE
oracle.install.db.OSDBA_GROUP=dba
oracle.install.db.OSOPER_GROUP=oper
oracle.install.db.OSBACKUPDBA_GROUP=backupdba
oracle.install.db.OSDGDBA_GROUP=dgdba
oracle.install.db.OSKMDBA_GROUP=kmdba
oracle.install.db.OSRACDBA_GROUP=racdba
oracle.install.db.rootconfig.executeRootScript=false
EOF

chown oracle:oinstall /tmp/db_install.rsp
echo "✓ Response file created"
echo ""

# Run Oracle installer as oracle user
echo "[2/3] Running Oracle Installer (15-20 minutes)..."
echo "-------------------------------------------"
echo "Installing Oracle Database 19c Enterprise Edition - Software Only"
echo "This will take 15-20 minutes. Please be patient..."
echo ""

su - oracle -c "cd /u01/app/oracle/product/19.0.0/dbhome_1 && ./runInstaller -silent -responseFile /tmp/db_install.rsp -waitforcompletion" 2>&1 | tee /tmp/oracle_install.log

# Check installation status
if grep -q "Successfully Setup Software" /tmp/oracle_install.log; then
    echo ""
    echo "✓ Oracle software installation completed successfully"
else
    echo ""
    echo "✗ Installation may have issues. Check log: /tmp/oracle_install.log"
    tail -50 /tmp/oracle_install.log
    exit 1
fi
echo ""

# Execute root scripts
echo "[3/3] Executing Root Configuration Scripts..."
echo "-------------------------------------------"

if [ -f /u01/app/oraInventory/orainstRoot.sh ]; then
    echo "Running orainstRoot.sh..."
    /u01/app/oraInventory/orainstRoot.sh
    echo "✓ orainstRoot.sh completed"
else
    echo "✗ orainstRoot.sh not found"
fi
echo ""

if [ -f /u01/app/oracle/product/19.0.0/dbhome_1/root.sh ]; then
    echo "Running root.sh..."
    /u01/app/oracle/product/19.0.0/dbhome_1/root.sh
    echo "✓ root.sh completed"
else
    echo "✗ root.sh not found"
fi
echo ""

# Verify installation
echo "Verifying Oracle Installation..."
echo "-------------------------------------------"
su - oracle -c '$ORACLE_HOME/bin/sqlplus -v'
echo ""

echo "============================================"
echo "  TP03 COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Summary:"
echo "  • Oracle 19c Enterprise Edition: Installed (Software Only)"
echo "  • Installation logs: /u01/app/oraInventory/logs/"
echo "  • Root scripts: Executed"
echo "  • SQL*Plus version: Verified"
echo ""
echo "Next: Run TP03b to create GDCPROD database using DBCA"
echo ""
echo "To verify, run as oracle user:"
echo "  su - oracle"
echo "  sqlplus -v"
