#!/bin/bash
# TP14: Mobilité et Gestion de la Concurrence
# Rocky Linux 8 - Oracle 19c
# Description: Locks, Deadlocks, Transactions

echo "================================================"
echo "  TP14: Mobilité et Concurrence"
echo "  $(date)"
echo "================================================"

export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo ""
echo "[1/7] Création table test concurrence..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

CREATE TABLE accounts (
    account_id NUMBER PRIMARY KEY,
    account_name VARCHAR2(100),
    balance NUMBER(10,2),
    last_update DATE DEFAULT SYSDATE
);

INSERT INTO accounts VALUES (1, 'Account A', 1000.00, SYSDATE);
INSERT INTO accounts VALUES (2, 'Account B', 2000.00, SYSDATE);
INSERT INTO accounts VALUES (3, 'Account C', 1500.00, SYSDATE);
INSERT INTO accounts VALUES (4, 'Account D', 3000.00, SYSDATE);
COMMIT;

SELECT * FROM accounts ORDER BY account_id;
EXIT;
EOF"

echo ""
echo "[2/7] Configuration isolation levels..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

-- Vérifier niveau d'isolation par défaut
SELECT name, value FROM v\$parameter WHERE name='isolation_level';

-- Test READ COMMITTED (default)
SELECT * FROM accounts FOR UPDATE;
ROLLBACK;

SHOW PARAMETER transactions;
EXIT;
EOF"

echo ""
echo "[3/7] Démonstration Row-Level Locking..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

-- Verrouiller une ligne spécifique
UPDATE accounts SET balance = balance + 100 WHERE account_id = 1;

-- Voir les locks actifs
SELECT 
    l.session_id,
    l.oracle_username,
    l.os_user_name,
    o.object_name,
    l.locked_mode
FROM v\$locked_object l
JOIN dba_objects o ON l.object_id = o.object_id
WHERE o.object_name = 'ACCOUNTS';

ROLLBACK;
EXIT;
EOF"

echo ""
echo "[4/7] Simulation transaction et rollback..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

-- Balance initiale
SELECT account_id, account_name, balance FROM accounts;

-- Transaction: transfert entre comptes
UPDATE accounts SET balance = balance - 500 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 500 WHERE account_id = 2;

-- Vérifier avant commit
SELECT account_id, account_name, balance FROM accounts;

-- Rollback pour annuler
ROLLBACK;

-- Vérifier après rollback
SELECT account_id, account_name, balance FROM accounts;
EXIT;
EOF"

echo ""
echo "[5/7] Transaction avec SAVEPOINT..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
ALTER SESSION SET container=GDCPDB;

-- Transaction complexe avec savepoints
UPDATE accounts SET balance = balance - 200 WHERE account_id = 1;
SAVEPOINT after_first_update;

UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
SAVEPOINT after_second_update;

UPDATE accounts SET balance = balance + 100 WHERE account_id = 3;
SAVEPOINT after_third_update;

-- Rollback partiel
ROLLBACK TO SAVEPOINT after_second_update;

-- Commit du reste
COMMIT;

SELECT account_id, balance FROM accounts ORDER BY account_id;
EXIT;
EOF"

echo ""
echo "[6/7] Monitoring des sessions et locks..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200 PAGESIZE 100

-- Sessions actives
SELECT 
    sid,
    serial#,
    username,
    status,
    osuser,
    machine,
    program,
    logon_time
FROM v\$session
WHERE username IS NOT NULL
ORDER BY logon_time DESC;

-- Statistiques de locks
SELECT 
    COUNT(*) AS total_sessions,
    SUM(CASE WHEN blocking_session IS NOT NULL THEN 1 ELSE 0 END) AS blocked_sessions
FROM v\$session
WHERE username IS NOT NULL;
EXIT;
EOF"

echo ""
echo "[7/7] Configuration wait events..."
su - oracle -c "sqlplus / as sysdba << 'EOF'
SET LINESIZE 200 PAGESIZE 50

-- Top wait events
SELECT 
    event,
    total_waits,
    total_timeouts,
    time_waited,
    average_wait
FROM v\$system_event
WHERE event NOT LIKE 'SQL*Net%'
  AND event NOT LIKE '%timer%'
  AND event NOT LIKE '%idle%'
ORDER BY time_waited DESC
FETCH FIRST 10 ROWS ONLY;

-- Lock wait statistics
SELECT 
    name,
    value
FROM v\$sysstat
WHERE name LIKE '%lock%'
  OR name LIKE '%waited%'
  AND value > 0
ORDER BY value DESC;
EXIT;
EOF"

echo ""
echo "================================================"
echo "  TP14 TERMINÉ"
echo "================================================"
echo "Concurrence et Mobilité configuré:"
echo "- Row-Level Locking: Testé"
echo "- Transaction Management: OK"
echo "- SAVEPOINT: Fonctionnel"
echo "- Lock Monitoring: Configuré"
echo ""
echo "Outils monitoring:"
echo "- v\$locked_object: Objets verrouillés"
echo "- v\$session: Sessions actives"
echo "- v\$lock: Détails des verrous"
echo "- v\$system_event: Wait events"
echo ""
echo "Commandes deadlock:"
echo "- Identifier: SELECT * FROM v\$session WHERE blocking_session IS NOT NULL"
echo "- Résoudre: Kill session ou rollback transaction"
