#!/bin/bash
############################################################
# TP01: Oracle 19c System Preparation for Rocky Linux 8
# Manual Setup (without oracle-database-preinstall package)
############################################################

set -e
echo "============================================"
echo "  TP01: Oracle 19c System Preparation"
echo "  $(date)"
echo "============================================"
echo ""

# System resources check
echo "[1/9] System Resources Check..."
echo "-------------------------------------------"
free -h
echo "CPU Cores: $(nproc)"
df -h /
echo ""

# SWAP creation (if needed)
echo "[2/9] SWAP Configuration..."
echo "-------------------------------------------"
if [ -f /swapfile ]; then
    echo "✓ SWAP file already exists"
else
    echo "Creating 4GB SWAP file..."
    dd if=/dev/zero of=/swapfile bs=1M count=4096
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
    echo "✓ SWAP created and activated"
fi
swapon --show
echo ""

# Install required packages
echo "[3/9] Installing Required Packages..."
echo "-------------------------------------------"
yum install -y \
    bc \
    binutils \
    elfutils-libelf \
    elfutils-libelf-devel \
    fontconfig-devel \
    glibc \
    glibc-devel \
    ksh \
    libaio \
    libaio-devel \
    libX11 \
    libXau \
    libXi \
    libXtst \
    libXrender \
    libXrender-devel \
    libgcc \
    libstdc++ \
    libstdc++-devel \
    libxcb \
    make \
    net-tools \
    nfs-utils \
    python3 \
    python3-configshell \
    python3-rtslib \
    python3-six \
    targetcli \
    smartmontools \
    sysstat \
    unzip \
    libnsl \
    libnsl2 \
    wget

echo "✓ Packages installed"
echo ""

# Create groups
echo "[4/9] Creating Oracle Groups..."
echo "-------------------------------------------"
if ! getent group oinstall > /dev/null; then
    groupadd -g 54321 oinstall
    echo "✓ oinstall group created"
else
    echo "✓ oinstall group exists"
fi

if ! getent group dba > /dev/null; then
    groupadd -g 54322 dba
    echo "✓ dba group created"
else
    echo "✓ dba group exists"
fi

if ! getent group oper > /dev/null; then
    groupadd -g 54323 oper
    echo "✓ oper group created"
else
    echo "✓ oper group exists"
fi

if ! getent group backupdba > /dev/null; then
    groupadd -g 54324 backupdba
    echo "✓ backupdba group created"
else
    echo "✓ backupdba group exists"
fi

if ! getent group dgdba > /dev/null; then
    groupadd -g 54325 dgdba
    echo "✓ dgdba group created"
else
    echo "✓ dgdba group exists"
fi

if ! getent group kmdba > /dev/null; then
    groupadd -g 54326 kmdba
    echo "✓ kmdba group created"
else
    echo "✓ kmdba group exists"
fi

if ! getent group racdba > /dev/null; then
    groupadd -g 54327 racdba
    echo "✓ racdba group created"
else
    echo "✓ racdba group exists"
fi
echo ""

# Create oracle user
echo "[5/9] Creating Oracle User..."
echo "-------------------------------------------"
if ! id oracle > /dev/null 2>&1; then
    useradd -u 54321 -g oinstall -G dba,oper,backupdba,dgdba,kmdba,racdba oracle
    echo "oracle:Oracle123" | chpasswd
    echo "✓ oracle user created with password Oracle123"
else
    echo "✓ oracle user exists"
    usermod -g oinstall -G dba,oper,backupdba,dgdba,kmdba,racdba oracle
    echo "oracle:Oracle123" | chpasswd
    echo "✓ oracle user updated"
fi
echo ""

# Create OFA directories
echo "[6/9] Creating OFA Directory Structure..."
echo "-------------------------------------------"
mkdir -p /u01/app/oracle/product/19.0.0/dbhome_1
mkdir -p /u01/app/oraInventory
chown -R oracle:oinstall /u01
chmod -R 775 /u01
echo "✓ Directory structure created:"
ls -ld /u01
ls -ld /u01/app
echo ""

# Kernel parameters
echo "[7/9] Configuring Kernel Parameters..."
echo "-------------------------------------------"
cat > /etc/sysctl.d/99-oracle.conf << 'EOF'
# Oracle Database 19c Kernel Parameters
fs.file-max = 6815744
kernel.sem = 250 32000 100 128
kernel.shmmni = 4096
kernel.shmall = 1073741824
kernel.shmmax = 4398046511104
kernel.panic_on_oops = 1
net.core.rmem_default = 262144
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
net.ipv4.conf.all.rp_filter = 2
net.ipv4.conf.default.rp_filter = 2
fs.aio-max-nr = 1048576
net.ipv4.ip_local_port_range = 9000 65500
EOF

sysctl -p /etc/sysctl.d/99-oracle.conf
echo "✓ Kernel parameters configured"
echo ""

# Resource limits
echo "[8/9] Configuring Resource Limits..."
echo "-------------------------------------------"
cat > /etc/security/limits.d/99-oracle.conf << 'EOF'
oracle   soft   nofile    1024
oracle   hard   nofile    65536
oracle   soft   nproc    16384
oracle   hard   nproc    16384
oracle   soft   stack    10240
oracle   hard   stack    32768
oracle   hard   memlock    134217728
oracle   soft   memlock    134217728
EOF

echo "✓ Resource limits configured"
cat /etc/security/limits.d/99-oracle.conf
echo ""

# SELinux and Firewall
echo "[9/9] Configuring SELinux and Firewall..."
echo "-------------------------------------------"
setenforce 0
sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
echo "✓ SELinux set to permissive"

systemctl stop firewalld
systemctl disable firewalld
echo "✓ Firewall disabled"
echo ""

echo "============================================"
echo "  TP01 COMPLETED SUCCESSFULLY"
echo "============================================"
echo ""
echo "Summary:"
echo "  • SWAP: 4GB configured"
echo "  • Oracle packages: Installed"
echo "  • Oracle user: oracle (password: Oracle123)"
echo "  • Oracle groups: oinstall, dba, oper, backupdba, dgdba, kmdba, racdba"
echo "  • ORACLE_BASE: /u01/app/oracle"
echo "  • ORACLE_HOME: /u01/app/oracle/product/19.0.0/dbhome_1"
echo "  • Kernel parameters: Configured"
echo "  • Resource limits: Configured"
echo "  • SELinux: Permissive"
echo "  • Firewall: Disabled"
echo ""
echo "Next: Run TP02 to configure environment and download Oracle binaries"
