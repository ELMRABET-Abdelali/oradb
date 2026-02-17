#!/bin/bash
# TP02 - Configuration Environnement et Téléchargement Binaires
# Oracle 19c - Rocky Linux 8
# Description: Variables d'environnement et download Oracle software

set -e

echo "================================================"
echo "  TP02: Installation Binaire Oracle 19c"
echo "  Rocky Linux 8"
echo "  $(date)"
echo "================================================"

# Vérifier utilisateur oracle
if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Ce script doit être exécuté en tant qu'oracle"
    echo "Commande: su - oracle"
    exit 1
fi

echo ""
echo "[1/4] Configuration variables d'environnement..."

# Créer .bash_profile
cat > ~/.bash_profile << 'EOF'
# .bash_profile Oracle 19c - Rocky Linux 8

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    . ~/.bashrc
fi

# Oracle Settings
export TMP=/tmp
export TMPDIR=$TMP
export ORACLE_HOSTNAME=$(hostname)
export ORACLE_UNQNAME=GDCPROD
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=/usr/sbin:/usr/local/bin:$PATH
export PATH=$ORACLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:/lib:/usr/lib
export CLASSPATH=$ORACLE_HOME/jlib:$ORACLE_HOME/rdbms/jlib
EOF

# Sourcer
source ~/.bash_profile
echo "✓ Variables Oracle configurées"
echo "  ORACLE_HOME=$ORACLE_HOME"
echo "  ORACLE_SID=$ORACLE_SID"

echo ""
echo "[2/4] Vérification Google Drive file ID..."
GOOGLE_DRIVE_ID="1Mi7B2HneMBIyxJ01tnA-ThQ9hr2CAsns"
echo "✓ File ID: $GOOGLE_DRIVE_ID"

echo ""
echo "[3/4] Installation gdown (Google Drive downloader)..."
# Try multiple methods to ensure gdown is installed
python3 -m pip install --user --quiet gdown 2>/dev/null || \
    pip3 install --user --quiet gdown 2>/dev/null || \
    pip3.9 install --user --quiet gdown 2>/dev/null || {
    echo "ERREUR: Impossible d'installer gdown"
    exit 1
}

# Ensure gdown is on PATH
export PATH="$HOME/.local/bin:$PATH"
if ! command -v gdown &> /dev/null; then
    echo "ERREUR: gdown introuvable après installation"
    echo "PATH: $PATH"
    exit 1
fi
echo "✓ gdown installé ($(gdown --version 2>/dev/null || echo 'version inconnue'))"

echo ""
echo "[4/4] Téléchargement Oracle 19c (3.06 GB)..."
echo "Destination: $ORACLE_HOME"
echo "Cela peut prendre 5-10 minutes selon la connexion..."

cd $ORACLE_HOME

if [ -f "LINUX.X64_193000_db_home.zip" ]; then
    echo "✓ Fichier déjà téléchargé"
else
    gdown $GOOGLE_DRIVE_ID -O LINUX.X64_193000_db_home.zip
    echo "✓ Téléchargement terminé"
fi

# Vérifier taille fichier
FILE_SIZE=$(du -h LINUX.X64_193000_db_home.zip | cut -f1)
echo "Taille fichier: $FILE_SIZE"

echo ""
echo "Extraction des binaires (6.5 GB)..."
echo "Cela prend environ 2-3 minutes..."
unzip -q LINUX.X64_193000_db_home.zip

# Nettoyer
rm -f LINUX.X64_193000_db_home.zip

echo ""
echo "================================================"
echo "  TP02 TERMINÉ - Binaires Oracle installés"
echo "================================================"
echo ""
echo "Fichiers extraits dans: $ORACLE_HOME"
echo "Taille totale: $(du -sh $ORACLE_HOME | cut -f1)"
echo ""
echo "Vérifications:"
ls -lh $ORACLE_HOME/bin/sqlplus 2>/dev/null && echo "✓ SQL*Plus présent" || echo "✗ SQL*Plus manquant"
ls -lh $ORACLE_HOME/bin/oracle 2>/dev/null && echo "✓ Oracle binary présent" || echo "✗ Oracle binary manquant"
test -f $ORACLE_HOME/runInstaller && echo "✓ runInstaller présent" || echo "✗ runInstaller manquant"

echo ""
echo "Prochaine étape: TP03 - Installation logiciel et création instance"
echo "Commande: bash tp03-installation.sh"
