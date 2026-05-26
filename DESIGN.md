# Design Document — MLIR Loop Parallelization Detector

---

## Problem Statement

Modern Fortran programs contain loops that are candidates for parallel
execution (e.g., OpenMP). Identifying which loops are safe to parallelize
requires dependency analysis. Doing this manually is error-prone and does
not scale. This tool automates that analysis using the compiler's own
intermediate representation (MLIR) as the analysis substrate.

---

## Approach

Instead of analyzing Fortran source text directly, we compile the source
to MLIR using flang-new and analyze the resulting FIR (Fortran IR) dialect.
This gives us a structured, SSA-form representation where array accesses
and control flow are explicit and unambiguous.

Pipeline:

    Fortran source (.f90)
          |
          v
    flang-new -fc1 -emit-mlir
          |
          v
    MLIR file (.mlir)   [FIR dialect]
          |
          v
    Symbol Table Builder
    (maps SSA values -> variable names via fir.declare + uniq_name)
          |
          v
    Loop Extractor
    (finds fir.do_loop / scf.for regions by brace-depth tracking)
          |
          v
    Access Analyzer
    (traces fir.array_coor -> fir.load / fir.store chains per loop)
          |
          v
    Dependency Classifier
    (detects read-write conflicts, reduction patterns)
          |
          v
    Classification Report

---

## Design Decisions

### 1. Use MLIR over source-level analysis

Alternatives considered:
- Parse Fortran source directly with regex
- Use GFortran's dump (-fdump-tree-all)
- Use LLVM IR after full lowering

MLIR was chosen because:
- FIR dialect preserves array structure (fir.array_coor keeps base + index)
- Variable names survive via fir.declare annotations (uniq_name)
- Available directly from flang-new without additional passes
- Structured regions make loop boundary extraction reliable

### 2. SSA chain tracing for access detection

Array accesses in FIR follow a two-step pattern:
    %ref = fir.array_coor %base(%shape) %index
    %val = fir.load %ref        (read)
    fir.store %val to %ref      (write)

We track the coord_map (ref SSA -> array name) built from array_coor,
then match load/store against that map. This avoids false positives from
scalar loads/stores that use unrelated SSA values.

### 3. Dependency classification rules

    Condition                              Classification
    -------------------------------------------------------
    Same array appears in both READ        Not safe
    and WRITE sets within one loop         (loop-carried dependency)

    Writes only to scalars, reads          Reduction
    from arrays                            (safe with reduction clause)

    All writes to arrays not also read     Likely parallelizable

### 4. Symbol table from fir.declare

flang-new 23 emits variable names via:
    %3 = fir.declare %1(%2) {uniq_name = "_QFEa"}

The uniq_name uses Fortran name mangling (_QFE prefix for local variables).
We strip the prefix to recover the original name (a, b, sum, etc.).

---

## Alternatives Considered

| Alternative                  | Reason Not Used                              |
|------------------------------|----------------------------------------------|
| Source-level regex parsing   | Cannot handle aliasing, complex expressions  |
| Polyhedral analysis (isl)    | Too heavy, requires affine loop structure    |
| LLVM IR analysis             | Array structure lost after lowering          |
| Full OpenMP pragma insertion | Out of scope; classification only            |
| GFortran GIMPLE dump         | Tied to GCC, not LLVM ecosystem              |

---

## Known Limitations

- Does not track inter-procedural dependencies (function calls inside loops)
- Indirect indexing (A(B(i))) is not symbolically resolved
- Assumes FIR dialect; HLFIR (newer flang) would need additional patterns
- Nested loops are treated independently, not hierarchically
