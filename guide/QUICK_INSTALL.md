# 🚀 Installation Rapide OracleDBA

## Installation en UNE Commande

### Sur Rocky Linux 8/9 ou RHEL 8/9

```bash
# 1. Installer Python 3.9 (si pas déjà installé)
sudo dnf module enable python39 -y && sudo dnf install -y python39 python39-pip git

# 2. Cloner et installer
git clone https://github.com/ELMRABET-Abdelali/oracledba.git && cd oracledba && bash install.sh

# 3. Recharger le shell
source ~/.bashrc

# 4. Vérifier
oradba --version
```

## ✅ C'est Tout !

Le script `install.sh` fait **TOUT automatiquement** :
- ✅ Installe/met à jour pip
- ✅ Installe toutes les dépendances
- ✅ Configure le PATH
- ✅ Vérifie que tout fonctionne
- ✅ Donne des instructions claires

## 🎯 Première Utilisation

```bash
# Vérifier les prérequis système
oradba precheck

# Corriger automatiquement les problèmes
oradba precheck --fix
sudo bash fix-precheck-issues.sh

# Générer les fichiers de réponse Oracle
oradba genrsp all

# Installer Oracle 19c
sudo oradba install full \
  --installer-zip /tmp/LINUX.X64_193000_db_home.zip \
  --sid PRODDB

# Tester l'installation
oradba test --report
```

## 🆘 Dépannage

### Si `oradba` n'est pas trouvé

```bash
# Recharger le shell
source ~/.bashrc

# OU utiliser via Python module
python3.9 -m oracledba.cli --version
```

### Si l'installation échoue

```bash
# Réexécuter l'installation
cd oracledba
bash install.sh
```

### Si erreur de modules manquants

```bash
# Le script install.sh corrige automatiquement ce problème
# Il installe psutil et tous les autres modules nécessaires
cd oracledba
bash install.sh
```

## 📚 Documentation Complète

- [Guide d'Installation](docs/INSTALLATION_GUIDE.md)
- [Guide de Tests](TESTING.md)
- [Nouveautés v1.0.0](WHAT_IS_NEW.md)
- [README Principal](README.md)

## ⏱️ Temps d'Installation

- **Installation package**: 2-3 minutes
- **Precheck + corrections**: 3-5 minutes
- **Installation Oracle 19c**: 30-45 minutes
- **TOTAL**: ~40-55 minutes

## 💡 Astuces

### Installation one-liner depuis n'importe où

```bash
curl -fsSL https://raw.githubusercontent.com/ELMRABET-Abdelali/oracledba/main/install.sh | bash
```

### Mise à jour vers la dernière version

```bash
cd oracledba
git pull
bash install.sh
```

### Installation pour un autre utilisateur

```bash
# Le script détecte automatiquement si vous êtes root ou user
# Il adapte l'installation en conséquence
```

## ✅ Test de Validation

Après installation, vérifiez que tout fonctionne :

```bash
# 1. Version
oradba --version
# Résultat attendu: OracleDBA version 1.0.0

# 2. Aide
oradba --help
# Résultat attendu: Liste de 25+ commandes

# 3. Precheck
oradba precheck
# Résultat attendu: Rapport des prérequis système

# 4. Génération fichiers
oradba genrsp all
# Résultat attendu: 3 fichiers .rsp créés dans /tmp/
```

Si tous ces tests passent, **l'installation est réussie** ! 🎉
