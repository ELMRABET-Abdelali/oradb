# 🔄 Mapping Scripts Shell ↔️ CLI oradba

Ce document explique la correspondance entre les **scripts shell originaux** testés et approuvés sur Rocky Linux 8 et les **commandes CLI oradba**.

---

## 📂 Structure des Scripts

### Scripts Originaux (Testés Rocky Linux 8)

Les scripts sont localisés dans:
```
/usr/local/share/oracledba/scripts/
├── tp01-system-readiness.sh
├── tp02-installation-binaire.sh
├── tp03-creation-instance.sh
├── tp04-fichiers-critiques.sh
├── tp05-gestion-stockage.sh
├── tp06-securite-acces.sh
├── tp07-flashback.sh
├── tp08-rman.sh
├── tp09-dataguard.sh
├── tp10-tuning.sh
├── tp11-patching.sh
├── tp12-multitenant.sh
├── tp13-ai-foundations.sh
├── tp14-mobilite-concurrence.sh
└── tp15-asm-rac-concepts.sh
```

---

## 🔗 Correspondance Scripts → CLI

### TP01: Préparation Système

**Script Shell:**
```bash
sudo /usr/local/share/oracledba/scripts/tp01-system-readiness.sh
```

**Commandes CLI Équivalentes:**
```bash
# Installation système complète
sudo oradba install system

# Vérifier prérequis seulement
oradba install check-prereqs

# Rapport détaillé
oradba install system-report
```

**Ce que fait le script:**
- ✅ Vérification RAM/CPU/Disque
- ✅ Création SWAP 4GB
- ✅ Création groupes Oracle (7 groupes)
- ✅ Création utilisateur oracle
- ✅ Installation packages système (80+ packages)
- ✅ Configuration kernel parameters
- ✅ Configuration limites système
- ✅ Désactivation firewall/SELinux

---

### TP02: Installation Binaires

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp02-installation-binaire.sh
```

**Commandes CLI Équivalentes:**
```bash
# Télécharger binaires
oradba install download-binaries --output /tmp

# Installer binaires
sudo oradba install binaries --config my-config.yml

# Vérifier installation
oradba install verify-binaries
```

**Ce que fait le script:**
- ✅ Configuration `.bash_profile` avec variables Oracle
- ✅ Décompression LINUX.X64_193000_db_home.zip
- ✅ Lancement `runInstaller` mode silencieux
- ✅ Exécution scripts root (`root.sh`, `orainstRoot.sh`)

**Variables configurées:**
```bash
ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
ORACLE_BASE=/u01/app/oracle
ORACLE_SID=GDCPROD
PATH=$ORACLE_HOME/bin:$PATH
LD_LIBRARY_PATH=$ORACLE_HOME/lib
```

---

### TP03: Création Instance

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp03-creation-instance.sh
```

**Commandes CLI Équivalentes:**
```bash
# Créer base complète
oradba install database --config my-config.yml

# Créer avec nom personnalisé
oradba install database --name PRODDB

# Start/Stop/Status
oradba db start
oradba db stop
oradba db status
```

**Ce que fait le script:**
- ✅ Création base via DBCA silencieux
- ✅ Configuration Listener (1521)
- ✅ Configuration TNS (tnsnames.ora, listener.ora)
- ✅ Activation ARCHIVELOG
- ✅ Configuration autostart (`/etc/oratab`)
- ✅ Création PDB (`GDCPDB`)

---

### TP04: Multiplexage Fichiers Critiques

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp04-fichiers-critiques.sh
```

**Commandes CLI Équivalentes:**
```bash
# Analyser fichiers actuels
oradba db analyze-critical-files

# Multiplexer automatiquement
oradba db multiplex-critical --auto

# Control files seulement
oradba db multiplex-control-files

# Ajouter membres redo
oradba db add-redo-members

