#!/bin/bash
# Installation Complète Oracle 19c - Rocky Linux 8
# Exécution automatique des 15 TPs
# Description: Master script pour installation end-to-end

set -e

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="/u01/app/oracle/admin/installation_logs"
START_TIME=$(date +%s)

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  INSTALLATION ORACLE 19c - ROCKY LINUX 8${NC}"
echo -e "${BLUE}  Installation Automatique Complète${NC}"
echo -e "${BLUE}  $(date)${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Créer répertoire logs
mkdir -p "$LOG_DIR"

# Fonction log
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERREUR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

# Fonction exécution TP
execute_tp() {
    local tp_num=$1
    local tp_name=$2
    local tp_script=$3
    local run_as=${4:-root}  # Par défaut root
    
    log "${BLUE}========== TP${tp_num}: ${tp_name} ==========${NC}"
    
    if [ ! -f "$tp_script" ]; then
        error "Script non trouvé: $tp_script"
    fi
    
    chmod +x "$tp_script"
    
    local log_file="$LOG_DIR/tp${tp_num}_$(date +%Y%m%d_%H%M%S).log"
    
    if [ "$run_as" == "root" ]; then
        log "Exécution en tant que root..."
        bash "$tp_script" 2>&1 | tee "$log_file"
    else
        log "Exécution en tant que oracle..."
        su - oracle -c "bash $tp_script" 2>&1 | tee "$log_file"
    fi
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        log "${GREEN}✓ TP${tp_num} terminé avec succès${NC}"
    else
        error "TP${tp_num} a échoué. Voir log: $log_file"
    fi
    
    echo ""
}

# Vérifications préalables
log "Vérifications préalables..."

# Vérifier OS
if ! grep -q "Rocky Linux release 8" /etc/rocky-release 2>/dev/null; then
    warning "Ce script est optimisé pour Rocky Linux 8"
fi

# Vérifier utilisateur
if [ "$EUID" -ne 0 ]; then
    error "Ce script doit être exécuté en tant que root"
fi

# Vérifier RAM minimum (2GB)
RAM_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
if [ $RAM_KB -lt 2000000 ]; then
    warning "RAM insuffisante (< 2GB). Recommandé: 4GB+"
fi

# Vérifier espace disque (minimum 40GB)
DISK_AVAIL=$(df / | tail -1 | awk '{print $4}')
if [ $DISK_AVAIL -lt 40000000 ]; then
    warning "Espace disque faible. Recommandé: 50GB+ disponible"
fi

log "✓ Vérifications préalables OK"
echo ""

# Demander confirmation
read -p "Lancer l'installation complète (15 TPs)? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Installation annulée"
    exit 0
fi

echo ""
log "Début installation complète..."
echo ""

# ========================================
# PHASE 1: INFRASTRUCTURE (TP01-03)
# ========================================
log "${BLUE}=== PHASE 1: INFRASTRUCTURE ===${NC}"

# TP01: System Readiness
execute_tp "01" "System Readiness" "$SCRIPT_DIR/tp01-system-readiness.sh" "root"

# TP02: Installation Binaire (en tant qu'oracle)
execute_tp "02" "Installation Binaire" "$SCRIPT_DIR/tp02-installation-binaire.sh" "oracle"

# TP03: Création Instance
log "TP03: Installation nécessite interventions manuelles"
warning "Exécuter manuellement:"
warning "  1. su - oracle"
warning "  2. bash $SCRIPT_DIR/tp03-creation-instance.sh"
warning "  3. Exécuter root.sh scripts quand demandé"
echo ""
read -p "Appuyez sur ENTRÉE après avoir terminé TP03..." -r
echo ""

# ========================================
# PHASE 2: FICHIERS CRITIQUES (TP04-05)
# ========================================
log "${BLUE}=== PHASE 2: FICHIERS CRITIQUES ===${NC}"

execute_tp "04" "Fichiers Critiques" "$SCRIPT_DIR/tp04-fichiers-critiques.sh" "oracle"
execute_tp "05" "Gestion Stockage" "$SCRIPT_DIR/tp05-gestion-stockage.sh" "oracle"

# ========================================
# PHASE 3: SÉCURITÉ (TP06-07)
# ========================================
log "${BLUE}=== PHASE 3: SÉCURITÉ ===${NC}"

