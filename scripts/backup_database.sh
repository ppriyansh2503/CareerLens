#!/usr/bin/env bash
# CareerLens Production SQLite Live Backup Script
# Performs non-blocking live online backup using SQLite backup API and runs integrity check.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${PROJECT_ROOT}/backups"
DB_PATH="${PROJECT_ROOT}/backend/careerlens.db"

# Fallback if db is in project root
if [[ ! -f "${DB_PATH}" && -f "${PROJECT_ROOT}/careerlens.db" ]]; then
    DB_PATH="${PROJECT_ROOT}/careerlens.db"
fi

if [[ ! -f "${DB_PATH}" ]]; then
    echo "[-] Error: Source database not found at ${DB_PATH}" >&2
    exit 1
fi

mkdir -p "${BACKUP_DIR}"

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
BACKUP_FILE="${BACKUP_DIR}/careerlens_backup_${TIMESTAMP}.db"

echo "[+] Initiating live backup of ${DB_PATH}..."
sqlite3 "${DB_PATH}" ".backup '${BACKUP_FILE}'"

echo "[+] Verifying backup integrity..."
INTEGRITY="$(sqlite3 "${BACKUP_FILE}" "PRAGMA integrity_check;")"

if [[ "${INTEGRITY}" != "ok" ]]; then
    echo "[-] Integrity check failed: ${INTEGRITY}" >&2
    rm -f "${BACKUP_FILE}"
    exit 1
fi

FILE_SIZE="$(du -h "${BACKUP_FILE}" | cut -f1)"
echo "[✓] Backup verified successfully: ${BACKUP_FILE} (${FILE_SIZE})"

# Retain only the last 14 backups
echo "[+] Pruning backups older than the most recent 14..."
ls -t "${BACKUP_DIR}"/careerlens_backup_*.db 2>/dev/null | tail -n +15 | xargs rm -f 2>/dev/null || true
echo "[✓] Backup process complete."
