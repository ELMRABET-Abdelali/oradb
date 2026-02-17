#!/bin/bash
# TP03 - Installation Oracle 19c et Création Instance
# Rocky Linux 8
# Description: Software installation + DBCA database creation

set -e

echo "================================================"
echo "  TP03: Installation Oracle et Création DB"
echo "  Rocky Linux 8 - Oracle 19c"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/6] Préparation fichier response pour installation..."

cat > /tmp/db_install.rsp << EOF
oracle.install.option=INSTALL_DB_SWONLY
UNIX_GROUP_NAME=oinstall
INVENTORY_LOCATION=/u01/app/oraInventory
ORACLE_HOME=$ORACLE_HOME
ORACLE_BASE=$ORACLE_BASE
oracle.install.db.InstallEdition=EE
oracle.install.db.OSDBA_GROUP=dba
oracle.install.db.OSOPER_GROUP=oper
oracle.install.db.OSBACKUPDBA_GROUP=backupdba
oracle.install.db.OSDGDBA_GROUP=dgdba
oracle.install.db.OSKMDBA_GROUP=kmdba
oracle.install.db.OSRACDBA_GROUP=racdba
SECURITY_UPDATES_VIA_MYORACLESUPPORT=false
DECLINE_SECURITY_UPDATES=true
EOF

echo "✓ Response file créé"

echo ""
echo "[2/6] Lancement installation Software Only..."
echo "Durée estimée: 15-20 minutes"
echo ""

cd $ORACLE_HOME
./runInstaller -silent \
    -responseFile /tmp/db_install.rsp \
    -ignorePrereq \
    -waitforcompletion

echo ""
echo "✓ Installation Software terminée"
echo ""
echo "IMPORTANT: Exécuter les scripts root (en tant que root):"
echo "  sudo /u01/app/oraInventory/orainstRoot.sh"
echo "  sudo $ORACLE_HOME/root.sh"
echo ""
read -p "Appuyez sur ENTRÉE après avoir exécuté les scripts root..."

echo ""
echo "[3/6] Configuration Listener..."

mkdir -p $ORACLE_HOME/network/admin

cat > $ORACLE_HOME/network/admin/listener.ora << 'EOF'
LISTENER =
  (DESCRIPTION_LIST =
    (DESCRIPTION =
      (ADDRESS = (PROTOCOL = TCP)(HOST = 0.0.0.0)(PORT = 1521))
      (ADDRESS = (PROTOCOL = IPC)(KEY = EXTPROC1521))
    )
  )

SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (GLOBAL_DBNAME = GDCPROD)
      (ORACLE_HOME = /u01/app/oracle/product/19.3.0/dbhome_1)
      (SID_NAME = GDCPROD)
    )
  )

ADR_BASE_LISTENER = /u01/app/oracle
EOF

# Démarrer listener
lsnrctl start

echo "✓ Listener configuré et démarré"

echo ""
echo "[4/6] Création base de données GDCPROD..."
echo "Configuration: CDB avec 1 PDB (GDCPDB)"
echo "Durée estimée: 10-15 minutes"
echo ""

dbca -silent \
  -createDatabase \
  -templateName General_Purpose.dbc \
  -gdbname GDCPROD \
  -sid GDCPROD \
  -createAsContainerDatabase true \
  -numberOfPDBs 1 \
  -pdbName GDCPDB \
  -pdbAdminPassword Oracle123 \
  -sysPassword SysOracle123 \
  -systemPassword SystemOracle123 \
  -datafileDestination '/u01/app/oracle/oradata' \
  -storageType FS \
  -characterSet AL32UTF8 \
  -nationalCharacterSet AL16UTF16 \
  -memoryPercentage 50 \
  -emConfiguration NONE \
  -ignorePreReqs

echo ""
echo "✓ Base de données créée"

echo ""
echo "[5/6] Configuration auto-start..."

# Ajouter à /etc/oratab
echo "GDCPROD:$ORACLE_HOME:Y" | sudo tee -a /etc/oratab

echo ""
echo "[6/6] Vérification installation..."

sqlplus -s / as sysdba << 'EOSQL'
SET PAGESIZE 100
SELECT name, open_mode, log_mode, cdb FROM v$database;
SELECT name, open_mode FROM v$pdbs;
EXIT;
EOSQL

echo ""
echo "================================================"
echo "  TP03 TERMINÉ - Oracle 19c Opérationnel"
echo "================================================"
echo ""
echo "Détails installation:"
echo "- CDB Name: GDCPROD"
echo "- PDB Name: GDCPDB"
echo "- Listener: Port 1521"
echo "- SYS Password: SysOracle123"
echo "- SYSTEM Password: SystemOracle123"
echo "- PDB Admin: Oracle123"
echo ""
echo "Connexion:"
echo "  sqlplus / as sysdba"
echo "  sqlplus sys/SysOracle123@localhost:1521/GDCPROD as sysdba"
echo ""
echo "Prochaine étape: TP04 - Multiplexage fichiers critiques"
