#!/bin/bash
############################################################
# TP02: Environment Setup & Oracle 19c Binaries Download
# Rocky Linux 8 - Run as root
############################################################

set -e
echo "============================================"
echo "  TP02: Environment & Oracle Binaries"
echo "  $(date)"
echo "============================================"
echo ""

# Install gdown tool for Google Drive downloads
echo "[1/4] Installing gdown (Google Drive downloader)..."
echo "-------------------------------------------"
pip3 install gdown || pip install gdown
echo "✓ gdown installed"
echo ""

# Configure oracle user environment
echo "[2/4] Configuring Oracle User Environment..."
echo "-------------------------------------------"
cat > /home/oracle/.bashrc << 'EOF'
# .bashrc for Oracle user

# Source global definitions
if [ -f /etc/bashrc ]; then
    . /etc/bashrc
fi

# Oracle Environment Variables
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=/u01/app/oracle/product/19.0.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
export NLS_LANG=AMERICAN_AMERICA.AL32UTF8
export ORACLE_UNQNAME=GDCPROD

# User specific aliases and functions
alias alert='tail -100f $ORACLE_BASE/diag/rdbms/$(echo $ORACLE_SID | tr A-Z a-z)/$ORACLE_SID/trace/alert_$ORACLE_SID.log 2>/dev/null || echo "Alert log not found"'
alias sqlplus='rlwrap sqlplus'
alias rman='rlwrap rman'
alias lsnr='lsnrctl status'
EOF

chown oracle:oinstall /home/oracle/.bashrc
echo "✓ Environment variables configured"
cat /home/oracle/.bashrc
echo ""

# Download Oracle 19c binaries
echo "[3/4] Downloading Oracle 19c Binaries (2.9GB)..."
echo "-------------------------------------------"
echo "This will take 5-10 minutes depending on connection speed..."
echo ""

ORACLE_HOME=/u01/app/oracle/product/19.0.0/dbhome_1
GOOGLE_DRIVE_ID="1W0x1kZ3WXuVPQrB3TZPk8nwL8chB8Cka"

# Download as oracle user
su - oracle -c "cd /tmp && gdown --id $GOOGLE_DRIVE_ID"

if [ -f /tmp/LINUX.X64_193000_db_home.zip ]; then
    echo "✓ Oracle 19c binaries downloaded successfully"
    ls -lh /tmp/LINUX.X64_193000_db_home.zip
else
    echo "✗ Download failed! Checking /tmp contents:"
    ls -lh /tmp/*.zip 2>/dev/null || echo "No zip files found in /tmp"
    exit 1
fi
echo ""

# Extract binaries to ORACLE_HOME
echo "[4/4] Extracting Oracle Binaries to ORACLE_HOME..."
echo "-------------------------------------------"
echo "Extracting to $ORACLE_HOME (this takes 3-5 minutes)..."
echo ""

su - oracle -c "cd $ORACLE_HOME && unzip -q /tmp/LINUX.X64_193000_db_home.zip"

# Verify extraction
if [ -f "$ORACLE_HOME/runInstaller" ]; then
    echo "✓ Binaries extracted successfully"
    echo ""
    echo "Oracle Home contents:"
    ls -l $ORACLE_HOME | head -20
    echo ""
    echo "Total size:"
    du -sh $ORACLE_HOME
else
    echo "✗ Extraction failed! runInstaller not found"
    exit 1
fi
echo ""

# Cleanup
echo "Cleaning up temporary files..."
rm -f /tmp/LINUX.X64_193000_db_home.zip
echo "✓ Cleanup complete"
echo ""

echo "============================================"
echo "  TP02 COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Summary:"
echo "  • Oracle environment variables: Configured in /home/oracle/.bashrc"
echo "  • ORACLE_BASE: /u01/app/oracle"
echo "  • ORACLE_HOME: /u01/app/oracle/product/19.0.0/dbhome_1"
echo "  • ORACLE_SID: GDCPROD"
echo "  • Oracle 19c binaries: Downloaded and extracted"
echo "  • runInstaller: Ready at \$ORACLE_HOME/runInstaller"
echo ""
echo "Next: Run TP03 to install Oracle Database software"
echo ""
echo "To verify environment as oracle user, run:"
echo "  su - oracle"
echo "  env | grep ORACLE"
