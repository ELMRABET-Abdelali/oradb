# 📚 Documentation OracleDBA

Documentation complète pour l'installation, la configuration et la gestion d'Oracle Database 19c sur Rocky Linux 8/9.

---

## 🎯 Par Où Commencer ?

### 👨‍🎓 Pour les Débutants
1. **[Quick Start Guide](guides/QUICKSTART.md)** - Démarrage rapide en 15 minutes
2. **[Guide d'Utilisation Complet](guides/GUIDE_UTILISATION.md)** - Tous les TPs avec exemples détaillés
3. **[Scripts Mapping](guides/SCRIPTS_MAPPING.md)** - Comprendre la correspondance scripts shell ↔️ CLI

### 👨‍💼 Pour les Administrateurs
1. **[Cheat Sheet](reference/CHEAT_SHEET.md)** - Aide-mémoire des commandes essentielles
2. **[Guide d'Installation](reference/INSTALL.yml)** - Procédures d'installation détaillées
3. **[Guide d'Utilisation](guides/GUIDE_UTILISATION.md)** - Exemples pratiques TP01-TP15

### 👨‍💻 Pour les Développeurs
1. **[Developer Guide](development/DEVELOPER_GUIDE.md)** - Architecture et contribution
2. **[Contributing Guidelines](development/CONTRIBUTING.md)** - Comment contribuer
3. **[Package Summary](deployment/PACKAGE_SUMMARY.md)** - Vue d'ensemble technique

### 🚀 Pour le Déploiement
1. **[GitHub Publishing Guide](deployment/GITHUB_GUIDE.md)** - Publier sur GitHub/PyPI
2. **[Package Summary](deployment/PACKAGE_SUMMARY.md)** - Informations de distribution

---

## 📁 Structure de la Documentation

```
docs/
│
├── guides/                          # Guides d'utilisation
│   ├── GUIDE_UTILISATION.md         # Guide complet (1300+ lignes)
│   ├── QUICKSTART.md                # Démarrage rapide
│   └── SCRIPTS_MAPPING.md           # Scripts shell ↔️ CLI
│
├── reference/                       # Documentation de référence
│   ├── CHEAT_SHEET.md              # Aide-mémoire commandes
│   └── INSTALL.yml                 # Guide installation YAML
│
├── development/                     # Pour développeurs
│   ├── DEVELOPER_GUIDE.md          # Architecture et patterns
│   └── CONTRIBUTING.md             # Guidelines contribution
│
└── deployment/                      # Déploiement et distribution
    ├── GITHUB_GUIDE.md             # Publication GitHub/PyPI
    └── PACKAGE_SUMMARY.md          # Résumé package
```

---

## 📖 Guides Détaillés

### 🎓 Guides d'Utilisation

#### [Guide d'Utilisation Complet](guides/GUIDE_UTILISATION.md)
Guide principal de 1300+ lignes couvrant:
- ✅ 3 méthodes d'installation (GitHub, PyPI, Script)
- ✅ Configuration YAML détaillée
- ✅ **15 chapitres (TP01-TP15)** avec exemples pratiques:
  - TP01: Préparation Système
  - TP02: Installation Binaires
  - TP03: Création Instance
  - TP04: Multiplexage Fichiers Critiques
  - TP05: Gestion Stockage
  - TP06: Sécurité et Accès
  - TP07: Flashback
  - TP08: RMAN Backup
  - TP09: Data Guard
  - TP10: Performance Tuning
  - TP11: Patching
  - TP12: Multi-tenant
  - TP13: AI Foundations
  - TP14: Mobilité et Concurrence
  - TP15: ASM et RAC
- ✅ Cas d'usage avancés (Production, Multi-PDB, Migration)
- ✅ Section dépannage complète

#### [Quick Start](guides/QUICKSTART.md)
Guide de démarrage rapide:
- Installation en 5 minutes
- Premier backup RMAN
- Création première PDB
- Exemples essentiels

#### [Scripts Mapping](guides/SCRIPTS_MAPPING.md)
Correspondance détaillée scripts shell (testés Rocky Linux 8) ↔️ commandes CLI:
- Ce que fait chaque script TP01-TP15
- Commandes SQL/RMAN/Shell exécutées
- 3 approches d'utilisation (Scripts directs, CLI, Hybride)
- Tableau récapitulatif complet

---

### 📚 Références Techniques

#### [Cheat Sheet](reference/CHEAT_SHEET.md)
Aide-mémoire de 700+ lignes avec toutes les commandes essentielles:
- Installation et configuration
- Gestion base de données
- RMAN backups
- Data Guard
- Performance tuning
- Multitenant CDB/PDB
- ASM et RAC
- Dépannage rapide

#### [Guide d'Installation YAML](reference/INSTALL.yml)
Procédures d'installation détaillées en format YAML:
- Prérequis système
- Installation pas-à-pas
- Configuration post-installation
- Validation

---

### 🔧 Documentation Développeurs

#### [Developer Guide](development/DEVELOPER_GUIDE.md)
Guide technique de 700+ lignes pour développeurs:
- Architecture du code (Manager pattern, CLI structure)
- Setup environnement développement
- Tests unitaires et intégration
- Style guide (Python, YAML, Shell)
- Workflow de contribution
- Exemple d'ajout de nouveau module

#### [Contributing Guidelines](development/CONTRIBUTING.md)
Comment contribuer au projet:
- Code of conduct
- Comment soumettre une issue
- Comment créer une pull request
- Standards de code
- Process de review

---

### 🚀 Déploiement

#### [GitHub Publishing Guide](deployment/GITHUB_GUIDE.md)
Guide complet pour publier le package sur GitHub:
- Création repository GitHub
- Configuration Git
- Tagging et releases
- CI/CD avec GitHub Actions
- Documentation automatique

#### [PyPI Publishing Guide](deployment/PYPI_GUIDE.md) 📝 **NOUVEAU**
Guide détaillé étape par étape pour publier sur PyPI (30+ pages):
- **Prérequis:** Création compte PyPI, configuration API tokens
- **Build & Test:** Construction du package, validation avec twine
- **Publication:** TestPyPI d'abord, puis Production
- **Scripts automatisés:** Disponibles dans `../deployment-tools/` (en dehors du package)
  - `publish.ps1` pour Windows PowerShell
  - `publish.sh` pour Linux/Mac Bash
- **Troubleshooting:** Résolution des erreurs courantes
- **Versioning:** Mise à jour et nouvelles releases
- **Badges PyPI** pour README

**🎯 Les scripts de publication ne font PAS partie du package distribué.**

**Usage Rapide (depuis deployment-tools/):**
```bash
# Windows PowerShell
cd ..\deployment-tools
.\publish.ps1 test   # Publier sur TestPyPI
.\publish.ps1 prod   # Publier sur PyPI Production

# Linux/Mac
cd ../deployment-tools
./publish.sh test    # Publier sur TestPyPI
./publish.sh prod    # Publier sur PyPI Production
```

#### [Package Summary](deployment/PACKAGE_SUMMARY.md)
Vue d'ensemble complète du package:
- Architecture globale
- Modules et fonctionnalités
- Statistiques (fichiers, lignes de code)
- Commandes disponibles
- Configuration

---

## 🔍 Recherche Rapide

### Vous cherchez à :

**Installer Oracle 19c ?**
→ [Quick Start](guides/QUICKSTART.md) ou [Guide Complet](guides/GUIDE_UTILISATION.md)

**Configurer RMAN Backup ?**
→ [Guide Utilisation - TP08](guides/GUIDE_UTILISATION.md#tp08-rman-backup) ou [Cheat Sheet - RMAN](reference/CHEAT_SHEET.md#-rman-backup-tp08)

**Mettre en place Data Guard ?**
→ [Guide Utilisation - TP09](guides/GUIDE_UTILISATION.md#tp09-data-guard)

**Optimiser les performances ?**
→ [Guide Utilisation - TP10](guides/GUIDE_UTILISATION.md#tp10-performance-tuning)

**Gérer les PDBs ?**
→ [Guide Utilisation - TP12](guides/GUIDE_UTILISATION.md#tp12-multi-tenant) ou [Cheat Sheet - PDB](reference/CHEAT_SHEET.md#-multitenant-cdbpdb-tp12)

**Comprendre les scripts shell ?**
→ [Scripts Mapping](guides/SCRIPTS_MAPPING.md)

**Contribuer au projet ?**
→ [Developer Guide](development/DEVELOPER_GUIDE.md) + [Contributing](development/CONTRIBUTING.md)

**Publier sur GitHub ?**
→ [GitHub Guide](deployment/GITHUB_GUIDE.md)

**Référence rapide des commandes ?**
→ [Cheat Sheet](reference/CHEAT_SHEET.md)

---

## 📊 Statistiques Documentation

- **Total:** ~5000 lignes de documentation
- **Guides:** 3 fichiers principaux
- **Références:** 2 fichiers techniques
- **Développement:** 2 guides développeurs
- **Déploiement:** 2 guides publication
- **Exemples:** 15 TPs complets avec code
- **Langues:** Français (peut être traduit en anglais)

---

## 🆘 Support

### Besoin d'aide ?

1. **Consultez d'abord:**
   - [Quick Start](guides/QUICKSTART.md) pour démarrage rapide
   - [Cheat Sheet](reference/CHEAT_SHEET.md) pour référence commandes
   - [Guide Complet](guides/GUIDE_UTILISATION.md) pour exemples détaillés

2. **Si problème technique:**
   - Vérifier section **Dépannage** dans [Guide Complet](guides/GUIDE_UTILISATION.md#-dépannage)
   - Consulter [Cheat Sheet - Dépannage](reference/CHEAT_SHEET.md#-dépannage-rapide)

3. **Pour contribuer:**
   - Lire [Developer Guide](development/DEVELOPER_GUIDE.md)
   - Suivre [Contributing Guidelines](development/CONTRIBUTING.md)

4. **Contact:**
   - 🐛 Issues: [GitHub Issues](https://github.com/ELMRABET-Abdelali/oracledba/issues)
   - 💬 Discussions: [GitHub Discussions](https://github.com/ELMRABET-Abdelali/oracledba/discussions)

---

## 📝 Licence

Ce projet est sous licence MIT. Voir [LICENSE](../LICENSE) pour plus de détails.

---

## 🙏 Contributions

Documentation maintenue par la communauté. Consultez [CONTRIBUTING.md](development/CONTRIBUTING.md) pour contribuer.

**Dernière mise à jour:** Février 2026  
**Version:** 1.0.0