# Rotation log
oradba db switch-logfile
```

**Ce que fait le script:**
- ✅ Affichage control files via `v$controlfile`
- ✅ Modification SPFILE pour 3 control files
- ✅ Copie physique control files
- ✅ Ajout membres aux 3 redo log groups
- ✅ Test rotation (`ALTER SYSTEM SWITCH LOGFILE`)
- ✅ Vérification via `v$logfile`

**SQL Exécuté:**
```sql
ALTER SYSTEM SET control_files='...','...','...' SCOPE=SPFILE;
ALTER DATABASE ADD LOGFILE MEMBER '...' TO GROUP 1;
ALTER SYSTEM SWITCH LOGFILE;
```

---

### TP05: Gestion Stockage

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp05-gestion-stockage.sh
```

**Commandes CLI Équivalentes:**
```bash
# Lister tablespaces
oradba db list-tablespaces

# Créer tablespace
oradba db create-tablespace --name GDC_DATA --size 1G --autoextend

# Ajouter datafile
oradba db add-datafile --tablespace GDC_DATA --size 1G

# Analyser utilisation
oradba db analyze-storage

# Rapport stockage
oradba db storage-report
```

**Ce que fait le script:**
- ✅ Création tablespace `GDC_DATA` (100M, AUTOEXTEND)
- ✅ Création tablespace `GDC_INDEX` (50M)
- ✅ Test ajout datafile
- ✅ Test resize datafile
- ✅ Activation OMF (Oracle Managed Files)
- ✅ Création tablespace avec OMF

**SQL Exécuté:**
```sql
CREATE TABLESPACE GDC_DATA DATAFILE '...' SIZE 100M AUTOEXTEND ON MAXSIZE 500M;
ALTER DATABASE DATAFILE '...' RESIZE 200M;
ALTER TABLESPACE GDC_DATA ADD DATAFILE '...' SIZE 100M;
```

---

### TP06: Sécurité et Accès

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp06-securite-acces.sh
```

**Commandes CLI Équivalentes:**
```bash
# Créer utilisateur
oradba security create-user --name GDC_ADMIN --password MyPass123

# Créer rôle
oradba security create-role --name GDC_DEVELOPER

# Assigner rôle
oradba security grant-role --role GDC_DEVELOPER --user GDC_ADMIN

# Créer profile
oradba security create-profile --name SECURE_PROFILE

# Lister utilisateurs
oradba security list-users
```

**Ce que fait le script:**
- ✅ Création utilisateur `GDC_ADMIN`
- ✅ Assignation tablespace `GDC_DATA` par défaut
- ✅ Création rôle `GDC_DEVELOPER`
- ✅ Assignation privilèges (CREATE TABLE, VIEW, PROCEDURE...)
- ✅ Création profile sécurité (password policy)
- ✅ Test connexion utilisateur

**SQL Exécuté:**
```sql
CREATE USER GDC_ADMIN IDENTIFIED BY "..." DEFAULT TABLESPACE GDC_DATA QUOTA UNLIMITED ON GDC_DATA;
CREATE ROLE GDC_DEVELOPER;
GRANT CREATE SESSION, CREATE TABLE TO GDC_DEVELOPER;
GRANT GDC_DEVELOPER TO GDC_ADMIN;
```

---

### TP07: Flashback

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp07-flashback.sh
```

**Commandes CLI Équivalentes:**
```bash
# Activer Flashback Database
oradba flashback enable --retention-hours 48

# Récupérer table DROP
oradba flashback drop-restore --table CLIENTS

# Query passé
oradba flashback query --table CLIENTS --minutes-ago 5

# Restaurer table
oradba flashback table --table CLIENTS --timestamp "..."

# Status
oradba flashback status
```

**Ce que fait le script:**
- ✅ Activation Flashback Database (MOUNT mode)
- ✅ Configuration retention (48h)
- ✅ Test DROP table + récupération Recycle Bin
- ✅ Test Flashback Query (AS OF TIMESTAMP)
- ✅ Test Flashback Table (ROW MOVEMENT)
- ✅ Vérification via `v$database`

