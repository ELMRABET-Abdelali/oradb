#!/bin/bash
################################################################################
# Oracle 19c Installation on Rocky Linux 8
# TP01: System Preparation
################################################################################

set -e
echo "============================================"
echo "  TP01: System Preparation for Rocky Linux 8"
echo "  $(date)"
echo "============================================"

if [ "$EUID" -ne 0 ]; then 
   echo "ERROR: Must run as root"
   exit 1
fi

echo ""
echo "[1/8] System Resources Check..."
echo "-------------------------------------------"
free -h | grep Mem
echo "CPU Cores: $(nproc)"
df -h / | tail -1

echo ""
echo "[2/8] Creating SWAP (4GB)..."
echo "-------------------------------------------"
if [ ! -f /swapfile ]; then
    dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    if ! grep -q "/swapfile" /etc/fstab; then
        echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
    fi
    echo "✓ SWAP created and activated"
else
    echo "✓ SWAP already exists"
    swapon /swapfile 2>/dev/null || echo "SWAP already active"
fi
swapon --show

echo ""
echo "[3/8] Installing Oracle Preinstall Package..."
echo "-------------------------------------------"
# This package does most of the work automatically!
yum install -y oracle-database-preinstall-19c

echo "✓ Oracle preinstall package installed"
echo "  (This automatically created oracle user, groups, kernel params, and limits)"

echo ""
echo "[4/8] Verifying Oracle User and Groups..."
echo "-------------------------------------------"
id oracle
echo "✓ Oracle user verified"

echo ""
echo "[5/8] Creating OFA Directory Structure..."
echo "-------------------------------------------"
mkdir -p /u01/app/oracle/product/19.0.0/dbhome_1
mkdir -p /u01/app/oraInventory
chown -R oracle:oinstall /u01
chmod -R 775 /u01
ls -ld /u01
echo "✓ OFA structure created"

echo ""
echo "[6/8] Installing Additional Required Packages..."
echo "-------------------------------------------"
yum install -y unzip wget bc which

echo "✓ Additional packages installed"

echo ""
echo "[7/8] Configuring SELinux and Firewall..."
echo "-------------------------------------------"
setenforce 0
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
echo "✓ SELinux set to permissive"

systemctl stop firewalld 2>/dev/null || true
systemctl disable firewalld 2>/dev/null || true
echo "✓ Firewall disabled (for lab environment)"

echo ""
echo "[8/8] Verification..."
echo "-------------------------------------------"
echo "SWAP: $(swapon --show | grep swapfile | awk '{print $3}' || echo 'Not found')"
echo "Oracle User: $(id oracle > /dev/null 2>&1 && echo 'OK' || echo 'FAIL')"
echo "/u01 Owner: $(ls -ld /u01 | awk '{print $3":"$4}')"
echo "SELinux: $(getenforce)"
echo "Kernel shmmax: $(sysctl kernel.shmmax | awk '{print $3}')"

echo ""
echo "============================================"
echo "  ✅ TP01 COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Next: TP02 - Configure Oracle environment and download binaries"
