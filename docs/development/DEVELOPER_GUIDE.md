# 🔧 Guide du Développeur - OracleDBA

Guide technique pour comprendre l'architecture, contribuer et personnaliser le package oracledba.

---

## 📁 Structure du Projet

```
oracledba/
│
├── oracledba/                          # Package Python principal
│   ├── __init__.py                     # Version et exports
│   ├── cli.py                          # CLI principale (850+ lignes)
│   ├── setup_wizard.py                 # Wizard interactif d'installation
│   │
│   ├── modules/                        # Modules fonctionnels
│   │   ├── __init__.py
│   │   ├── install.py                  # Installation Oracle (TP01-03)
│   │   ├── rman.py                     # RMAN Backup/Recovery (TP08)
│   │   ├── dataguard.py                # Data Guard (TP09)
│   │   ├── tuning.py                   # Performance Tuning (TP10)
│   │   ├── asm.py                      # ASM Management (TP15)
│   │   ├── rac.py                      # RAC Management (TP15)
│   │   ├── pdb.py                      # Multitenant CDB/PDB (TP12)
│   │   ├── flashback.py                # Flashback (TP07)
│   │   ├── security.py                 # Security (TP06)
│   │   ├── nfs.py                      # NFS Server/Client
│   │   └── database.py                 # Core DB operations
│   │
│   ├── utils/                          # Utilitaires
│   │   ├── __init__.py
│   │   ├── logger.py                   # Logging structuré (Rich)
│   │   └── oracle_client.py            # Wrapper cx_Oracle
│   │
│   ├── scripts/                        # Scripts shell/SQL testés
│   │   ├── tp01-system-readiness.sh    # Rocky Linux 8 preparation
│   │   ├── tp02-installation-binaire.sh
│   │   ├── tp03-creation-instance.sh
│   │   └── ... (TP04-TP15)
│   │
│   └── configs/                        # Configurations
│       └── default-config.yml          # Template configuration
│
├── examples/                           # Exemples d'utilisation
│   ├── production-config.yml           # Config production
│   ├── rac-config.yml                  # Config RAC
│   └── system-check.sh                 # Vérification système
│
├── tests/                              # Tests unitaires
│   ├── test_install.py
│   ├── test_rman.py
│   └── ...
│
├── docs/                               # Documentation
│   ├── GUIDE_UTILISATION.md            # Guide utilisateur complet
│   ├── SCRIPTS_MAPPING.md              # Mapping scripts ↔️ CLI
│   └── DEVELOPER_GUIDE.md              # Ce fichier
│
├── setup.py                            # Configuration package Python
├── pyproject.toml                      # Configuration moderne Python
├── requirements.txt                    # Dépendances
├── Makefile                            # Commandes de développement
├── MANIFEST.in                         # Fichiers à inclure dans package
└── README.md                           # Documentation principale
```

---

## 🏗️ Architecture Technique

### Pattern: Manager Classes

Chaque module suit le pattern **Manager**:

```python
# Exemple: oracledba/modules/rman.py

class RMANManager:
    """Gestion des opérations RMAN"""
    
    def __init__(self, config_path=None):
        """Initialisation avec config YAML optionnelle"""
        self.config = self._load_config(config_path)
        self.logger = logger.get_logger(__name__)
    
    def setup(self, retention_days=7, compression=True):
        """Configure RMAN (appelle script TP08)"""
        # 1. Valider environnement Oracle
        # 2. Générer commandes RMAN
        # 3. Exécuter via subprocess
        # 4. Logger résultats
    
    def backup(self, backup_type='full', tag=None):
        """Exécute backup RMAN"""
        # Appelle script shell ou génère RMAN script
    
    def restore(self, point_in_time=None):
        """Restaure base de données"""
        # Logique de restauration
```

**Avantages:**
- ✅ Séparation des responsabilités
- ✅ Réutilisable (import RMANManager)
- ✅ Testable unitairement
- ✅ Configuration centralisée

### Pattern: CLI Commands (Click)

Le CLI utilise **Click** pour structure hiérarchique:

```python
# oracledba/cli.py

import click

@click.group()
def main():
    """CLI principal oradba"""
    pass

# Groupe RMAN
@main.group()
def rman():
    """💾 RMAN Backup and Recovery"""
    pass

@rman.command('backup')
@click.option('--type', type=click.Choice(['full', 'incremental', 'archive']))
@click.option('--tag', help='Backup tag')
def rman_backup(type, tag):
    """Perform RMAN backup"""
    from .modules.rman import RMANManager
    mgr = RMANManager()
    mgr.backup(type, tag)
```