**SQL Exécuté:**
```sql
ALTER DATABASE FLASHBACK ON;
DROP TABLE test_table;
SELECT * FROM recyclebin;
FLASHBACK TABLE test_table TO BEFORE DROP;
SELECT * FROM table AS OF TIMESTAMP ...;
FLASHBACK TABLE table TO TIMESTAMP ...;
```

---

### TP08: RMAN Backup

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp08-rman.sh
```

**Commandes CLI Équivalentes:**
```bash
# Configure RMAN
oradba rman setup --retention-days 7 --compression

# Backup FULL
oradba rman backup --type full --tag DAILY_FULL

# Backup incrémental
oradba rman backup --type incremental

# Backup archives
oradba rman backup --type archive --delete-input

# Lister backups
oradba rman list-backups

# Restaurer
oradba rman restore --point-in-time "..."
```

**Ce que fait le script:**
- ✅ Configuration RMAN (retention, compression, parallelism)
- ✅ Backup niveau 0 (FULL avec ARCHIVELOG)
- ✅ Simulation activité base
- ✅ Backup niveau 1 (INCREMENTAL)
- ✅ Backup archivelogs
- ✅ Validation backups (`VALIDATE BACKUPSET`)
- ✅ Simulation corruption + restore

**RMAN Exécuté:**
```rman
CONFIGURE RETENTION POLICY TO REDUNDANCY 2;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';
BACKUP INCREMENTAL LEVEL 0 DATABASE PLUS ARCHIVELOG;
BACKUP INCREMENTAL LEVEL 1 DATABASE;
LIST BACKUP SUMMARY;
RESTORE DATABASE;
RECOVER DATABASE;
```

---

### TP09: Data Guard

**Script Shell:**
```bash
# Sur PRIMARY:
su - oracle
/usr/local/share/oracledba/scripts/tp09-dataguard.sh

# Sur STANDBY (après PRIMARY):
su - oracle
/usr/local/share/oracledba/scripts/tp09-dataguard-standby.sh
```

**Commandes CLI Équivalentes:**
```bash
# PRIMARY: Setup Data Guard
oradba dataguard setup-primary --standby-host 167.172.176.22

# PRIMARY: Créer Standby
oradba dataguard create-standby --standby-host 167.172.176.22

# Démarrer APPLY
oradba dataguard start-apply --standby-host 167.172.176.22

# Status
oradba dataguard status

# Switchover
oradba dataguard switchover --to-standby
```

**Ce que fait le script:**
- ✅ Activation `FORCE LOGGING` sur PRIMARY
- ✅ Création Standby Redo Logs (4 groupes)
- ✅ Configuration paramètres Data Guard (`LOG_ARCHIVE_DEST_2`, etc.)
- ✅ Copie password file vers STANDBY
- ✅ Duplication via `RMAN DUPLICATE FROM ACTIVE`
- ✅ Démarrage MRP (Managed Recovery Process)
- ✅ Vérification synchronisation via `v$archived_log`

**SQL Exécuté:**
```sql
-- PRIMARY
ALTER DATABASE FORCE LOGGING;
ALTER DATABASE ADD STANDBY LOGFILE GROUP 11 SIZE 200M;
ALTER SYSTEM SET LOG_ARCHIVE_CONFIG='DG_CONFIG=(GDCPROD,GDCSTBY)';
ALTER SYSTEM SET LOG_ARCHIVE_DEST_2='SERVICE=GDCSTBY...';

-- STANDBY
STARTUP NOMOUNT;
-- (RMAN DUPLICATE)
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT;
```

---

### TP10: Performance Tuning

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp10-tuning.sh
```

**Commandes CLI Équivalentes:**
```bash
# Health check
oradba tuning health-check

# Rapport AWR
oradba tuning awr-report --hours 1

# Top SQL
oradba tuning top-sql --limit 10

# SQL Tuning Advisor
oradba tuning sql-advisor --sql-id 8fzx3m2kp9qrt

# Memory advisor
oradba tuning memory-advisor

# Dashboard temps réel
oradba tuning dashboard
```

