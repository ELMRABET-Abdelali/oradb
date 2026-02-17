#!/bin/bash
# Check actual datafile paths
su - oracle -c 'sqlplus -s "/ as sysdba"' <<'EOF'
SET LINESIZE 200
SET PAGESIZE 100
COL FILE_NAME FORMAT A80
SELECT FILE_NAME FROM DBA_DATA_FILES ORDER BY FILE_NAME;
EXIT;
EOF
