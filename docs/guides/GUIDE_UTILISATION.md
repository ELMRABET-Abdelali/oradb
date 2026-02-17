# 📘 Guide Complet d'Utilisation - OracleDBA

**Package complet pour l'administration Oracle Database 19c sur Rocky Linux 8/9**

Version: 1.0.0  
Date: Février 2026  
Testé sur: Rocky Linux 8.x / RHEL 8.x  
Oracle: 19c Enterprise Edition

---

## 📑 Table des Matières

- [🚀 Installation du Package](#-installation-du-package)
- [⚙️ Configuration Initiale](#️-configuration-initiale)
- [📦 Installation Oracle Complète](#-installation-oracle-complète)
- [💡 Exemples par Chapitre (TP01-TP15)](#-exemples-par-chapitre)
  - [TP01: Préparation Système](#tp01-préparation-système)
  - [TP02: Installation Binaires](#tp02-installation-binaires)
  - [TP03: Création Instance](#tp03-création-instance)
  - [TP04: Multiplexage Fichiers Critiques](#tp04-multiplexage-fichiers-critiques)
  - [TP05: Gestion Stockage](#tp05-gestion-stockage)
  - [TP06: Sécurité et Accès](#tp06-sécurité-et-accès)
  - [TP07: Flashback](#tp07-flashback)
  - [TP08: RMAN Backup](#tp08-rman-backup)
  - [TP09: Data Guard](#tp09-data-guard)
  - [TP10: Performance Tuning](#tp10-performance-tuning)
  - [TP11: Patching](#tp11-patching)
  - [TP12: Multi-tenant](#tp12-multi-tenant)
  - [TP13: AI Foundations](#tp13-ai-foundations)
  - [TP14: Mobilité et Concurrence](#tp14-mobilité-et-concurrence)
  - [TP15: ASM et RAC](#tp15-asm-et-rac)
- [🔧 Cas d'Usage Avancés](#-cas-dusage-avancés)
- [❓ Dépannage](#-dépannage)

---

## 🚀 Installation du Package

### Méthode 1: Via GitHub (Recommandée)

```bash
# 1. Cloner le repository
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba

# 2. Installation avec pip (mode développement)
pip install -e .

# 3. Vérifier l'installation
oradba --version
oradba --help
```

### Méthode 2: Via PyPI (après publication)

```bash
# Installation depuis PyPI
pip install oracledba

# Vérifier
oradba --version
```

### Méthode 3: Installation Script Automatique

```bash
# Télécharger et installer automatiquement
curl -o install.sh https://raw.githubusercontent.com/ELMRABET-Abdelali/oracledba/main/install.sh
chmod +x install.sh
sudo ./install.sh

# Le script installe:
# - Python 3.8+
# - pip et virtualenv
# - oracledba package
# - Tous les prérequis
```

### Prérequis Système

**Rocky Linux 8/9 ou RHEL 8/9:**
```bash
# Vérifier la version
cat /etc/redhat-release

# Installer Python 3.8+ si nécessaire
sudo dnf install -y python38 python38-pip

# Vérifier Python
python3 --version  # Doit afficher >= 3.8
```

**Vérifier les ressources:**
```bash
# RAM minimum: 4 GB
free -h

# Espace disque: 50 GB sur /u01
df -h /

# CPU: 2 cores minimum
nproc
```

---

## ⚙️ Configuration Initiale

### Créer votre fichier de configuration

```bash
# 1. Copier le template par défaut
mkdir -p ~/oracledba-config
cp /usr/local/lib/python3.8/site-packages/oracledba/configs/default-config.yml ~/oracledba-config/my-config.yml

# OU si installation en mode développement
cp configs/default-config.yml ~/oracledba-config/my-config.yml

# 2. Éditer selon votre environnement
vi ~/oracledba-config/my-config.yml
```

### Configuration Minimale (my-config.yml)

```yaml
# Configuration pour serveur single instance
system:
  os: "Rocky Linux 8"
  min_ram_gb: 4
  min_disk_gb: 50
  hostname: "oracledb01"

oracle:
  version: "19.3.0.0.0"
  oracle_base: "/u01/app/oracle"
  oracle_home: "/u01/app/oracle/product/19.3.0/dbhome_1"

database:
  db_name: "ORCL"
  sid: "ORCL"
  sys_password: "ChangeMe123"  # CHANGEZ-MOI!
  system_password: "ChangeMe123"  # CHANGEZ-MOI!
  enable_archivelog: true
  enable_flashback: true

backup:
  rman_retention_days: 7
  backup_location: "/u01/app/oracle/backup"
  fra_size_gb: 20
```

### Configuration Production (Exemple)

Voir: `examples/production-config.yml` pour configuration complète avec:
- Memory tuning
- Backup avancé
- Data Guard
- Security hardening

### Configuration RAC (Exemple)

Voir: `examples/rac-config.yml` pour configuration cluster avec:
- Multiple nodes
- Shared storage (NFS/ASM)
- Interconnect privé
- Scan listeners

---

## 📦 Installation Oracle Complète

### Option 1: Installation Automatique Complète (--all)

```bash
# Installation tout-en-un avec configuration par défaut
sudo oradba install full --config ~/oracledba-config/my-config.yml

# Ce qui est exécuté:
# 1. Préparation système (TP01: users, groups, kernel params, swap)
# 2. Installation binaires Oracle (TP02: unzip, runInstaller)
# 3. Création base de données (TP03: DBCA, listener)
# 4. Configuration initiale (multiplexage, archivelog)
```

### Option 2: Installation Pas-à-Pas

```bash
# Étape 1: Préparer le système seulement
sudo oradba install system --config ~/oracledba-config/my-config.yml

# Étape 2: Installer les binaires
sudo oradba install binaries --config ~/oracledba-config/my-config.yml

# Étape 3: Créer la base de données
sudo oradba install database --config ~/oracledba-config/my-config.yml
```

### Option 3: Installation Sélective

```bash
# Sauter la préparation système (si déjà faite)
sudo oradba install full --config ~/oracledba-config/my-config.yml --skip-system

# Sauter l'installation binaires (si déjà installés)
sudo oradba install full --config ~/oracledba-config/my-config.yml --skip-binaries

# Installation VM (NFS client ready)
sudo oradba install vm-init --config ~/oracledba-config/my-config.yml --nfs-server 192.168.1.100
```

### Vérification Post-Installation

```bash
# Vérifier le statut de la base
oradba db status

# Sortie attendue:
# ✓ Instance: RUNNING
# ✓ Database: OPEN
# ✓ Listener: ONLINE
# ✓ Archive Mode: ENABLED
# ✓ Flashback: ON
```

---

## 💡 Exemples par Chapitre

### TP01: Préparation Système

**Objectif:** Configurer Rocky Linux 8 pour Oracle (users, groups, kernel params, swap)

#### Utilisation Commandes CLI

```bash
# 1. Préparer le système complet (exécuter en root)
sudo oradba install system

# 2. Vérifier les prérequis (sans modification)
oradba install check-prereqs

# 3. Afficher le rapport de préparation
oradba install system-report
```

#### Script Shell Direct (pour comprendre ce qui se passe)

```bash
# Exécuter le script TP01 original
sudo su - root
cd /usr/local/share/oracledba/scripts
./tp01-system-readiness.sh

# Le script fait:
# - Vérification RAM/CPU/Disque
# - Création SWAP 4GB
# - Création groupes Oracle (oinstall, dba, oper, etc.)
# - Création utilisateur oracle
# - Installation packages système
# - Configuration kernel parameters (/etc/sysctl.conf)
# - Configuration limites (/etc/security/limits.conf)
# - Désactivation firewall/SELinux
```

#### Vérification

```bash
# Vérifier utilisateur oracle créé
id oracle

# Sortie attendue:
# uid=54321(oracle) gid=54321(oinstall) groups=54321(oinstall),54322(dba),54323(oper),...

# Vérifier kernel params
sysctl -a | grep -E 'shmmax|shmall|shmmni'

# Vérifier SWAP
free -h | grep Swap
# Swap: 4.0G
```

#### Configuration YAML pour TP01

```yaml
# Personnaliser la préparation système
system:
  swap_size_gb: 8  # 8GB au lieu de 4GB
  disable_firewall: true
  disable_selinux: true

oracle_users:
  - name: "oracle"
    password: "MySecurePassword123"  # Changer mot de passe
```

---

### TP02: Installation Binaires

**Objectif:** Déployer les binaires Oracle 19c et configurer ORACLE_HOME

#### Utilisation Commandes CLI

```bash
# 1. Télécharger binaires Oracle (Google Drive)
oradba install download-binaries --output /tmp

# 2. Transférer binaires sur serveur (si depuis PC local)
scp LINUX.X64_193000_db_home.zip oracle@192.168.1.10:/u01/app/oracle/product/19.3.0/dbhome_1/

# 3. Installer binaires via CLI
sudo oradba install binaries --config ~/oracledba-config/my-config.yml

# 4. Vérifier installation
oradba install verify-binaries
```

#### Script Shell Direct

```bash
# Exécuter TP02 (en tant qu'oracle)
su - oracle
cd /usr/local/share/oracledba/scripts
./tp02-installation-binaire.sh

# Le script fait:
# - Configuration .bash_profile avec variables Oracle
# - Décompression ZIP dans $ORACLE_HOME
# - Lancement runInstaller en mode silencieux
# - Exécution scripts root (root.sh)
```

#### Configuration Avancée

```yaml
oracle:
  version: "19.3.0.0.0"
  edition: "EE"  # Enterprise Edition
  oracle_home: "/u01/app/oracle/product/19.3.0/dbhome_1"
  
  # Customiser l'installation
  install_options:
    install_type: "INSTALL_DB_SWONLY"  # Software Only
    decline_security_updates: true
    
  # Groupes de sécurité
  security_groups:
    dba_group: "dba"
    oper_group: "oper"
    backupdba_group: "backupdba"
    dgdba_group: "dgdba"
    kmdba_group: "kmdba"
```

#### Vérification

```bash
# Se connecter en oracle
su - oracle

# Vérifier variables d'environnement
echo $ORACLE_HOME
# /u01/app/oracle/product/19.3.0/dbhome_1

echo $ORACLE_SID
# ORCL

# Vérifier binaires installés
ls -lh $ORACLE_HOME/bin/sqlplus
$ORACLE_HOME/bin/sqlplus -version
```

---

### TP03: Création Instance

**Objectif:** Créer la base de données GDCPROD avec DBCA et démarrer le Listener

#### Utilisation Commandes CLI

```bash
# 1. Créer base avec configuration par défaut
oradba install database --config ~/oracledba-config/my-config.yml

# 2. Créer base avec nom personnalisé
oradba install database --name PRODDB --config ~/oracledba-config/my-config.yml

# 3. Créer base CDB avec 2 PDBs
oradba install database --cdb --pdbs PDB1,PDB2 --config ~/oracledba-config/my-config.yml

# 4. Démarrer/arrêter base
oradba db start
oradba db stop
oradba db status
```

#### Script Shell Direct

```bash
# Exécuter TP03 (en tant qu'oracle)
su - oracle
cd /usr/local/share/oracledba/scripts
./tp03-creation-instance.sh

# Le script fait:
# - Création base via DBCA en mode silencieux
# - Configuration Listener (listener.ora, tnsnames.ora)
# - Activation mode ARCHIVELOG
# - Configuration autostart (/etc/oratab)
```

#### Configuration Database

```yaml
database:
  db_name: "PRODDB"
  sid: "PRODDB"
  db_unique_name: "PRODDB"
  
  # CDB/PDB
  cdb: true
  pdbs:
    - name: "PDB_SALES"
      admin_user: "salesadm"
      admin_password: "Sales123"
    - name: "PDB_HR"
      admin_user: "hradm"
      admin_password: "Hr123"
  
  # Mémoire
  sga_target_mb: 4096  # 4GB SGA
  pga_aggregate_target_mb: 2048  # 2GB PGA
  
  # Stockage
  datafile_dest: "/u01/app/oracle/oradata"
  recovery_dest: "/u01/app/oracle/fast_recovery_area"
  recovery_size_gb: 50
  
  # Options
  enable_archivelog: true
  enable_force_logging: true
  enable_flashback: true
```

#### Vérification

```bash
# Connexion SQL*Plus
sqlplus / as sysdba

SQL> SELECT instance_name, status FROM v$instance;
-- INSTANCE_NAME: PRODDB
-- STATUS: OPEN

SQL> SELECT name, log_mode, flashback_on FROM v$database;
-- LOG_MODE: ARCHIVELOG
-- FLASHBACK_ON: YES

SQL> SHOW PDBS;
-- PDB_SALES: READ WRITE
-- PDB_HR: READ WRITE

# Vérifier Listener
lsnrctl status
-- Status: READY
-- Services: PRODDB, PDB_SALES, PDB_HR
```

---

### TP04: Multiplexage Fichiers Critiques

**Objectif:** Sécuriser Control Files et Redo Logs par multiplexage

#### Utilisation Commandes CLI

```bash
# 1. Analyser état actuel des fichiers critiques
oradba db analyze-critical-files

# 2. Multiplexer automatiquement (control files + redo logs)
oradba db multiplex-critical --auto

# 3. Multiplexer contrôle files seulement
oradba db multiplex-control-files --locations /u01/oradata,/u02/oradata

# 4. Ajouter membres Redo Log
oradba db add-redo-members --location /u02/oradata

# 5. Forcer rotation log (switch)
oradba db switch-logfile
```

#### Script Shell Direct

```bash
# Exécuter TP04
su - oracle
cd /usr/local/share/oracledba/scripts
./tp04-fichiers-critiques.sh

# Le script fait:
# - Affichage control files actuels (v$controlfile)
# - Modification SPFILE avec 2+ control files
# - Arrêt base + copie physique + démarrage
# - Ajout membres aux redo log groups
# - Test rotation (ALTER SYSTEM SWITCH LOGFILE)
```

#### SQL Manuel (Pour Comprendre)

```sql
-- Connexion
sqlplus / as sysdba

-- 1. Vérifier control files actuels
SELECT name FROM v$controlfile;

-- 2. Modifier SPFILE pour ajouter control file
ALTER SYSTEM SET control_files=
  '/u01/app/oracle/oradata/PRODDB/control01.ctl',
  '/u01/app/oracle/oradata/PRODDB/control02.ctl',
  '/u02/app/oracle/oradata/PRODDB/control03.ctl'
  SCOPE=SPFILE;

-- 3. Redémarrer pour appliquer
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;

-- 4. Copier fichier au niveau OS (en tant que oracle)
-- cp control01.ctl control02.ctl
-- cp control01.ctl /u02/.../control03.ctl

ALTER DATABASE OPEN;

-- 5. Ajouter membres redo logs
ALTER DATABASE ADD LOGFILE MEMBER 
  '/u02/app/oracle/oradata/PRODDB/redo01b.log' TO GROUP 1;
  
ALTER DATABASE ADD LOGFILE MEMBER 
  '/u02/app/oracle/oradata/PRODDB/redo02b.log' TO GROUP 2;

-- 6. Vérifier
SELECT group#, member FROM v$logfile ORDER BY group#;

-- 7. Forcer rotation
ALTER SYSTEM SWITCH LOGFILE;
```

#### Vérification

```bash
# Vérifier multiplexage réussi
oradba db show-critical-files

# Affichage:
# Control Files: 3 copies
#   - /u01/.../control01.ctl
#   - /u01/.../control02.ctl
#   - /u02/.../control03.ctl
#
# Redo Log Groups:
#   Group 1: 2 members
#     - /u01/.../redo01a.log
#     - /u02/.../redo01b.log
```

---

### TP05: Gestion Stockage

**Objectif:** Créer et gérer les Tablespaces (GDC_DATA, GDC_INDEX)

#### Utilisation Commandes CLI

```bash
# 1. Lister tablespaces existants
oradba db list-tablespaces

# 2. Créer tablespace applicatif
oradba db create-tablespace --name GDC_DATA --size 1G --autoextend --maxsize 10G

# 3. Créer tablespace pour index
oradba db create-tablespace --name GDC_INDEX --size 500M --autoextend

# 4. Ajouter datafile à tablespace existant
oradba db add-datafile --tablespace GDC_DATA --size 1G

# 5. Redimensionner datafile
oradba db resize-datafile --file /u01/.../gdc_data01.dbf --size 2G

# 6. Analyser l'utilisation
oradba db analyze-storage
```

#### Script Shell Direct

```bash
# Exécuter TP05
su - oracle
cd /usr/local/share/oracledba/scripts
./tp05-gestion-stockage.sh

# Le script fait:
# - Création tablespace GDC_DATA (100M, autoextend)
# - Création tablespace GDC_INDEX (50M)
# - Test ajout datafile
# - Activation OMF (Oracle Managed Files)
# - Création tablespace test avec OMF
```

#### SQL Manuel

```sql
-- Connexion à PDB
sqlplus / as sysdba
ALTER SESSION SET CONTAINER=PDB1;

-- 1. Lister tablespaces
SELECT tablespace_name, status, contents 
FROM dba_tablespaces;

-- 2. Créer tablespace DATA
CREATE TABLESPACE GDC_DATA
DATAFILE '/u01/app/oracle/oradata/PDB1/gdc_data01.dbf'
SIZE 1G
AUTOEXTEND ON
NEXT 100M
MAXSIZE 10G
EXTENT MANAGEMENT LOCAL
SEGMENT SPACE MANAGEMENT AUTO;

-- 3. Créer tablespace INDEX
CREATE TABLESPACE GDC_INDEX
DATAFILE '/u01/app/oracle/oradata/PDB1/gdc_index01.dbf'
SIZE 500M
AUTOEXTEND ON;

-- 4. Ajouter datafile
ALTER TABLESPACE GDC_DATA
ADD DATAFILE '/u01/app/oracle/oradata/PDB1/gdc_data02.dbf'
SIZE 1G;

-- 5. Redimensionner
ALTER DATABASE DATAFILE '/u01/.../gdc_data01.dbf' RESIZE 2G;

-- 6. Analyser utilisation
SELECT 
  tablespace_name,
  ROUND(SUM(bytes)/1024/1024, 2) AS size_mb,
  ROUND(SUM(maxbytes)/1024/1024, 2) AS maxsize_mb
FROM dba_data_files
GROUP BY tablespace_name;
```

#### Vérification

```bash
# Rapport stockage
oradba db storage-report

# Affichage:
# Tablespace          Size(MB)   Used(MB)   Free(MB)   %Used
# SYSTEM              800        750        50         93.75
# SYSAUX              600        500        100        83.33
# USERS               100        50         50         50.00
# GDC_DATA            1024       150        874        14.65
# GDC_INDEX           512        80         432        15.63
```

---

### TP06: Sécurité et Accès

**Objectif:** Créer utilisateurs, rôles, profiles de sécurité

#### Utilisation Commandes CLI

```bash
# 1. Créer utilisateur applicatif
oradba security create-user --name GDC_ADMIN --password MyPass123 \
  --default-tablespace GDC_DATA --quota 5G

# 2. Créer rôle métier
oradba security create-role --name GDC_DEVELOPER \
  --privileges "CREATE TABLE,CREATE VIEW,CREATE PROCEDURE"

# 3. Assigner rôle à utilisateur
oradba security grant-role --role GDC_DEVELOPER --user GDC_ADMIN

# 4. Créer profile de sécurité
oradba security create-profile --name SECURE_PROFILE \
  --failed-login-attempts 5 --password-life-days 90

# 5. Appliquer profile
oradba security assign-profile --profile SECURE_PROFILE --user GDC_ADMIN

# 6. Lister utilisateurs
oradba security list-users
```

#### Script Shell Direct

```bash
# Exécuter TP06
su - oracle
cd /usr/local/share/oracledba/scripts
./tp06-securite-acces.sh

# Le script fait:
# - Création utilisateur GDC_ADMIN
# - Création rôle GDC_DEVELOPER avec privilèges
# - Affectation rôle à utilisateur
# - Création profile de sécurité (password policy)
# - Test connexion
```

#### SQL Manuel

```sql
-- Connexion à PDB
sqlplus / as sysdba
ALTER SESSION SET CONTAINER=PDB1;

-- 1. Créer utilisateur
CREATE USER GDC_ADMIN 
IDENTIFIED BY "SecurePass2026#"
DEFAULT TABLESPACE GDC_DATA
TEMPORARY TABLESPACE TEMP
QUOTA 5G ON GDC_DATA
QUOTA 1G ON GDC_INDEX;

-- 2. Créer rôle
CREATE ROLE GDC_DEVELOPER;

-- 3. Assigner privilèges au rôle
GRANT CREATE SESSION TO GDC_DEVELOPER;
GRANT CREATE TABLE TO GDC_DEVELOPER;
GRANT CREATE VIEW TO GDC_DEVELOPER;
GRANT CREATE PROCEDURE TO GDC_DEVELOPER;
GRANT CREATE SEQUENCE TO GDC_DEVELOPER;
GRANT CREATE TRIGGER TO GDC_DEVELOPER;

-- 4. Assigner rôle à utilisateur
GRANT GDC_DEVELOPER TO GDC_ADMIN;

-- 5. Créer profile sécurisé
CREATE PROFILE SECURE_PROFILE LIMIT
  FAILED_LOGIN_ATTEMPTS 5
  PASSWORD_LIFE_TIME 90
  PASSWORD_REUSE_TIME 365
  PASSWORD_REUSE_MAX 5
  PASSWORD_LOCK_TIME 1/24  -- 1 heure
  PASSWORD_GRACE_TIME 7;   -- 7 jours

-- 6. Assigner profile
ALTER USER GDC_ADMIN PROFILE SECURE_PROFILE;

-- 7. Vérifier
SELECT username, account_status, profile, default_tablespace
FROM dba_users
WHERE username = 'GDC_ADMIN';
```

#### Test Connexion

```bash
# Test connexion utilisateur
sqlplus GDC_ADMIN/SecurePass2026#@localhost:1521/PDB1

SQL> SELECT * FROM session_privs;
-- Affiche tous les privilèges
```

---

### TP07: Flashback

**Objectif:** Récupérer données supprimées (Flashback Drop, Query, Table)

#### Utilisation Commandes CLI

```bash
# 1. Activer Flashback Database
oradba flashback enable --retention-hours 48

# 2. Récupérer table supprimée (Recycle Bin)
oradba flashback drop-restore --table CLIENTS

# 3. Interroger données passées (5 minutes ago)
oradba flashback query --table CLIENTS --minutes-ago 5

# 4. Restaurer table à timestamp
oradba flashback table --table CLIENTS --timestamp "2026-02-15 14:30:00"

# 5. Désactiver Flashback
oradba flashback disable
```

#### Script Shell Direct

```bash
# Exécuter TP07
su - oracle
cd /usr/local/share/oracledba/scripts
./tp07-flashback.sh

# Le script fait:
# - Activation Flashback Database
# - Test DROP table + récupération via Recycle Bin
# - Test Flashback Query (AS OF TIMESTAMP)
# - Test Flashback Table
```

#### SQL Manuel

```sql
-- 1. Activer Flashback Database (en MOUNT)
sqlplus / as sysdba
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
ALTER DATABASE ARCHIVELOG;
ALTER DATABASE FLASHBACK ON;
ALTER DATABASE OPEN;

-- 2. Vérifier
SELECT flashback_on FROM v$database;
-- YES

-- 3. Créer table test
ALTER SESSION SET CONTAINER=PDB1;
CREATE TABLE test_flashback (
  id NUMBER,
  data VARCHAR2(100),
  created_date DATE
);
INSERT INTO test_flashback VALUES (1, 'Original', SYSDATE);
COMMIT;

-- 4. Enregistrer timestamp
SELECT SYSTIMESTAMP FROM dual;
-- 2026-02-16 10:30:00

-- 5. Modifier données
UPDATE test_flashback SET data = 'Modified';
COMMIT;

-- 6. Flashback Query (voir anciennes données)
SELECT * FROM test_flashback 
AS OF TIMESTAMP TO_TIMESTAMP('2026-02-16 10:30:00', 'YYYY-MM-DD HH24:MI:SS')
WHERE id = 1;
-- Affiche: Original

-- 7. Restaurer table à ancien timestamp
ALTER TABLE test_flashback ENABLE ROW MOVEMENT;

FLASHBACK TABLE test_flashback 
TO TIMESTAMP TO_TIMESTAMP('2026-02-16 10:30:00', 'YYYY-MM-DD HH24:MI:SS');

SELECT * FROM test_flashback WHERE id = 1;
-- Data retourné à: Original

-- 8. Test Recycle Bin
DROP TABLE test_flashback;

SELECT object_name, original_name FROM recyclebin;
-- Affiche table supprimée

FLASHBACK TABLE test_flashback TO BEFORE DROP;
-- Table restaurée!
```

#### Vérification

```bash
# Statut Flashback
oradba flashback status

# Affichage:
# Flashback Database: ENABLED
# Flashback Retention: 48 hours
# Oldest Flashback SCN: 85723945
# Oldest Flashback Time: 2026-02-14 10:30:00
```

---

### TP08: RMAN Backup

**Objectif:** Configurer et exécuter sauvegardes RMAN (Full, Incrémental, Archive)

#### Utilisation Commandes CLI

```bash
# 1. Configurer RMAN
oradba rman setup --retention-days 7 --compression

# 2. Backup complet (niveau 0)
oradba rman backup --type full --tag DAILY_FULL

# 3. Backup incrémental (niveau 1)
oradba rman backup --type incremental --tag HOURLY_INC

# 4. Backup archivelogs uniquement
oradba rman backup --type archive --delete-input

# 5. Lister backups
oradba rman list-backups

# 6. Valider backups
oradba rman validate

# 7. Restaurer base complète
oradba rman restore --point-in-time "2026-02-16 14:00:00"
```

#### Script Shell Direct

```bash
# Exécuter TP08
su - oracle
cd /usr/local/share/oracledba/scripts
./tp08-rman.sh

# Le script fait:
# - Configuration RMAN (retention, compression, autobackup)
# - Backup niveau 0 (FULL)
# - Simulation activité base
# - Backup niveau 1 (INCREMENTAL)
# - Backup archivelogs
# - Validation backups
# - Simulation corruption + restauration
```

#### RMAN Manuel

```bash
# Connexion RMAN
rman target /

# 1. Configuration
CONFIGURE RETENTION POLICY TO RECOVERY WINDOW OF 7 DAYS;
CONFIGURE CONTROLFILE AUTOBACKUP ON;
CONFIGURE CONTROLFILE AUTOBACKUP FORMAT FOR DEVICE TYPE DISK TO '/u01/backup/%F';
CONFIGURE DEVICE TYPE DISK BACKUP TYPE TO COMPRESSED BACKUPSET;
CONFIGURE COMPRESSION ALGORITHM 'MEDIUM';

# 2. Backup Full (niveau 0)
BACKUP AS COMPRESSED BACKUPSET 
  INCREMENTAL LEVEL 0 
  DATABASE 
  PLUS ARCHIVELOG DELETE INPUT
  TAG 'FULL_L0';

# 3. Backup Incrémental (niveau 1)
BACKUP AS COMPRESSED BACKUPSET 
  INCREMENTAL LEVEL 1 
  DATABASE 
  TAG 'INC_L1';

# 4. Backup Archivelogs
BACKUP ARCHIVELOG ALL DELETE INPUT;

# 5. Lister backups
LIST BACKUP SUMMARY;
LIST BACKUP OF DATABASE;
LIST BACKUP OF ARCHIVELOG ALL;

# 6. Valider backups
VALIDATE DATABASE;
VALIDATE BACKUPSET ALL;

# 7. Restauration complète
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
RESTORE DATABASE;
RECOVER DATABASE;
ALTER DATABASE OPEN;

# 8. Restauration Point-in-Time
SHUTDOWN IMMEDIATE;
STARTUP MOUNT;
SET UNTIL TIME "TO_DATE('2026-02-16 14:00:00', 'YYYY-MM-DD HH24:MI:SS')";
RESTORE DATABASE;
RECOVER DATABASE;
ALTER DATABASE OPEN RESETLOGS;
```

#### Vérification

```bash
# Rapport RMAN
oradba rman report

# Affichage:
# Last Full Backup: 2026-02-16 02:00:00 (Size: 8.5 GB compressed)
# Last Incremental: 2026-02-16 14:00:00 (Size: 450 MB)
# Last Archivelog: 2026-02-16 15:30:00 (Size: 120 MB)
# Recovery Window: 7 days
# Obsolete Backups: 0
```

---

### TP09: Data Guard

**Objectif:** Configurer réplication Physical Standby pour haute disponibilité

#### Utilisation Commandes CLI

```bash
# Sur PRIMARY (164.92.143.64):

# 1. Configurer Primary pour Data Guard
oradba dataguard setup-primary --standby-host 167.172.176.22

# 2. Créer standby via duplication
oradba dataguard create-standby --standby-host 167.172.176.22 \
  --standby-sid GDCSTBY

# 3. Démarrer synchronisation
oradba dataguard start-apply --standby-host 167.172.176.22

# 4. Vérifier synchronisation
oradba dataguard status

# 5. Switchover (basculement planifié)
oradba dataguard switchover --to-standby

# 6. Failover (basculement urgence)
oradba dataguard failover --standby-host 167.172.176.22
```

#### Script Shell Direct

```bash
# Sur PRIMARY:
su - oracle
cd /usr/local/share/oracledba/scripts
./tp09-dataguard.sh

# Le script fait (sur PRIMARY):
# - Activation FORCE LOGGING
# - Création Standby Redo Logs
# - Configuration parameters Data Guard
# - Création password file pour réplication

# Sur STANDBY (exécuter après):
# - Préparation environnement
# - Duplication via RMAN DUPLICATE
# - Démarrage APPLY (MRP)
# - Vérification LAG
```

#### Configuration Manuelle PRIMARY

```sql
-- Sur PRIMARY
sqlplus / as sysdba

-- 1. Activer FORCE LOGGING
ALTER DATABASE FORCE LOGGING;

-- 2. Créer Standby Redo Logs (1 de plus que online redo)
ALTER DATABASE ADD STANDBY LOGFILE GROUP 11 SIZE 200M;
ALTER DATABASE ADD STANDBY LOGFILE GROUP 12 SIZE 200M;
ALTER DATABASE ADD STANDBY LOGFILE GROUP 13 SIZE 200M;
ALTER DATABASE ADD STANDBY LOGFILE GROUP 14 SIZE 200M;

-- 3. Configurer paramètres Data Guard
ALTER SYSTEM SET LOG_ARCHIVE_CONFIG='DG_CONFIG=(GDCPROD,GDCSTBY)';

ALTER SYSTEM SET LOG_ARCHIVE_DEST_1=
  'LOCATION=/u01/app/oracle/archive VALID_FOR=(ALL_LOGFILES,ALL_ROLES) DB_UNIQUE_NAME=GDCPROD';

ALTER SYSTEM SET LOG_ARCHIVE_DEST_2=
  'SERVICE=GDCSTBY ASYNC VALID_FOR=(ONLINE_LOGFILES,PRIMARY_ROLE) DB_UNIQUE_NAME=GDCSTBY';

ALTER SYSTEM SET LOG_ARCHIVE_DEST_STATE_2=ENABLE;

ALTER SYSTEM SET FAL_SERVER=GDCSTBY;
ALTER SYSTEM SET FAL_CLIENT=GDCPROD;

ALTER SYSTEM SET STANDBY_FILE_MANAGEMENT=AUTO;
```

#### Configuration STANDBY

```bash
# 1. Copier password file de PRIMARY vers STANDBY
scp $ORACLE_HOME/dbs/orapwGDCPROD oracle@standby:$ORACLE_HOME/dbs/

# 2. Créer initfile sur STANDBY
cat > $ORACLE_HOME/dbs/initGDCSTBY.ora << EOF
*.db_name='GDCPROD'
*.db_unique_name='GDCSTBY'
EOF

# 3. Démarrer STANDBY en NOMOUNT
sqlplus / as sysdba
STARTUP NOMOUNT PFILE='$ORACLE_HOME/dbs/initGDCSTBY.ora';

# 4. Dupliquer depuis PRIMARY via RMAN
rman TARGET sys/password@GDCPROD AUXILIARY sys/password@GDCSTBY

DUPLICATE TARGET DATABASE
  FOR STANDBY
  FROM ACTIVE DATABASE
  DORECOVER
  NOFILENAMECHECK;

# 5. Démarrer APPLY sur STANDBY
ALTER DATABASE RECOVER MANAGED STANDBY DATABASE DISCONNECT FROM SESSION;
```

#### Vérification

```sql
-- Sur PRIMARY
SELECT dest_name, status, error FROM v$archive_dest WHERE dest_name='LOG_ARCHIVE_DEST_2';
-- STATUS: VALID

SELECT thread#, max(sequence#) FROM v$archived_log GROUP BY thread#;
-- Sequence: 125

-- Sur STANDBY
SELECT process, status FROM v$managed_standby;
-- MRP0: APPLYING_LOG

SELECT thread#, max(sequence#) FROM v$archived_log WHERE applied='YES' GROUP BY thread#;
-- Sequence: 125 (doit correspondre à PRIMARY)
```

---

### TP10: Performance Tuning

**Objectif:** Analyser et optimiser performances (AWR, SQL Tuning, Memory)

#### Utilisation Commandes CLI

```bash
# 1. Analyser santé système
oradba tuning health-check

# 2. Générer rapport AWR (dernière heure)
oradba tuning awr-report --hours 1 --output /tmp/awr_report.html

# 3. Analyser SQL lents (Top 10)
oradba tuning top-sql --limit 10

# 4. Tuning automatique SQL spécifique
oradba tuning sql-advisor --sql-id 8fzx3m2kp9qrt

# 5. Analyser mémoire SGA/PGA
oradba tuning memory-advisor

# 6. Optimiser paramètres automatiquement
oradba tuning auto-tune --apply

# 7. Monitorer sessions actives
oradba tuning monitor-sessions --interval 5
```

#### Script Shell Direct

```bash
# Exécuter TP10
su - oracle
cd /usr/local/share/oracledba/scripts
./tp10-tuning.sh

# Le script fait:
# - Vérification Alert Log
# - Analyse utilisation tablespaces
# - Check Library Cache Hit Ratio
# - Génération rapport AWR
# - Analyse Top SQL
# - SQL Tuning Advisor
```

#### SQL Manuel - Analyse Performance

```sql
-- Connexion
sqlplus / as sysdba

-- 1. Vérifier Hit Ratios (Cache)
SELECT 
  ROUND((1 - (phy.value / (cur.value + con.value))) * 100, 2) AS "Buffer Cache Hit%"
FROM 
  v$sysstat cur,
  v$sysstat con,
  v$sysstat phy
WHERE 
  cur.name = 'db block gets' AND
  con.name = 'consistent gets' AND
  phy.name = 'physical reads';
-- Idéal: > 95%

-- 2. Library Cache Hit Ratio
SELECT 
  ROUND((1 - (SUM(reloads) / SUM(pins))) * 100, 2) AS "Library Cache Hit%"
FROM v$librarycache;
-- Idéal: > 99%

-- 3. Top SQL par temps CPU
SELECT 
  sql_id,
  ROUND(elapsed_time/1000000, 2) AS elapsed_sec,
  executions,
  ROUND(elapsed_time/executions/1000000, 2) AS avg_sec,
  SUBSTR(sql_text, 1, 60) AS sql_text
FROM v$sql
WHERE executions > 0
ORDER BY elapsed_time DESC
FETCH FIRST 10 ROWS ONLY;

-- 4. Sessions actives
SELECT 
  sid,
  serial#,
  username,
  status,
  program,
  sql_id,
  event,
  wait_time_micro/1000000 AS wait_sec
FROM v$session
WHERE status = 'ACTIVE'
  AND username IS NOT NULL;

-- 5. Générer AWR Report (dernier snapshot)
@$ORACLE_HOME/rdbms/admin/awrrpt.sql
-- Choisir format HTML
-- Choisir nombre de jours: 1
-- Choisir dernier snapshot
```

#### AWR Report Automatique

```bash
# Créer snapshot manuel
sqlplus / as sysdba << EOF
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT();
EOF

# Attendre activité (1 heure)
sleep 3600

# Créer second snapshot
sqlplus / as sysdba << EOF
EXEC DBMS_WORKLOAD_REPOSITORY.CREATE_SNAPSHOT();
EOF

# Générer rapport entre 2 snapshots
sqlplus / as sysdba << EOF
SET LINESIZE 200
SET PAGESIZE 1000
SPOOL /tmp/awr_report.html
SELECT output FROM TABLE(DBMS_WORKLOAD_REPOSITORY.AWR_REPORT_HTML(
  l_dbid => (SELECT dbid FROM v\$database),
  l_inst_num => 1,
  l_bid => (SELECT MAX(snap_id)-1 FROM dba_hist_snapshot),
  l_eid => (SELECT MAX(snap_id) FROM dba_hist_snapshot)
));
SPOOL OFF;
EOF
```

#### Vérification

```bash
# Dashboard performance
oradba tuning dashboard

# Affichage:
# ==========================================
# PERFORMANCE DASHBOARD
# ==========================================
# Buffer Cache Hit Ratio: 97.8%  ✓
# Library Cache Hit:      99.2%  ✓
# SGA Usage:              70%    ✓
# PGA Usage:              45%    ✓
# Active Sessions:        12
# Top Wait Event:         db file sequential read
# Alert Log Errors:       0      ✓
```

---

### TP11: Patching

**Objectif:** Appliquer patches Oracle (RU, PSU, Security)

#### Utilisation Commandes CLI

```bash
# 1. Vérifier patches installés
oradba patch list-installed

# 2. Télécharger patch depuis My Oracle Support
oradba patch download --patch-id 35648110 --output /tmp

# 3. Vérifier conflits avant application
oradba patch analyze --patch-file /tmp/p35648110.zip

# 4. Appliquer patch (arrêt base requis)
oradba patch apply --patch-file /tmp/p35648110.zip

# 5. Rollback patch si problème
oradba patch rollback --patch-id 35648110

# 6. Vérifier post-patching
oradba patch verify
```

#### Script Shell Direct

```bash
# Exécuter TP11 (vérification uniquement)
su - oracle
cd /usr/local/share/oracledba/scripts
./tp11-patching.sh

# Le script fait:
# - Vérification version OPatch
# - Liste patches actuels (opatch lsinventory)
# - Affichage patches SQL appliqués (dba_registry_sqlpatch)
# - Workflow patching (documentation)
```

#### Procédure Manuelle Patching

```bash
# 1. Sauvegarder Oracle Home
tar -czf /backup/oracle_home_backup_$(date +%Y%m%d).tar.gz $ORACLE_HOME

# 2. Télécharger patch .zip depuis MOS

# 3. Vérifier OPatch à jour
$ORACLE_HOME/OPatch/opatch version
# Si ancien, télécharger OPatch 12.2.0.1.x depuis MOS

# 4. Extraire patch
unzip -q p35648110_190000_Linux-x86-64.zip -d /tmp/patch

# 5. Vérifier conflits
cd /tmp/patch/35648110
$ORACLE_HOME/OPatch/opatch prereq CheckConflictAgainstOHWithDetail -ph .

# 6. Arrêter base de données
sqlplus / as sysdba << EOF
SHUTDOWN IMMEDIATE;
EXIT;
EOF

# 7. Arrêter listener
lsnrctl stop

# 8. Appliquer patch
cd /tmp/patch/35648110
$ORACLE_HOME/OPatch/opatch apply

# 9. Redémarrer base
sqlplus / as sysdba << EOF
STARTUP;
EXIT;
EOF

# 10. Appliquer patch SQL (datapatch)
cd $ORACLE_HOME/OPatch
./datapatch -verbose

# 11. Vérifier patch appliqué
$ORACLE_HOME/OPatch/opatch lsinventory

sqlplus / as sysdba << EOF
SELECT patch_id, patch_uid, version, status, description 
FROM dba_registry_sqlpatch
ORDER BY action_time DESC;
EXIT;
EOF
```

#### Vérification

```sql
-- Vérifier patches installés
SELECT 
  patch_id,
  patch_uid,
  version,
  status,
  action,
  action_time,
  description
FROM dba_registry_sqlpatch
ORDER BY action_time DESC;

-- Vérifier composants database
SELECT 
  comp_name,
  version,
  status
FROM dba_registry
WHERE status != 'VALID';
-- Doit être vide
```

---

### TP12: Multi-tenant

**Objectif:** Gérer architecture CDB/PDB (create, clone, plug/unplug)

#### Utilisation Commandes CLI

```bash
# 1. Lister PDBs
oradba pdb list

# 2. Créer nouvelle PDB
oradba pdb create --name PDB_FINANCE --admin-user finadm --admin-pass Finance123

# 3. Cloner PDB existante
oradba pdb clone --source PDB1 --target PDB1_DEV

# 4. Ouvrir/Fermer PDB
oradba pdb open --name PDB_FINANCE
oradba pdb close --name PDB_FINANCE

# 5. Unplugged PDB (export)
oradba pdb unplug --name PDB_TEST --xml /tmp/pdb_test.xml

# 6. Plug PDB (import)
oradba pdb plug --xml /tmp/pdb_test.xml --name PDB_TEST_NEW

# 7. Drop PDB
oradba pdb drop --name PDB_OLD --including-datafiles
```

#### Script Shell Direct

```bash
# Exécuter TP12
su - oracle
cd /usr/local/share/oracledba/scripts
./tp12-multitenant.sh

# Le script fait:
# - Vérification mode CDB
# - Création PDB (PDB_PHOENIX)
# - Ouverture PDB
# - Connexion et création objet dans PDB
# - Clone PDB
```

#### SQL Manuel

```sql
-- Connexion CDB$ROOT
sqlplus / as sysdba

-- 1. Vérifier mode CDB
SELECT name, cdb FROM v$database;
-- CDB: YES

SHOW PDBS;

-- 2. Créer PDB
CREATE PLUGGABLE DATABASE PDB_SALES
ADMIN USER salesadm IDENTIFIED BY Sales123
ROLES = (DBA)
FILE_NAME_CONVERT = ('/pdbseed/', '/pdb_sales/');

-- 3. Ouvrir PDB
ALTER PLUGGABLE DATABASE PDB_SALES OPEN;

-- 4. Sauvegarder état (autostart)
ALTER PLUGGABLE DATABASE PDB_SALES SAVE STATE;

-- 5. Connexion à PDB
ALTER SESSION SET CONTAINER=PDB_SALES;

SELECT name FROM v$pdbs;
-- PDB_SALES

-- 6. Cloner PDB
CREATE PLUGGABLE DATABASE PDB_SALES_DEV 
FROM PDB_SALES
FILE_NAME_CONVERT = ('/pdb_sales/', '/pdb_sales_dev/');

ALTER PLUGGABLE DATABASE PDB_SALES_DEV OPEN;

-- 7. Unplugged PDB
ALTER PLUGGABLE DATABASE PDB_SALES_DEV CLOSE;

ALTER PLUGGABLE DATABASE PDB_SALES_DEV
UNPLUG INTO '/tmp/pdb_sales_dev.xml';

DROP PLUGGABLE DATABASE PDB_SALES_DEV KEEP DATAFILES;

-- 8. Plug PDB sur autre serveur
CREATE PLUGGABLE DATABASE PDB_SALES_PROD
USING '/tmp/pdb_sales_dev.xml'
NOCOPY
TEMPFILE REUSE;

ALTER PLUGGABLE DATABASE PDB_SALES_PROD OPEN;

-- 9. Lister toutes PDBs
SELECT 
  pdb_id,
  pdb_name,
  status,
  open_mode
FROM cdb_pdbs
ORDER BY pdb_id;
```

#### Vérification

```bash
# Status PDBs
oradba pdb status

# Affichage:
# PDB Name          ID   Status    Open Mode      Restricted
# -----------------------------------------------------------
# PDB$SEED          2    NORMAL    READ ONLY      NO
# PDB_SALES         3    NORMAL    READ WRITE     NO
# PDB_HR            4    NORMAL   READ WRITE     NO
# PDB_FINANCE       5    NORMAL    READ WRITE     NO
# PDB_SALES_DEV     6    NORMAL    READ WRITE     NO
```

---

### TP13: AI Foundations

**Objectif:** Activer Oracle Machine Learning et Auto-Indexing

#### Utilisation Commandes CLI

```bash
# 1. Vérifier capacités ML
oradba ai check-capabilities

# 2. Activer Auto-Indexing (mode observation)
oradba ai enable-auto-index --mode report-only

# 3. Lister recommandations auto-index
oradba ai list-auto-index-recommendations

# 4. Appliquer auto-indexes automatiquement
oradba ai enable-auto-index --mode implement

# 5. Activer SQL Automatic Tuning
oradba ai enable-auto-tuning

# 6. Vérifier OML (Oracle Machine Learning)
oradba ai setup-oml
```

#### Script Shell Direct

```bash
# Exécuter TP13
su - oracle
cd /usr/local/share/oracledba/scripts
./tp13-ai-foundations.sh

# Le script fait:
# - Vérification composants JAVA/OML
# - Configuration Auto-Indexing
# - Vérification Automatic SQL Tuning
# - Documentation OML
```

#### SQL Manuel

```sql
-- Connexion
sqlplus / as sysdba

-- 1. Vérifier composants ML
SELECT comp_name, version, status 
FROM dba_registry 
WHERE comp_id IN ('JAVAVM', 'XML');

-- 2. Activer Auto-Indexing (19c+)
EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_MODE', 'REPORT ONLY');

-- 3. Vérifier configuration
SELECT parameter_name, parameter_value 
FROM dba_auto_index_config;

-- 4. Après période observation, activer implémentation
EXEC DBMS_AUTO_INDEX.CONFIGURE('AUTO_INDEX_MODE', 'IMPLEMENT');

-- 5. Lister auto-indexes créés
SELECT 
  owner,
  index_name,
  table_name,
  auto,
  visibility
FROM dba_indexes
WHERE auto = 'YES';

-- 6. Rapports auto-indexing
SELECT 
  DBMS_AUTO_INDEX.REPORT_ACTIVITY() 
FROM dual;

-- 7. Automatic SQL Tuning (déjà actif par défaut)
SELECT client_name, status 
FROM dba_autotask_client
WHERE client_name = 'sql tuning advisor';
-- Status: ENABLED

-- 8. Vérifier résultats SQL Tuning Advisor
SELECT 
  task_name,
  execution_start,
  status,
  recommendation_count
FROM dba_advisor_log
WHERE owner = 'SYS'
  AND task_name LIKE 'SYS_AUTO_SQL_TUNING%'
ORDER BY execution_start DESC
FETCH FIRST 10 ROWS ONLY;
```

#### Vérification

```bash
# Rapport AI/ML
oradba ai report

# Affichage:
# ==========================================
# AI/ML CAPABILITIES STATUS
# ==========================================
# Oracle Machine Learning:  AVAILABLE
# Auto-Indexing:            ENABLED (Report Only)
# Auto SQL Tuning:          ENABLED
# Java VM:                  VALID
#
# Auto-Index Statistics:
# - Indexes Created:        5
# - Performance Gain:       23%
# - Recommendations:        12
```

---

### TP14: Mobilité et Concurrence

**Objectif:** Data Pump export/import, gestion locks, audit

#### Utilisation Commandes CLI

```bash
# 1. Export schema avec Data Pump
oradba datapump export --schema GDC_ADMIN --file export_gdc.dmp --dir /backup

# 2. Import schema
oradba datapump import --file export_gdc.dmp --schema GDC_ADMIN --dir /backup

# 3. Export table spécifique
oradba datapump export --table GDC_ADMIN.CUSTOMERS --file customers.dmp

# 4. Analyser locks actifs
oradba db analyze-locks

# 5. Tuer session bloquante
oradba db kill-session --sid 125 --serial 38456

# 6. Activer audit
oradba security enable-audit --actions "CREATE SESSION,CREATE TABLE"

# 7. Consulter logs audit
oradba security audit-report --last-hours 24
```

#### Script Shell Direct

```bash
# Exécuter TP14
su - oracle
cd /usr/local/share/oracledba/scripts
./tp14-mobilite-concurrence.sh

# Le script fait:
# - Création directory Oracle pour Data Pump
# - Export schema avec expdp
# - Simulation lock (deux sessions)
# - Détection et résolution lock
# - Activation audit
# - Consultation logs audit
```

#### Data Pump Manuel

```bash
# 1. Créer directory
sqlplus / as sysdba << EOF
CREATE OR REPLACE DIRECTORY BACKUP_DIR AS '/u01/backup/datapump';
GRANT READ, WRITE ON DIRECTORY BACKUP_DIR TO system;
EXIT;
EOF

# 2. Export schema complet
expdp system/password@PDB1 \
  DIRECTORY=BACKUP_DIR \
  DUMPFILE=schema_export_%U.dmp \
  LOGFILE=schema_export.log \
  SCHEMAS=GDC_ADMIN \
  PARALLEL=2 \
  COMPRESSION=ALL

# 3. Export table spécifique
expdp GDC_ADMIN/password@PDB1 \
  DIRECTORY=BACKUP_DIR \
  DUMPFILE=customers.dmp \
  TABLES=CUSTOMERS \
  COMPRESSION=ALL

# 4. Import sur autre base
impdp system/password@PDB2 \
  DIRECTORY=BACKUP_DIR \
  DUMPFILE=schema_export_%U.dmp \
  LOGFILE=schema_import.log \
  REMAP_SCHEMA=GDC_ADMIN:GDC_ADMIN_DEV \
  PARALLEL=2
```

#### Gestion Locks Manuel

```sql
-- 1. Détecter locks
SELECT 
  s1.username AS blocker,
  s1.sid AS blocker_sid,
  s1.serial# AS blocker_serial,
  s2.username AS waiter,
  s2.sid AS waiter_sid,
  s2.serial# AS waiter_serial,
  lo.object_id,
  do.object_name
FROM 
  v$lock l1,
  v$lock l2,
  v$session s1,
  v$session s2,
  v$locked_object lo,
  dba_objects do
WHERE 
  s1.sid = l1.sid AND
  s2.sid = l2.sid AND
  l1.block = 1 AND
  l2.request > 0 AND
  l1.id1 = l2.id1 AND
  l1.id2 = l2.id2 AND
  lo.session_id = s1.sid AND
  do.object_id = lo.object_id;

-- 2. Tuer session bloquante
ALTER SYSTEM KILL SESSION '125,38456' IMMEDIATE;

-- 3. Activer audit
AUDIT SESSION;
AUDIT CREATE TABLE;
AUDIT DROP TABLE;

-- 4. Consulter audit
SELECT 
  username,
  action_name,
  timestamp,
  returncode
FROM dba_audit_trail
WHERE timestamp > SYSDATE - 1
ORDER BY timestamp DESC;
```

#### Vérification

```bash
# Vérifier export réussi
ls -lh /u01/backup/datapump/
# -rw-r-----. 1 oracle oinstall 850M Feb 16 15:30 schema_export_01.dmp

# Vérifier audit activé
sqlplus / as sysdba << EOF
SELECT parameter, value FROM v\$option WHERE parameter = 'Unified Auditing';
EXIT;
EOF
```

---

### TP15: ASM et RAC

**Objectif:** Comprendre architecture ASM/RAC (conceptuel et simulation)

#### Utilisation Commandes CLI

```bash
# 1. Vérifier configuration cluster
oradba rac check-cluster

# 2. Préparer environnement pour Grid Infrastructure
oradba rac prepare-grid --nodes node1,node2 --nfs-server 192.168.1.100

# 3. Simuler architecture ASM (documentation)
oradba asm show-architecture

# 4. Créer Disk Group ASM (si Grid installé)
oradba asm create-diskgroup --name DATA --disks /dev/sd[b-d] --redundancy NORMAL

# 5. Vérifier Disk Groups
oradba asm list-diskgroups

# 6. Status cluster RAC
oradba rac cluster-status

# 7. Ajouter node au cluster
oradba rac add-node --node node3 --vip 192.168.1.13
```

#### Script Shell Direct

```bash
# Exécuter TP15 (conceptuel)
su - oracle
cd /usr/local/share/oracledba/scripts
./tp15-asm-rac-concepts.sh

# Le script fait:
# - Affichage architecture ASM (diagrammes ASCII)
# - Affichage architecture RAC
# - Comparaison ASM vs File System
# - Comparaison RAC vs Data Guard
# - Prérequis Grid Infrastructure
# - Workflow installation Grid+RAC
```

#### Configuration NFS pour RAC (Simulation)

```bash
# Sur serveur NFS (192.168.1.100):
sudo oradba nfs setup-server --export-path /oracleshared --clients "192.168.1.11,192.168.1.12"

# Sur nodes RAC (node1, node2):
sudo oradba nfs setup-client --nfs-server 192.168.1.100 --mount-point /oracleshared

# Vérifier partage accessible
df -h | grep oracleshared
# 192.168.1.100:/oracleshared  500G  50G  450G  10%  /oracleshared
```

#### ASM Commands (si Grid Infrastructure installé)

```bash
# Se connecter à ASM instance
export ORACLE_SID=+ASM
sqlplus / as sysasm

-- Lister Disk Groups
SELECT 
  name,
  state,
  type,
  total_mb,
  free_mb,
  ROUND((total_mb - free_mb) / total_mb * 100, 2) AS used_pct
FROM v$asm_diskgroup;

-- Lister disques
SELECT 
  dg.name AS diskgroup,
  d.path,
  d.total_mb,
  d.free_mb
FROM 
  v$asm_disk d,
  v$asm_diskgroup dg
WHERE d.group_number = dg.group_number;

-- Créer Disk Group
CREATE DISKGROUP DATA NORMAL REDUNDANCY
  DISK '/dev/sdb', '/dev/sdc', '/dev/sdd'
  ATTRIBUTE 'compatible.asm' = '19.0';

-- Ajouter disque à Disk Group
ALTER DISKGROUP DATA ADD DISK '/dev/sde';

-- Vérifier Re-balance
SELECT operation, state, power, actual, est_minutes
FROM v$asm_operation;
```

#### RAC Status (si cluster installé)

```bash
# Vérifier statut cluster
crsctl status resource -t

# Vérifier tous les nodes
olsnodes -n -s -t

# Status base RAC
srvctl status database -d RACPROD

# Démarrer instance sur node2
srvctl start instance -d RACPROD -i RACPROD2

# Relocate service vers node1
srvctl relocate service -d RACPROD -s SALES_SVC -i RACPROD2 -t RACPROD1
```

#### Vérification

```bash
# Architecture report
oradba rac architecture-report

# Affichage:
# ==========================================
# RAC ARCHITECTURE
# ==========================================
# Cluster Name:       RACCLUSTER
# Nodes:              2 (node1, node2)
# Grid Version:       19.3.0.0.0
# Database:           RACPROD
# Instances:          RACPROD1 (node1), RACPROD2 (node2)
# 
# ASM:
# - Disk Group DATA:  500 GB (Normal Redundancy)
# - Disk Group FRA:   200 GB (Normal Redundancy)
# - Disks:            6 (/dev/sd[b-g])
#
# Network:
# - Public:           eth0 (192.168.1.x)
# - Private:          eth1 (10.0.0.x)
# - Scan Listeners:   3
```

---

## 🔧 Cas d'Usage Avancés

### Cas 1: Installation Production avec Data Guard

```bash
# 1. Installer PRIMARY
sudo oradba install full --config production-primary.yml

# 2. Activer Data Guard sur PRIMARY
oradba dataguard setup-primary --standby-host standby.domain.com

# 3. Installer STANDBY
sudo oradba install full --config production-standby.yml --skip-database

# 4. Créer STANDBY via duplication
oradba dataguard create-standby --standby-host standby.domain.com

# 5. Automatiser backups PRIMARY
crontab -e
# 0 2 * * * /usr/local/bin/oradba rman backup --type full
# 0 */6 * * * /usr/local/bin/oradba rman backup --type incremental

# 6. Monitorer synchronisation
watch -n 10 "oradba dataguard status"
```

### Cas 2: Déploiement Multi-PDB pour Microservices

```bash
# 1. Créer CDB principale
oradba install database --cdb

# 2. Créer PDB par microservice
oradba pdb create --name PDB_AUTH --admin-user authadm --admin-pass Auth123
oradba pdb create --name PDB_ORDERS --admin-user ordersadm --admin-pass Orders123
oradba pdb create --name PDB_INVENTORY --admin-user invadm --admin-pass Inv123

# 3. Configurer connection per-PDB
for pdb in AUTH ORDERS INVENTORY; do
  oradba db configure-service --pdb PDB_$pdb --service ${pdb}_SVC --preferred-instance 1
done

# 4. Test connexion applicative
sqlplus authadm/Auth123@server:1521/AUTH_SVC
```

### Cas 3: Migration depuis Autre Serveur

```bash
# Sur ancien serveur:
# 1. Export complet
oradba datapump export --full --file full_export.dmp --dir /backup

# 2. Transférer dump
rsync -avz /backup/full_export.dmp oracle@newserver:/import/

# Sur nouveau serveur:
# 3. Installer Oracle
sudo oradba install full --config migration-config.yml

# 4. Import
oradba datapump import --full --file /import/full_export.dmp

# 5. Vérifier intégrité
oradba db validate-all
```

### Cas 4: Setup Environnement Développement Rapide

```bash
# Installation minimale (skip checks)
oradba install full --config dev-config.yml --skip-system-checks --fast

# Créer PDB développement
oradba pdb create --name PDB_DEV --admin-user devadm --admin-pass Dev123

# Désactiver archivelog (dev uniquement!)
oradba db disable-archivelog

# Import données test
oradba datapump import --file test_data.dmp --schema TESTUSER
```

---

## ❓ Dépannage

### Problème: Installation échoue (prérequis)

```bash
# Vérifier détails
oradba install check-prereqs --verbose

# Forcer installation packages manquants
sudo dnf install -y $(oradba install list-required-packages)

# Retry installation
sudo oradba install full --config my-config.yml --force
```

### Problème: Base ne démarre pas

```bash
# Diagnostic
oradba db diagnose

# Check alert log
oradba db tail-alert --lines 100

# Démarrer en mode diagnostic
oradba db start --mode nomount
oradba db start --mode mount

# Vérifier control files
sqlplus / as sysdba << EOF
SELECT name, status FROM v\$controlfile;
EXIT;
EOF
```

### Problème: RMAN backup échoue

```bash
# Vérifier espace disque
df -h /u01/backup

# Vérifier archivelog space
oradba db analyze-archivelog-usage

# Nettoyer vieux archivelogs
oradba rman delete-obsolete

# Retry backup
oradba rman backup --type full --force
```

### Problème: Data Guard désynchronisé

```bash
# Vérifier LAG
oradba dataguard check-lag

# Re-synchroniser
oradba dataguard resync --force

# Si trop de lag, recréer standby
oradba dataguard rebuild-standby --standby-host standby.domain.com
```

### Problème: Performance dégradée

```bash
# Analyse rapide
oradba tuning health-check

# AWR report
oradba tuning awr-report --last-hours 1

# Top SQL
oradba tuning top-sql --limit 20

# Appliquer recommandations
oradba tuning auto-tune --apply
```

---

## 📞 Support

**Documentation:**
- GitHub: https://github.com/ELMRABET-Abdelali/oracledba
- Issues: https://github.com/ELMRABET-Abdelali/oracledba/issues

**Exemples:**
- Voir dossier `examples/` pour configurations type
- Scripts originaux dans `/usr/local/share/oracledba/scripts/`

**Aide Commande:**
```bash
oradba --help
oradba install --help
oradba rman --help
oradba dataguard --help
```

---

**Auteur:** DBA Formation Team  
**Licence:** MIT  
**Version:** 1.0.0  
**Dernière mise à jour:** Février 2026
