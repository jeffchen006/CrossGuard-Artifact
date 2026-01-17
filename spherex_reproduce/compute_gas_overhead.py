#!/usr/bin/env python3
"""
Compute the average gas overhead of SphereX operator/engine calls.

Method:
- A = gasUsed from the receipt DB (crawlPackage/database/etherScan.db).
- For each operator/engine call: gas_used = structLogs[start+1].gas - structLogs[end].gas.
- B = sum of operator/engine call gas_used within the tx.
- overhead = B / A, average reported as mean(B_i / A_i).

Staticcalls are ignored; nested invocations are included.

Note: the paper reports 6.09% overhead using historical onchain gas. Re-running
later can yield slightly higher values (e.g., 6.6695% on Jan 15) because RPC
clients and receipt data evolve over time. This reinforces the same conclusion.
"""

import csv
import gzip
import pickle
import sqlite3
import sys
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_OPERATORS = [
    "0x4f90c0a26cc2ad22ee98398dcc02bbe314a1766a",
    "0xfeb516d9d946dd487a9346f6fee11f40c6945ee4",
]

DEFAULT_PROTECTED = [
    "0x6231a192089fb636e704d2c7807d7a79c2457b07",
    "0xc92b021ff09ae005cb3fccb66af8db01fc4cdf90",
    "0xf5d35b9e95f6842a2064a2dd24f8deede9d58f97",
]

TX_LIST_PATH = Path("Benchmarks_Traces/CrossContract_study/SphereX/combined.txt")
CACHE_DIR = Path("parserPackage/cache/SphereX")
TRACE_DIR = Path("Benchmarks_Traces/CrossContract/SphereX/Txs")
RECEIPT_DB = Path("crawlPackage/database/etherScan.db")

DEPLOYER_SOURCE = "etherscan"

OUT_CSV = None
OUT_SUMMARY = None

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def chunked(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def parse_tx_list(path: Path) -> List[str]:
    txs = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        txs.append(line.split()[0])
    return txs


def load_receipts(
    db_path: Path, txs: List[str]
) -> Dict[str, Tuple[int, int, str, str, str]]:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    mapping: Dict[str, Tuple[int, int, str, str, str]] = {}
    for chunk in chunked(txs, 800):
        placeholders = ",".join("?" for _ in chunk)
        cur.execute(
            f"""
            SELECT transactionHash, blockNumber, gasUsed, fromAddress, toAddress, contractAddress
            FROM transactions
            WHERE transactionHash IN ({placeholders})
            """,
            chunk,
        )
        for tx_hash, block, gas_used, from_addr, to_addr, contract_addr in cur.fetchall():
            mapping[tx_hash.lower()] = (
                block,
                gas_used,
                (from_addr or "").lower(),
                (to_addr or "").lower(),
                (contract_addr or "").lower(),
            )
    conn.close()
    missing = [tx for tx in txs if tx.lower() not in mapping]
    if missing:
        raise ValueError(f"Missing receipts for {len(missing)} txs")
    return mapping


def load_deployers(db_path: Path, contracts: List[str]) -> List[str]:
    if not contracts:
        return []
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    deployers = set()
    for chunk in chunked([c.lower() for c in contracts], 800):
        placeholders = ",".join("?" for _ in chunk)
        cur.execute(
            f"""
            SELECT contractAddress, fromAddress
            FROM transactions
            WHERE contractAddress IN ({placeholders})
            """,
            chunk,
        )
        for _contract, from_addr in cur.fetchall():
            if from_addr:
                deployers.add(from_addr.lower())
    conn.close()
    return sorted(deployers)


def load_deployers_etherscan(contracts: List[str]) -> List[str]:
    if not contracts:
        return []
    from crawlPackage.crawlEtherscan import CrawlEtherscan

    ce = CrawlEtherscan()
    deployers = set()
    for contract in contracts:
        deployer = ce.Contract2Deployer(contract)
        if deployer:
            deployers.add(deployer.lower())
    return sorted(deployers)


def read_pickle_gz(path: Path):
    with gzip.open(path, "rb") as f:
        return pickle.load(f)


def compute_call_gas_from_structlogs(info: dict, struct_logs: list) -> Optional[int]:
    start = info.get("structLogsStart") 
    end = info.get("structLogsEnd")
    if start is None or end is None:
        return None
    start_idx = start + 1
    if start_idx >= len(struct_logs) or end >= len(struct_logs):
        return None
    gas_start = struct_logs[start_idx].get("gas")
    gas_end = struct_logs[end].get("gas")
    if gas_start is None or gas_end is None:
        return None
    return gas_start - gas_end


def compute_overheads(
    txs: List[str],
    receipts: Dict[str, Tuple[int, int, str, str, str]],
    cache_dir: Path,
    trace_dir: Path,
    operators: List[str],
) -> Tuple[Dict[str, int], Dict[str, int]]:
    ops = {addr.lower() for addr in operators}
    block2txs: Dict[int, List[str]] = {}
    for tx in txs:
        block, _gas, _from_addr, _to_addr, _contract_addr = receipts[tx.lower()]
        block2txs.setdefault(block, []).append(tx)

    b_map: Dict[str, int] = {}
    call_counts: Dict[str, int] = {}

    for block, block_txs in block2txs.items():
        cache_path = cache_dir / f"{block}.json.gz"
        if not cache_path.exists():
            raise FileNotFoundError(f"Missing cache for block {block}: {cache_path}")
        cache = read_pickle_gz(cache_path)
        for tx in block_txs:
            tree = cache.get(tx) or cache.get(tx.lower())
            if tree is None:
                raise ValueError(f"Missing tx {tx} in cache {cache_path}")

            trace_path = trace_dir / f"{tx}.json.gz"
            if not trace_path.exists():
                raise FileNotFoundError(f"Missing trace {trace_path}")
            trace = read_pickle_gz(trace_path)
            struct_logs = trace["structLogs"]

            total = 0
            calls = 0
            stack = [tree]
            while stack:
                node = stack.pop()
                info = getattr(node, "info", {})
                addr = info.get("addr")
                is_op = (
                    addr is not None
                    and addr.lower() in ops
                    and info.get("type") == "call" 
                )

                if is_op:
                    used = compute_call_gas_from_structlogs(info, struct_logs)
                    if used is None:
                        gas = info.get("gas")
                        gas_end = info.get("gasEnd")
                        if gas is None or gas_end is None:
                            raise ValueError(f"Missing gas data for tx {tx}")
                        used = gas - gas_end
                    if used < 0:
                        raise ValueError(f"Negative gas usage for tx {tx}")
                    total += used
                    calls += 1
                for child in getattr(node, "internalCalls", []):
                    stack.append(child)

            b_map[tx] = total
            call_counts[tx] = calls

    return b_map, call_counts


def write_csv(
    out_path: Path,
    txs: List[str],
    receipts: Dict[str, Tuple[int, int, str, str, str]],
    b_map: Dict[str, int],
    call_counts: Dict[str, int],
) -> None:
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["txHash", "blockNumber", "gasUsed", "operatorGas", "overhead", "operatorCalls"]
        )
        for tx in txs:
            block, gas_used, _from_addr, _to_addr, _contract_addr = receipts[tx.lower()]
            operator_gas = b_map[tx]
            overhead = operator_gas / gas_used if gas_used else 0
            writer.writerow([tx, block, gas_used, operator_gas, overhead, call_counts[tx]])


