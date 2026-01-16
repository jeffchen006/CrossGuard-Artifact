#!/usr/bin/env python3

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


FORGE_CMD = [
    "forge",
    "test",
    "--gas-report",
    "--evm-version",
    "cancun",
    "-vvv",
    "--match-contract",
    "CrossGuardGasComparisonTest",
    "--optimizer-runs",
    "10000",
]


@dataclass(frozen=True)
class GasRow:
    function_name: str
    min_gas: int
    avg_gas: int
    median_gas: int
    max_gas: int
    calls: int


class SafeExprError(Exception):
    pass


def _safe_eval_add_sub(expr: str) -> int:
    """Safely evaluate an expression containing only integers, + and -.

    Examples: "42758 - 26358 - 6352 - 9708", "10+2-3".
    """

    def _check(node: ast.AST) -> None:
        allowed = (
            ast.Expression,
            ast.BinOp,
            ast.Add,
            ast.Sub,
            ast.UnaryOp,
            ast.UAdd,
            ast.USub,
            ast.Constant,
        )
        if not isinstance(node, allowed):
            raise SafeExprError(f"Unsupported syntax in expression: {type(node).__name__}")
        for child in ast.iter_child_nodes(node):
            _check(child)

    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise SafeExprError(f"Invalid expression syntax: {expr!r}") from e

    _check(tree)

    def _eval(node: ast.AST) -> int:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, int):
                raise SafeExprError("Only integer constants are allowed")
            return int(node.value)
        if isinstance(node, ast.UnaryOp):
            val = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return val
            if isinstance(node.op, ast.USub):
                return -val
            raise SafeExprError("Only unary + and - are allowed")
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            raise SafeExprError("Only + and - are allowed")
        raise SafeExprError(f"Unsupported node: {type(node).__name__}")

    return _eval(tree)


def parse_expected_file(path: Path) -> Dict[str, Tuple[str, int]]:
    """Returns mapping key -> (expr, evaluated_value)."""
    text = path.read_text(encoding="utf-8")
    results: Dict[str, Tuple[str, int]] = {}

    # Matches lines like:
    # "Instrument_prepost": 42758 - 26358 - 6352 - 9708,
    pattern = re.compile(r'^\s*"(?P<key>[^"]+)"\s*:\s*(?P<expr>[^,]+)\s*,?\s*$')
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("#"):
            continue
        m = pattern.match(line)
        if not m:
            continue
        key = m.group("key").strip()
        expr = m.group("expr").strip()
        value = _safe_eval_add_sub(expr)
        results[key] = (expr, value)

    if not results:
        raise RuntimeError(f"No expected expressions found in {path}")

    return results


def run_forge(cmd: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"forge exited with code {proc.returncode}\n{proc.stdout}")
    return proc.stdout


def parse_enter_exit_gas(output: str) -> Tuple[int, int]:
    enter_re = re.compile(r"Enter_Func gas:\s*(\d+)")
    exit_re = re.compile(r"Exit_Func gas:\s*(\d+)")

    enter = enter_re.search(output)
    exit_ = exit_re.search(output)
    if not enter or not exit_:
        raise RuntimeError("Could not find Enter_Func/Exit_Func gas lines in forge output")

    return int(enter.group(1)), int(exit_.group(1))


def parse_gas_report_tables(output: str) -> Dict[str, Dict[str, GasRow]]:
    """Parse gas-report tables into mapping: contract_label -> function_name -> GasRow."""

    # Detect table context from the top header line inside the box.
    # Note: Foundry prints multi-column tables, so the header line looks like:
    # | src/Instrumented_Contract.sol:Contract2Protect Contract |                 | ... |
    # We'll capture the *first* cell (between the first two pipes).
    row_re = re.compile(
        r"^\|\s*(?P<fn>\w+)\s*\|\s*(?P<min>\d+)\s*\|\s*(?P<avg>\d+)\s*\|\s*(?P<median>\d+)\s*\|\s*(?P<max>\d+)\s*\|\s*(?P<calls>\d+)\s*\|\s*$"
    )

    tables: Dict[str, Dict[str, GasRow]] = {}
    current_contract: Optional[str] = None

    for raw_line in output.splitlines():
        line = raw_line.rstrip("\n")

        # Contract header lines include " Contract" and a .sol reference.
        if line.startswith("|") and ".sol:" in line and " Contract" in line:
            parts = line.split("|")
            if len(parts) >= 3:
                first_cell = parts[1].strip()
                if ".sol:" in first_cell and first_cell.endswith("Contract"):
                    # Use the right side of the colon as label, e.g. "Contract2Protect Contract".
                    label = first_cell.split(":", 1)[1].strip()
                    current_contract = label
                    tables.setdefault(current_contract, {})
                    continue

        m = row_re.match(line)
        if m and current_contract:
            row = GasRow(
                function_name=m.group("fn"),
                min_gas=int(m.group("min")),
                avg_gas=int(m.group("avg")),
                median_gas=int(m.group("median")),
                max_gas=int(m.group("max")),
                calls=int(m.group("calls")),
            )
            tables[current_contract][row.function_name] = row

    return tables


