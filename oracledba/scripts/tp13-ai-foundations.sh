#!/bin/bash
# TP13 - AI/ML Foundations dans Oracle
# Oracle Machine Learning, Data Mining, Python Integration
# Rocky Linux 8 - Oracle 19c

set -e

echo "================================================"
echo "  TP13: AI/ML Foundations"
echo "  Oracle Machine Learning"
echo "  Rocky Linux 8 - Oracle 19c"
echo "  $(date)"
echo "================================================"

if [ "$(whoami)" != "oracle" ]; then
    echo "ERREUR: Exécuter en tant qu'oracle"
    exit 1
fi

source ~/.bash_profile

echo ""
echo "[1/6] Vérification Oracle Data Mining (ODM)..."

sqlplus -s / as sysdba << 'EOSQL'
-- Vérifier composants ML/DM
SELECT comp_name, version, status 
FROM dba_registry 
WHERE comp_name LIKE '%DATA MINING%' OR comp_name LIKE '%MACHINE LEARNING%';

-- Alternative: Vérifier packages ML
SELECT object_name, object_type, status
FROM dba_objects
WHERE object_name LIKE 'DBMS_DATA_MINING%'
   OR object_name LIKE 'DBMS_PREDICTIVE%'
ORDER BY object_name;

EXIT;
EOSQL

echo ""
echo "[2/6] Installation schéma et données pour ML..."

sqlplus / as sysdba << 'EOSQL'
ALTER SESSION SET CONTAINER=gdcpdb;

-- Créer utilisateur ML
CREATE USER mluser IDENTIFIED BY MlPass123
  DEFAULT TABLESPACE users
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON users;

GRANT CREATE SESSION TO mluser;
GRANT CREATE TABLE TO mluser;
GRANT CREATE VIEW TO mluser;
GRANT CREATE MINING MODEL TO mluser;
GRANT CREATE PROCEDURE TO mluser;

-- Privileges spécifiques ML
GRANT EXECUTE ON DBMS_DATA_MINING TO mluser;
GRANT EXECUTE ON DBMS_DATA_MINING_TRANSFORM TO mluser;
GRANT SELECT ON SYS.DBA_MINING_MODELS TO mluser;

EXIT;
EOSQL

echo "✓ Utilisateur ML créé"

echo ""
echo "[3/6] Création dataset pour modèle prédictif..."

sqlplus mluser/MlPass123@localhost:1521/gdcpdb << 'EOSQL'
-- Table données clients pour prédiction churn
CREATE TABLE customer_data (
    customer_id NUMBER PRIMARY KEY,
    age NUMBER,
    income NUMBER,
    tenure_months NUMBER,
    monthly_charges NUMBER(10,2),
    total_charges NUMBER(10,2),
    num_services NUMBER,
    contract_type VARCHAR2(20),
    payment_method VARCHAR2(30),
    has_churned NUMBER(1)  -- 0=retained, 1=churned
);

-- Générer données test
BEGIN
    FOR i IN 1..5000 LOOP
        INSERT INTO customer_data VALUES (
            i,
            ROUND(DBMS_RANDOM.VALUE(18, 80)),  -- age
            ROUND(DBMS_RANDOM.VALUE(20000, 150000)),  -- income
            ROUND(DBMS_RANDOM.VALUE(1, 72)),  -- tenure_months
            ROUND(DBMS_RANDOM.VALUE(30, 150), 2),  -- monthly_charges
            ROUND(DBMS_RANDOM.VALUE(100, 10000), 2),  -- total_charges
            ROUND(DBMS_RANDOM.VALUE(1, 6)),  -- num_services
            CASE MOD(i, 3) 
                WHEN 0 THEN 'Month-to-month'
                WHEN 1 THEN 'One year'
                ELSE 'Two year'
            END,  -- contract_type
            CASE MOD(i, 4)
                WHEN 0 THEN 'Credit card'
                WHEN 1 THEN 'Bank transfer'
                WHEN 2 THEN 'Electronic check'
                ELSE 'Mailed check'
            END,  -- payment_method
            -- Simulation churn basé sur facteurs
            CASE 
                WHEN MOD(i, 3) = 0 AND DBMS_RANDOM.VALUE < 0.3 THEN 1
                WHEN MOD(i, 10) < 2 THEN 1
                ELSE 0
            END  -- has_churned
        );
    END LOOP;
    COMMIT;
END;
/

-- Statistics
EXEC DBMS_STATS.GATHER_TABLE_STATS('MLUSER', 'CUSTOMER_DATA');

-- Vérifier distribution
SELECT has_churned, COUNT(*) AS count, 
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM customer_data
GROUP BY has_churned;

EXIT;
EOSQL

echo "✓ Dataset créé (5000 clients)"

echo ""
echo "[4/6] Configuration et création modèle ML..."

sqlplus mluser/MlPass123@localhost:1521/gdcpdb << 'EOSQL'
SET SERVEROUTPUT ON

-- Créer settings pour algorithme
BEGIN
    -- Nettoyer si existe
    BEGIN
        DBMS_DATA_MINING.DROP_MODEL('churn_prediction_model');
    EXCEPTION
        WHEN OTHERS THEN NULL;
    END;
    
    -- Créer modèle de classification (Decision Tree)
    DBMS_DATA_MINING.CREATE_MODEL(
        model_name          => 'churn_prediction_model',
        mining_function     => DBMS_DATA_MINING.CLASSIFICATION,
        data_table_name     => 'customer_data',
        case_id_column_name => 'customer_id',
        target_column_name  => 'has_churned',
        settings_table_name => NULL
    );
    
    DBMS_OUTPUT.PUT_LINE('Modèle créé: churn_prediction_model');
