# MLIR Loop Parallelization Detector

A static analysis tool that detects whether loops in Fortran programs
are safe to parallelize, using MLIR emitted by flang-new (LLVM Flang).

---

## What It Does

- Compiles a Fortran source file to MLIR using flang-new
- Extracts all fir.do_loop / scf.for loop regions
- Builds a symbol table from fir.declare annotations
- Traces array accesses (fir.array_coor, fir.load, fir.store)
- Classifies each loop as:
    - Likely parallelizable   — no loop-carried dependencies
    - Not safe                — same array is read and written (dependency)
    - Reduction               — scalar accumulation over array reads

---

## Dependencies

- Python 3.6+
- flang-new (LLVM Flang, tested with version 23.0.0)

Install LLVM/Flang on Ubuntu:
    sudo apt install flang

Or build from source:
    https://github.com/llvm/llvm-project

---

## Repository Structure

    loop-detector/
    ├── src/
    │   └── mlir_loop_analyzer.py   # Main analysis tool
    ├── testcases/
    │   ├── test.f90                # Basic test (parallel, dependency, reduction)
    │   ├── test_parallel.f90       # All loops parallelizable
    │   ├── test_dependency.f90     # Loop-carried dependency cases
    │   ├── test_reduction.f90      # Reduction loop cases
    │   └── test_nested.f90         # Nested loop cases
    ├── archives 
    ├── build.sh                    # Dependency check script
    ├── run.sh                      # Run script
    ├── README.md
    ├── DESIGN.md
    ├── IMPLEMENTATION.md
    └── EVALUATION.md

---

## How to Run

    chmod +x build.sh run.sh

    ./build.sh
    ./run.sh testcases/test.f90

---

## Example Output

    MLIR  : test.mlir
    Arrays: {'%3': 'a', '%6': 'b'}
    Loops : 3

    Loop 1: Likely parallelizable
      Reason : no loop-carried dependencies detected
      Accesses:
        READ   b
        WRITE  a

    Loop 2: Not safe
      Reason : loop-carried dependency — array 'a' is both read and written
      Accesses:
        READ   a
        WRITE  a

    Loop 3: Reduction (safe with reduction clause)
      Reason : only reads from arrays; scalar accumulation detected
      Accesses:
        READ   a

---

## Test Cases

| Test File           | Loop | Expected Result                        |
|---------------------|------|----------------------------------------|
| test.f90            | 1    | Likely parallelizable                  |
| test.f90            | 2    | Not safe (loop-carried dependency)     |
| test.f90            | 3    | Reduction (safe with reduction clause) |
| test_parallel.f90   | all  | Likely parallelizable                  |
| test_dependency.f90 | all  | Not safe                               |
| test_reduction.f90  | all  | Reduction                              |
| test_nested.f90     | all  | Varies                                 |

---

## Limitations

- Analyzes MLIR at the FIR dialect level (before full lowering)
- Does not track indirect array indexing across function calls
- Reduction detection is conservative (scalar write + array read pattern)
- Nested loops are extracted and analyzed independently

---

## Author

Developed as part of a compiler analysis project using LLVM/Flang and MLIR.
