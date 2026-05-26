#!/usr/bin/env python3

import argparse
import pathlib
import subprocess
import re
import sys


# ============================================================
# Generate MLIR from Fortran
# ============================================================

def generate_mlir(fortran_file):
    output_mlir = pathlib.Path(fortran_file).stem + ".mlir"
    cmd = ["flang-new", "-fc1", "-emit-mlir", fortran_file, "-o", output_mlir]
    result = subprocess.run(cmd, capture_output=True, text=True)
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
        stripped = line.strip()

        is_loop_start = (
            re.search(r'\bfir\.do_loop\b', stripped) or
            re.search(r'\bscf\.for\b', stripped)
        )

        if is_loop_start and start is None:
            start = i
            depth = line.count("{") - line.count("}")
            continue

        if start is not None:
            depth += line.count("{") - line.count("}")
            if depth <= 0 and line.count("}") > 0:
                loops.append("\n".join(lines[start:i+1]))
                start = None
                depth = 0

    return loops


# ============================================================
# Build symbol table
# ============================================================

def build_symbol_table(lines):
    symbols = {}

    for line in lines:
        s = line.strip()

        # ----------------------------------------------------------
        # fir.declare with uniq_name  (what flang 23 actually emits)
        # e.g. %3 = fir.declare %1(%2) {uniq_name = "_QFEa"} : ...
        # ----------------------------------------------------------
        m = re.search(
            r'(%\w+)\s*=\s*fir\.declare\s.*uniq_name\s*=\s*"([^"]+)"',
            s
        )
        if m:
            ssa  = m.group(1)
            # _QFEa  ->  a,   _QFEsuma  ->  suma
            raw  = m.group(2)
            name = re.sub(r'^_QF\w*E', '', raw) or raw   # strip Fortran mangling
            symbols[ssa] = name
            continue

        # ----------------------------------------------------------
        # Fallback: fir.alloca / fir.declare with bindc_name
        # ----------------------------------------------------------
        m = re.search(
            r'(%\w+)\s*=\s*(?:fir\.alloca|fir\.declare).*bindc_name\s*=\s*"([^"]+)"',
            s
        )
        if m:
            symbols[m.group(1)] = m.group(2)

    return symbols


# ============================================================
# Analyze loop accesses
# ============================================================

def analyze_loop(loop_text, symbols):
    accesses  = []
    coord_map = {}   # ref SSA  ->  array name

    for line in loop_text.splitlines():
        s = line.strip()

        # ---- fir.array_coor  -----------------------------------
        # %30 = fir.array_coor %6(%5) %29 : (...)
        m = re.search(r'(%\w+)\s*=\s*fir\.array_coor\s+(%\w+)', s)
        if m:
            cssa, base = m.group(1), m.group(2)
            if base in symbols:
                coord_map[cssa] = symbols[base]

        # ---- fir.coordinate_of  --------------------------------
        m = re.search(r'(%\w+)\s*=\s*fir\.coordinate_of\s+(%\w+)', s)
        if m:
            cssa, base = m.group(1), m.group(2)
            if base in symbols:
                coord_map[cssa] = symbols[base]

        # ---- hlfir.designate  ----------------------------------
        m = re.search(r'(%\w+)\s*=\s*hlfir\.designate\s+(%\w+)', s)
        if m:
            cssa, base = m.group(1), m.group(2)
            if base in symbols:
                coord_map[cssa] = symbols[base]

        # ---- fir.load / memref.load  ---------------------------
        m = re.search(r'(%\w+)\s*=\s*(?:fir|memref)\.load\s+(%\w+)', s)
        if m:
            addr = m.group(2)
            if addr in coord_map:
                accesses.append({"type": "read", "array": coord_map[addr]})

        # ---- fir.store / memref.store  -------------------------
        m = re.search(r'(?:fir|memref)\.store\s+(%\w+)\s+to\s+(%\w+)', s)
        if m:
            addr = m.group(2)
            if addr in coord_map:
                accesses.append({"type": "write", "array": coord_map[addr]})

        # ---- hlfir.assign  -------------------------------------
        m = re.search(r'hlfir\.assign\s+(%\w+)\s+to\s+(%\w+)', s)
        if m:
            src, dst = m.group(1), m.group(2)
            if dst in coord_map:
                accesses.append({"type": "write", "array": coord_map[dst]})
            if src in coord_map:
                accesses.append({"type": "read",  "array": coord_map[src]})

    return accesses


# ============================================================
# Classify loop
# ============================================================

def classify_loop(accesses):
    reads  = set()
    writes = {}

    for a in accesses:
        arr = a["array"]
        if a["type"] == "read":
            reads.add(arr)
        else:
            writes[arr] = writes.get(arr, 0) + 1

    # Loop-carried dependency: same array is both read and written
    for arr in writes:
        if arr in reads:
            return (
                "Not safe",
                f"loop-carried dependency — array '{arr}' is both read and written"
            )

    # Pure reduction: no array writes, only scalar reads (sum = sum + A(i))
    if not writes and reads:
        return (
            "Reduction (safe with reduction clause)",
            "only reads from arrays; scalar accumulation detected"
        )

    return (
        "Likely parallelizable",
        "no loop-carried dependencies detected"
    )


# ============================================================
# Main analysis
# ============================================================

def analyze_mlir(mlir_file):
    text  = pathlib.Path(mlir_file).read_text()
    lines = text.splitlines()

    symbols = build_symbol_table(lines)
    loops   = extract_loops(text)

    print(f"\nMLIR  : {mlir_file}")
    print(f"Arrays: { {k: v for k, v in symbols.items()} }")
    print(f"Loops : {len(loops)}\n")

    for i, loop in enumerate(loops, 1):
        accesses          = analyze_loop(loop, symbols)
        status, reason    = classify_loop(accesses)

        print(f"Loop {i}: {status}")
        print(f"  Reason : {reason}")

        if accesses:
            print("  Accesses:")
            for acc in accesses:
                print(f"    {acc['type'].upper():5}  {acc['array']}")
        else:
            print("  (no array accesses detected)")
        print()


# ============================================================
# Entry point
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="MLIR Loop Parallelization Detector")
    parser.add_argument("--file", required=True, help="Fortran source file")
    args    = parser.parse_args()
    mlir_file = generate_mlir(args.file)
    analyze_mlir(mlir_file)

if __name__ == "__main__":
    main()