def compute_actual_metrics(
    tables: Dict[str, Dict[str, GasRow]],
    enter_gas: int,
    exit_gas: int,
) -> Dict[str, Tuple[str, int]]:
    """Compute metrics using Median gas values (to match expected.txt usage)."""

    def get_median(contract_label_contains: str, function_name: str) -> int:
        for contract_label, rows in tables.items():
            if contract_label_contains in contract_label:
                if function_name not in rows:
                    raise RuntimeError(
                        f"Missing function {function_name} in contract table {contract_label}"
                    )
                return rows[function_name].median_gas
        raise RuntimeError(f"Missing contract table containing {contract_label_contains!r}")

    instr_bare = get_median("Contract2Protect", "updateCurrentTimestampBare")
    instr_topdown = get_median("Contract2Protect", "updateCurrentTimestampTopDown")
    instr_sload = get_median("Contract2Protect", "updateCurrentTimestampTopDownSload")
    instr_sstore = get_median("Contract2Protect", "updateCurrentTimestampTopDownSstore")

    merged_bare = get_median("MergedCrossGuardContract", "updateCurrentTimestampBare")
    merged_topdown = get_median("MergedCrossGuardContract", "updateCurrentTimestampTopDown")
    merged_sload = get_median("MergedCrossGuardContract", "updateCurrentTimestampTopDownSload")
    merged_sstore = get_median("MergedCrossGuardContract", "updateCurrentTimestampTopDownSstore")

    metrics: Dict[str, Tuple[str, int]] = {}

    expr = f"{instr_topdown} - {instr_bare} - {enter_gas} - {exit_gas}"
    metrics["Instrument_prepost"] = (expr, _safe_eval_add_sub(expr))

    expr = f"{instr_sload} - {instr_topdown}"
    metrics["Instrument_sload"] = (expr, _safe_eval_add_sub(expr))

    expr = f"{instr_sstore} - {instr_topdown}"
    metrics["Instrument_sstore"] = (expr, _safe_eval_add_sub(expr))

    expr = f"{merged_topdown} - {merged_bare}"
    metrics["merge_instrument_prepost"] = (expr, _safe_eval_add_sub(expr))

    expr = f"{merged_sload} - {merged_topdown}"
    metrics["merge_instrument_sload"] = (expr, _safe_eval_add_sub(expr))

    expr = f"{merged_sstore} - {merged_topdown}"
    metrics["merge_instrument_sstore"] = (expr, _safe_eval_add_sub(expr))

    return metrics


def format_report(title: str, mapping: Dict[str, Tuple[str, int]]) -> str:
    lines = [title]
    for key in sorted(mapping.keys()):
        expr, val = mapping[key]
        lines.append(f"  {key}: {val}    ({expr})")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Run forge gas experiment, compute metrics, and compare against ./expected.txt"
        )
    )
    ap.add_argument(
        "--expected",
        default="expected.txt",
        help="Path to expected expressions file (default: expected.txt)",
    )
    ap.add_argument(
        "--solc",
        default=None,
        help=(
            "Optional: force forge to use a specific solc (version like '0.8.26'/'solc:0.8.26' "
            "or a path like '/usr/local/bin/solc'). Useful for reproducible Docker runs."
        ),
    )
    ap.add_argument(
        "--no-run",
        action="store_true",
        help="Do not run forge; read forge output from --output-file",
    )
    ap.add_argument(
        "--output-file",
        default=None,
        help="If --no-run is set: path to file containing forge output",
    )
    ap.add_argument(
        "--print-raw",
        action="store_true",
        help="Print the raw forge output (useful for debugging parsing)",
    )

    args = ap.parse_args(argv)

    repo_root = Path(__file__).resolve().parent
    expected_path = (repo_root / args.expected).resolve()

    expected = parse_expected_file(expected_path)

    if args.no_run:
        if not args.output_file:
            raise SystemExit("--no-run requires --output-file")
        output = Path(args.output_file).read_text(encoding="utf-8", errors="replace")
    else:
        cmd = list(FORGE_CMD)
        if args.solc:
            # Insert near the end; forge accepts it anywhere but keeping flags grouped.
            cmd.extend(["--use", args.solc])
        output = run_forge(cmd, cwd=repo_root)

    if args.print_raw:
        print(output)

    enter_gas, exit_gas = parse_enter_exit_gas(output)
    tables = parse_gas_report_tables(output)
    actual = compute_actual_metrics(tables, enter_gas=enter_gas, exit_gas=exit_gas)

    # Compare on keys that exist in expected.txt
    mismatches: list[str] = []
    for key, (_expr, expected_val) in expected.items():
        if key not in actual:
            mismatches.append(f"{key}: missing in actual")
            continue
        actual_val = actual[key][1]
        if actual_val != expected_val:
            mismatches.append(f"{key}: expected {expected_val}, actual {actual_val}")

    print(format_report("Expected (evaluated from expected.txt):", expected))
    print()
    print(format_report("Actual (computed from forge output):", actual))
    print()

    if mismatches:
        print("MISMATCHES:")
        for m in mismatches:
            print(f"  - {m}")
        return 2

    print("OK: actual matches expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
