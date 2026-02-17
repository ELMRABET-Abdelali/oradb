# 📦 Guide de Publication sur PyPI

Guide complet pour publier le package **oracledba** sur PyPI afin que les utilisateurs puissent l'installer avec `pip install oracledba`.

---

## 📋 Prérequis

### 1. Créer un compte PyPI

1. **Compte de Test (Recommandé pour commencer):**
   - Allez sur https://test.pypi.org/account/register/
   - Créez un compte (email, username, password)
   - Vérifiez votre email

2. **Compte Production:**
   - Allez sur https://pypi.org/account/register/
   - Créez un compte (même process)
   - Vérifiez votre email

### 2. Installer les outils nécessaires

```bash
# Installer les outils de build et publication
pip install --upgrade pip
pip install --upgrade build twine

# Vérifier l'installation
python -m build --version
twine --version
```

### 3. Configurer l'authentification PyPI

#### Option A: API Token (Recommandé)

1. **Créer un token sur PyPI:**
   - PyPI Test: https://test.pypi.org/manage/account/token/
   - PyPI Prod: https://pypi.org/manage/account/token/
   - Cliquez sur "Add API token"
   - Nom du token: `oracledba-upload`
   - Copiez le token (commence par `pypi-...`)

2. **Configurer le fichier `~/.pypirc`:**

```bash
# Créer le fichier de configuration
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-VOTRE_TOKEN_PRODUCTION_ICI

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-VOTRE_TOKEN_TEST_ICI
EOF

# Sécuriser le fichier
chmod 600 ~/.pypirc
```

#### Option B: Username/Password (Non recommandé)

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = votre_username_pypi
password = votre_password_pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = votre_username_test
password = votre_password_test
EOF

chmod 600 ~/.pypirc
```

---

## 🚀 Publication Étape par Étape

### Étape 1: Vérifier le package

```bash
cd c:\Users\DELL\Desktop\DBA\dbadministration\digitalocean-setup\oracledba

# Vérifier que tous les fichiers nécessaires sont présents
ls -la

# Fichiers requis:
# ✅ setup.py
# ✅ pyproject.toml
# ✅ README.md
# ✅ LICENSE
# ✅ MANIFEST.in
# ✅ requirements.txt
```

### Étape 2: Nettoyer les anciens builds

```bash
# Supprimer les anciens builds (si existants)
rm -rf dist/ build/ *.egg-info

# Sur Windows PowerShell:
# Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

### Étape 3: Vérifier setup.py

Assurez-vous que [setup.py](../../setup.py) contient les bonnes informations:

```python
setup(
    name="oracledba",  # Nom du package sur PyPI
    version="1.0.0",   # Version initiale
    author="DBA Formation Team",
    author_email="dba@formation.com",
    description="Complete Oracle 19c DBA package with installation, backup, tuning, ASM, RAC and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ELMRABET-Abdelali/oracledba",
    # ... rest of config
)
```

### Étape 4: Builder le package

```bash
# Créer les distributions (source + wheel)
python -m build

# Cela créera:
# dist/oracledba-1.0.0.tar.gz       (distribution source)
# dist/oracledba-1.0.0-py3-none-any.whl  (wheel pour installation rapide)
```

**Sortie attendue:**
```
Successfully built oracledba-1.0.0.tar.gz and oracledba-1.0.0-py3-none-any.whl
```

### Étape 5: Vérifier le package

```bash
# Vérifier que les distributions sont correctes
twine check dist/*

# Sortie attendue:
# Checking dist/oracledba-1.0.0.tar.gz: PASSED
# Checking dist/oracledba-1.0.0-py3-none-any.whl: PASSED
```

### Étape 6: Test sur TestPyPI (Recommandé)

```bash
# Upload sur TestPyPI d'abord
twine upload --repository testpypi dist/*

# Entrez votre username/password si demandé (ou utilise ~/.pypirc)
```

**Sortie attendue:**
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading oracledba-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
Uploading oracledba-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 

View at:
https://test.pypi.org/project/oracledba/1.0.0/
```

### Étape 7: Tester l'installation depuis TestPyPI

```bash
# Créer un environnement de test
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Installer depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ oracledba

# Tester la commande
oradba --version
oradba --help

