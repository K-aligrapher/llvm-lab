#!/bin/bash
set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: ./run.sh <fortran_file.f90>"
    exit 1
fi

FORTRAN_FILE=$1

if [ ! -f "$FORTRAN_FILE" ]; then
    echo "ERROR: File '$FORTRAN_FILE' not found."
    exit 1
fi

echo "[run] Analyzing: $FORTRAN_FILE"
python3 mlir_loop_analyzer.py --file "$FORTRAN_FILE"
