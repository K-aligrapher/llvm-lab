#!/bin/bash
set -e

echo "[build] Checking dependencies..."

if ! command -v flang-new &> /dev/null; then
    echo "ERROR: flang-new not found. Install LLVM/Flang first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found."
    exit 1
fi

echo "[build] All dependencies found."
echo "[build] Nothing to compile — tool runs directly via Python."
echo "[build] Done."
