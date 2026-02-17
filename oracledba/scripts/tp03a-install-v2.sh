#!/bin/bash
################################################################################
# TP03: Oracle Software Installation (Simplified)
################################################################################

echo "============================================"
echo "  TP03: Oracle Software Installation"
echo "  $(date)"
echo "============================================"

# Set variables
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/19.0.0/dbhome_1

echo ""
echo "[1/4] Creating Oracle Inventory Location File..."
echo "-------------------------------------------"

cat > /etc/oraInst.loc <<EOF
inventory_loc=/u01/app/oraInventory
inst_group=oinstall
EOF

chown oracle:oinstall /etc/oraInst.loc
chmod 664 /etc/oraInst.loc

echo "✓ Oracle inventory file created"
cat /etc/oraInst.loc

echo ""
echo "[2/4] Installing Oracle Software (Software Only)..."
echo "-------------------------------------------"
echo "This will take 15-20 minutes. Progress will be shown..."
echo ""

# Run Oracle installer as oracle user with proper environment
runuser -l oracle -c '
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/19.0.0/dbhome_1
cd $ORACLE_HOME

./runInstaller -ignorePrereq -ignoreInternalDriverError -waitforcompletion -silent \
    -responseFile ${ORACLE_HOME}/install/response/db_install.rsp \
    oracle.install.option=INSTALL_DB_SWONLY \
    ORACLE_HOSTNAME=centosdba \
    UNIX_GROUP_NAME=oinstall \
    ORACLE_HOME=${ORACLE_HOME} \
    ORACLE_BASE=${ORACLE_BASE} \
    oracle.install.db.InstallEdition=EE \
    oracle.install.db.OSDBA_GROUP=dba \
    oracle.install.db.OSOPER_GROUP=oper \
    oracle.install.db.OSBACKUPDBA_GROUP=backupdba \
    oracledba
    oracle.install.db.OSKMDBA_GROUP=kmdba \
    oracle.install.db.OSRACDBA_GROUP=racdba \
    oracle.install.db.rootconfig.executeRootScript=false
'

INSTALL_STATUS=$?
echo ""
echo "Installation completed with status: $INSTALL_STATUS"

if [ $INSTALL_STATUS -eq 0 ] || [ $INSTALL_STATUS -eq 6 ]; then
    echo "✓ Oracle Software installation successful"
else
    echo "⚠ Installation completed with warnings/errors (code: $INSTALL_STATUS)"
fi

echo ""
echo "[3/4] Executing Root Configuration Scripts..."
echo "-------------------------------------------"

# Execute orainstRoot.sh
if [ -f /u01/app/oraInventory/orainstRoot.sh ]; then
    echo "Executing orainstRoot.sh..."
    bash /u01/app/oraInventory/orainstRoot.sh
    echo "✓ orainstRoot.sh completed"
else
    echo "⚠ orainstRoot.sh not found - may need to run manually"
fi

# Execute root.sh
if [ -f $ORACLE_HOME/root.sh ]; then
    echo ""
    echo "Executing root.sh..."
    bash $ORACLE_HOME/root.sh
    echo "✓ root.sh completed"
else
    echo "⚠ root.sh not found - may need to run manually"
fi

echo ""
echo "[4/4] Verification..."
echo "-------------------------------------------"

# Check if Oracle binaries are properly linked
if [ -f $ORACLE_HOME/bin/sqlplus ]; then
    echo "✓ SQL*Plus binary found"
    runuser -l oracle -c 'export ORACLE_HOME=/u01/app/oracle/product/19.0.0/dbhome_1; $ORACLE_HOME/bin/sqlplus -version'
else
    echo "⚠ SQL*Plus not found"
fi

echo ""
echo "============================================"
echo "  ✓ TP03a COMPLETED"
echo "============================================"
echo ""
echo "Next: TP03b - Create database with DBCA"
