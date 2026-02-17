# Quick Start Guide

## Installation rapide

```bash
# Installer avec pip
pip install oracledba

# Ou depuis GitHub
git clone https://github.com/ELMRABET-Abdelali/oracledba.git
cd oracledba
pip install -e .
```

## Première utilisation

### 1. Setup interactif

```bash
oradba-setup
```

Le wizard vous guidera à travers toutes les étapes de configuration.

### 2. Installation complète

```bash
# Installation complète avec configuration par défaut
oradba install --full

# Avec fichier de configuration personnalisé
oradba install --config my-config.yml --full
```

### 3. Vérifier l'installation

```bash
# Statut de la base
oradba status

# Se connecter à SQL*Plus
oradba sqlplus --sysdba
```

## Commandes essentielles

### Gestion de base

```bash
oradba start              # Démarrer la base
oradba stop               # Arrêter la base
oradba restart            # Redémarrer la base
oradba status             # Statut de la base
oradba sqlplus --sysdba   # Connecter à SQL*Plus
```

### RMAN - Backup

```bash
oradba rman --setup                # Configurer RMAN
oradba rman --backup full          # Backup complet
oradba rman --backup incremental   # Backup incrémental
oradba rman --list                 # Lister les backups
```

### Multitenant (PDB)

```bash
oradba pdb --create PDB1           # Créer PDB
oradba pdb --list                  # Lister PDBs
oradba pdb --open PDB1             # Ouvrir PDB
oradba pdb --clone PDB1 PDB2       # Cloner PDB
```

### Data Guard

```bash
oradba dataguard --setup --primary-host db1 --standby-host db2 --db-name PROD
oradba dataguard --status
oradba dataguard --switchover
```

### Performance Tuning

```bash
oradba tuning --analyze            # Analyser performance
oradba tuning --awr                # Rapport AWR
oradba tuning --addm               # Rapport ADDM
```

### ASM

```bash
oradba asm --setup --disks /dev/sdb /dev/sdc
oradba asm --create-diskgroup --name DATA --redundancy NORMAL --disks /dev/sdb
oradba asm --status
```

### RAC

```bash
oradba rac --setup --nodes node1 node2 --vip 192.168.1.101 192.168.1.102
oradba rac --add-node --hostname node3 --vip 192.168.1.103
oradba rac --status
```

### Sécurité

```bash
oradba security --audit --enable    # Activer audit
oradba security --encryption        # Configurer TDE
oradba security --users --list      # Lister users
```

### Monitoring

```bash
oradba monitor --tablespaces        # Utilisation tablespaces
oradba monitor --sessions           # Sessions actives
oradba logs --alert                 # Alert log
oradba logs --listener              # Listener log
```

### NFS

```bash
oradba nfs --setup-server --export /u01/shared
oradba nfs --setup-client --server 192.168.1.10 --mount /u01/nfs
```

## Configuration VM

### Initialiser une nouvelle VM

```bash
# Pour une base de données standard
oradba vm-init --role database

# Pour un nœud RAC
oradba vm-init --role rac-node --node-number 2

# Pour un standby Data Guard
oradba vm-init --role dataguard-standby
```

## Configuration personnalisée

### Créer un fichier de configuration

```bash
# Copier le template
cp oracledba/configs/default-config.yml my-config.yml

# Éditer (modifier passwords, chemins, etc.)
nano my-config.yml

# Utiliser
oradba install --config my-config.yml --full
```

### Variables d'environnement

Ajouter à `.bash_profile` ou `.bashrc`:

```bash
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH
```

## Exemples d'utilisation

### Scenario 1: Installation nouvelle VM

```bash
# 1. Préparer le système
oradba install --system

# 2. Installer les binaires Oracle
oradba install --binaries

# 3. Créer la base de données
oradba install --database

# 4. Configurer les backups
oradba rman --setup

# 5. Créer des PDBs
oradba pdb --create PDB1
oradba pdb --create PDB2
```

### Scenario 2: Setup Data Guard

```bash
# Sur le primary
oradba dataguard --setup --primary-host primary.local --standby-host standby.local --db-name PROD

# Vérifier
oradba dataguard --status
```

### Scenario 3: Configuration RAC 2 nœuds

```bash
# Setup NFS partagé
oradba nfs --setup-server --export /u01/shared --clients "192.168.1.0/24"

# Sur chaque nœud
oradba nfs --setup-client --server nfs-server --remote-path /u01/shared --mount-point /u01/nfs

# Configurer RAC
oradba rac --setup \
  --nodes node1 node2 \
  --vip 192.168.1.101 192.168.1.102
```

## Aide

```bash
# Aide générale
oradba --help

# Aide pour une commande spécifique
oradba install --help
oradba rman --help
oradba pdb --help
```

## Dépannage

### Base ne démarre pas

```bash
# Voir les logs
oradba logs --alert --tail 100

# Vérifier paramètres
oradba sqlplus --sysdba
SQL> show parameter sga
SQL> show parameter pga
```

### Problème de backup

```bash
# Vérifier configuration RMAN
oradba sqlplus --sysdba
SQL> exit
rman target /
RMAN> show all;
```

### Espace insuffisant

```bash
# Vérifier utilisation
oradba monitor --tablespaces

# Ajouter datafile si nécessaire
oradba sqlplus --sysdba
SQL> ALTER TABLESPACE USERS ADD DATAFILE SIZE 1G;
```

## Support

- Documentation: [GitHub Wiki](https://github.com/ELMRABET-Abdelali/oracledba/wiki)
- Issues: [GitHub Issues](https://github.com/ELMRABET-Abdelali/oracledba/issues)
- Email: dba@formation.com

---

**Prêt à commencer? Lancez `oradba-setup` maintenant!** 🚀
