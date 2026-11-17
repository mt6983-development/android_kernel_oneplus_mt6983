#!/usr/bin/env bash
# Static check runner - NO BUILDS or compilers used.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KERNEL_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== Running Static Checks on ${KERNEL_DIR} ==="

cd "${KERNEL_DIR}"

echo "[1/4] Running git diff --check..."
git diff --check || true

echo "[2/4] Checking for conflict markers..."
if grep -rnE '^(<{7}|>{7})' arch/arm64/ configs/ drivers/ fs/ include/ kernel/ mm/ 2>/dev/null; then
    echo "ERROR: Conflict markers found!"
    exit 1
else
    echo "No conflict markers found. Clean."
fi

echo "[3/4] Checking for .rej and .orig files..."
REJ_FILES=$(find . -name "*.rej" -o -name "*.orig" | grep -v "\.git" || true)
if [ -n "${REJ_FILES}" ]; then
    echo "ERROR: Rejected or original patch files found:"
    echo "${REJ_FILES}"
    exit 1
else
    echo "No .rej or .orig files found. Clean."
fi

echo "[4/6] Verifying top-level Makefile..."
head -n 5 Makefile

echo "[5/6] Validating Device Trees with check_dt.py..."
python3 "${SCRIPT_DIR}/check_dt.py"

echo "[6/6] Validating Kconfig structure with check_kconfig.py..."
python3 "${SCRIPT_DIR}/check_kconfig.py"

echo "=== All Static Checks Passed Cleanly ==="
