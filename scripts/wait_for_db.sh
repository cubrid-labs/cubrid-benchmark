#!/usr/bin/env bash

set -euo pipefail

CUBRID_HOST="${CUBRID_HOST:-localhost}"
CUBRID_PORT="${CUBRID_PORT:-33000}"
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
TIMEOUT_SECONDS=120
SLEEP_SECONDS=2

check_port() {
  python3 - "$1" "$2" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)
try:
    result = sock.connect_ex((host, port))
finally:
    sock.close()
sys.exit(0 if result == 0 else 1)
PY
}

start_time="$(date +%s)"
echo "Waiting for CUBRID at ${CUBRID_HOST}:${CUBRID_PORT} and MySQL at ${MYSQL_HOST}:${MYSQL_PORT}"

while true; do
  cubrid_ok=0
  mysql_ok=0

  if check_port "${CUBRID_HOST}" "${CUBRID_PORT}"; then
    cubrid_ok=1
  fi

  if check_port "${MYSQL_HOST}" "${MYSQL_PORT}"; then
    mysql_ok=1
  fi

  if [ "${cubrid_ok}" -eq 1 ] && [ "${mysql_ok}" -eq 1 ]; then
    echo "Both databases are reachable."
    exit 0
  fi

  now="$(date +%s)"
  elapsed=$((now - start_time))
  if [ "${elapsed}" -ge "${TIMEOUT_SECONDS}" ]; then
    echo "Timed out after ${TIMEOUT_SECONDS}s waiting for database readiness."
    exit 1
  fi

  echo "Still waiting... (${elapsed}s elapsed)"
  sleep "${SLEEP_SECONDS}"
done