execute_tp "06" "Sécurité et Accès" "$SCRIPT_DIR/tp06-securite-acces.sh" "oracle"
execute_tp "07" "Flashback Technologies" "$SCRIPT_DIR/tp07-flashback.sh" "oracle"

# ========================================
# PHASE 4: BACKUP & HA (TP08-09)
# ========================================
log "${BLUE}=== PHASE 4: BACKUP & HAUTE DISPONIBILITÉ ===${NC}"

execute_tp "08" "RMAN Backup" "$SCRIPT_DIR/tp08-rman.sh" "oracle"
execute_tp "09" "Data Guard Prep" "$SCRIPT_DIR/tp09-dataguard.sh" "oracle"

# ========================================
# PHASE 5: TUNING & MAINTENANCE (TP10-11)
# ========================================
log "${BLUE}=== PHASE 5: TUNING & MAINTENANCE ===${NC}"

execute_tp "10" "Performance Tuning" "$SCRIPT_DIR/tp10-tuning.sh" "oracle"
execute_tp "11" "Patching" "$SCRIPT_DIR/tp11-patching.sh" "oracle"

# ========================================
# PHASE 6: AVANCÉ (TP12-15)
# ========================================
log "${BLUE}=== PHASE 6: FONCTIONNALITÉS AVANCÉES ===${NC}"

execute_tp "12" "Multitenant" "$SCRIPT_DIR/tp12-multitenant.sh" "oracle"
execute_tp "13" "AI/ML Foundations" "$SCRIPT_DIR/tp13-ai-foundations.sh" "oracle"
execute_tp "14" "Mobilité et Concurrence" "$SCRIPT_DIR/tp14-mobilite-concurrence.sh" "oracle"
execute_tp "15" "ASM et RAC Concepts" "$SCRIPT_DIR/tp15-asm-rac-concepts.sh" "oracle"

# ========================================
# RAPPORT FINAL
# ========================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(((DURATION % 3600) / 60))
SECONDS=$((DURATION % 60))

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  INSTALLATION TERMINÉE AVEC SUCCÈS !${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Durée totale: ${HOURS}h ${MINUTES}m ${SECONDS}s"
echo ""
echo "Logs: $LOG_DIR"
echo ""

# Rapport final
su - oracle -c 'sqlplus -s / as sysdba << "EOSQL"
SET LINESIZE 200 PAGESIZE 100

PROMPT === DATABASE ===
SELECT name, open_mode, log_mode, database_role FROM v$database;

PROMPT
PROMPT === INSTANCE ===
SELECT instance_name, host_name, version, status, 
       startup_time, archiver, database_status
FROM v$instance;

PROMPT
PROMPT === PDBs ===
SELECT name, open_mode, restricted FROM v$pdbs ORDER BY con_id;

PROMPT
PROMPT === TABLESPACES ===
SELECT tablespace_name, status, contents, 
       ROUND(SUM(bytes)/1024/1024/1024, 2) AS size_gb
FROM dba_data_files
GROUP BY tablespace_name, status, contents
ORDER BY tablespace_name;

PROMPT
PROMPT === REDO LOGS ===
SELECT group#, thread#, bytes/1024/1024 AS mb, members, status, archived
FROM v$log ORDER BY group#;

PROMPT
PROMPT === BACKUP INFO ===
SELECT * FROM v$rman_status WHERE ROWNUM <= 5 ORDER BY start_time DESC;

EXIT;
EOSQL'

echo ""
echo -e "${BLUE}Informations de connexion:${NC}"
echo "  CDB: sqlplus / as sysdba"
echo "  PDB: sqlplus sys/SysOracle123@localhost:1521/gdcpdb as sysdba"
echo ""
echo -e "${BLUE}Utilisateurs créés:${NC}"
echo "  - dev_user/DevPass123"
echo "  - app_user/AppPass123"
echo "  - readonly_user/ReadPass123"
echo "  - mluser/MlPass123"
echo ""
echo -e "${BLUE}Prochaines étapes:${NC}"
echo "  1. Configurer firewall si nécessaire"
echo "  2. Planifier backups RMAN automatiques"
echo "  3. Configurer monitoring (EM Cloud Control ou autre)"
echo "  4. Tester connexions applications"
echo "  5. Documenter configuration spécifique"
echo ""
echo -e "${GREEN}Félicitations! Oracle 19c est opérationnel.${NC}"
echo ""
