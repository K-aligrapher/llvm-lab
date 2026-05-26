#!/usr/bin/env python3

import argparse
import pathlib
import subprocess
import tempfile
import re
import sys

# ============================================================
# Generate MLIR from Fortran
# ============================================================

def generate_mlir(fortran_file):

    output_mlir = pathlib.Path(fortran_file).stem + ".mlir"

    cmd = [
        "flang-new",
        "-fc1",
        "-emit-mlir",
        fortran_file,
        "-o",
        output_mlir
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(result.stderr)
        sys.exit("MLIR generation failed")

    return output_mlir


# ============================================================
# Extract loops
# ============================================================

def extract_loops(text):

    loops = []

    lines = text.splitlines()

    start = None
    depth = 0

    for i, line in enumerate(lines):

        if ("fir.do_loop" in line or "scf.for" in line) and "{" in line:

            start = i
            depth = line.count("{") - line.count("}")

        elif start is not None:

            depth += line.count("{")
            depth -= line.count("}")

            if depth == 0:

                loop_text = "\n".join(lines[start:i+1])

                loops.append(loop_text)

                start = None

    return loops


# ============================================================
# Build FIR symbol table
# ============================================================

def build_symbol_table(lines):

    symbols = {}

    arrays = []

    for line in lines:

        # ----------------------------------------------------
        # Match array allocations
        #
        # Example:
        # %3 = fir.alloca !fir.array<10xi32>
        # ----------------------------------------------------

        if "fir.alloca" in line and "array" in line:

            m = re.search(r'(%\d+)', line)

            if m:
                arrays.append(m.group(1))

        # ----------------------------------------------------
        # Match scalars with bindc_name
        # ----------------------------------------------------

        m = re.search(
            r'(%\d+)\s*=\s*fir\.alloca.*bindc_name\s*=\s*"([^"]+)"',
            line
        )

        if m:

            ssa = m.group(1)
            name = m.group(2)

            symbols[ssa] = name

    # --------------------------------------------------------
    # Fallback for unnamed arrays
    # --------------------------------------------------------

    if len(arrays) >= 1:
        symbols[arrays[0]] = "A"

    if len(arrays) >= 2:
        symbols[arrays[1]] = "B"

    if len(arrays) >= 3:
        symbols[arrays[2]] = "C"

    return symbols


# ============================================================
# Analyze loop memory accesses
# ============================================================

def analyze_loop(loop_text, symbols):

    accesses = []

    coord_map = {}

    lines = loop_text.splitlines()

    for line in lines:

        line = line.strip()

        # ====================================================
        # fir.array_coor
        #
        # Example:
        # %34 = fir.array_coor %3(%2) %33
        # ====================================================

        m = re.search(
            r'(%\d+)\s*=\s*fir\.array_coor\s+(%\d+)\(',
            line
        )

        if m:

            coord_ssa = m.group(1)
            base_array = m.group(2)

            if base_array in symbols:

                coord_map[coord_ssa] = symbols[base_array]

        # ====================================================
        # fir.coordinate_of
        # ====================================================

        m = re.search(
            r'(%\d+)\s*=\s*fir\.coordinate_of\s+(%\d+)',
            line
        )

        if m:

            coord_ssa = m.group(1)
            base_array = m.group(2)

            if base_array in symbols:

                coord_map[coord_ssa] = symbols[base_array]

        # ====================================================
        # LOAD
        # ====================================================

        m = re.search(
            r'(%\d+)\s*=\s*fir\.load\s+(%\d+)',
            line
        )

        if m:

            address = m.group(2)

            if address in coord_map:

                accesses.append({
                    "type": "read",
                    "array": coord_map[address]
                })

        # ====================================================
        # STORE
        # ====================================================

        m = re.search(
            r'fir\.store\s+(%\d+)\s+to\s+(%\d+)',
            line
        )

        if m:

            address = m.group(2)

            if address in coord_map:

                accesses.append({
                    "type": "write",
                    "array": coord_map[address]
                })

    return accesses


# ============================================================
# Dependency analysis
# ============================================================

def classify_loop(accesses):

    write_count = {}

    read_arrays = set()

    for access in accesses:

        if access["type"] == "write":

            arr = access["array"]

            write_count[arr] = write_count.get(arr, 0) + 1

        elif access["type"] == "read":

            read_arrays.add(access["array"])

    # --------------------------------------------------------
    # Multiple writes to same array
    # --------------------------------------------------------

    for arr, count in write_count.items():

        if count > 1 and arr in read_arrays:

            return (
                "Not safe",
                f"possible dependency on array '{arr}'"
            )

    return (
        "Likely parallelizable",
        "no repeated dependent writes detected"
    )


# ============================================================
# Main MLIR analysis
# ============================================================

def analyze_mlir(mlir_file):

    text = pathlib.Path(mlir_file).read_text()

    lines = text.splitlines()

    symbols = build_symbol_table(lines)

    loops = extract_loops(text)

    print(f"\nMLIR: {mlir_file}")
    print(f"Loops found: {len(loops)}")

    for i, loop in enumerate(loops, 1):

        accesses = analyze_loop(loop, symbols)

        status, reason = classify_loop(accesses)

        print(f"\nLoop {i}: {status}")
        print(f"Reason: {reason}")

        if accesses:

            print("Accesses:")

            for access in accesses:

                print(
                    f"  {access['type'].upper()} {access['array']}"
                )

        else:

            print("  No array accesses detected")


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="MLIR Loop Parallelization Detector"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Fortran source file"
    )

    args = parser.parse_args()

    mlir_file = generate_mlir(args.file)

    analyze_mlir(mlir_file)


if __name__ == "__main__":
    main()
