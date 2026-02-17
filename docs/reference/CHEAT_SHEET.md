# 📋 OracleDBA - Aide-Mémoire (Cheat Sheet)

Guide de référence rapide pour toutes les commandes oradba essentielles.

---

## 🚀 Installation

```bash
# Depuis GitHub
git clone https://github.com/ELMRABET-Abdelali/oracledba.git && cd oracledba && pip install -e .

# Depuis PyPI
pip install oracledba

# Avec support Oracle complet
pip install oracledba[oracle]

# Vérifier installation
oradba --version
oradba --help
```

---

## 📦 Installation Oracle 19c (TP01-03)

### Installation Complète (Automatique)

```bash
# Une seule commande pour tout installer
sudo oradba install full --config my-config.yml

# Avec options
sudo oradba install full --skip-system          # Sauter préparation système
sudo oradba install full --skip-binaries        # Sauter installation binaires
```

### Installation Pas-à-Pas

```bash
# TP01: Préparation système (users, groups, kernel, swap)
sudo oradba install system

# TP02: Installation binaires Oracle
sudo oradba install binaries

# TP03: Création base de données
oradba install database
oradba install database --name PRODDB           # Nom personnalisé
oradba install database --cdb --pdbs PDB1,PDB2  # CDB avec PDBs
```

### Vérification

```bash
oradba install check-prereqs          # Vérifier prérequis
oradba install verify-binaries        # Vérifier binaires installés
oradba install system-report          # Rapport système détaillé
```

---

## 🗄️ Gestion Base de Données

### Statut et Contrôle

```bash
oradba db status                      # Statut instance, listener, mode
oradba db start                       # Démarrer base
oradba db stop                        # Arrêter base (SHUTDOWN IMMEDIATE)
oradba db restart                     # Redémarrer
oradba db mount                       # Monter sans ouvrir
oradba db open                        # Ouvrir base
```

### Connexion SQL

```bash
oradba db sqlplus                     # SQL*Plus normal
oradba db sqlplus --sysdba            # SQL*Plus en SYSDBA
oradba db exec script.sql             # Exécuter script SQL
```

### Monitoring

```bash
oradba db monitor-sessions            # Sessions actives
oradba db monitor-tablespaces         # Utilisation tablespaces
oradba db tail-alert --lines 100      # Alert log (dernières 100 lignes)
oradba db diagnose                    # Diagnostic global
```

---

## 💾 Stockage (TP04-05)

### Fichiers Critiques (TP04)

```bash
# Multiplexage automatique
oradba db multiplex-critical --auto

# Control files
oradba db multiplex-control-files --locations /u01,/u02

# Redo logs
oradba db add-redo-members --location /u02
oradba db switch-logfile

# Analyse
oradba db analyze-critical-files
oradba db show-critical-files
```

### Tablespaces (TP05)

```bash
# Lister
oradba db list-tablespaces

# Créer
oradba db create-tablespace --name DATA --size 1G --autoextend --maxsize 10G

# Gérer
oradba db add-datafile --tablespace DATA --size 1G
oradba db resize-datafile --file /path/to/file.dbf --size 2G

# Analyser
oradba db analyze-storage
oradba db storage-report
```

---

## 🔐 Sécurité (TP06)

### Utilisateurs

```bash
# Créer
oradba security create-user --name APP_USER --password Pass123 \
  --default-tablespace DATA --quota 5G

# Lister
oradba security list-users
oradba security list-users --filter APP%       # Avec filtre
```

### Rôles et Privilèges

```bash
# Créer rôle
oradba security create-role --name DEVELOPER \
  --privileges "CREATE TABLE,CREATE VIEW"

# Assigner rôle
oradba security grant-role --role DEVELOPER --user APP_USER

# Révoquer
oradba security revoke-role --role DEVELOPER --user APP_USER
```

### Profiles de Sécurité

```bash
# Créer profile
oradba security create-profile --name SECURE \
  --failed-login-attempts 5 --password-life-days 90

# Assigner
oradba security assign-profile --profile SECURE --user APP_USER
```

### Audit

```bash
# Activer
oradba security enable-audit --actions "CREATE SESSION,DROP TABLE"

# Consulter logs
oradba security audit-report --last-hours 24
```

---

## ⏮️ Flashback (TP07)

