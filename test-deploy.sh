#!/bin/bash
# Test: Save a config, then deploy it to create a real PDB
set -e

BASE="http://localhost:5000"
COOKIE="/tmp/infra-cookies.txt"

# Login
curl -s -c $COOKIE -b $COOKIE -X POST \
  -d "username=admin&password=admin123" "$BASE/login" -o /dev/null

# Save a config
echo "=== SAVE CONFIG ==="
curl -s -b $COOKIE -X POST \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "name: test-deploy\ndescription: Test deployment\npdb:\n  name: TESTDPL\n  admin_user: testdpl_admin\n  admin_password: Oracle123\ntablespaces:\n- name: TESTDPL_DATA\n  size_mb: 50\n  autoextend: true\n  max_size_mb: 200\n  datafile_path: /u01/app/oracle/oradata/GDCPROD/TESTDPL/testdpl_data01.dbf\nusers:\n- username: TEST_APP\n  password: TestApp123\n  default_tablespace: TESTDPL_DATA\n  temp_tablespace: TEMP\n  quota: UNLIMITED\n  roles:\n  - CONNECT\n  - RESOURCE\nprotection:\n  archivelog: true\n  flashback: true\n"}' \
  "$BASE/api/infrastructure/configs/save" | python3 -m json.tool

# List saved configs
echo ""
echo "=== LIST CONFIGS ==="
curl -s -b $COOKIE "$BASE/api/infrastructure/configs" | python3 -m json.tool

# Deploy the config
echo ""
echo "=== DEPLOY CONFIG ==="
curl -s -b $COOKIE -X POST \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "name: test-deploy\ndescription: Test deployment\npdb:\n  name: TESTDPL\n  admin_user: testdpl_admin\n  admin_password: Oracle123\ntablespaces:\n- name: TESTDPL_DATA\n  size_mb: 50\n  autoextend: true\n  max_size_mb: 200\n  datafile_path: /u01/app/oracle/oradata/GDCPROD/TESTDPL/testdpl_data01.dbf\nusers:\n- username: TEST_APP\n  password: TestApp123\n  default_tablespace: TESTDPL_DATA\n  temp_tablespace: TEMP\n  quota: UNLIMITED\n  roles:\n  - CONNECT\n  - RESOURCE\nprotection:\n  archivelog: true\n  flashback: true\n"}' \
  "$BASE/api/infrastructure/configs/deploy" | python3 -m json.tool

echo ""
echo "=== DONE ==="
