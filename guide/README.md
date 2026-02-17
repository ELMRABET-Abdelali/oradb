# 🗄️ OracleDBA - Complete Oracle Database Administration Package

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Oracle 19c](https://img.shields.io/badge/Oracle-19c-red.svg)](https://www.oracle.com/database/)

Un package complet pour l'installation, la configuration et la gestion d'Oracle Database 19c sur Rocky Linux 8/9.

## 🎉 **ONE-BUTTON Installation Complete!**

```bash
# Installation complète Oracle 19c en une seule commande
sudo oradba install all
```

✨ **30-45 minutes** pour une installation complète automatisée:
- ✅ Configuration système (utilisateurs, kernel, packages)
- ✅ Téléchargement binaires Oracle (3GB depuis Google Drive)
- ✅ Installation logiciel Oracle (runInstaller)
- ✅ Création base de données GDCPROD avec PDB

**📖 Voir [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) pour le guide complet**

## 🚀 Fonctionnalités

### 🎯 Basé sur Scripts Testés Rocky Linux 8

Ce package est construit sur **15 scripts shell testés et approuvés** (TP01-TP15) couvrant l'intégralité du cycle de vie Oracle Database 19c. Consultez [SCRIPTS_MAPPING.md](SCRIPTS_MAPPING.md) pour la correspondance détaillée.

### ✨ Fonctionnalités Principales

- ✅ **Installation complète** d'Oracle 19c Enterprise Edition (ONE-CLICK!)
- 🔧 **Configuration système** automatique (users, groups, kernel parameters)
- 💾 **RMAN** - Backups automatisés et récupération
- 🔄 **Data Guard** - Configuration standby database
- ⚡ **Performance Tuning** - Optimisation SQL et mémoire
- 🏢 **Multitenant** - Gestion CDB/PDB
- 💿 **ASM** - Automatic Storage Management
- 🔗 **RAC** - Real Application Clusters (concepts et setup)
- 🔐 **Sécurité** - Users, roles, privilèges
- 📊 **Flashback** - Technologies de récupération
- 🤖 **AI/ML** - Oracle Machine Learning
- 🌐 **NFS Setup** - Configuration serveur NFS pour RAC

### 📦 Complete Feature Set - Functionality-Based Commands

All database administration tasks accessible via intuitive CLI commands:

| Feature | CLI Command | Description |
|----|-------------|-------------|
| **System Setup** | `install system` | Prepare system (users, kernel, swap, packages) |
| **Oracle Binaries** | `install binaries` | Download Oracle 19c binaries (3GB) |
| **Database Creation** | `install database` | Create database instance with DBCA |
| **Critical Files** | `configure multiplexing` | Multiplex control files and redo logs |
| **Storage Mgmt** | `configure storage` | Tablespaces and datafile management |
| **Security** | `configure users` | Users, roles, and profiles |
| **Flashback** | `configure flashback` | Flashback Database and Query |
| **RMAN Backup** | `configure backup` | RMAN backups (Full, Incremental, Archive) |
| **Data Guard** | `configure dataguard` | Physical Standby setup |
| **Performance** | `maintenance tune` | Performance tuning and AWR |
| **Patching** | `maintenance patch` | Apply Oracle patches (RU, PSU) |
| **Multitenant** | `advanced multitenant` | CDB/PDB management |
| **AI/ML** | `advanced ai-ml` | AI Foundations and Machine Learning |
| **Data Mobility** | `advanced data-mobility` | Data Pump and transportable tablespaces |
| **ASM/RAC** | `advanced asm-rac` | ASM and RAC Concepts |

**💡 Quick Commands:**
```bash
# List all available configuration labs
oradba labs

# Install everything
sudo oradba install all

# Configure essential features
sudo oradba configure all

# View database status
oradba status
```

📖 **See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed examples**

## 📦 Installation

### Installation rapide via pip

```bash
pip install oracledba
```

### Installation depuis GitHub

```bash
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba
pip install -e .
```

### Installation avec support Oracle

```bash
pip install oracledba[oracle]
```

## ⚡ Démarrage Rapide

### 1️⃣ Installation Oracle 19c Complète (Mode Automatique) 🆕

**Option A: Installation en Un Clic (Recommandé)**

```bash
# Installation complète automatique
sudo oradba install all
```

**Option B: Installation Étape par Étape**

```bash
# 1. Installer le package
pip install oracledba

# 2. Préparer configuration (optionnel)
oradba-wizard  # Assistant interactif

# 3. Installation par étapes
sudo oradba install system      # Configure system
sudo oradba install binaries    # Download Oracle (3GB)
sudo oradba install software    # Run runInstaller  
sudo oradba install database    # Create DB with DBCA

# 4. Vérifier
oradba status
sqlplus / as sysdba
```

**Résultat:** Base Oracle 19c opérationnelle en 30-45 minutes ! ✅

### 2️⃣ Configuration Post-Installation

```bash
# Configure toutes les fonctionnalités essentielles
sudo oradba configure all

# Ou configurer individuellement:
sudo oradba configure multiplexing   # Critical files
sudo oradba configure storage        # Tablespaces
sudo oradba configure backup         # RMAN setup
sudo oradba configure flashback      # Flashback DB
```

### 3️⃣ Exemples d'Utilisation Quotidienne

```bash
# Status de la base
oradba status

# Backup complet quotidien
oradba rman backup --type full --tag DAILY_FULL

# Vérifier santé système
oradba monitor tablespaces
oradba monitor sessions

# Créer nouvelle PDB
oradba pdb create --name PDB_SALES

# Export schema
oradba datapump export --schema GDC_ADMIN --file /backup/gdc_admin.dmp

# Vérifier Data Guard synchronisation
oradba dataguard status

# Voir les logs
oradba logs alert
oradba logs listener
```

### 4️⃣ Voir Toutes les Fonctionnalités

```bash
# Liste toutes les configurations disponibles
oradba labs

# Aide sur les commandes
oradba --help
oradba install --help
oradba configure --help
```
```

### 4️⃣ Configuration Production avec Data Guard

```bash
# Sur PRIMARY:
oradba install full --config production-primary.yml
oradba dataguard setup-primary --standby-host standby.server.com

# Sur STANDBY:
oradba install full --config production-standby.yml --skip-database
oradba dataguard create-standby --primary-host primary.server.com

# Automatiser backups (crontab PRIMARY)
0 2 * * * /usr/local/bin/oradba rman backup --type full
0 */6 * * * /usr/local/bin/oradba rman backup --type incremental
```

📚 **Pour plus d'exemples, voir [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)**

## 🎯 Utilisation

### Installation complète d'Oracle 19c

```bash
# Installation interactive avec wizard
oradba-setup

# Installation complète automatique
oradba install --full

# Installation par étapes
oradba install --system          # Préparation système
oradba install --binaries        # Installation binaires Oracle
oradba install --database        # Création de la base de données
```

### Gestion des modules

```bash
# RMAN - Backup et Recovery
oradba rman --setup              # Configuration RMAN
oradba rman --backup full        # Backup complet
oradba rman --backup incremental # Backup incrémental
oradba rman --restore            # Restauration

# Data Guard
oradba dataguard --setup         # Configuration Data Guard
oradba dataguard --status        # Statut
oradba dataguard --switchover    # Switchover

# Performance Tuning
oradba tuning --analyze          # Analyse performance
oradba tuning --awr              # Rapport AWR
oradba tuning --addm             # ADDM Report
oradba tuning --sql-trace        # Traçage SQL

# ASM - Automatic Storage Management
oradba asm --setup               # Configuration ASM
oradba asm --create-diskgroup    # Créer diskgroup
oradba asm --status              # Statut ASM

# RAC - Real Application Clusters
oradba rac --setup               # Configuration RAC
oradba rac --add-node            # Ajouter nœud
oradba rac --status              # Statut cluster

# Multitenant (CDB/PDB)
oradba pdb --create NAME         # Créer PDB
oradba pdb --clone SRC DEST      # Cloner PDB
oradba pdb --list                # Lister PDBs
oradba pdb --open NAME           # Ouvrir PDB
oradba pdb --close NAME          # Fermer PDB

# Flashback
oradba flashback --enable        # Activer Flashback
oradba flashback --restore       # Restaurer avec Flashback

# Sécurité
oradba security --audit          # Configuration audit
oradba security --encryption     # Configurer TDE
oradba security --users          # Gestion users

# NFS Server
oradba nfs --setup               # Configuration NFS
oradba nfs --mount               # Monter NFS
oradba nfs --share               # Partager répertoire
```

### Gestion de base

```bash
# Statut de la base
oradba status

# Démarrer/Arrêter
oradba start
oradba stop
oradba restart

# Connecter à SQL*Plus
oradba sqlplus
oradba sqlplus --sysdba

# Logs et monitoring
oradba logs --alert              # Alert log
oradba logs --listener           # Listener log
oradba monitor --tablespaces     # Surveillance tablespaces
oradba monitor --sessions        # Sessions actives
```

### Scripts personnalisés

```bash
# Exécuter un script SQL
oradba exec script.sql

# Exécuter un script bash
oradba exec script.sh

# Exécuter des commandes RMAN
oradba rman --script backup.rman
```

## 📋 Configuration

### Fichier de configuration YAML

Créez un fichier `oradba-config.yml`:

```yaml
# Configuration OracleDBA
system:
  os: "Rocky Linux 8"
  min_ram_gb: 4
  min_disk_gb: 50

oracle:
  version: "19.3.0.0.0"
  edition: "EE"
  oracle_base: "/u01/app/oracle"
  oracle_home: "/u01/app/oracle/product/19.3.0/dbhome_1"

database:
  db_name: "GDCPROD"
  sid: "GDCPROD"
  cdb: true
  pdbs:
    - name: "PDB1"
      admin_password: "Oracle123"

backup:
  location: "/u01/backup"
  retention_days: 7
  compression: true

nfs:
  server: "192.168.1.10"
  export_path: "/u01/shared"
  mount_point: "/u01/nfs"
```

Utiliser la configuration:

```bash
oradba install --config oradba-config.yml
```

### Variables d'environnement

```bash
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib
```

## 🏗️ Architecture

```
oracledba/
├── oracledba/
│   ├── __init__.py
│   ├── cli.py                 # CLI principale
│   ├── setup_wizard.py        # Wizard d'installation
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── install.py         # Installation Oracle
│   │   ├── rman.py            # RMAN management
│   │   ├── dataguard.py       # Data Guard
│   │   ├── tuning.py          # Performance tuning
│   │   ├── asm.py             # ASM management
│   │   ├── rac.py             # RAC management
│   │   ├── pdb.py             # Multitenant
│   │   ├── flashback.py       # Flashback
│   │   ├── security.py        # Security
│   │   └── nfs.py             # NFS management
│   ├── scripts/               # Scripts bash/SQL
│   ├── configs/               # Configurations YAML
│   ├── templates/             # Templates Jinja2
│   └── utils/                 # Utilitaires
│       ├── logger.py
│       ├── oracle_client.py
│       └── ssh_client.py
├── tests/
├── docs/
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
└── requirements.txt
```

## 📚 Documentation Complète

### 🌟 Guides Principaux (Recommandés)

**[📖 Documentation Hub](docs/)** - Toute la documentation organisée

#### Pour Démarrer
- **[⚡ Quick Start](docs/guides/QUICKSTART.md)** - Démarrage rapide en 15 minutes
- **[📘 Guide d'Utilisation Complet](docs/guides/GUIDE_UTILISATION.md)** - Guide complet avec exemples pour TOUS les TPs (TP01-TP15)
  - Installation (3 méthodes: GitHub, PyPI, Script)
  - Configuration YAML détaillée
  - Exemples pratiques pour chaque chapitre (1300+ lignes)
  - Cas d'usage avancés (Production, Multi-PDB, Migration)
  - Section dépannage complète

#### Référence Rapide
- **[📋 Cheat Sheet](docs/reference/CHEAT_SHEET.md)** - Aide-mémoire des commandes essentielles
- **[🔄 Scripts Mapping](docs/guides/SCRIPTS_MAPPING.md)** - Correspondance scripts shell testés ↔️ CLI
- **[📄 Guide Installation](docs/reference/INSTALL.yml)** - Procédures d'installation détaillées

#### Pour Développeurs
- **[🔧 Developer Guide](docs/development/DEVELOPER_GUIDE.md)** - Architecture et contribution
- **[🤝 Contributing](docs/development/CONTRIBUTING.md)** - Comment contribuer

#### Pour Déploiement
- **[🚀 GitHub Publishing Guide](docs/deployment/GITHUB_GUIDE.md)** - Publier sur GitHub/PyPI
- **[📦 PyPI Publishing Guide](docs/deployment/PYPI_GUIDE.md)** - Guide complet pour publier sur PyPI
- **[📦 Package Summary](docs/deployment/PACKAGE_SUMMARY.md)** - Vue d'ensemble technique

> **💡 Scripts de publication automatisés disponibles:**
> - Les scripts `publish.ps1` (Windows) et `publish.sh` (Linux/Mac) sont dans `../deployment-tools/`
> - Voir [docs/deployment/PYPI_GUIDE.md](docs/deployment/PYPI_GUIDE.md) pour les instructions complètes
> - **Note:** Ces scripts ne font PAS partie du package distribué sur PyPI

### 📁 Exemples de Configuration

- [Configuration Production](examples/production-config.yml)
- [Configuration RAC](examples/rac-config.yml)
- [Script de vérification système](examples/system-check.sh)

### 📑 Autres Ressources

- [Changelog](CHANGELOG.md) - Historique des versions

## 🔧 Configuration VM et NFS

### Créer une nouvelle VM pour Oracle

```bash
# Sur la nouvelle VM
oradba vm-init --role database
oradba install --full --config mydb.yml

# Pour un nœud RAC
oradba vm-init --role rac-node --node-number 2
```

### Configuration NFS pour RAC

```bash
# Sur le serveur NFS
oradba nfs --setup-server --export /u01/shared

# Sur les clients RAC
oradba nfs --setup-client --server 192.168.1.10 --mount /u01/shared
```

## 🐳 Docker Support

```bash
# Builder l'image
docker build -t oracledba:latest .

# Lancer un conteneur
docker run -it --name oracle19c oracledba:latest

# Utiliser docker-compose
docker-compose up -d
```

## 🧪 Tests

```bash
# Exécuter les tests
pytest

# Avec couverture
pytest --cov=oracledba

# Tests d'intégration
pytest tests/integration/
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **DBA Formation Team** - *Initial work*

## 🙏 Remerciements

- Oracle Corporation pour la documentation
- Rocky Linux Community
- Tous les contributeurs du projet

## 📞 Support

- 📧 Email: dba@formation.com
- 🐛 Issues: [GitHub Issues](https://github.com/ELMRABET-Abdelali/oracledba/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ELMRABET-Abdelali/oracledba/discussions)

## 📈 Roadmap

- [ ] Support pour Oracle 21c
- [ ] Interface web de monitoring
- [ ] Support Kubernetes
- [ ] Ansible playbooks
- [ ] Terraform modules
- [ ] Support multi-cloud (AWS RDS, Azure, GCP)

---

⭐ Si ce projet vous aide, n'hésitez pas à lui donner une étoile sur GitHub !