```bash
# Activer Flashback Database
oradba flashback enable --retention-hours 48

# Récupérer table DROP
oradba flashback drop-restore --table CUSTOMERS

# Interroger passé (5 minutes ago)
oradba flashback query --table CUSTOMERS --minutes-ago 5

# Restaurer table à timestamp
oradba flashback table --table CUSTOMERS \
  --timestamp "2026-02-16 14:30:00"

# Désactiver
oradba flashback disable

# Status
oradba flashback status
```

---

## 💾 RMAN Backup (TP08)

### Configuration

```bash
# Setup RMAN
oradba rman setup --retention-days 7 --compression

# Vérifier config
oradba rman show-config
```

### Backups

```bash
# Backup FULL (niveau 0)
oradba rman backup --type full --tag DAILY_FULL

# Backup incrémental (niveau 1)
oradba rman backup --type incremental --tag HOURLY_INC

# Backup archivelogs uniquement
oradba rman backup --type archive --delete-input

# Backup avec compression
oradba rman backup --type full --compression high
```

### Gestion Backups

```bash
# Lister backups
oradba rman list-backups
oradba rman list-backups --type full          # Seulement full
oradba rman list-backups --last-days 7        # Derniers 7 jours

# Valider backups
oradba rman validate
oradba rman validate --backupset 12345

# Supprimer obsolètes
oradba rman delete-obsolete
oradba rman delete-obsolete --force           # Sans confirmation

# Crosscheck
oradba rman crosscheck
```

### Restauration

```bash
# Restaurer base complète
oradba rman restore

# Restaurer à point dans le temps
oradba rman restore --point-in-time "2026-02-16 14:00:00"

# Restaurer tablespace spécifique
oradba rman restore --tablespace USERS

# Restaurer datafile
oradba rman restore --datafile 4
```

### Rapports

```bash
oradba rman report                            # Rapport global
oradba rman report --obsolete                 # Backups obsolètes
oradba rman report --need-backup              # Fichiers à sauvegarder
```

---

## 🔄 Data Guard (TP09)

### Setup PRIMARY

```bash
# Configuration PRIMARY pour Data Guard
oradba dataguard setup-primary --standby-host standby.server.com

# Vérifier configuration
oradba dataguard verify-primary
```

### Créer STANDBY

```bash
# Sur PRIMARY: Créer standby via duplication
oradba dataguard create-standby --standby-host standby.server.com

# Sur STANDBY: Démarrer APPLY
oradba dataguard start-apply
```

### Monitoring

```bash
# Status global
oradba dataguard status

# Vérifier LAG
oradba dataguard check-lag

# Vérifier transport logs
oradba dataguard check-transport

# Monitoring continu
watch -n 10 "oradba dataguard status"
```

### Switchover / Failover

```bash
# Switchover planifié (PRIMARY → STANDBY)
oradba dataguard switchover --to-standby

# Failover urgence (si PRIMARY down)
oradba dataguard failover --standby-host standby.server.com --force

# Re-synchroniser après problème
oradba dataguard resync --force
```

---

## ⚡ Performance Tuning (TP10)

### Santé Système

```bash
# Health check rapide
oradba tuning health-check

# Dashboard temps réel
oradba tuning dashboard

# Surveiller mémoire
oradba tuning memory-advisor
```

### Rapports AWR

```bash
# Générer rapport AWR (dernière heure)
oradba tuning awr-report --hours 1 --output /tmp/awr.html

# Entre timestamps
oradba tuning awr-report --begin "2026-02-16 10:00:00" \
  --end "2026-02-16 11:00:00"

# Créer snapshot manuel
oradba tuning awr-snapshot
```

### SQL Tuning

```bash
# Top SQL (10 plus lents)
oradba tuning top-sql --limit 10

# Top SQL par critère
oradba tuning top-sql --by cpu                # Par CPU
oradba tuning top-sql --by elapsed            # Par temps écoulé
oradba tuning top-sql --by executions         # Par nombre exécutions

# SQL Tuning Advisor sur SQL spécifique
oradba tuning sql-advisor --sql-id 8fzx3m2kp9qrt

# Auto-tuning (appliquer recommandations)
oradba tuning auto-tune --apply
```

### Monitoring Sessions

```bash
# Sessions actives avec détails
oradba tuning monitor-sessions --interval 5   # Refresh toutes les 5s

# Top sessions par ressources
oradba tuning top-sessions --limit 20
```

---

## 🔧 Patching (TP11)