**Ce que fait le script:**
- ✅ Lecture Alert Log (dernières 50 lignes)
- ✅ Vérification utilisation tablespaces
- ✅ Calcul Buffer Cache Hit Ratio
- ✅ Calcul Library Cache Hit Ratio
- ✅ Génération rapport AWR (dernier snapshot)
- ✅ Analyse Top SQL par CPU
- ✅ Exécution SQL Tuning Advisor

**SQL Exécuté:**
```sql
SELECT tablespace_name, used_percent FROM dba_tablespace_usage_metrics;
SELECT (1 - SUM(reloads)/SUM(pins)) FROM v$librarycache;
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT();
SELECT sql_id, elapsed_time FROM v$sql ORDER BY elapsed_time DESC;
```

---

### TP11: Patching

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp11-patching.sh
```

**Commandes CLI Équivalentes:**
```bash
# Lister patches installés
oradba patch list-installed

# Analyser patch
oradba patch analyze --patch-file /tmp/p35648110.zip

# Appliquer patch
oradba patch apply --patch-file /tmp/p35648110.zip

# Rollback
oradba patch rollback --patch-id 35648110

# Vérifier
oradba patch verify
```

**Ce que fait le script:**
- ✅ Vérification version OPatch
- ✅ Liste patches via `opatch lsinventory`
- ✅ Liste patches SQL via `dba_registry_sqlpatch`
- ✅ Documentation workflow patching
- ✅ Vérification composants `dba_registry`

**Commandes Exécutées:**
```bash
$ORACLE_HOME/OPatch/opatch version
$ORACLE_HOME/OPatch/opatch lsinventory
$ORACLE_HOME/OPatch/opatch prereq CheckConflictAgainstOHWithDetail
$ORACLE_HOME/OPatch/opatch apply
$ORACLE_HOME/OPatch/datapatch -verbose
```

---

### TP12: Multi-tenant

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp12-multitenant.sh
```

**Commandes CLI Équivalentes:**
```bash
# Lister PDBs
oradba pdb list

# Créer PDB
oradba pdb create --name PDB_FINANCE --admin-user finadm

# Cloner PDB
oradba pdb clone --source PDB1 --target PDB1_DEV

# Ouvrir/Fermer
oradba pdb open --name PDB_FINANCE
oradba pdb close --name PDB_FINANCE

# Drop PDB
oradba pdb drop --name PDB_OLD --including-datafiles
```

**Ce que fait le script:**
- ✅ Vérification mode CDB (`SELECT cdb FROM v$database`)
- ✅ Liste PDBs via `SHOW PDBS`
- ✅ Création PDB (`CREATE PLUGGABLE DATABASE`)
- ✅ Ouverture PDB
- ✅ Sauvegarde état (`SAVE STATE`)
- ✅ Test connexion PDB
- ✅ Clone PDB via `FROM` clause

**SQL Exécuté:**
```sql
SHOW PDBS;
CREATE PLUGGABLE DATABASE PDB_PHOENIX ADMIN USER phxadmin IDENTIFIED BY ...;
ALTER PLUGGABLE DATABASE PDB_PHOENIX OPEN;
ALTER PLUGGABLE DATABASE PDB_PHOENIX SAVE STATE;
ALTER SESSION SET CONTAINER=PDB_PHOENIX;
```

---

### TP13: AI Foundations

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp13-ai-foundations.sh
```

**Commandes CLI Équivalentes:**
```bash
# Vérifier capacités ML
oradba ai check-capabilities

# Activer Auto-Indexing
oradba ai enable-auto-index --mode report-only

# Lister recommandations
oradba ai list-auto-index-recommendations

