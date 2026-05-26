import re


# -------- Loop Extraction (FIR + SCF) --------
def extract_loops(content):
    loops = []
    lines = content.split("\n")

    start = None
    brace_count = 0

    for i, line in enumerate(lines):
        if "fir.do_loop" in line or "scf.for" in line:
            start = i
            brace_count = line.count("{") - line.count("}")

        elif start is not None:
            brace_count += line.count("{")
            brace_count -= line.count("}")

            if brace_count == 0:
                loop_text = "\n".join(lines[start:i+1])
                loops.append(loop_text)
                start = None

    return loops


# -------- Parse Memory Operations --------
def parse_loop(loop_text):
    lines = loop_text.split("\n")

    memory_ops = []
    addr_map = {}   # SSA addr → (array, index expression)

    for line in lines:
        line = line.strip()

        # -------- Address computation --------
        # Matches: %addr = fir.coordinate_of %A, %i
        coord_match = re.search(
            r"(%\w+)\s*=\s*.*coordinate.*\s+(%\w+),\s*(.+)", line)

        if coord_match:
            addr = coord_match.group(1)
            array = coord_match.group(2)
            index = coord_match.group(3).strip()
            addr_map[addr] = (array, index)

        # -------- LOAD --------
        load_match = re.search(r"fir\.load\s+(%\w+)", line)
        if load_match:
            addr = load_match.group(1)
            array, index = addr_map.get(addr, ("unknown", "unknown"))

            memory_ops.append({
                "type": "load",
                "array": array,
                "index": index,
                "raw": line
            })

        # -------- STORE --------
        store_match = re.search(r"fir\.store\s+(%\w+)\s+to\s+(%\w+)", line)
        if store_match:
            addr = store_match.group(2)
            array, index = addr_map.get(addr, ("unknown", "unknown"))

            memory_ops.append({
                "type": "store",
                "array": array,
                "index": index,
                "raw": line
            })

    return memory_ops


# -------- Index Relationship Detection --------
def normalize_index(idx):
    """Clean index string"""
    return idx.replace(" ", "")


def is_same_index(i1, i2):
    return normalize_index(i1) == normalize_index(i2)


def is_shifted(i1, i2):
    """
    Detect patterns like:
    i vs i-1
    %i vs arith.subi %i, 1
    """
    i1 = normalize_index(i1)
    i2 = normalize_index(i2)

    # simple textual heuristic
    if i1 == i2:
        return False

    # detect "-1" pattern
    if "-1" in i1 or "-1" in i2:
        return True

    # detect MLIR arithmetic form
    if "subi" in i1 or "subi" in i2:
        return True

    return False


# -------- Dependency + Reduction Analysis --------
def dependency_analysis(memory_ops):
    dependency_found = False
    reduction_found = False

    for i in range(len(memory_ops)):
        for j in range(len(memory_ops)):

            if i == j:
                continue

            op1 = memory_ops[i]
            op2 = memory_ops[j]

            if op1["array"] != op2["array"]:
                continue

            # -------- WRITE → READ (RAW dependency) --------
            if op1["type"] == "store" and op2["type"] == "load":

                if is_same_index(op1["index"], op2["index"]):
                    continue

                if is_shifted(op1["index"], op2["index"]):
                    dependency_found = True

            # -------- WRITE → WRITE --------
            if op1["type"] == "store" and op2["type"] == "store":

                if not is_same_index(op1["index"], op2["index"]):
                    # different indices → might still be safe
                    continue

                dependency_found = True

            # -------- REDUCTION DETECTION --------
            # Pattern: sum = sum + A(i)
            if op1["type"] == "store" and op2["type"] == "load":

                if is_same_index(op1["index"], op2["index"]):
                    reduction_found = True

    return dependency_found, reduction_found


# -------- Pretty Print --------
def print_loop_analysis(idx, ops, dep, red):
    print(f"\n🔍 Loop {idx+1}")

    if not ops:
        print("  (No memory ops detected)")
        return

    for op in ops:
        print(f"  {op['type'].upper()} → {op['array']}[{op['index']}]")

    if dep:
        print("  ❌ NOT parallelizable (loop-carried dependency)")
    elif red:
        print("  ⚠️ Reduction (parallelizable with reduction)")
    else:
        print("  ✅ Parallelizable")


# -------- Main Analyzer --------
def analyze_mlir(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    loops = extract_loops(content)

    if not loops:
        print("❌ No loops found.")
        return

    for idx, loop in enumerate(loops):
        ops = parse_loop(loop)
        dep, red = dependency_analysis(ops)
        print_loop_analysis(idx, ops, dep, red)


# -------- Entry --------
if __name__ == "__main__":
    analyze_mlir("test.mlir")
