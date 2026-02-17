# Installation Automatique Oracle 19c sur Rocky Linux 8

## 📚 Vue d'ensemble

Ce repository contient une collection complète de scripts d'installation et de configuration pour Oracle Database 19c Enterprise Edition sur Rocky Linux 8.

**Formation complète DBA:** 15 modules couvrant de la préparation système jusqu'aux concepts RAC avancés.

## 🎯 Objectifs

- ✅ Installation automatisée Oracle 19c
- ✅ Configuration production-ready
- ✅ Scripts modulaires et réutilisables
- ✅ Documentation complète en français
- ✅ Compatible Rocky Linux 8 / RHEL 8 / CentOS 8

## 📋 Prérequis

### Matériel minimum
- **RAM:** 4 GB (minimum 2 GB)
- **Disk:** 50 GB disponible
- **CPU:** 2 cores minimum
- **Swap:** 4 GB

### Logiciel
- **OS:** Rocky Linux 8.x
- **Accès:** root et utilisateur oracle
- **Réseau:** Connexion internet pour téléchargements
- **Port:** 1521 (listener Oracle)

## 🚀 Installation Rapide

### Option 1: Installation Complète Automatique

```bash
# Cloner repository
cd /root
git clone <repository-url> oracle-installation
cd oracle-installation/scripts

# Exécuter installation complète (root requis)
chmod +x install-oracle-complete.sh
./install-oracle-complete.sh
```

L'installation complète prend environ **2-3 heures** selon la machine.

### Option 2: Installation Module par Module

```bash
# Chaque TP peut être exécuté individuellement
cd scripts/

# TP01: Préparation système (en tant que root)
./tp01-system-readiness.sh

# TP02-15: Exécuter en tant qu'oracle
su - oracle
./tp02-installation-binaire.sh
./tp03-creation-instance.sh
# ... etc
```

## 📖 Structure des TPs

### Phase 1: Infrastructure (TP01-03)
- **TP01:** System Readiness
  - Configuration kernel
  - Packages requis
  - Utilisateurs/groupes Oracle
  - Structure OFA

- **TP02:** Installation Binaire
  - Variables environnement
  - Download Oracle 19c (3 GB)
  - Extraction binaires

- **TP03:** Création Instance
  - Installation software
  - DBCA database creation
  - Listener configuration

### Phase 2: Fichiers Critiques (TP04-05)
- **TP04:** Multiplexage
  - Control files (3 copies)
  - Redo logs (4 groups, 2 membres)
  - ARCHIVELOG mode

- **TP05:** Gestion Stockage
  - Tablespaces
  - Datafiles dynamiques
  - OMF (Oracle Managed Files)

### Phase 3: Sécurité (TP06-07)
- **TP06:** Sécurité et Accès
  - Users, roles, privileges
  - Profiles de sécurité
  - Audit configuration

- **TP07:** Flashback Technologies
  - Flashback Database
  - Flashback Query / Table / Drop
  - Restore Points

### Phase 4: Backup & HA (TP08-09)
- **TP08:** RMAN Backup
  - Full backup niveau 0
  - Incremental niveau 1
  - Archive logs
  - Validation

- **TP09:** Data Guard
  - Configuration primary
  - Standby redo logs
  - FAL configuration

### Phase 5: Tuning & Maintenance (TP10-11)
- **TP10:** Performance Tuning
  - AWR snapshots
  - SQL Tuning Advisor
  - Indexation
  - Statistics

- **TP11:** Patching
  - OPatch utility
  - Pre-patch backup
  - Datapatch process
  - Post-patch validation

### Phase 6: Avancé (TP12-15)
- **TP12:** Multitenant
  - CDB/PDB architecture
  - Clone PDB
  - Unplug/Plug
  - Resource Manager

- **TP13:** AI/ML Foundations
  - Oracle Machine Learning
  - Predictive models
  - Python integration (cx_Oracle)

- **TP14:** Mobilité et Concurrence
  - Data Pump (expdp/impdp)
  - Transportable Tablespaces
  - Lock management

- **TP15:** ASM et RAC
  - ASM architecture
  - RAC concepts
  - Cache Fusion
  - Grid Infrastructure

## 🛠️ Scripts Disponibles

| Script | Description | Durée | User |
|--------|-------------|-------|------|
| `tp01-system-readiness.sh` | Préparation système | 5 min | root |
| `tp02-installation-binaire.sh` | Download Oracle | 10 min | oracle |
| `tp03-creation-instance.sh` | Créer base GDCPROD | 20 min | oracle |
| `tp04-fichiers-critiques.sh` | Multiplexage | 5 min | oracle |
| `tp05-gestion-stockage.sh` | Tablespaces | 5 min | oracle |
| `tp06-securite-acces.sh` | Sécurité | 5 min | oracle |
| `tp07-flashback.sh` | Flashback | 10 min | oracle |
| `tp08-rman.sh` | RMAN backup | 15 min | oracle |
| `tp09-dataguard.sh` | Data Guard prep | 10 min | oracle |
| `tp10-tuning.sh` | Performance | 15 min | oracle |
| `tp11-patching.sh` | Patching | 5 min | oracle |
| `tp12-multitenant.sh` | Multitenant | 10 min | oracle |
| `tp13-ai-foundations.sh` | AI/ML | 10 min | oracle |
| `tp14-mobilite-concurrence.sh` | Mobilité | 10 min | oracle |
| `tp15-asm-rac-concepts.sh` | ASM/RAC | 5 min | oracle |