# Rapport AI/ML
oradba ai report
```

**Ce que fait le script:**
- ✅ Vérification composants JAVA/OML (`dba_registry`)
- ✅ Configuration Auto-Indexing
- ✅ Affichage config auto-index (`dba_auto_index_config`)
- ✅ Vérification Automatic SQL Tuning (`dba_autotask_client`)
- ✅ Documentation OML

**SQL Exécuté:**
```sql
SELECT comp_name, status FROM dba_registry WHERE comp_id = 'JAVAVM';
EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_MODE', 'REPORT ONLY');
SELECT parameter_name, parameter_value FROM dba_auto_index_config;
SELECT client_name, status FROM dba_autotask_client;
```

---

### TP14: Mobilité et Concurrence

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp14-mobilite-concurrence.sh
```

**Commandes CLI Équivalentes:**
```bash
# Export Data Pump
oradba datapump export --schema GDC_ADMIN --file export.dmp

# Import
oradba datapump import --file export.dmp --schema GDC_ADMIN

# Analyser locks
oradba db analyze-locks

# Tuer session
oradba db kill-session --sid 125 --serial 38456

# Activer audit
oradba security enable-audit --actions "CREATE SESSION"
```

**Ce que fait le script:**
- ✅ Création directory Oracle (`CREATE DIRECTORY`)
- ✅ Export schema avec `expdp`
- ✅ Simulation lock (deux sessions concurrentes)
- ✅ Détection lock via `v$lock` + `v$session`
- ✅ Résolution lock (`ALTER SYSTEM KILL SESSION`)
- ✅ Activation audit (`AUDIT SESSION`)
- ✅ Consultation `dba_audit_trail`

**Commandes Exécutées:**
```sql
CREATE DIRECTORY BACKUP_DIR AS '/u01/backup';
-- Shell: expdp system/... DIRECTORY=BACKUP_DIR SCHEMAS=GDC_ADMIN
SELECT blocking_session FROM v$session WHERE blocking_session IS NOT NULL;
ALTER SYSTEM KILL SESSION 'sid,serial#';
AUDIT SESSION;
```

---

### TP15: ASM et RAC Concepts

**Script Shell:**
```bash
su - oracle
/usr/local/share/oracledba/scripts/tp15-asm-rac-concepts.sh
```

**Commandes CLI Équivalentes:**
```bash
# Vérifier cluster
oradba rac check-cluster

# Préparer Grid
oradba rac prepare-grid --nodes node1,node2

# Architecture ASM
oradba asm show-architecture

# Lister Disk Groups
oradba asm list-diskgroups

# Status RAC
oradba rac cluster-status
```

**Ce que fait le script:**
- ✅ Vérification configuration RAC (`/etc/oracle/olr.loc`)
- ✅ Affichage architecture ASM (diagrammes ASCII)
- ✅ Affichage architecture RAC
- ✅ Comparaison ASM vs File System
- ✅ Comparaison RAC vs Data Guard
- ✅ Documentation Grid Infrastructure
- ✅ Workflow installation Grid+RAC

**Concepts Couverts:**
```
ASM Architecture:
- Disk Groups (DATA, FRA, GRID)
- Redundancy (External, Normal, High)
- Re-balance automatique

RAC Architecture:
- Multiple instances → 1 database
- Cache Fusion (interconnect)
- Voting disks, OCR
- Scan Listeners
```

---

## 🚀 Utilisation Pratique

### Approche 1: Utiliser Scripts Directs

Si vous préférez comprendre **en détail** ce qui se passe:

```bash
# Exécuter scripts dans l'ordre
sudo /usr/local/share/oracledba/scripts/tp01-system-readiness.sh
su - oracle
./tp02-installation-binaire.sh
./tp03-creation-instance.sh
# etc...
```

**Avantages:**
- ✅ Voir chaque commande exécutée
- ✅ Comprendre le workflow
- ✅ Personnaliser facilement

**Inconvénients:**
- ❌ Répétitif pour plusieurs serveurs
- ❌ Pas de configuration centralisée
- ❌ Gestion manuelle d'erreurs

---

