#!/bin/bash
pkill -f 'web_server' 2>/dev/null
pkill -f 'oradba' 2>/dev/null
sleep 2
nohup oradba install gui --host 0.0.0.0 > /tmp/gui.log 2>&1 &
sleep 4
echo "HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/login)"
echo "---LOG---"
tail -15 /tmp/gui.log