**Structure CLI:**
```
oradba
├── install
│   ├── full
│   ├── system
│   ├── binaries
│   └── database
├── rman
│   ├── setup
│   ├── backup
│   ├── restore
│   └── list-backups
├── dataguard
│   ├── setup-primary
│   ├── create-standby
│   ├── start-apply
│   └── status
└── ... (autres groupes)
```

### Pattern: Script Execution

Les scripts shell testés sont appelés via `subprocess`:

```python
import subprocess
from pathlib import Path

class ScriptExecutor:
    """Exécute scripts shell avec gestion d'erreurs"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent / "scripts"
    
    def run_script(self, script_name, args=None):
        """Execute shell script"""
        script_path = self.script_dir / script_name
        
        cmd = [str(script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Script failed: {result.stderr}")
        
        return result.stdout
```

### Pattern: Configuration YAML

Configuration centralisée avec PyYAML:

```python
import yaml
from pathlib import Path

class Config:
    """Gestion configuration YAML"""
    
    def __init__(self, config_path=None):
        if config_path:
            self.data = self._load_yaml(config_path)
        else:
            # Charger configuration par défaut
            default_config = Path(__file__).parent / "configs" / "default-config.yml"
            self.data = self._load_yaml(default_config)
    
    def _load_yaml(self, path):
        with open(path) as f:
            return yaml.safe_load(f)
    
    def get(self, key, default=None):
        """Get config value with dot notation: system.min_ram_gb"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            value = value.get(k, default)
            if value is None:
                return default
        return value
```

---

## 🔨 Développement Local

### Setup Environnement

```bash
# 1. Cloner repository
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba

# 2. Créer virtualenv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
.\venv\Scripts\activate  # Windows

# 3. Installer en mode développement
pip install -e .[dev]

# 4. Installer pre-commit hooks
pre-commit install
```

### Commandes Makefile

```bash
# Installer dépendances
make install

# Lancer tests
make test

# Lancer tests avec couverture
make test-coverage

# Linter (flake8, black)
make lint

# Formater code
make format

# Build package
make build

# Nettoyer fichiers temporaires
make clean

# Générer documentation
make docs
```

### Tests Unitaires

```python
# tests/test_rman.py

import pytest
from oracledba.modules.rman import RMANManager

@pytest.fixture
def rman_manager():
    """Fixture: RMANManager avec config test"""
    return RMANManager(config_path="tests/fixtures/test-config.yml")

def test_rman_setup(rman_manager):
    """Test configuration RMAN"""
    result = rman_manager.setup(retention_days=7, compression=True)
    assert result.success is True
    assert "CONFIGURE RETENTION POLICY" in result.output

def test_rman_backup_full(rman_manager):
    """Test backup full"""
    result = rman_manager.backup(backup_type='full')
    assert result.success is True
    assert "BACKUP INCREMENTAL LEVEL 0" in result.commands_executed
```

### Tests d'Intégration

```python
# tests/integration/test_full_install.py

import pytest
from oracledba.modules.install import InstallManager

@pytest.mark.integration
@pytest.mark.slow
def test_full_installation():
    """Test installation complète (TP01+TP02+TP03)"""
    mgr = InstallManager(config_path="tests/fixtures/integration-config.yml")
    
    # TP01: System preparation
    result_system = mgr.install_system()
    assert result_system.success is True
    
    # TP02: Binaries
    result_binaries = mgr.install_binaries()
    assert result_binaries.success is True
    
    # TP03: Database
    result_db = mgr.create_database()
    assert result_db.success is True
```

---

## 🎨 Style Guide

### Code Python

Suivre **PEP 8** avec quelques ajustements:

```python
# Imports groupés
import os
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console

from oracledba.modules import install
from oracledba.utils import logger

# Classes: PascalCase
class RMANManager:
    pass

# Fonctions/méthodes: snake_case
def install_oracle_database():
    pass

# Constantes: UPPER_CASE
DEFAULT_ORACLE_HOME = "/u01/app/oracle/product/19.3.0/dbhome_1"

# Private methods: _prefixed
def _load_config(self, path):
    pass

# Docstrings: Google style
def backup(self, backup_type='full', tag=None):
    """Execute RMAN backup.
    
    Args:
        backup_type (str): Type of backup (full, incremental, archive)
        tag (str, optional): Backup tag for identification
    
    Returns:
        BackupResult: Result object with status and output
    
    Raises:
        RMANError: If backup fails
    """
    pass
```