## 💾 Configuration Finale

Après installation complète, vous aurez:

```
CDB: GDCPROD
├── PDB: GDCPDB (principal)
├── PDB: PDB2 (test)
└── PDB: PDB3 (clone GDCPDB)

Utilisateurs:
├── SYS (DBA)
├── SYSTEM (DBA)
├── dev_user (développeur)
├── app_user (applicatif)
├── readonly_user (lecture seule)
└── mluser (machine learning)

Tablespaces:
├── SYSTEM
├── SYSAUX
├── USERS
├── TEMP / TEMP2
├── UNDOTBS1
├── GDCDATA (données métier)
└── OMF_TEST (Oracle Managed Files)

Backup:
├── Control Files: 3 copies multiplexées
├── Redo Logs: 4 groups × 2 membres
├── Archivelog: Mode activé
├── RMAN: Level 0 + Level 1 configuré
└── FRA: 20 GB

Flashback:
├── Flashback Database: ON (2 jours)
└── Restore Point: before_tp07 (guaranteed)
```

## 🔧 Post-Installation

### Vérifier statut

```bash
# En tant qu'oracle
su - oracle
sqlplus / as sysdba

SQL> SELECT name, open_mode FROM v$database;
SQL> SELECT name, open_mode FROM v$pdbs;
SQL> SELECT * FROM v$instance;
```

### Connexions

```bash
# CDB Root
sqlplus / as sysdba
sqlplus sys/SysOracle123@localhost:1521/GDCPROD as sysdba

# PDB
sqlplus sys/SysOracle123@localhost:1521/gdcpdb as sysdba

# Utilisateurs applicatifs
sqlplus dev_user/DevPass123@localhost:1521/gdcpdb
sqlplus mluser/MlPass123@localhost:1521/gdcpdb
```

### Commandes utiles

```bash
# Status listener
lsnrctl status

# Status database
srvctl status database -d GDCPROD  # RAC only
ps -ef | grep ora_pmon  # Single instance

# Logs
tail -f $ORACLE_BASE/diag/rdbms/gdcprod/GDCPROD/trace/alert_GDCPROD.log

# RMAN
rman target /
RMAN> LIST BACKUP SUMMARY;
```

## 📊 Logs et Dépannage

### Emplacements logs

```
Installation: /u01/app/oracle/admin/installation_logs/
Alert Log:    $ORACLE_BASE/diag/rdbms/gdcprod/GDCPROD/trace/alert_GDCPROD.log
Listener:     $ORACLE_BASE/diag/tnslsnr/$(hostname)/listener/trace/
RMAN:         $ORACLE_BASE/backup/
Data Pump:    /u01/app/oracle/admin/datapump/
```

### Problèmes courants

**1. Erreur "cannot connect to database"**
```bash
# Vérifier instance
ps -ef | grep ora_pmon_GDCPROD

# Vérifier listener
lsnrctl status

# Démarrer si nécessaire
sqlplus / as sysdba
SQL> STARTUP;
```

**2. Espace disque insuffisant**
```bash
# Vérifier utilisation
df -h /u01

# Nettoyer archivelogs
rman target /
RMAN> DELETE NOPROMPT ARCHIVELOG ALL COMPLETED BEFORE 'SYSDATE-1';
```

**3. PDB ne s'ouvre pas**
```sql
ALTER PLUGGABLE DATABASE gdcpdb OPEN;
ALTER PLUGGABLE DATABASE gdcpdb SAVE STATE;
```

## 🌐 Ressources

### Documentation Oracle
- [Oracle 19c Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/)
- [DBA Guide](https://docs.oracle.com/en/database/oracle/oracle-database/19/admin/)
- [RAC Administration](https://docs.oracle.com/en/database/oracle/oracle-database/19/racad/)

### Scripts et Outils
- [OPatch Updates](https://support.oracle.com) - My Oracle Support
- [RMAN Best Practices](https://www.oracle.com/technetwork/database/features/availability/maa-096855.html)

### Community
- [Oracle Community Forums](https://community.oracle.com/)
- [Ask TOM](https://asktom.oracle.com/)
- [Oracle Base](https://oracle-base.com/)

## 📝 License

Scripts éducatifs pour formation DBA Oracle.
Oracle Database 19c nécessite licence commerciale Oracle.

## 👥 Auteurs

Formation DBA - Adaptation Rocky Linux 8
Basé sur méthodologie Oracle certifiée

## 🤝 Contribution

Pour améliorer les scripts:
1. Fork le repository
2. Créer feature branch
3. Commit changements
4. Push et créer Pull Request

## ⚠️ Avertissements

- **Production:** Tester en environnement dev avant production
- **Sécurité:** Changer tous les mots de passe par défaut
- **Backup:** Configurer backups automatiques RMAN
- **Patching:** Appliquer patches de sécurité Oracle régulièrement

## 📞 Support

Pour questions ou problèmes:
- Ouvrir une issue GitHub
- Consulter logs dans `/u01/app/oracle/admin/installation_logs/`
- Vérifier alert.log Oracle

---

**Dernière mise à jour:** Janvier 2025
**Version Oracle:** 19.3.0.0.0 Enterprise Edition
**OS Certifié:** Rocky Linux 8.8+ / RHEL 8