```bash
# Lister patches installés
oradba patch list-installed

# Analyser patch avant application
oradba patch analyze --patch-file /tmp/p35648110.zip

# Appliquer patch
oradba patch apply --patch-file /tmp/p35648110.zip

# Rollback si problème
oradba patch rollback --patch-id 35648110

# Vérifier état post-patch
oradba patch verify
```

---

## 🏢 Multitenant CDB/PDB (TP12)

### Gestion PDBs

```bash
# Lister PDBs
oradba pdb list
oradba pdb status

# Créer PDB
oradba pdb create --name PDB_SALES --admin-user salesadm --admin-pass Sales123

# Cloner PDB
oradba pdb clone --source PDB1 --target PDB1_DEV

# Ouvrir/Fermer
oradba pdb open --name PDB_SALES
oradba pdb close --name PDB_SALES

# Ouvrir toutes les PDBs
oradba pdb open --all
```

### Plug/Unplug PDB

```bash
# Unplugged PDB (export XML)
oradba pdb unplug --name PDB_TEST --xml /tmp/pdb_test.xml

# Plug PDB (import)
oradba pdb plug --xml /tmp/pdb_test.xml --name PDB_TEST_NEW

# Drop PDB
oradba pdb drop --name PDB_OLD --including-datafiles
```

### Connexion PDB

```bash
# Se connecter à PDB spécifique
oradba db sqlplus --pdb PDB_SALES --user salesadm
```

---

## 🤖 AI/ML (TP13)

```bash
# Vérifier capacités AI/ML
oradba ai check-capabilities

# Auto-Indexing (mode observation)
oradba ai enable-auto-index --mode report-only

# Auto-Indexing (implémentation)
oradba ai enable-auto-index --mode implement

# Lister recommandations auto-index
oradba ai list-auto-index-recommendations

# Activer Auto SQL Tuning
oradba ai enable-auto-tuning

# Rapport AI/ML
oradba ai report

# Setup Oracle Machine Learning
oradba ai setup-oml
```

---

## 📦 Data Pump (TP14)

### Export

```bash
# Export schema complet
oradba datapump export --schema GDC_ADMIN --file gdc_admin.dmp --dir /backup

# Export table spécifique
oradba datapump export --table GDC_ADMIN.CUSTOMERS --file customers.dmp

# Export avec compression
oradba datapump export --schema GDC_ADMIN --file schema.dmp --compression all

# Export parallèle
oradba datapump export --schema GDC_ADMIN --file schema_%U.dmp --parallel 4
```

### Import

```bash
# Import schema
oradba datapump import --file gdc_admin.dmp --schema GDC_ADMIN --dir /backup

# Import avec remap schema
oradba datapump import --file prod.dmp --remap-schema PROD:DEV

# Import table spécifique
oradba datapump import --file full.dmp --table CUSTOMERS
```

### Concurrence et Locks

```bash
# Analyser locks actifs
oradba db analyze-locks

# Afficher sessions bloquantes
oradba db show-blocking-sessions

# Tuer session bloquante
oradba db kill-session --sid 125 --serial 38456
```

---

## 💿 ASM et RAC (TP15)

### ASM

```bash
# Vérifier configuration ASM
oradba asm check

# Créer Disk Group
oradba asm create-diskgroup --name DATA --disks /dev/sd[b-d] \
  --redundancy NORMAL

# Lister Disk Groups
oradba asm list-diskgroups

# Status ASM
oradba asm status

# Ajouter disque
oradba asm add-disk --diskgroup DATA --disk /dev/sde

# Afficher architecture
oradba asm show-architecture
```

### RAC

```bash
# Vérifier cluster
oradba rac check-cluster

# Préparer Grid Infrastructure
oradba rac prepare-grid --nodes node1,node2 --nfs-server 192.168.1.100

# Status cluster
oradba rac cluster-status

# Ajouter node
oradba rac add-node --node node3 --vip 192.168.1.13

# Status instances
oradba rac instances-status

# Rapport architecture
oradba rac architecture-report
```

---

## 🌐 NFS (Pour RAC ou Shared Storage)

### Setup Serveur NFS

```bash
# Installer et configurer serveur NFS
oradba nfs setup-server --export-path /oracleshared \
  --clients "192.168.1.11,192.168.1.12,192.168.1.13"

# Vérifier exports
oradba nfs list-exports
```