### Approche 2: Utiliser CLI oradba

Pour **automatisation** et **production**:

```bash
# Configuration YAML unique
vi ~/my-config.yml

# Installation complète en une commande
sudo oradba install full --config ~/my-config.yml

# Gestion quotidienne
oradba db status
oradba rman backup --type full
oradba tuning health-check
```

**Avantages:**
- ✅ Configuration centralisée (YAML)
- ✅ Idempotent (relancer sans risque)
- ✅ Logs structurés
- ✅ Gestion erreurs intégrée
- ✅ Adapté CI/CD

**Inconvénients:**
- ❌ Abstraction du détail
- ❌ Nécessite apprentissage CLI

---

### Approche 3: Hybride (Recommandée)

**Formation:** Utiliser scripts directs pour comprendre

```bash
# Phase apprentissage (TP01-TP15)
./tp01-system-readiness.sh  # Comprendre chaque étape
./tp02-installation-binaire.sh
...
```

**Production:** Utiliser CLI pour automatisation

```bash
# Déploiement serveurs production
ansible-playbook -i inventory deploy-oracle.yml
# → appelle: oradba install full --config production.yml

# Gestion quotidienne
crontab:
  0 2 * * * /usr/local/bin/oradba rman backup --type full
```

---

## 📊 Tableau Récapitulatif

| TP | Script Shell | Commande CLI | Fonctionnalité |
|---|---|---|---|
| **01** | `tp01-system-readiness.sh` | `oradba install system` | Préparation OS, users, kernel |
| **02** | `tp02-installation-binaire.sh` | `oradba install binaries` | Installation binaires Oracle |
| **03** | `tp03-creation-instance.sh` | `oradba install database` | Création base DBCA |
| **04** | `tp04-fichiers-critiques.sh` | `oradba db multiplex-critical` | Multiplexage control/redo |
| **05** | `tp05-gestion-stockage.sh` | `oradba db create-tablespace` | Gestion tablespaces |
| **06** | `tp06-securite-acces.sh` | `oradba security create-user` | Users, rôles, profiles |
| **07** | `tp07-flashback.sh` | `oradba flashback enable` | Flashback Database |
| **08** | `tp08-rman.sh` | `oradba rman backup` | Backups RMAN |
| **09** | `tp09-dataguard.sh` | `oradba dataguard setup-primary` | Data Guard HA |
| **10** | `tp10-tuning.sh` | `oradba tuning awr-report` | Performance tuning |
| **11** | `tp11-patching.sh` | `oradba patch apply` | Patching Oracle |
| **12** | `tp12-multitenant.sh` | `oradba pdb create` | CDB/PDB management |
| **13** | `tp13-ai-foundations.sh` | `oradba ai enable-auto-index` | AI/ML features |
| **14** | `tp14-mobilite-concurrence.sh` | `oradba datapump export` | Data Pump, locks |
| **15** | `tp15-asm-rac-concepts.sh` | `oradba rac check-cluster` | ASM/RAC concepts |

---

## 🎓 Scripts = Source de Vérité

Les **scripts shell sont la référence testée et validée** sur Rocky Linux 8.

Le **CLI oradba** est une **abstraction** qui:
1. ✅ Appelle les mêmes scripts sous le capot
2. ✅ Ajoute gestion configuration YAML
3. ✅ Ajoute gestion d'erreurs robuste
4. ✅ Ajoute logs structurés
5. ✅ Permet automatisation (Ansible, Terraform, etc.)

**En cas de doute:** Consultez toujours le script shell source pour comprendre exactement ce qui est exécuté !

---

## 📚 Ressources

- **Scripts originaux:** `/usr/local/share/oracledba/scripts/`
- **Guide d'utilisation:** `GUIDE_UTILISATION.md`
- **Configuration exemples:** `examples/production-config.yml`
- **Aide CLI:** `oradba --help`

---

**Auteur:** DBA Formation Team  
**Version:** 1.0.0  
**Date:** Février 2026
