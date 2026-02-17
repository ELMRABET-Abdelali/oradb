# Guide de mise sur GitHub

## 📤 Étapes pour publier sur GitHub

### 1. Créer un repository sur GitHub

1. Allez sur https://github.com
2. Cliquez sur "New repository"
3. Nom: `oracledba`
4. Description: "Complete Oracle Database Administration Package for Oracle 19c"
5. Choisir "Public" ou "Private"
6. **NE PAS** initialiser avec README (nous en avons déjà un)
7. Cliquer "Create repository"

### 2. Initialiser Git localement

```bash
cd /path/to/oracledba

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - OracleDBA v1.0.0"
```

### 3. Connecter au repository GitHub

```bash
# Remplacer 'yourusername' par votre nom d'utilisateur GitHub
git remote add origin https://github.com/ELMRABET-Abdelali/oracledba.git

# Pousser vers GitHub
git branch -M main
git push -u origin main
```

### 4. Créer des tags pour les versions

```bash
# Créer un tag pour v1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

# Pousser les tags
git push origin v1.0.0
```

## 🔑 Utiliser SSH au lieu de HTTPS (Recommandé)

```bash
# Générer une clé SSH si vous n'en avez pas
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copier la clé publique
cat ~/.ssh/id_ed25519.pub

# Ajouter la clé sur GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key

# Changer l'URL remote pour SSH
git remote set-url origin git@github.com:ELMRABET-Abdelali/oracledba.git
```

## 📝 Workflow de développement

### Créer une branche pour un nouveau feature

```bash
# Créer et basculer sur une nouvelle branche
git checkout -b feature/ma-nouvelle-fonctionnalite

# Faire des modifications...

# Ajouter les changements
git add .

# Commiter
git commit -m "Add: nouvelle fonctionnalité"

# Pousser la branche
git push origin feature/ma-nouvelle-fonctionnalite
```

### Créer une Pull Request

1. Aller sur GitHub
2. Cliquer sur "Compare & pull request"
3. Décrire les changements
4. Créer la Pull Request

### Merger dans main

```bash
# Retour sur main
git checkout main

# Merger la branche
git merge feature/ma-nouvelle-fonctionnalite

# Pousser
git push origin main

# Supprimer la branche locale (optionnel)
git branch -d feature/ma-nouvelle-fonctionnalite
```

## 🏷️ Gestion des versions

### Créer une nouvelle release

```bash
# Mettre à jour la version dans setup.py et pyproject.toml

# Commit des changements
git add setup.py pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.1.0"

# Créer un tag
git tag -a v1.1.0 -m "Release v1.1.0 - Description"

# Pousser
git push origin main
git push origin v1.1.0
```

### Sur GitHub

1. Aller dans "Releases"
2. Cliquer "Draft a new release"
3. Choisir le tag (v1.1.0)
4. Titre: "Version 1.1.0"
5. Description: Copier depuis CHANGELOG.md
6. Publier

## 📦 Publier sur PyPI

### Configuration

```bash
# Installer twine
pip install twine

# Créer ~/.pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
EOF
```

### Build et Upload

```bash
# Build
python setup.py sdist bdist_wheel

# Upload vers PyPI
twine upload dist/*

# Ou vers Test PyPI d'abord
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

## 🔒 Fichiers sensibles

### NE JAMAIS commiter

- Mots de passe
- Clés SSH privées
- Fichiers de configuration avec credentials
- Fichiers .env avec secrets

### .gitignore est configuré pour ignorer

- `*config*password*.yml`
- `*config*prod*.yml`
- `secrets.yml`
- `credentials.yml`
- `*.pem`
- `*.key`
- `id_rsa` (sans .pub)

## 📊 README Badges (Optionnel)

Ajouter ces badges au README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/oracledba.svg)](https://badge.fury.io/py/oracledba)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/oracledba)](https://pepy.tech/project/oracledba)
```

## 📚 Documentation avec GitHub Pages

```bash
# Créer une branche gh-pages
git checkout --orphan gh-pages

# Préparer la documentation
mkdir docs
# Ajouter votre documentation HTML

# Commit et push
git add .
git commit -m "Add documentation"
git push origin gh-pages

# Activer GitHub Pages:
# Repository → Settings → Pages → Source: gh-pages branch
```

## 🤝 Collaboration

### Donner accès à d'autres développeurs

1. Repository → Settings → Collaborators
2. Add people
3. Choisir le niveau d'accès

### Protéger la branche main

1. Repository → Settings → Branches
2. Add rule
3. Branch name pattern: `main`
4. Activer:
   - Require pull request reviews before merging
   - Require status checks to pass

## 🔄 Synchroniser avec upstream (si fork)

```bash
# Ajouter upstream
git remote add upstream https://github.com/original/oracledba.git

# Récupérer les changements
git fetch upstream

# Merger dans main
git checkout main
git merge upstream/main
git push origin main
```

## 📈 GitHub Actions (CI/CD)

Créer `.github/workflows/tests.yml`:

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
        pip install -e .[dev]
    - name: Run tests
      run: |
        pytest
```

## 📞 Support et Communication

### GitHub Issues

Les utilisateurs peuvent ouvrir des issues pour:
- Bugs
- Feature requests
- Questions
- Documentation

### GitHub Discussions

Activer pour:
- Questions générales
- Annonces
- Idées
- Show and tell

## ✅ Checklist finale avant publication

- [ ] README.md complet et clair
- [ ] LICENSE présent
- [ ] CHANGELOG.md à jour
- [ ] .gitignore configuré
- [ ] Pas de fichiers sensibles
- [ ] setup.py et pyproject.toml corrects
- [ ] Requirements.txt complet
- [ ] Tests passent (si applicable)
- [ ] Documentation claire
- [ ] Exemples de configuration
- [ ] CONTRIBUTING.md présent

## 🎉 Publication

```bash
# Vérification finale
git status
git log --oneline -5

# Pousser vers GitHub
git push origin main
git push --tags

# Annoncer sur les réseaux sociaux, forums DBA, etc.
```

---

**Votre package est maintenant sur GitHub et prêt à être utilisé par la communauté DBA!** 🚀
