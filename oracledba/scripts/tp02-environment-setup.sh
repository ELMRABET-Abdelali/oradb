#!/bin/bash
################################################################################
# TP02: Configure Oracle Environment and Download Binaries
################################################################################

echo "============================================"
echo "  TP02: Environment Configuration"
echo "  $(date)"
echo "============================================"

# Must run as oracle user for profile configuration
if [ "$USER" != "oracle" ]; then
    echo "Configuring as root, then switching to oracle..."
fi

echo ""
echo "[1/3] Configuring Oracle Environment Variables..."
echo "-------------------------------------------"

# Configure oracle user's .bashrc
cat >> /home/oracle/.bashrc << 'EOF'

# --- Oracle 19c Configuration ---
export ORACLE_HOSTNAME=centosdba
export ORACLE_UNQNAME=GDCPROD
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/19.0.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:/lib:/usr/lib
export CLASSPATH=$ORACLE_HOME/jlib:$ORACLE_HOME/rdbms/jlib
EOF

echo "✓ Environment variables configured in /home/oracle/.bashrc"

echo ""
echo "[2/3] Downloading Oracle 19c Binaries..."
echo "-------------------------------------------"
echo "Installing gdown for Google Drive download..."

# Install python3-pip if not present
dnf install -y python3-pip wget > /dev/null 2>&1

# Install gdown as oracle user
su - oracle -c "pip3 install --user gdown --quiet"

echo "✓ gdown installed"
echo ""
echo "Downloading Oracle 19c ZIP (2.8 GB) - This will take several minutes..."
echo "Progress will be shown below:"

# Download as oracle user to ORACLE_HOME
su - oracle -c "cd /u01/app/oracle/product/19.0.0/dbhome_1 && ~/.local/bin/gdown 1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns -O LINUX.X64_193000_db_home.zip"

echo ""
echo "[3/3] Verifying Download..."
echo "-------------------------------------------"

ZIP_SIZE=$(stat -c%s "/u01/app/oracle/product/19.0.0/dbhome_1/LINUX.X64_193000_db_home.zip" 2>/dev/null || echo "0")
if [ "$ZIP_SIZE" -gt 2500000000 ]; then
    echo "✓ Download successful"
    echo "  File size: $(echo "scale=2; $ZIP_SIZE/1024/1024/1024" | bc) GB"
    ls -lh /u01/app/oracle/product/19.0.0/dbhome_1/LINUX.X64_193000_db_home.zip
else
    echo "✗ Download failed or incomplete"
    echo "  Expected size: ~2.8 GB, Got: $(echo "scale=2; $ZIP_SIZE/1024/1024/1024" | bc) GB"
    exit 1
fi

echo ""
echo "============================================"
echo "  ✓ TP02 COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Verification:"
echo "  - Environment: $(su - oracle -c 'echo $ORACLE_HOME')"
echo "  - Binary ZIP: Present ($(ls -lh /u01/app/oracle/product/19.0.0/dbhome_1/*.zip 2>/dev/null | awk '{print $5}'))"
echo ""
echo "Next: TP03 - Extract binaries and install Oracle software"
