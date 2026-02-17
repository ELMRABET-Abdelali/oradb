#!/bin/bash
################################################################################
# Oracle 19c Installation on CentOS Stream 9
# TP01: System Preparation
################################################################################

set -e
echo "============================================"
echo "  TP01: System Preparation Started"
echo "  $(date)"
echo "============================================"

# Check if running as root
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
    echo "✓ SWAP created"
else
    echo "✓ SWAP already exists"
    swapon /swapfile 2>/dev/null || echo "SWAP already active"
fi
swapon --show

echo ""
echo "[3/8] Creating Oracle Groups..."
echo "-------------------------------------------"
groupadd -g 54321 oinstall 2>/dev/null || echo "Group oinstall exists"
groupadd -g 54322 dba 2>/dev/null || echo "Group dba exists"
groupadd -g 54323 oper 2>/dev/null || echo "Group oper exists"
groupadd -g 54324 backupdba 2>/dev/null || echo "Group backupdba exists"
groupadd -g 54325 dgdba 2>/dev/null || echo "Group dgdba exists"
groupadd -g 54326 kmdba 2>/dev/null || echo "Group kmdba exists"
groupadd -g 54327 racdba 2>/dev/null || echo "Group racdba exists"
echo "✓ Groups created"

echo ""
echo "[4/8] Creating Oracle User..."
echo "-------------------------------------------"
if ! id oracle &>/dev/null; then
    useradd -u 54321 -g oinstall -G dba,oper,backupdba,dgdba,kmdba,racdba,wheel -m -s /bin/bash oracle
    echo "oracle:Oracle123" | chpasswd
    echo "✓ User oracle created (password: Oracle123)"
else
    echo "✓ User oracle exists"
fi
id oracle

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
echo "[6/8] Installing Oracle Prerequisites..."
echo "-------------------------------------------"
dnf install -y bc binutils compat-openssl11 elfutils-libelf \
    glibc glibc-devel ksh libaio libaio-devel \
    libgcc libnsl libstdc++ libstdc++-devel libxcrypt-compat \
    make policycoreutils policycoreutils-python-utils \
    smartmontools sysstat unzip libnsl2

echo "✓ Prerequisites installed"

echo ""
echo "[7/8] Configuring SELinux and Firewall..."
echo "-------------------------------------------"
setenforce 0
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
echo "✓ SELinux set to permissive"

systemctl stop firewalld 2>/dev/null || true
systemctl disable firewalld 2>/dev/null || true
echo "✓ Firewall disabled"

echo ""
echo "[8/8] Configuring Kernel Parameters..."
echo "-------------------------------------------"
cat > /etc/sysctl.d/98-oracle.conf << 'EOF'
# Oracle 19c Kernel Parameters
fs.file-max = 6815744
kernel.sem = 250 32000 100 128
kernel.shmmni = 4096
kernel.shmall = 1073741824
kernel.shmmax = 4398046511104
net.core.rmem_default = 262144
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
fs.aio-max-nr = 1048576
net.ipv4.ip_local_port_range = 9000 65500
EOF
sysctl -p /etc/sysctl.d/98-oracle.conf
echo "✓ Kernel parameters applied"

echo ""
echo "[8b/8] Configuring User Limits..."
echo "-------------------------------------------"
cat > /etc/security/limits.d/oracle-database-limits.conf << 'EOF'
oracle   soft   nofile    1024
oracle   hard   nofile    65536
oracle   soft   nproc     16384
oracle   hard   nproc     16384
oracle   soft   stack     10240
oracle   hard   stack     32768
oracle   hard   memlock   134217728
oracle   soft   memlock   134217728
EOF
echo "✓ User limits configured"

echo ""
echo "============================================"
echo "  ✓ TP01 COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Verification:"
echo "  - SWAP: $(swapon --show | grep swapfile | awk '{print $3}')"
echo "  - Oracle user: $(id oracle 2>/dev/null && echo 'OK' || echo 'FAIL')"
echo "  - /u01 owner: $(ls -ld /u01 | awk '{print $3":"$4}')"
echo "  - SELinux: $(getenforce)"
echo ""
echo "Next: TP02 - Configure environment and download binaries"
