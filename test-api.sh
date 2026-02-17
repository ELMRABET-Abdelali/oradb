#!/bin/bash
# Login and get session cookie
COOKIE=$(curl -s -c - -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -L | grep -o 'session=[^;]*' || true)

# Use cookie jar approach
curl -s -c /tmp/cookies.txt -b /tmp/cookies.txt -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123" \
  -H "Content-Type: application/x-www-form-urlencoded" -L -o /dev/null

echo "=== DATABASES ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/databases/list 2>&1 | head -5
echo ""
echo "=== TABLESPACES ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/storage/tablespaces 2>&1 | head -5
echo ""
echo "=== CONTROLFILES ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/storage/controlfile/list 2>&1 | head -3
echo ""
echo "=== REDO LOGS ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/storage/redolog/list 2>&1 | head -5
echo ""
echo "=== ARCHIVELOG STATUS ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/protection/archivelog/status 2>&1
echo ""
echo "=== FRA STATUS ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/protection/fra/status 2>&1
echo ""
echo "=== SECURITY USERS ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/security/users 2>&1 | head -5
echo ""
echo "=== AUDIT ==="
curl -s -b /tmp/cookies.txt http://localhost:5000/api/security/audit 2>&1 | head -3
echo ""
echo "=== DASHBOARD ==="
curl -s -b /tmp/cookies.txt -o /dev/null -w "HTTP_%{http_code}" http://localhost:5000/dashboard
echo ""
echo "=== DONE ==="
