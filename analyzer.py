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

    for line in lines:
        line = line.strip()

        # LOAD
        load_match = re.search(r"fir\.load\s+(%\w+)", line)
        if load_match:
            memory_ops.append({
                "type": "load",
                "ssa": load_match.group(1),
                "array": "unknown",
                "index": "unknown"
            })

        # STORE
        store_match = re.search(r"fir\.store\s+(%\w+)\s+to\s+(%\w+)", line)
        if store_match:
            memory_ops.append({
                "type": "store",
                "ssa": store_match.group(1),
                "array": store_match.group(2),
                "index": "unknown"
            })

    return memory_ops


# -------- Dependency + Reduction Analysis --------
def dependency_analysis(memory_ops):
    dependencies = []
    reductions = []

    for i in range(len(memory_ops)):
        for j in range(len(memory_ops)):
            if i == j:
                continue

            op1 = memory_ops[i]
            op2 = memory_ops[j]

            # Only compare same memory target
            if op1["array"] != op2["array"]:
                continue

            # Reduction pattern: value reused
            if op1["type"] == "store" and op2["type"] == "load":
                if op1["ssa"] == op2["ssa"]:
                    reductions.append(op1["array"])

            # Multiple writes → dependency risk
            if op1["type"] == "store" and op2["type"] == "store":
                dependencies.append((op1, op2))

    return dependencies, reductions


# -------- Main Analyzer --------
def analyze_mlir(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    loops = extract_loops(content)

    if not loops:
        print("❌ No loops found.")
        return

    for idx, loop in enumerate(loops):
        print(f"\n🔍 Loop {idx+1}")

        ops = parse_loop(loop)

        if not ops:
            print("  (No memory operations detected)")
            continue

        for op in ops:
            print(f"  {op['type'].upper()} → {op['array']} (SSA: {op['ssa']})")

        deps, reds = dependency_analysis(ops)

        if reds:
            print("  ⚠️ Reduction detected")

        if deps:
            print("  ❌ Possible dependency (multiple writes to same memory)")
        elif not reds:
            print("  ✅ Likely parallelizable")


# -------- Entry --------
if __name__ == "__main__":
    analyze_mlir("test2.mlir")
