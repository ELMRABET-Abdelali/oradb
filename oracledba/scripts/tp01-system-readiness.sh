#!/bin/bash
# TP01 - Préparation Système Rocky Linux 8
# Oracle 19c - Installation automatique
# Description: Configuration système complète pour Oracle Database

set -e  # Arrêt si erreur

echo "================================================"
echo "  TP01: Préparation Système Rocky Linux 8"
echo "  Oracle 19c Enterprise Edition"
echo "  $(date)"
echo "================================================"

# Vérifier que le script est exécuté en root
if [ "$EUID" -ne 0 ]; then 
    echo "ERREUR: Ce script doit être exécuté en root"
    exit 1
fi

echo ""
echo "[1/8] Vérification des ressources système..."
echo "RAM totale: $(free -h | grep Mem | awk '{print $2}')"
echo "Espace disque /u01: $(df -h / | tail -1 | awk '{print $4}')"
echo "CPUs: $(nproc)"

# Vérifier RAM minimum (2GB)
RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
if [ $RAM_KB -lt 2000000 ]; then
    echo "ATTENTION: RAM insuffisante (< 2GB)"
fi

echo ""
echo "[2/8] Configuration SWAP (4GB)..."
if [ ! -f /swapfile ]; then
    dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    
    # Permanent dans fstab
    if ! grep -q '/swapfile' /etc/fstab; then
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
    echo "✓ SWAP 4GB créé et activé"
else
    echo "✓ SWAP déjà configuré"
fi

echo ""
echo "[3/8] Création groupes Oracle..."
getent group oinstall > /dev/null 2>&1 || groupadd -g 54321 oinstall
getent group dba > /dev/null 2>&1 || groupadd -g 54322 dba
getent group oper > /dev/null 2>&1 || groupadd -g 54323 oper
getent group backupdba > /dev/null 2>&1 || groupadd -g 54324 backupdba
getent group dgdba > /dev/null 2>&1 || groupadd -g 54325 dgdba
getent group kmdba > /dev/null 2>&1 || groupadd -g 54326 kmdba
getent group racdba > /dev/null 2>&1 || groupadd -g 54327 racdba
echo "✓ Groupes Oracle créés"

echo ""
echo "[4/8] Création utilisateur oracle..."
if ! id oracle > /dev/null 2>&1; then
    useradd -u 54321 -g oinstall -G dba,oper,backupdba,dgdba,kmdba,racdba oracle
    echo "oracle:Oracle123" | chpasswd
    echo "✓ Utilisateur oracle créé (password: Oracle123)"
else
    echo "✓ Utilisateur oracle existe déjà"
fi

echo ""
echo "[5/8] Installation packages requis..."
dnf update -y -q

dnf install -y -q \
    bc binutils compat-openssl10 elfutils-libelf elfutils-libelf-devel \
    fontconfig-devel glibc glibc-devel ksh libaio libaio-devel \
    libX11 libXau libXi libXtst libXrender libXrender-devel \
    libgcc libstdc++ libstdc++-devel libxcb make net-tools nfs-utils \
    python3 python3-configshell python3-rtslib python3-six \
    smartmontools sysstat unixODBC libnsl libnsl2 libnsl2-devel \
    tar zip unzip wget

echo "✓ Packages installés"

echo ""
echo "[6/8] Configuration kernel parameters..."
cat >> /etc/sysctl.conf << 'EOF'
# Oracle 19c Kernel Parameters - Rocky Linux 8
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

sysctl -p > /dev/null 2>&1
echo "✓ Paramètres kernel appliqués"

echo ""
echo "[7/8] Configuration limites utilisateur..."
cat >> /etc/security/limits.conf << 'EOF'
# Oracle 19c User Limits
oracle   soft   nofile    1024
oracle   hard   nofile    65536
oracle   soft   nproc    16384
oracle   hard   nproc    16384
oracle   soft   stack    10240
oracle   hard   stack    32768
oracle   hard   memlock    134217728
oracle   soft   memlock    134217728
EOF
echo "✓ Limites utilisateur configurées"

echo ""
echo "[8/8] Création structure OFA..."
mkdir -p /u01/app/oracle/product/19.3.0/dbhome_1
mkdir -p /u01/app/oraInventory
mkdir -p /u01/app/oracle/oradata
mkdir -p /u01/app/oracle/fast_recovery_area
mkdir -p /u01/app/oracle/admin
mkdir -p /u01/app/oracle/backup

chown -R oracle:oinstall /u01
chmod -R 775 /u01
echo "✓ Structure /u01 créée"

# SELinux et Firewall
setenforce 0 2>/dev/null || true
sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config 2>/dev/null || true

echo ""
echo "================================================"
echo "  TP01 TERMINÉ - Système prêt pour Oracle 19c"
echo "================================================"
echo ""
echo "Récapitulatif:"
echo "- SWAP: $(swapon --show | grep swapfile | awk '{print $3}')"
echo "- Utilisateur: oracle (uid=54321)"
echo "- Groupes: oinstall, dba, oper, backupdba, dgdba, kmdba, racdba"
echo "- Structure: /u01/app/oracle créée"
echo "- Packages: 50+ installés"
echo "- Kernel: Paramètres Oracle appliqués"
echo ""
echo "Prochaine étape: TP02 - Configuration environnement Oracle"
echo "Commande: su - oracle && source ~/.bash_profile"
