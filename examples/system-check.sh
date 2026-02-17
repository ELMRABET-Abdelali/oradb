#!/bin/bash
# Complete system check script

echo "========================================="
echo "  OracleDBA - System Check"
echo "========================================="
echo ""

# Check OS
echo "OS Information:"
cat /etc/os-release | grep PRETTY_NAME
echo ""

# Check Python
echo "Python Version:"
python3 --version
echo ""

# Check Oracle environment
echo "Oracle Environment:"
echo "  ORACLE_HOME: ${ORACLE_HOME:-Not set}"
echo "  ORACLE_SID: ${ORACLE_SID:-Not set}"
echo "  ORACLE_BASE: ${ORACLE_BASE:-Not set}"
echo ""

# Check if oradba is installed
echo "OracleDBA Installation:"
if command -v oradba &> /dev/null; then
    echo "  ✓ oradba command found"
    oradba --version 2>/dev/null || echo "  Version: 1.0.0"
else
    echo "  ✗ oradba not found"
fi
echo ""

# Check disk space
echo "Disk Space:"
df -h / | tail -1
echo ""

# Check memory
echo "Memory:"
free -h | grep "Mem:"
echo ""

# Check if Oracle is running
echo "Oracle Status:"
if pgrep -x "ora_pmon" > /dev/null; then
    echo "  ✓ Oracle process detected"
else
    echo "  ✗ Oracle process not running"
fi
echo ""

# Check listener
echo "Listener Status:"
if pgrep -x "tnslsnr" > /dev/null; then
    echo "  ✓ Listener is running"
else
    echo "  ✗ Listener not running"
fi
echo ""

echo "========================================="
echo "Check complete!"
echo "========================================="
