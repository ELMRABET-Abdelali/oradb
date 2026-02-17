#!/bin/bash
# Test Infrastructure API endpoints
set -e

BASE="http://localhost:5000"
COOKIE="/tmp/infra-cookies.txt"

# Login
echo "=== LOGIN ==="
curl -s -c $COOKIE -b $COOKIE -X POST \
  -d "username=admin&password=admin123" \
  "$BASE/login" -o /dev/null -w "HTTP %{http_code}\n"

# Test Infrastructure Page
echo ""
echo "=== INFRASTRUCTURE PAGE ==="
curl -s -b $COOKIE "$BASE/infrastructure" -o /dev/null -w "HTTP %{http_code}\n"

# Test Nodes API
echo ""
echo "=== NODES ==="
curl -s -b $COOKIE "$BASE/api/infrastructure/nodes" | python3 -m json.tool 2>/dev/null || curl -s -b $COOKIE "$BASE/api/infrastructure/nodes"

# Test Storage API
echo ""
echo "=== STORAGE POOLS ==="
curl -s -b $COOKIE "$BASE/api/infrastructure/storage" | python3 -m json.tool 2>/dev/null || curl -s -b $COOKIE "$BASE/api/infrastructure/storage"

# Test Configs API
echo ""
echo "=== SAVED CONFIGS ==="
curl -s -b $COOKIE "$BASE/api/infrastructure/configs" | python3 -m json.tool 2>/dev/null || curl -s -b $COOKIE "$BASE/api/infrastructure/configs"

# Test Template API
echo ""
echo "=== CONFIG TEMPLATE ==="
curl -s -b $COOKIE "$BASE/api/infrastructure/configs/template" | python3 -m json.tool 2>/dev/null || curl -s -b $COOKIE "$BASE/api/infrastructure/configs/template"

echo ""
echo "=== ALL TESTS DONE ==="