### Setup Client NFS

```bash
# Monter NFS sur client
oradba nfs setup-client --nfs-server 192.168.1.100 \
  --mount-point /oracleshared

# Vérifier montage
oradba nfs check-mount
```

---

## 📊 Scripts Shell Directs

Si vous préférez exécuter les scripts shell testés directement:

```bash
# TP01: Préparation système
sudo /usr/local/share/oracledba/scripts/tp01-system-readiness.sh

# TP02: Installation binaires
su - oracle
/usr/local/share/oracledba/scripts/tp02-installation-binaire.sh

# TP03: Création instance
/usr/local/share/oracledba/scripts/tp03-creation-instance.sh

# TP04: Multiplexage
/usr/local/share/oracledba/scripts/tp04-fichiers-critiques.sh

# TP05: Stockage
/usr/local/share/oracledba/scripts/tp05-gestion-stockage.sh

# TP06: Sécurité
/usr/local/share/oracledba/scripts/tp06-securite-acces.sh

# TP07: Flashback
/usr/local/share/oracledba/scripts/tp07-flashback.sh

# TP08: RMAN
/usr/local/share/oracledba/scripts/tp08-rman.sh

# TP09: Data Guard
/usr/local/share/oracledba/scripts/tp09-dataguard.sh

# TP10: Tuning
/usr/local/share/oracledba/scripts/tp10-tuning.sh

# TP11: Patching
/usr/local/share/oracledba/scripts/tp11-patching.sh

# TP12: Multitenant
/usr/local/share/oracledba/scripts/tp12-multitenant.sh

# TP13: AI
/usr/local/share/oracledba/scripts/tp13-ai-foundations.sh

# TP14: Data Pump
/usr/local/share/oracledba/scripts/tp14-mobilite-concurrence.sh

# TP15: ASM/RAC
/usr/local/share/oracledba/scripts/tp15-asm-rac-concepts.sh
```

---

## ⚙️ Configuration

### Fichier YAML

```yaml
# ~/my-oracle-config.yml

system:
  os: "Rocky Linux 8"
  min_ram_gb: 4
  swap_size_gb: 4

oracle:
  version: "19.3.0.0.0"
  oracle_base: "/u01/app/oracle"
  oracle_home: "/u01/app/oracle/product/19.3.0/dbhome_1"

database:
  db_name: "PRODDB"
  sid: "PRODDB"
  cdb: true
  sys_password: "ChangeMe123"
  enable_archivelog: true
  enable_flashback: true

backup:
  rman_retention_days: 7
  backup_location: "/u01/backup"
  compression: true
```

### Utiliser Config

```bash
oradba install full --config ~/my-oracle-config.yml
```

---

## 🔍 Aide et Documentation

```bash
# Aide générale
oradba --help

# Aide par module
oradba install --help
oradba rman --help
oradba dataguard --help
oradba tuning --help
oradba pdb --help

# Version
oradba --version
```

### Documentation Complète

- 📘 [Guide Complet](GUIDE_UTILISATION.md) - Tous les TPs avec exemples
- 🔄 [Mapping Scripts](SCRIPTS_MAPPING.md) - Scripts shell ↔️ CLI
- 🔧 [Guide Développeur](DEVELOPER_GUIDE.md) - Architecture et contribution
- 📝 [README](README.md) - Vue d'ensemble
- ⚡ [Quick Start](QUICKSTART.md) - Démarrage rapide

---

## 🆘 Dépannage Rapide

```bash
# Vérifier statut complet
oradba db diagnose

# Logs
oradba db tail-alert --lines 50
oradba db tail-listener --lines 50

# Espace disque
df -h /u01

# Processus Oracle
ps aux | grep ora_

# Listener
lsnrctl status

# Connexion SQL*Plus
sqlplus / as sysdba
SQL> SELECT instance_name, status FROM v$instance;
SQL> SELECT name, open_mode FROM v$database;
```

---

## 🔗 Liens Utiles

- **GitHub:** https://github.com/ELMRABET-Abdelali/oracledba
- **Issues:** https://github.com/ELMRABET-Abdelali/oracledba/issues
- **Oracle Docs:** https://docs.oracle.com/en/database/oracle/oracle-database/19/

---

**💡 Conseil:** Ajoutez cette page en favoris pour accès rapide !

**Version:** 1.0.0  
**Date:** Février 2026
