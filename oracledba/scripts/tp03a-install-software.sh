#!/bin/bash
################################################################################
# TP03: Extract Binaries and Install Oracle Software
################################################################################

echo "============================================"
echo "  TP03: Oracle Software Installation"
echo "  $(date)"
echo "============================================"

echo ""
echo "[1/7] E extraiting Oracle 19c Binaries..."
echo "-------------------------------------------"
echo "This will take 5-10 minutes..."

su - oracle -c "cd /u01/app/oracle/product/19.0.0/dbhome_1 && unzip -oq LINUX.X64_193000_db_home.zip"

echo "✓ Binaries extracted"
echo "Checking extracted files:"
su - oracle -c "ls -1 /u01/app/oracle/product/19.0.0/dbhome_1 | head -10"

echo ""
echo "[2/7] Creating Oracle Inventory Location File..."
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
echo "[3/7] Installing Oracle Software (Software Only)..."
echo "-------------------------------------------"
echo "This will take 15-20 minutes. Please wait..."

# Run Oracle installer as oracle user
su - oracle << 'EOSU'
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
    oracle.install.db.OSDGDBA_GROUP=dgdba \
    oracle.install.db.OSKMDBA_GROUP=kmdba \
    oracle.install.db.OSRACDBA_GROUP=racdba \
    oracle.install.db.rootconfig.executeRootScript=false

echo "Installation completed with status: $?"
EOSU

echo ""
echo "✓ Oracle Software installation completed"

echo ""
echo "[4/7] Executing Root Configuration Scripts..."
echo "-------------------------------------------"

# Execute orainstRoot.sh
if [ -f /u01/app/oraInventory/orainstRoot.sh ]; then
    echo "Executing orainstRoot.sh..."
    /u01/app/oraInventory/orainstRoot.sh
    echo "✓ orainstRoot.sh completed"
else
    echo "⚠ orainstRoot.sh not found"
fi

# Execute root.sh
if [ -f /u01/app/oracle/product/19.0.0/dbhome_1/root.sh ]; then
    echo ""
    echo "Executing root.sh..."
    /u01/app/oracle/product/19.0.0/dbhome_1/root.sh
    echo "✓ root.sh completed"
else
    echo "⚠ root.sh not found"
fi

echo ""
echo "============================================"
echo "  ✓ TP03 Part 1 COMPLETED SUCCESSFULLY"
echo " ============================================"
echo ""
echo "Software installation completed."
echo "Next: TP03 Part 2 - Create database with DBCA"