# Si tout fonctionne, désactiver l'environnement
deactivate
rm -rf test_env
```

### Étape 8: Publication sur PyPI Production 🎉

**⚠️ ATTENTION: Une fois publié sur PyPI, vous ne pouvez PAS:**
- Supprimer une version
- Re-uploader la même version
- Modifier le contenu d'une version

```bash
# Upload sur PyPI PRODUCTION
twine upload dist/*
```

**Sortie attendue:**
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading oracledba-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
Uploading oracledba-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 

View at:
https://pypi.org/project/oracledba/1.0.0/
```

### Étape 9: Vérifier sur PyPI

1. **Visitez la page du package:**
   - https://pypi.org/project/oracledba/

2. **Vérifiez que tout est correct:**
   - ✅ README s'affiche correctement
   - ✅ Version correcte
   - ✅ Liens GitHub fonctionnels
   - ✅ Metadata correcte

### Étape 10: Tester l'installation finale

```bash
# Créer un nouvel environnement propre
python -m venv final_test
source final_test/bin/activate  # Windows: final_test\Scripts\activate

# Installer depuis PyPI PRODUCTION
pip install oracledba

# Tester toutes les commandes
oradba --version
oradba --help
oradba system check

# Désactiver
deactivate
rm -rf final_test
```

---

## 🏷️ Publier une nouvelle version

Quand vous voulez publier une mise à jour:

### 1. Mettre à jour le numéro de version

**Dans [setup.py](../../setup.py):**
```python
setup(
    name="oracledba",
    version="1.0.1",  # Incrémenter la version
    # ...
)
```

**Dans [CHANGELOG.md](../../CHANGELOG.md):**
```markdown
## [1.0.1] - 2026-02-XX

### Added
- Nouvelle fonctionnalité X

### Fixed
- Bug Y corrigé
```

### 2. Committer les changements

```bash
git add setup.py CHANGELOG.md
git commit -m "Bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags
```

### 3. Rebuilder et republier

```bash
# Nettoyer
rm -rf dist/ build/ *.egg-info

# Builder
python -m build

# Vérifier
twine check dist/*

# Uploader
twine upload dist/*
```

---

## 📊 Badge PyPI dans README

Ajoutez ces badges dans [README.md](../../README.md) pour montrer la version:

```markdown
[![PyPI version](https://badge.fury.io/py/oracledba.svg)](https://badge.fury.io/py/oracledba)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oracledba.svg)](https://pypi.org/project/oracledba/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/oracledba.svg)](https://pypi.org/project/oracledba/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## 🔍 Résolution de problèmes

### Erreur: "Invalid or non-existent authentication"

```bash
# Vérifier le fichier .pypirc
cat ~/.pypirc

# Recréer le token sur PyPI et mettre à jour le fichier
```

### Erreur: "File already exists"

Vous essayez de re-uploader la même version. Solutions:
1. Incrémenter la version dans setup.py
2. Rebuilder avec `python -m build`
3. Uploader la nouvelle version

### Erreur: "Package name already taken"

Le nom `oracledba` est déjà pris. Solutions:
1. Choisir un autre nom (ex: `oracledba-automation`)
2. Changer dans setup.py: `name="oracledba-automation"`
3. Les utilisateurs installeront avec: `pip install oracledba-automation`

### Erreur lors du build

```bash
# Mettre à jour les outils
pip install --upgrade setuptools wheel build twine

# Vérifier que setup.py est correct
python setup.py check
```

---

## 📝 Checklist Publication

Avant de publier sur PyPI Production:

- [ ] ✅ setup.py vérifié (version, URLs, metadata)
- [ ] ✅ README.md à jour et formaté en Markdown
- [ ] ✅ LICENSE présent (MIT)
- [ ] ✅ CHANGELOG.md à jour
- [ ] ✅ Tests passent (`pytest` si configuré)
- [ ] ✅ Tous les scripts sont inclus dans MANIFEST.in
- [ ] ✅ Build réussi (`python -m build`)
- [ ] ✅ Vérification réussie (`twine check dist/*`)
- [ ] ✅ Test sur TestPyPI réussi
- [ ] ✅ Installation test réussie
- [ ] ✅ Commit et tag Git créés
- [ ] ✅ Push vers GitHub effectué

---

## 🎯 Commandes Rapides

```bash
# Workflow complet
cd oracledba/
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test d'abord
# Si OK:
twine upload dist/*  # Production
```

---

## 📚 Ressources

- **PyPI:** https://pypi.org/
- **Test PyPI:** https://test.pypi.org/
- **Documentation officielle:** https://packaging.python.org/
- **Twine docs:** https://twine.readthedocs.io/
- **Guide complet:** https://packaging.python.org/tutorials/packaging-projects/

---

## 💡 Conseils

1. **Toujours tester sur TestPyPI d'abord**
2. **Utiliser des tokens API au lieu de passwords**
3. **Suivre le versioning sémantique:** MAJOR.MINOR.PATCH
4. **Documenter chaque version dans CHANGELOG.md**
5. **Créer des tags Git pour chaque version**
6. **Ne jamais committer le fichier .pypirc** (contient secrets)

---

**Prêt à publier? Suivez les étapes ci-dessus!** 🚀

**Questions? Créez une issue sur:** https://github.com/ELMRABET-Abdelali/oracledba/issues
