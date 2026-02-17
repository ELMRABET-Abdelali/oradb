# 🧪 Tests pour OracleDBA Package

Ce fichier contient des tests unitaires et d'intégration pour le package OracleDBA.

## Structure des Tests

```
tests/
├── test_precheck.py      # Tests pré-installation
├── test_install.py       # Tests installation
├── test_response_files.py # Tests response files
├── test_downloader.py    # Tests téléchargement
├── test_testing.py       # Tests du système de test
├── test_rman.py          # Tests RMAN
├── test_database.py      # Tests database
└── conftest.py           # Configuration pytest
```

## Exécuter les Tests

```bash
# Installer les dépendances de dev
pip install -e ".[dev]"

# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=oracledba --cov-report=html

# Tests spécifiques
pytest tests/test_precheck.py
pytest tests/test_install.py -v

# Tests avec sortie détaillée
pytest -vv -s
```

## Tests Disponibles

### Test Pre-Check

```bash
pytest tests/test_precheck.py -v
```

Tests:
- ✓ Vérification OS
- ✓ Vérification RAM/SWAP
- ✓ Vérification packages
- ✓ Vérification kernel parameters
- ✓ Génération script de correction

### Test Installation

```bash
pytest tests/test_install.py -v
```

Tests:
- ✓ Chargement configuration
- ✓ Vérification scripts
- ✓ Préparation système
- ✓ Installation binaires
- ✓ Création database

### Test Response Files

```bash
pytest tests/test_response_files.py -v
```

Tests:
- ✓ Génération DB_INSTALL.rsp
- ✓ Génération DBCA.rsp
- ✓ Génération NETCA.rsp
- ✓ Validation contenu
- ✓ Configuration personnalisée

### Test Downloader

```bash
pytest tests/test_downloader.py -v
```

Tests:
- ✓ Téléchargement depuis URL
- ✓ Vérification MD5
- ✓ Extraction ZIP
- ✓ Gestion erreurs

### Test Testing Suite

```bash
pytest tests/test_testing.py -v
```

Tests:
- ✓ Tests environnement
- ✓ Tests binaires
- ✓ Tests listener
- ✓ Tests database
- ✓ Génération rapport

## Tests Manuels sur VM

### Test 1: Installation Fresh

```bash
# Sur VM vierge Rocky Linux 8
ssh root@YOUR_VM_IP

# Installer package
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba
pip3 install -e .

# Test precheck
oradba precheck --fix
bash fix-precheck-issues.sh
oradba precheck  # Doit passer

# Test download
oradba download database
# Placer le fichier manuellement

# Test installation
oradba install system
oradba vm-init --role database
# Note: Installation complète nécessite binaires Oracle
```

### Test 2: Response Files

```bash
# Générer response files
oradba genrsp all --output-dir /tmp

# Vérifier contenu
cat /tmp/db_install.rsp
cat /tmp/dbca.rsp
cat /tmp/netca.rsp

# Valider avec Oracle
$ORACLE_HOME/runInstaller -silent -responseFile /tmp/db_install.rsp -ignorePrereq
```

### Test 3: Tests Post-Installation

```bash
# Après installation complète Oracle
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD

# Lancer tests
oradba test --report

# Vérifier rapport
cat oracle-test-report.txt
```

## Tests d'Intégration Continue (CI/CD)

### GitHub Actions

Créer `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest --cov=oracledba
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Métriques de Qualité

### Couverture de Code

Objectif: > 80% de couverture

```bash
pytest --cov=oracledba --cov-report=term-missing
```

### Linting et Style

```bash
# Flake8 (PEP8)
flake8 oracledba/ --max-line-length=120

# Black (formatage)
black oracledba/ --check

# MyPy (type checking)
mypy oracledba/
```

### Tests de Performance

```bash
# Temps d'exécution
time oradba precheck
time oradba test

# Profiling
python -m cProfile -o profile.stats oradba/cli.py precheck
```

## Résultats Attendus

### Precheck

```
✓ All checks passed!
System is ready for Oracle 19c installation.
```

### Test Suite

```
Summary: 11/11 tests passed
✓ All tests passed!
Oracle 19c is fully operational.
```

### Coverage

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
oracledba/__init__.py                 3      0   100%
oracledba/cli.py                    145     12    92%
oracledba/modules/precheck.py       198     15    92%
oracledba/modules/testing.py        235     18    92%
oracledba/modules/install.py        126     10    92%
-----------------------------------------------------
TOTAL                              1245    102    92%
```

## Dépannage Tests

### Problème: Tests échouent sur VM

```bash
# Installer dépendances manquantes
pip install pytest pytest-cov pytest-mock

# Vérifier Python version
python3 --version  # Doit être >= 3.8

# Exécuter en mode verbose
pytest -vv -s
```

### Problème: Import errors

```bash
# Installer en mode editable
pip install -e .

# Vérifier PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

### Problème: Tests permissions

```bash
# Certains tests nécessitent root
sudo pytest tests/test_precheck.py
```

## Contribution

Pour ajouter des tests:

1. Créer fichier `tests/test_nouvelle_fonction.py`
2. Importer pytest et le module à tester
3. Écrire fonctions `test_*`
4. Exécuter `pytest` pour valider
5. Vérifier couverture avec `pytest --cov`

Exemple:

```python
# tests/test_nouvelle_fonction.py
import pytest
from oracledba.modules import nouvelle_fonction

def test_basic_functionality():
    result = nouvelle_fonction.ma_fonction()
    assert result == expected_value

def test_error_handling():
    with pytest.raises(ValueError):
        nouvelle_fonction.ma_fonction(bad_input)
```

## Checklist Avant Release

- [ ] Tous les tests passent
- [ ] Couverture > 80%
- [ ] Flake8 sans erreurs
- [ ] Documentation à jour
- [ ] Tests manuels sur VM OK
- [ ] Performance acceptable
- [ ] Changelog mis à jour

---

**Pour plus d'informations:** Voir [CONTRIBUTING.md](CONTRIBUTING.md)