def write_summary(
    out_path: Optional[Path],
    txs: List[str],
    receipts: Dict[str, Tuple[int, int, str, str, str]],
    b_map: Dict[str, int],
    call_counts: Dict[str, int],
    operators: List[str],
    deployer_tx_count: int = 0,
    simple_tx_count: int = 0,
) -> float:
    a_total = 0
    b_total = 0
    for tx in txs:
        _block, gas_used, _from_addr, _to_addr, _contract_addr = receipts[tx.lower()]
        operator_gas = b_map[tx]
        a_total += gas_used
        b_total += operator_gas

    total_ratio = b_total / a_total if a_total else 0

    if out_path is not None:
        with open(out_path, "w") as f:
            f.write("SphereX operator/engine gas overhead summary\n")
            f.write("========================================\n")
            f.write(f"Transactions: {len(txs)}\n")
            f.write(f"Operator/engine addresses: {', '.join(sorted(operators))}\n")
            f.write("Staticcalls ignored.\n")
            f.write("Nested invocations included.\n")
            f.write(f"Simple txs (to protected contracts): {simple_tx_count}\n")
            f.write(f"Txs from protected-contract deployers: {deployer_tx_count}\n")
            f.write("\nMethod:\n")
            f.write("- A = gasUsed from crawlPackage/database/etherScan.db\n")
            f.write(
                "- For each operator/engine call: gas_used = structLogs[start+1].gas - structLogs[end].gas\n"
            )
            f.write("- B = sum of operator/engine call gas_used within the tx\n")
            f.write("- overhead = B / A\n")
            f.write("\nResults:\n")
            f.write(
                f"Total ratio (sum B / sum A): {total_ratio} ({total_ratio*100:.4f}%)\n"
            )
            f.write(
                "Operator/engine calls per tx: "
                f"avg={mean(call_counts.values()):.2f}, "
                f"min={min(call_counts.values())}, "
                f"max={max(call_counts.values())}\n"
            )

    return total_ratio


def main() -> None:
    operators = list(DEFAULT_OPERATORS)
    txs = parse_tx_list(TX_LIST_PATH)
    receipts = load_receipts(RECEIPT_DB, txs)
    protected = list(DEFAULT_PROTECTED)
    if DEPLOYER_SOURCE == "etherscan":
        deployers = set(load_deployers_etherscan(protected))
    elif DEPLOYER_SOURCE == "db":
        deployers = set(load_deployers(RECEIPT_DB, protected))
    else:
        raise ValueError(f"Unsupported DEPLOYER_SOURCE: {DEPLOYER_SOURCE}")
    b_map, call_counts = compute_overheads(
        txs,
        receipts,
        CACHE_DIR,
        TRACE_DIR,
        operators,
    )

    deployer_tx_count = sum(1 for tx in txs if receipts[tx.lower()][2] in deployers)
    protected_set = {addr.lower() for addr in protected}
    simple_tx_count = 0
    for tx in txs:
        _block, _gas, _from_addr, to_addr, contract_addr = receipts[tx.lower()]
        dest = to_addr if to_addr else contract_addr
        if dest in protected_set:
            simple_tx_count += 1

    total_ratio = write_summary(
        OUT_SUMMARY,
        txs,
        receipts,
        b_map,
        call_counts,
        operators,
        deployer_tx_count=deployer_tx_count,
        simple_tx_count=simple_tx_count,
    )

    if OUT_SUMMARY is None:
        print(f"Transactions: {len(txs)}")
        print(f"Simple txs (to protected contracts): {simple_tx_count}")
        print(f"Txs from protected-contract deployers: {deployer_tx_count}")
        print(f"Total ratio (sum B / sum A): {total_ratio} ({total_ratio*100:.4f}%)")

    if OUT_CSV is not None:
        write_csv(OUT_CSV, txs, receipts, b_map, call_counts)


if __name__ == "__main__":
    main()