### Configuration YAML

```yaml
# Utiliser 2 espaces pour indentation
# Commenter chaque section
# Groupe logique avec séparateurs

# ============================================================================
# SYSTEM CONFIGURATION
# ============================================================================
system:
  os: "Rocky Linux 8"
  min_ram_gb: 4
  min_disk_gb: 50

# ============================================================================
# ORACLE INSTALLATION
# ============================================================================
oracle:
  version: "19.3.0.0.0"
  edition: "EE"
```

### Scripts Shell

```bash
#!/bin/bash
# Description: Brief description
# Author: Your Name
# Date: 2026-02-16

set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Exit on pipe failure

# Constants (UPPER_CASE)
readonly ORACLE_HOME="/u01/app/oracle/product/19.3.0/dbhome_1"
readonly LOG_FILE="/tmp/script.log"

# Functions (lowercase)
function check_prerequisites() {
    echo "[INFO] Checking prerequisites..."
    # Implementation
}

function main() {
    echo "================================================"
    echo "  Script Name - Description"
    echo "  $(date)"
    echo "================================================"
    
    check_prerequisites
    # Main logic
}

# Execute
main "$@"
```

---

## 🔄 Workflow de Contribution

### 1. Fork et Clone

```bash
# Fork sur GitHub
# Puis clone local
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba
git remote add upstream https://github.com/ELMRABET-Abdelali/oracledba.git
```

### 2. Créer Branche Feature

```bash
# Sync avec upstream
git fetch upstream
git checkout main
git merge upstream/main

# Créer branche
git checkout -b feature/add-datapump-module
```

### 3. Développer avec Tests

```bash
# Créer module
touch oracledba/modules/datapump.py

# Créer tests
touch tests/test_datapump.py

# Développer...
# Tester localement
make test

# Formater code
make format
```

### 4. Commit et Push

```bash
# Commit avec message conventionnel
git add .
git commit -m "feat(datapump): add export/import functionality

- Add DataPumpManager class
- Implement export_schema, import_schema methods
- Add tests
- Update documentation

Closes #42"

# Push
git push origin feature/add-datapump-module
```

### 5. Pull Request

1. Ouvrir PR sur GitHub
2. Remplir template PR
3. Attendre review
4. Corriger si commentaires
5. Merge après approbation

---

## 📝 Convention Commit Messages

Format: `<type>(<scope>): <description>`

**Types:**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction bug
- `docs`: Documentation
- `style`: Formatage
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

**Exemples:**
```
feat(rman): add incremental backup level 2
fix(dataguard): correct switchover command syntax
docs(guide): add examples for TP10 tuning
refactor(install): simplify system preparation logic
test(pdb): add unit tests for clone operation
```

---

## 🧩 Ajouter un Nouveau Module

### Exemple: Module Data Pump

**1. Créer fichier module:**

```python
# oracledba/modules/datapump.py

import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

class DataPumpManager:
    """Oracle Data Pump Export/Import management"""
    
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.oracle_home = self.config.get('oracle.oracle_home')
    
    def export_schema(self, schema, dumpfile, directory='/backup'):
        """Export schema with expdp"""
        console.print(f"[bold blue]Exporting schema {schema}...[/bold blue]")
        
        cmd = [
            f"{self.oracle_home}/bin/expdp",
            f"system/{self.config.get('database.system_password')}",
            f"DIRECTORY=BACKUP_DIR",
            f"DUMPFILE={dumpfile}",
            f"SCHEMAS={schema}",
            "COMPRESSION=ALL"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✓ Export completed[/green]")
            return True
        else:
            console.print(f"[red]✗ Export failed: {result.stderr}[/red]")
            return False
    
    def import_schema(self, dumpfile, schema, directory='/backup'):
        """Import schema with impdp"""
        console.print(f"[bold blue]Importing schema {schema}...[/bold blue]")
        
        cmd = [
            f"{self.oracle_home}/bin/impdp",
            f"system/{self.config.get('database.system_password')}",
            f"DIRECTORY=BACKUP_DIR",
            f"DUMPFILE={dumpfile}",
            f"SCHEMAS={schema}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("[green]✓ Import completed[/green]")
            return True
        else:
            console.print(f"[red]✗ Import failed: {result.stderr}[/red]")
            return False
    
    def _load_config(self, config_path):
        # Config loading logic
        pass
```

