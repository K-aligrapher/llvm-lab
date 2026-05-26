# Implementation Document — MLIR Loop Parallelization Detector

---

## Technology Stack

| Component        | Technology                        |
|------------------|-----------------------------------|
| Compiler frontend| flang-new (LLVM Flang 23.0.0)     |
| IR format        | MLIR — FIR dialect                |
| Analysis tool    | Python 3.6+                       |
| Regex engine     | Python re module                  |
| Input            | Fortran 90 source files (.f90)    |
| Output           | Terminal classification report    |

---

## Module Breakdown

### 1. generate_mlir(fortran_file)

Invokes flang-new as a subprocess:
    flang-new -fc1 -emit-mlir <file.f90> -o <file.mlir>

Exits with an error message if flang-new returns non-zero.
Returns the path to the generated .mlir file.

### 2. extract_loops(text)

Scans the MLIR text line by line maintaining a brace-depth counter.

Trigger condition:
    Line contains fir.do_loop or scf.for (regex word-boundary match)

Depth tracking:
    depth += count of '{' on line
    depth -= count of '}' on line
    When depth reaches 0 and a '}' was seen -> loop region ends

This correctly handles:
    - Single-line brace opens (fir.do_loop ... {)
    - Nested blocks inside loops (if regions, nested loops)

Returns a list of strings, each being the full text of one loop region.

### 3. build_symbol_table(lines)

Two-pass regex scan over all lines in the MLIR file.

Primary pattern (flang 23 FIR):
    (%\w+)\s*=\s*fir\.declare\s.*uniq_name\s*=\s*"([^"]+)"

Captures:
    Group 1: SSA value (%3, %6, ...)
    Group 2: mangled name (_QFEa, _QFEb, ...)

Name demangling:
    re.sub(r'^_QF\w*E', '', raw_name)
    _QFEa     -> a
    _QFEb     -> b
    _QFEsum   -> sum

Fallback pattern (bindc_name, older flang / HLFIR):
    (%\w+)\s*=\s*(?:fir|hlfir)\.(?:alloca|declare).*bindc_name\s*=\s*"([^"]+)"

Returns dict: { "%3": "a", "%6": "b", "%12": "sum", ... }

### 4. analyze_loop(loop_text, symbols)

Maintains two maps:
    coord_map: { ref_SSA -> array_name }   built from array_coor
    accesses:  list of { type, array }     built from load/store

Patterns matched (in order per line):

    fir.array_coor:
        (%\w+)\s*=\s*fir\.array_coor\s+(%\w+)
        -> coord_map[result] = symbols[base]

    fir.coordinate_of:
        (%\w+)\s*=\s*fir\.coordinate_of\s+(%\w+)
        -> coord_map[result] = symbols[base]

    hlfir.designate:
        (%\w+)\s*=\s*hlfir\.designate\s+(%\w+)
        -> coord_map[result] = symbols[base]

    fir.load / memref.load:
        (%\w+)\s*=\s*(?:fir|memref)\.load\s+(%\w+)
        -> if addr in coord_map: accesses += READ

    fir.store / memref.store:
        (?:fir|memref)\.store\s+(%\w+)\s+to\s+(%\w+)
        -> if addr in coord_map: accesses += WRITE

    hlfir.assign:
        hlfir\.assign\s+(%\w+)\s+to\s+(%\w+)
        -> dst in coord_map: WRITE, src in coord_map: READ

Returns list of { "type": "read"/"write", "array": name }

### 5. classify_loop(accesses)

Builds:
    reads  = set of array names that appear in READ accesses
    writes = dict of array name -> write count

Rules applied in order:

    Rule 1 — Dependency:
        For any array in writes: if it also appears in reads -> Not safe

    Rule 2 — Reduction:
        writes is empty AND reads is non-empty -> Reduction

    Rule 3 — Default:
        Likely parallelizable

---

## Data Flow Example (test.f90 Loop 2)

MLIR lines inside Loop 2:
    %31 = fir.array_coor %3(%2) %30   -> coord_map[%31] = "a"
    %32 = fir.load %31                -> READ  a
    %35 = fir.array_coor %3(%2) %34   -> coord_map[%35] = "a"
    fir.store %32 to %35              -> WRITE a

classify_loop:
    reads  = { "a" }
    writes = { "a": 1 }
    "a" in writes AND "a" in reads -> Not safe

---

## Error Handling

| Scenario                        | Handling                              |
|---------------------------------|---------------------------------------|
| flang-new not installed         | build.sh checks with command -v       |
| flang-new compilation failure   | stderr printed, sys.exit called       |
| No loops found in MLIR          | Reports "Loops: 0", exits cleanly     |
| No accesses detected in a loop  | Reports "(no array accesses detected)"|
| Unknown array SSA value         | Silently skipped (not in symbols dict)|

---

## File Layout

    src/mlir_loop_analyzer.py
    |
    +-- generate_mlir()       line ~15
    +-- extract_loops()       line ~35
    +-- build_symbol_table()  line ~70
    +-- analyze_loop()        line ~115
    +-- classify_loop()       line ~185
    +-- analyze_mlir()        line ~215
    +-- main()                line ~250
