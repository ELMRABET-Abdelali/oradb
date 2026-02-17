# 🚀 Guide d'Installation et Utilisation - OracleDBA Package

**Version:** 1.0.0  
**Date:** Février 2026

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Installation du Package](#installation-du-package)
3. [Vérification Pré-Installation](#vérification-pré-installation)
4. [Téléchargement Oracle 19c](#téléchargement-oracle-19c)
5. [Installation Oracle Complète](#installation-oracle-complète)
6. [Tests Post-Installation](#tests-post-installation)
7. [Utilisation Avancée](#utilisation-avancée)
8. [Dépannage](#dépannage)

---

## 🎯 Vue d'Ensemble

Le package **OracleDBA** fournit un système complet d'installation, configuration et administration d'Oracle 19c sur Rocky Linux 8/9. Il inclut:

✅ **Vérification système** automatique  
✅ **Téléchargement** et extraction Oracle  
✅ **Installation silencieuse** avec response files  
✅ **Tests automatiques** complets  
✅ **Gestion RMAN, Data Guard, ASM, RAC**  
✅ **Tuning et monitoring**  

---

## 📦 Installation du Package

### Méthode 1: Installation depuis GitHub

```bash
# Cloner le repository
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba

# Installer le package
sudo pip3 install -e .

# Vérifier l'installation
oradba --version
```

### Méthode 2: Installation depuis PyPI (à venir)

```bash
pip install oracledba
```

### Méthode 3: Installation automatique sur VM

```bash
# Télécharger le script d'installation
curl -O https://raw.githubusercontent.com/ELMRABET-Abdelali/oracledba/main/install.sh

# Exécuter l'installation
sudo bash install.sh
```

---

## 🔍 Vérification Pré-Installation

Avant d'installer Oracle, vérifiez que votre système répond aux exigences:

```bash
# Vérification complète du système
sudo oradba precheck

# Générer un script de correction automatique
sudo oradba precheck --fix

# Exécuter les corrections
sudo bash fix-precheck-issues.sh
```

### Ce qui est vérifié:

- ✓ Distribution Linux (Rocky/CentOS/RHEL 8/9)
- ✓ RAM minimum 8 GB
- ✓ SWAP minimum 8 GB
- ✓ Espace disque minimum 50 GB
- ✓ Packages système requis
- ✓ Paramètres kernel
- ✓ Configuration réseau
- ✓ SELinux (Permissive/Disabled)
- ✓ Firewall

---

## 📥 Téléchargement Oracle 19c

### Option 1: Téléchargement Manuel

```bash
# Afficher les instructions de téléchargement
oradba download database

# Placer le fichier téléchargé dans:
# /opt/oracle/install/LINUX.X64_193000_db_home.zip
```

### Option 2: URL Personnalisée

Si vous avez les binaires sur un serveur web ou OCI Bucket:

```bash
# Télécharger depuis URL personnalisée
oradba download database --url "https://your-server.com/oracle19c.zip" --dir /opt/oracle/install
```

### Option 3: Extraction Manuelle

Si vous avez déjà le ZIP:

```bash
# Extraire vers ORACLE_HOME
oradba download extract /path/to/LINUX.X64_193000_db_home.zip --to /u01/app/oracle/product/19.3.0/dbhome_1
```

---

## 🛠️ Installation Oracle Complète

### Étape par Étape

#### 1. Préparer le Système

```bash
# Installer les packages système, créer users/groups, configurer kernel
sudo oradba install system

# Vérifier la préparation
oradba precheck
```

#### 2. Initialiser la VM

```bash
# Pour une base de données standalone
sudo oradba vm-init --role database

# Pour un nœud RAC
sudo oradba vm-init --role rac-node --node-number 1

# Pour un standby Data Guard
sudo oradba vm-init --role dataguard-standby
```

#### 3. Générer les Response Files

```bash
# Générer tous les fichiers de réponse
oradba genrsp all --config /opt/oracle/config/default.yml --output-dir /tmp

# Ou générer individuellement
oradba genrsp db-install --output /tmp/db_install.rsp
oradba genrsp dbca --output /tmp/dbca.rsp
```

#### 4. Installation Complète

```bash
# Installation complète automatique
sudo oradba install full --config /opt/oracle/config/default.yml

# Ou étape par étape:
sudo oradba install binaries --config /opt/oracle/config/default.yml
sudo oradba install database --config /opt/oracle/config/default.yml --name GDCPROD
```

### Installation Rapide (One-Liner)

```bash
# Tout en une seule commande
sudo oradba precheck --fix && \
sudo bash fix-precheck-issues.sh && \
sudo oradba install full --config /opt/oracle/config/default.yml
```

---

## 🧪 Tests Post-Installation

### Tests Automatiques Complets

```bash
# Lancer tous les tests
oradba test

# Avec rapport détaillé
oradba test --report

# Spécifier ORACLE_HOME et SID
oradba test --oracle-home /u01/app/oracle/product/19.3.0/dbhome_1 --oracle-sid GDCPROD
```

### Tests Couverts

- ✓ Variables d'environnement Oracle
- ✓ Binaires Oracle (sqlplus, rman, lsnrctl)
- ✓ Listener status et enregistrement
- ✓ Connexion base de données
- ✓ Status instance (OPEN)
- ✓ Tablespaces (SYSTEM, SYSAUX, etc.)
- ✓ Utilisateurs (SYS, SYSTEM)
- ✓ PDB (si multitenant)
- ✓ Archive log mode
- ✓ Configuration RMAN
- ✓ Métriques performance (SGA, PGA, sessions)

### Résultat Attendu

```
Oracle 19c Test Results
┌────────────────────┬────────┬─────────────────────────────┐
│ Test               │ Status │ Details                     │
├────────────────────┼────────┼─────────────────────────────┤
│ ENVIRONMENT        │ ✓ PASS │ ✓ ORACLE_HOME exists        │
│ BINARIES           │ ✓ PASS │ ✓ sqlplus found             │
│ LISTENER           │ ✓ PASS │ ✓ Listener is running       │
│ DATABASE           │ ✓ PASS │ ✓ Database connection OK    │
│ INSTANCE           │ ✓ PASS │ ✓ Instance status: OPEN     │
└────────────────────┴────────┴─────────────────────────────┘

✓ All tests passed!
Oracle 19c is fully operational.
```

---

## 🎯 Utilisation Avancée

### Gestion Quotidienne

```bash
# Démarrer la base
oradba start

# Arrêter la base
oradba stop

# Redémarrer
oradba restart

# Vérifier le status
oradba status

# Se connecter à SQL*Plus
oradba sqlplus
```

### Backup RMAN

```bash
# Configuration RMAN
oradba rman setup --retention 7 --compression

# Backup complet
oradba rman backup --type full --tag DAILY_BACKUP

# Backup incrémental
oradba rman backup --type incremental

# Backup archive logs
oradba rman backup --type archive

# Restauration
oradba rman restore --point-in-time "2026-02-15 14:30:00"
```

### Data Guard

```bash
# Setup Data Guard
oradba dataguard setup --primary-host db1 --standby-host db2

# Switchover
oradba dataguard switchover

# Failover
oradba dataguard failover

# Vérifier status
oradba dataguard status
```

### ASM et RAC

```bash
# Créer diskgroup ASM
oradba asm create --diskgroup DATA --disks /dev/sdb,/dev/sdc

# Setup RAC
oradba rac setup --nodes 2 --scan-name rac-scan

# Vérifier RAC
oradba rac status
```

### Multitenant PDB

```bash
# Créer PDB
oradba pdb create --name APPPDB --admin-password Oracle123

# Ouvrir PDB
oradba pdb open --name APPPDB

# Fermer PDB
oradba pdb close --name APPPDB

# Lister PDBs
oradba pdb list
```

### Tuning

```bash
# Analyser les performances
oradba tuning analyze

# Tuning SQL
oradba tuning sql

# AWR report
oradba tuning awr --days 1

# Recommandations
oradba tuning advisor
```

### Monitoring

```bash
# Monitor tablespaces
oradba monitor tablespaces

# Monitor sessions
oradba monitor sessions

# Sessions actives uniquement
oradba monitor sessions --active-only

# Voir alert log
oradba logs alert --tail 100

# Voir listener log
oradba logs listener
```

---

## 📊 Configuration Personnalisée

### Fichier de Configuration

Créer `/opt/oracle/config/mydb.yml`:

```yaml
oracle:
  version: "19c"
  edition: "EE"
  base: "/u01/app/oracle"
  home: "/u01/app/oracle/product/19.3.0/dbhome_1"
  inventory_location: "/u01/app/oraInventory"
  oracle_group: "oinstall"
  dba_group: "dba"

database:
  db_name: "GDCPROD"
  sid: "GDCPROD"
  pdb_name: "GDCPDB"
  charset: "AL32UTF8"
  memory_gb: 4
  storage_type: "FS"  # FS ou ASM
  data_file_dest: "/u01/app/oracle/oradata"
  fra_dest: "/u01/app/oracle/fast_recovery_area"
  fra_size_gb: 20

system:
  oracle_user: "oracle"
  oracle_password: "Oracle123"
  
network:
  listener_port: 1521
  hostname: "db.example.com"

backup:
  retention_days: 7
  backup_dir: "/u01/backup"
  compression: true
```

### Utiliser la Configuration

```bash
# Toutes les commandes acceptent --config
oradba install full --config /opt/oracle/config/mydb.yml
oradba genrsp all --config /opt/oracle/config/mydb.yml
oradba test --config /opt/oracle/config/mydb.yml
```

---

## 🐛 Dépannage

### Problème: Precheck échoue

```bash
# Voir les détails
sudo oradba precheck

# Générer et exécuter les corrections
sudo oradba precheck --fix
sudo bash fix-precheck-issues.sh

# Re-vérifier
sudo oradba precheck
```

### Problème: Installation binaires échoue

```bash
# Vérifier les logs
cat /u01/app/oraInventory/logs/installActions*.log

# Vérifier ORACLE_HOME
ls -la $ORACLE_HOME

# Vérifier permissions
sudo chown -R oracle:oinstall /u01/app/oracle
```

### Problème: Tests échouent

```bash
# Tester connexion manuelle
sqlplus / as sysdba

# Vérifier listener
lsnrctl status

# Vérifier instance
ps -ef | grep pmon

# Re-démarrer
oradba restart
```

### Problème: Listener ne démarre pas

```bash
# Vérifier configuration
cat $ORACLE_HOME/network/admin/listener.ora

# Re-créer listener
netca -silent -responseFile /tmp/netca.rsp

# Démarrer manuellement
lsnrctl start
```

---

## 📞 Support

### Documentation

- **GitHub**: https://github.com/ELMRABET-Abdelali/oracledba
- **Wiki**: https://github.com/ELMRABET-Abdelali/oracledba/wiki
- **Issues**: https://github.com/ELMRABET-Abdelali/oracledba/issues

### Commandes d'Aide

```bash
# Aide générale
oradba --help

# Aide par commande
oradba install --help
oradba rman --help
oradba test --help
```

### Logs

```bash
# Logs Oracle
oradba logs alert
oradba logs listener

# Logs système
journalctl -u oracle-database -f
```

---

## 🎓 Exemples Complets

### Exemple 1: Installation Fresh sur VM Vierge

```bash
# 1. Installer le package
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba
sudo pip3 install -e .

# 2. Vérifier le système
sudo oradba precheck --fix
sudo bash fix-precheck-issues.sh

# 3. Télécharger Oracle (manuel)
# Placer LINUX.X64_193000_db_home.zip dans /opt/oracle/install/

# 4. Installation complète
sudo oradba install system
sudo oradba vm-init --role database
sudo oradba install full

# 5. Tester
oradba test --report

# 6. Utiliser
oradba status
oradba sqlplus
```

### Exemple 2: Setup Data Guard

```bash
# Sur Primary
oradba dataguard setup --primary-host db-primary --standby-host db-standby
oradba rman backup --type full

# Sur Standby
oradba vm-init --role dataguard-standby
oradba dataguard restore

# Vérifier
oradba dataguard status
```

### Exemple 3: RAC Installation

```bash
# Node 1
sudo oradba vm-init --role rac-node --node-number 1
sudo oradba asm create --diskgroup DATA

# Node 2
sudo oradba vm-init --role rac-node --node-number 2

# Setup RAC
sudo oradba rac setup --nodes 2 --scan-name rac-scan

# Vérifier
oradba rac status
```

---

## 🏆 Bonnes Pratiques

1. **Toujours** exécuter `precheck` avant installation
2. **Sauvegarder** les fichiers de configuration
3. **Tester** après chaque changement majeur
4. **Monitorer** régulièrement avec `oradba monitor`
5. **Backups** quotidiens avec RMAN
6. **Documenter** vos modifications

---

**🎉 Félicitations ! Vous êtes prêt à utiliser OracleDBA !**

Pour plus d'aide: `oradba --help` ou consultez la documentation complète sur GitHub.