**2. Ajouter commandes CLI:**

```python
# Dans oracledba/cli.py

@main.group()
def datapump():
    """📦 Data Pump Export/Import"""
    pass

@datapump.command('export')
@click.option('--schema', required=True, help='Schema name')
@click.option('--file', required=True, help='Dump file name')
@click.option('--dir', default='/backup', help='Directory path')
def datapump_export(schema, file, dir):
    """Export schema with Data Pump"""
    from .modules.datapump import DataPumpManager
    mgr = DataPumpManager()
    mgr.export_schema(schema, file, dir)

@datapump.command('import')
@click.option('--schema', required=True, help='Schema name')
@click.option('--file', required=True, help='Dump file name')
@click.option('--dir', default='/backup', help='Directory path')
def datapump_import(schema, file, dir):
    """Import schema with Data Pump"""
    from .modules.datapump import DataPumpManager
    mgr = DataPumpManager()
    mgr.import_schema(file, schema, dir)
```

**3. Créer tests:**

```python
# tests/test_datapump.py

import pytest
from oracledba.modules.datapump import DataPumpManager

@pytest.fixture
def datapump_manager():
    return DataPumpManager(config_path="tests/fixtures/test-config.yml")

def test_export_schema(datapump_manager, mocker):
    """Test export schema"""
    mock_subprocess = mocker.patch('subprocess.run')
    mock_subprocess.return_value.returncode = 0
    
    result = datapump_manager.export_schema('TEST_SCHEMA', 'test.dmp')
    
    assert result is True
    assert mock_subprocess.called

def test_import_schema(datapump_manager, mocker):
    """Test import schema"""
    mock_subprocess = mocker.patch('subprocess.run')
    mock_subprocess.return_value.returncode = 0
    
    result = datapump_manager.import_schema('test.dmp', 'TEST_SCHEMA')
    
    assert result is True
```

**4. Documenter:**

Ajouter section dans `GUIDE_UTILISATION.md`:

```markdown
### TP14: Data Pump

#### Utilisation Commandes CLI

\```bash
# Export schema
oradba datapump export --schema GDC_ADMIN --file gdc_admin.dmp

# Import schema
oradba datapump import --schema GDC_ADMIN --file gdc_admin.dmp
\```
```

---

## 🐛 Debug et Troubleshooting

### Activer Logs Détaillés

```bash
# Variable d'environnement
export ORADBA_LOG_LEVEL=DEBUG

# Ou dans code
import logging
logging.getLogger('oracledba').setLevel(logging.DEBUG)
```

### Tracer Exécution Scripts

```python
# oracledba/utils/script_executor.py

import subprocess
from rich.console import Console

console = Console()

def run_script_with_trace(script_path):
    """Execute with full tracing"""
    console.print(f"[yellow]Executing: {script_path}[/yellow]")
    
    result = subprocess.run(
        [script_path],
        capture_output=True,
        text=True,
        check=False
    )
    
    console.print("[cyan]STDOUT:[/cyan]")
    console.print(result.stdout)
    
    if result.stderr:
        console.print("[red]STDERR:[/red]")
        console.print(result.stderr)
    
    return result
```

---

## 📚 Ressources

### Documentation Oracle

- [Oracle 19c Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/)
- [RMAN Documentation](https://docs.oracle.com/en/database/oracle/oracle-database/19/bradv/)
- [Data Guard Concepts](https://docs.oracle.com/en/database/oracle/oracle-database/19/sbydb/)

### Python

- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Console](https://rich.readthedocs.io/)
- [PyYAML](https://pyyaml.org/)
- [pytest](https://docs.pytest.org/)

### Tools

- [pre-commit](https://pre-commit.com/)
- [black](https://black.readthedocs.io/)
- [flake8](https://flake8.pycqa.org/)

---

## 🤝 Questions ?

- 💬 GitHub Discussions: https://github.com/ELMRABET-Abdelali/oracledba/discussions
- 🐛 GitHub Issues: https://github.com/ELMRABET-Abdelali/oracledba/issues
- 📧 Email: dba@formation.com

---

**Bon développement ! 🚀**
