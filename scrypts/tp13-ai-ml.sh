#!/bin/bash
# TP13: AI Vector Search et Machine Learning
# Rocky Linux 8 - Oracle 19c
# Description: Préparation pour Oracle AI et ML

echo "================================================"
echo "  TP13: AI Foundations & Machine Learning"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/5] Vérification Oracle Text..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;
SELECT comp_name, version, status FROM dba_registry WHERE comp_name LIKE '%Text%';
EXIT;
EOF"

echo ""
echo "[2/5] Création table avec données texte pour AI/ML..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

CREATE TABLE ml_training_data (
    id NUMBER PRIMARY KEY,
    category VARCHAR2(50),
    text_data VARCHAR2(4000),
    sentiment NUMBER(1),
    created_date DATE DEFAULT SYSDATE
);

-- Données exemple pour training
INSERT INTO ml_training_data VALUES (1, 'POSITIVE', 'Excellent product, very satisfied', 1, SYSDATE);
INSERT INTO ml_training_data VALUES (2, 'NEGATIVE', 'Poor quality, not recommended', 0, SYSDATE);
INSERT INTO ml_training_data VALUES (3, 'POSITIVE', 'Amazing service, will buy again', 1, SYSDATE);
INSERT INTO ml_training_data VALUES (4, 'NEGATIVE', 'Disappointed with purchase', 0, SYSDATE);
INSERT INTO ml_training_data VALUES (5, 'POSITIVE', 'Great value for money', 1, SYSDATE);
INSERT INTO ml_training_data VALUES (6, 'POSITIVE', 'Highly recommended product', 1, SYSDATE);
INSERT INTO ml_training_data VALUES (7, 'NEGATIVE', 'Not worth the price', 0, SYSDATE);
INSERT INTO ml_training_data VALUES (8, 'POSITIVE', 'Superb quality and fast delivery', 1, SYSDATE);
COMMIT;

SELECT category, COUNT(*), AVG(sentiment) FROM ml_training_data GROUP BY category;
EXIT;
EOF"

echo ""
echo "[3/5] Configuration DBMS_DATA_MINING..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

-- Vérifier que Data Mining est disponible
SELECT * FROM v\$option WHERE parameter = 'Data Mining';

-- Statistiques sur les données
EXEC DBMS_STATS.gather_table_stats(USER, 'ML_TRAINING_DATA');

SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT category) AS categories,
    MIN(LENGTH(text_data)) AS min_text_length,
    MAX(LENGTH(text_data)) AS max_text_length,
    AVG(LENGTH(text_data)) AS avg_text_length
FROM ml_training_data;
EXIT;
EOF"

echo ""
echo "[4/5] Création index Text pour recherche..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

BEGIN
    CTX_DDL.create_preference('my_lexer', 'BASIC_LEXER');
    CTX_DDL.create_preference('my_wordlist', 'BASIC_WORDLIST');
    CTX_DDL.set_attribute('my_wordlist', 'stemmer', 'ENGLISH');
END;
/

CREATE INDEX idx_ml_text ON ml_training_data(text_data)
INDEXTYPE IS CTXSYS.CONTEXT
PARAMETERS ('lexer my_lexer wordlist my_wordlist');

-- Test recherche texte
SELECT id, category, text_data, sentiment
FROM ml_training_data
WHERE CONTAINS(text_data, 'excellent OR great', 1) > 0;
EXIT;
EOF"

echo ""
echo "[5/5] Préparation pour Oracle Machine Learning..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

-- Création vue pour analyse
CREATE OR REPLACE VIEW ml_analytics AS
SELECT 
    category,
    sentiment,
    LENGTH(text_data) AS text_length,
    CASE 
        WHEN LENGTH(text_data) < 30 THEN 'SHORT'
        WHEN LENGTH(text_data) < 50 THEN 'MEDIUM'
        ELSE 'LONG'
    END AS text_category
FROM ml_training_data;

SELECT * FROM ml_analytics;

-- Statistiques basiques
SELECT 
    category,
    text_category,
    COUNT(*) AS count,
    AVG(sentiment) AS avg_sentiment
FROM ml_analytics
GROUP BY category, text_category
ORDER BY category, text_category;
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP13 TERMINÉ"
echo "================================================"
echo "AI & ML Foundations configuré:"
echo "- Oracle Text: Index créé"
echo "- Training Data: 8 records"
echo "- Data Mining: Disponible"
echo "- Text Search: Fonctionnel"
echo ""
echo "Pour Oracle AI Vector Search (23ai+):"
echo "- Upgrade vers Oracle 23c"
echo "- CREATE VECTOR INDEX"
echo "- VECTOR_DISTANCE() function"
echo ""
echo "Pour Oracle Machine Learning:"
echo "- OML4Py: Python integration"
echo "- OML Notebooks: Web interface"
echo "- AutoML: Automated model building"