END;
/

-- Vérifier modèle
SELECT model_name, mining_function, algorithm, target_attribute,
       creation_date, model_size
FROM user_mining_models
WHERE model_name = 'CHURN_PREDICTION_MODEL';

-- Voir détails modèle
SELECT name, value 
FROM user_mining_model_attributes
WHERE model_name = 'CHURN_PREDICTION_MODEL'
  AND name IN ('TARGET_ATTRIBUTE', 'ALGORITHM_TYPE')
ORDER BY name;

EXIT;
EOSQL

echo "✓ Modèle ML créé (Classification)"

echo ""
echo "[5/6] Application modèle pour prédictions..."

sqlplus mluser/MlPass123@localhost:1521/gdcpdb << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100

-- Créer nouveaux clients à scorer
CREATE TABLE new_customers AS
SELECT * FROM customer_data WHERE customer_id > 4500;

-- Supprimer colonne churn (on veut la prédire)
ALTER TABLE new_customers DROP COLUMN has_churned;

-- Appliquer modèle pour prédire churn
CREATE TABLE churn_predictions AS
SELECT customer_id, 
       age, income, tenure_months, monthly_charges,
       PREDICTION(churn_prediction_model USING *) AS predicted_churn,
       ROUND(PREDICTION_PROBABILITY(churn_prediction_model, 1 USING *), 3) AS churn_probability
FROM new_customers;

-- Afficher top 10 risques churn
SELECT customer_id, age, tenure_months, monthly_charges,
       predicted_churn, churn_probability
FROM churn_predictions
WHERE predicted_churn = 1
ORDER BY churn_probability DESC
FETCH FIRST 10 ROWS ONLY;

-- Statistiques prédictions
SELECT predicted_churn, COUNT(*) AS count,
       AVG(churn_probability) AS avg_probability
FROM churn_predictions
GROUP BY predicted_churn
ORDER BY predicted_churn;

EXIT;
EOSQL

echo "✓ Prédictions générées pour nouveaux clients"

echo ""
echo "[6/6] Configuration Oracle Machine Learning (OML4Py)..."

# Installation Python et cx_Oracle
echo "Installation modules Python..."
sudo dnf install -y -q python3-devel python3-pip gcc

# En tant qu'oracle
pip3 install --user --quiet cx_Oracle pandas numpy 2>/dev/null || true

# Test connexion Python
cat > /tmp/test_oml.py << 'PYEOF'
import cx_Oracle
import sys

try:
    # Connexion
    dsn = cx_Oracle.makedsn('localhost', 1521, service_name='gdcpdb')
    conn = cx_Oracle.connect(user='mluser', password='MlPass123', dsn=dsn)
    cursor = conn.cursor()
    
    # Query simple
    cursor.execute("SELECT COUNT(*) FROM customer_data")
    count = cursor.fetchone()[0]
    print(f"✓ Python connecté: {count} rows in customer_data")
    
    # Query prédictions
    cursor.execute("""
        SELECT predicted_churn, COUNT(*), AVG(churn_probability)
        FROM churn_predictions
        GROUP BY predicted_churn
        ORDER BY predicted_churn
    """)
    
    print("\nPrédictions par catégorie:")
    for row in cursor:
        print(f"  Churn={row[0]}: {row[1]} clients, avg_prob={row[2]:.3f}")
    
    cursor.close()
    conn.close()
    print("\n✓ Oracle Machine Learning via Python: OK")
    
except Exception as e:
    print(f"✗ Erreur: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

python3 /tmp/test_oml.py

echo ""
echo "================================================"
echo "  TP13 TERMINÉ - ML Foundations OK"
echo "================================================"
echo ""

# Rapport final
sqlplus -s mluser/MlPass123@localhost:1521/gdcpdb << 'EOSQL'
SET LINESIZE 200 PAGESIZE 100

PROMPT === MODÈLES ML ===
SELECT model_name, mining_function, algorithm, 
       target_attribute, creation_date
FROM user_mining_models
ORDER BY creation_date DESC;

PROMPT
PROMPT === DATASET INFO ===
SELECT 'customer_data' AS table_name, COUNT(*) AS rows FROM customer_data
UNION ALL
SELECT 'new_customers', COUNT(*) FROM new_customers
UNION ALL
SELECT 'churn_predictions', COUNT(*) FROM churn_predictions;

PROMPT
PROMPT === PRÉDICTIONS SUMMARY ===
SELECT 
    CASE predicted_churn WHEN 1 THEN 'CHURN' ELSE 'RETAIN' END AS prediction,
    COUNT(*) AS customers,
    ROUND(AVG(churn_probability), 3) AS avg_probability,
    ROUND(MIN(churn_probability), 3) AS min_probability,
    ROUND(MAX(churn_probability), 3) AS max_probability
FROM churn_predictions
GROUP BY predicted_churn
ORDER BY predicted_churn;

EXIT;
EOSQL

echo ""
echo "Oracle Machine Learning configuré:"
echo "- Algorithm: Classification (Decision Tree)"
echo "- Dataset: 5000 clients"
echo "- Modèle: churn_prediction_model"
echo "- Prédictions: Génées pour nouveaux clients"
echo "- Python: cx_Oracle intégré"
echo ""
echo "Fonctionnalités disponibles:"
echo "- DBMS_DATA_MINING: API PL/SQL"
echo "- PREDICTION(): Fonction SQL"
echo "- OML4Py: Integration Python"
echo "- Notebooks: Oracle ML Notebooks (web UI)"
echo ""
echo "Prochaine étape: TP14 - Mobilité et Concurrence"
