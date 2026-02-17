#!/bin/bash
export ORACLE_HOME=/u01/app/oracle/product/19.3.0/dbhome_1
export ORACLE_SID=GDCPROD
export PATH=$ORACLE_HOME/bin:$PATH

echo "=== RAW CONTROLFILE ==="
echo "SET PAGESIZE 1000
SET LINESIZE 300
SET FEEDBACK OFF
SET HEADING ON
SET COLSEP '|'
SELECT name AS \"NAME\", NVL(status, 'OK') AS \"STATUS\" FROM v\$controlfile;
EXIT;" | su - oracle -c "$ORACLE_HOME/bin/sqlplus -s '/ as sysdba'"

echo ""
echo "=== RAW REDO LOGS ==="
echo "SET PAGESIZE 1000
SET LINESIZE 300
SET FEEDBACK OFF
SET HEADING ON
SET COLSEP '|'
SELECT f.group# AS \"GROUP#\", f.member AS \"MEMBER\", f.type AS \"TYPE\",
       l.status AS \"STATUS\", ROUND(l.bytes/1024/1024) AS \"SIZE_MB\", l.members AS \"MEMBERS\"
FROM v\$logfile f JOIN v\$log l ON f.group# = l.group#
ORDER BY f.group#, f.member;
EXIT;" | su - oracle -c "$ORACLE_HOME/bin/sqlplus -s '/ as sysdba'"

echo ""
echo "=== RAW FRA ==="
echo "SET PAGESIZE 1000
SET LINESIZE 300
SET FEEDBACK OFF
SET HEADING ON
SET COLSEP '|'
SELECT name AS \"NAME\", ROUND(space_limit/1024/1024) AS \"SIZE_MB\", ROUND(space_used/1024/1024) AS \"USED_MB\" FROM v\$recovery_file_dest;
EXIT;" | su - oracle -c "$ORACLE_HOME/bin/sqlplus -s '/ as sysdba'"

echo ""
echo "=== RAW USERS ==="
echo "SET PAGESIZE 1000
SET LINESIZE 300
SET FEEDBACK OFF
SET HEADING ON
SET COLSEP '|'
SELECT username AS \"USERNAME\", account_status AS \"ACCOUNT_STATUS\",
       default_tablespace AS \"DEFAULT_TABLESPACE\", profile AS \"PROFILE\",
       TO_CHAR(created, 'YYYY-MM-DD') AS \"CREATED\"
FROM dba_users WHERE oracle_maintained = 'N' ORDER BY username;
EXIT;" | su - oracle -c "$ORACLE_HOME/bin/sqlplus -s '/ as sysdba'"
