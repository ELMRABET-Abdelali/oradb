# 🚀 Guides de Déploiement OracleDBA

Ce dossier contient tous les guides nécessaires pour publier et déployer le package OracleDBA.

---

## 📦 Publication sur PyPI

### Option 1: Scripts Automatisés (Recommandé) ⭐

Le moyen le plus rapide de publier sur PyPI !

**⚠️ Important:** Les scripts de publication sont dans `../deployment-tools/` (en dehors du package).

#### Windows (PowerShell)

```powershell
# Aller dans le dossier deployment-tools
cd ..\deployment-tools

# Publier sur TestPyPI (recommandé d'abord)
.\publish.ps1 test

# Publier sur PyPI Production
.\publish.ps1 prod

# Publier sur Test puis demander confirmation pour Production
.\publish.ps1 both
```

#### Linux/Mac (Bash)

```bash
# Aller dans le dossier deployment-tools
cd ../deployment-tools

# Rendre le script exécutable (première fois seulement)
chmod +x publish.sh

# Publier sur TestPyPI (recommandé d'abord)
./publish.sh test

# Publier sur PyPI Production
./publish.sh prod

# Publier sur Test puis demander confirmation pour Production
./publish.sh both
```

**Ce que fait le script automatiquement:**
- ✅ Vérifie que tous les outils sont installés (python, pip, build, twine)
- ✅ Nettoie les anciens builds (dist/, build/, *.egg-info)
- ✅ Détecte automatiquement la version depuis setup.py
- ✅ Vérifie les fichiers requis (README, LICENSE, etc.)
- ✅ Build le package (source + wheel)
- ✅ Valide avec twine
- ✅ Upload vers TestPyPI ou PyPI avec confirmation
- ✅ Affiche les liens et commandes d'installation

### Option 2: Manuelle (Étape par étape)

Suivez le guide complet : **[PYPI_GUIDE.md](PYPI_GUIDE.md)**

Ce guide de 30+ pages contient:
- 📋 Configuration compte PyPI et API tokens
- 🔧 Installation des outils (build, twine)
- 📦 Building du package
- ✅ Validation et tests
- 🚀 Publication TestPyPI et Production
- 🏷️ Gestion des versions
- 🐛 Troubleshooting complet

---

## 🌐 Publication sur GitHub

### Guide complet: [GITHUB_GUIDE.md](GITHUB_GUIDE.md)

**Repository actuel:** https://github.com/ELMRABET-Abdelali/oracledba

Étapes principales:

```bash
# 1. Initialiser Git (si pas déjà fait)
cd oracledba/
git init

# 2. Ajouter les fichiers
git add .
git commit -m "Initial commit - OracleDBA v1.0.0"

# 3. Connecter au repository GitHub
git remote add origin https://github.com/ELMRABET-Abdelali/oracledba.git
git branch -M main
git push -u origin main

# 4. Créer un tag de version
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## 📊 Vue d'Ensemble du Package

Consultez **[PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md)** pour:
- Architecture complète du package
- Liste de tous les modules et scripts
- Statistiques détaillées (70 fichiers, 5000+ lignes de docs)
- Commandes CLI disponibles
- Configuration YAML

---

## 🎯 Workflow Complet de Publication Recommandé

### 1️⃣ Préparation

```bash
# Vérifier que tous les fichiers sont à jour
git status

# Mettre à jour la version dans setup.py si nécessaire
# Mettre à jour CHANGELOG.md
```

### 2️⃣ Test Local

```bash
# Tester l'installation locale
pip install -e .
oradba --version
oradba --help

# Exécuter les tests (si configurés)
pytest
```

### 3️⃣ Publication Git

```bash
# Committer et pusher
git add .
git commit -m "Your commit message"
git push origin main

# Créer tag (si nouvelle version)
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 4️⃣ Publication PyPI

```bash
# Publier d'abord sur TestPyPI
.\publish.ps1 test      # Windows
./publish.sh test       # Linux/Mac

# Tester l'installation depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ oracledba

# Si OK, publier sur Production
.\publish.ps1 prod      # Windows
./publish.sh prod       # Linux/Mac
```

### 5️⃣ Vérification

- ✅ Vérifier la page PyPI: https://pypi.org/project/oracledba/
- ✅ Tester l'installation: `pip install oracledba`
- ✅ Vérifier GitHub: https://github.com/ELMRABET-Abdelali/oracledba
- ✅ Tester les commandes CLI

---

## 🔐 Configuration PyPI (Première fois)

### 1. Créer un compte PyPI

- **Test:** https://test.pypi.org/account/register/
- **Production:** https://pypi.org/account/register/

### 2. Créer un API Token

1. Aller sur https://pypi.org/manage/account/token/
2. Cliquer "Add API token"
3. Nom: `oracledba-upload`
4. Copier le token (commence par `pypi-...`)

### 3. Configurer `.pypirc`

**Windows:** `C:\Users\VOTRE_USER\.pypirc`  
**Linux/Mac:** `~/.pypirc`

```ini
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
```

**Important:** Ne jamais committer le fichier `.pypirc` (contient des secrets)

---

## 📚 Ressources Additionnelles

- **PyPI Packaging Guide:** https://packaging.python.org/
- **Twine Documentation:** https://twine.readthedocs.io/
- **Semantic Versioning:** https://semver.org/
- **GitHub Actions (CI/CD):** https://docs.github.com/en/actions

---

## 🆘 Support

Des questions sur le déploiement?

- 📖 Lire les guides détaillés dans ce dossier
- 🐛 Créer une issue: https://github.com/ELMRABET-Abdelali/oracledba/issues
- 💬 Discussion: https://github.com/ELMRABET-Abdelali/oracledba/discussions

---

**Bonne publication! 🎉**
