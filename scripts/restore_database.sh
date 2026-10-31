#!/usr/bin/env bash
# CareerLens Production SQLite Restore Script
# Safely restores a database from an authenticated SQLite backup with integrity verification.
# Never overwrites the live production database unless explicitly confirmed with --confirm-live-overwrite.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIVE_DB_PRIMARY="${PROJECT_ROOT}/backend/careerlens.db"
LIVE_DB_SECONDARY="${PROJECT_ROOT}/careerlens.db"

usage() {
    echo "Usage: $0 <backup_file> <target_database_path> [--confirm-live-overwrite]"
    echo ""
    echo "Arguments:"
    echo "  backup_file             Path to the valid SQLite backup file to restore."
    echo "  target_database_path    Path where the database should be restored."
    echo "  --confirm-live-overwrite Optional flag required ONLY if restoring over the live production database."
    echo ""
    echo "Example:"
    echo "  $0 backups/careerlens_backup_20261031.db /tmp/restored_test.db"
    exit 1
}

if [[ $# -lt 2 ]]; then
    usage
fi

BACKUP_FILE="$1"
TARGET_DB="$2"
CONFIRM_FLAG="${3:-}"

# 1. Validate that the backup file exists
if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "[-] Error: Backup file not found at: ${BACKUP_FILE}" >&2
    exit 1
fi

# 2. Validate backup file integrity before attempting restore
echo "[+] Validating backup file integrity..."
INTEGRITY="$(sqlite3 "${BACKUP_FILE}" "PRAGMA integrity_check;" 2>&1 || true)"
if [[ "${INTEGRITY}" != "ok" ]]; then
    echo "[-] Error: Backup file failed integrity check: ${INTEGRITY}" >&2
    exit 1
fi
echo "[✓] Backup file integrity verified (status: ok)."

# 3. Guard against accidental live database overwrite
RESOLVED_TARGET="$(cd "$(dirname "${TARGET_DB}")" 2>/dev/null && pwd)/$(basename "${TARGET_DB}")" || RESOLVED_TARGET="${TARGET_DB}"
RESOLVED_LIVE_1="$(cd "$(dirname "${LIVE_DB_PRIMARY}")" 2>/dev/null && pwd)/$(basename "${LIVE_DB_PRIMARY}")" || RESOLVED_LIVE_1="${LIVE_DB_PRIMARY}"
RESOLVED_LIVE_2="$(cd "$(dirname "${LIVE_DB_SECONDARY}")" 2>/dev/null && pwd)/$(basename "${LIVE_DB_SECONDARY}")" || RESOLVED_LIVE_2="${LIVE_DB_SECONDARY}"

IS_LIVE_TARGET=false
if [[ "${RESOLVED_TARGET}" == "${RESOLVED_LIVE_1}" || "${RESOLVED_TARGET}" == "${RESOLVED_LIVE_2}" ]]; then
    IS_LIVE_TARGET=true
fi

if [[ "${IS_LIVE_TARGET}" == "true" ]]; then
    if [[ "${CONFIRM_FLAG}" != "--confirm-live-overwrite" ]]; then
        echo "[-] ERROR: Destination is the LIVE PRODUCTION DATABASE: ${RESOLVED_TARGET}" >&2
        echo "[-] Overwriting the live database is blocked by default." >&2
        echo "[-] To proceed, you must explicitly pass: --confirm-live-overwrite" >&2
        exit 2
    fi

    echo "[!] CAUTION: Target is the live production database. Creating pre-restore safety backup..."
    SAFETY_BACKUP_DIR="${PROJECT_ROOT}/backups"
    mkdir -p "${SAFETY_BACKUP_DIR}"
    SAFETY_BACKUP="${SAFETY_BACKUP_DIR}/safety_backup_pre_restore_$(date +"%Y%m%d_%H%M%S").db"
    if [[ -f "${RESOLVED_TARGET}" ]]; then
        sqlite3 "${RESOLVED_TARGET}" ".backup '${SAFETY_BACKUP}'"
        echo "[✓] Safety backup created: ${SAFETY_BACKUP}"
    fi
fi

# 4. Clean up any stale WAL/SHM files for the target database before restoration
TARGET_DIR="$(dirname "${RESOLVED_TARGET}")"
mkdir -p "${TARGET_DIR}"

if [[ -f "${RESOLVED_TARGET}-wal" ]]; then
    echo "[+] Removing stale WAL file: ${RESOLVED_TARGET}-wal"
    rm -f "${RESOLVED_TARGET}-wal"
fi

if [[ -f "${RESOLVED_TARGET}-shm" ]]; then
    echo "[+] Removing stale SHM file: ${RESOLVED_TARGET}-shm"
    rm -f "${RESOLVED_TARGET}-shm"
fi

# 5. Restore safely using SQLite's online backup mechanism
echo "[+] Restoring database to: ${RESOLVED_TARGET}..."
sqlite3 "${BACKUP_FILE}" ".backup '${RESOLVED_TARGET}'"

# 6. Verify restored database integrity
echo "[+] Verifying restored database integrity..."
RESTORE_CHECK="$(sqlite3 "${RESOLVED_TARGET}" "PRAGMA integrity_check;" 2>&1 || true)"
if [[ "${RESTORE_CHECK}" != "ok" ]]; then
    echo "[-] Error: Restored database failed integrity check: ${RESTORE_CHECK}" >&2
    exit 1
fi

FILE_SIZE="$(du -h "${RESOLVED_TARGET}" | cut -f1)"
echo "[✓] Database restoration completed successfully!"
echo "[✓] Target: ${RESOLVED_TARGET} (${FILE_SIZE})"
echo "[✓] Integrity status: ok"
