import argparse
import ast
import csv
import io
import os
import re
import sys


MARK_YES = "Yes"
MARK_NO = "No"
MARK_HALF = "Half"
MARK_NA = "N/A"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

AE_LOG_FILES = {
    "baseline": "logs/baseline.txt",
    "rr": "logs/RR.txt",
    "rr_re": "logs/RR_RE.txt",
    "rr_re_erc20": "logs/RR_RE_ERC20.txt",
    "crossguard": "logs/RR_RE_ERC20_RAW.txt",
    "fb_1h": "logs/RR_RE_ERC20_RAW_1hour.txt",
    "fb_1d": "logs/RR_RE_ERC20_RAW_1day.txt",
    "fb_3d": "logs/RR_RE_ERC20_RAW_3days.txt",
}
AE_TRACE_FILES = {
    "trace2inv_wo_ts": "logs/trace2inv0_CrossGuard_woTS_compared.txt",
    "trace2inv_w_ts": "logs/trace2inv1_CrossGuard_wTS_compared.txt",
}


def _read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _resolve_path(log_dir, filename):
    base_dir = log_dir or SCRIPT_DIR
    return os.path.join(base_dir, filename)


def _ensure_paths(paths, label):
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(f"Missing {label}: {joined}")



def parse_final_like_log(path):
    records = {}
    current = None
    section = None

    # final*.txt is often generated from console output and can contain hard line-wraps.
    # This means list literals may be split across multiple physical lines (even mid-token).
    pending_list = None

    def _extract_list_literals_with_pos(text: str):
        # Extract all top-level Python-like list literals from a line.
        # final*.txt often prints: [ ... ] <count> (<addr>, <txhash>)
        # and can contain multiple list literals on one physical line.
        out = []
        i = 0
        n = len(text)
        while i < n:
            if text[i] != "[":
                i += 1
                continue
            start = i
            depth = 0
            while i < n:
                ch = text[i]
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        end = i
                        out.append((start, end, text[start : end + 1]))
                        break
                i += 1
            i += 1
        return out

    def _canonicalize_sig(sig_text: str):
        # Prefer a canonical, hashable representation so that wrapped/whitespace-variant
        # prints collapse to the same key.
        sig_text = sig_text.strip()
        try:
            val = ast.literal_eval(sig_text)
        except Exception:
            # Fallback: aggressively normalize whitespace.
            return re.sub(r"\s+", "", sig_text)
        if isinstance(val, list):
            return tuple(str(x).strip() for x in val)
        return str(val).strip()

    def _ensure_current(benchmark: str):
        nonlocal current
        if benchmark not in records:
            records[benchmark] = {
                "benchmark": benchmark,
                "deployer_tx": None,
                "simple_tx": None,
                "another_tx": None,
                "mev_tx": None,
                "user_tx": None,
                "hack_tx": None,
                "fp_ratio_percent": None,
                "gas_overhead_percent": None,
                "cf_deployer": set(),
                "cf_simple": set(),
                "cf_another": set(),
                "cf_mev": set(),
                "cf_user": set(),
                "cf_hack": set(),
            }
        current = records[benchmark]
        return current

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            stripped = line.strip()

            # If we're currently accumulating a wrapped list literal, keep consuming lines
            # until the brackets balance again.
            if pending_list is not None:
                pending_list["buf"] += stripped
                for ch in stripped:
                    if ch == "[":
                        pending_list["depth"] += 1
                    elif ch == "]":
                        pending_list["depth"] -= 1
                if pending_list["depth"] <= 0:
                    text = pending_list["buf"]
                    base_section = pending_list["section"]
                    headers = pending_list["headers"]
                    lits = _extract_list_literals_with_pos(text)
                    for lit_start, _, sig in lits:
                        sec_for_sig = base_section
                        if headers:
                            for hpos, hsec in reversed(headers):
                                if hpos < lit_start:
                                    sec_for_sig = hsec
                                    break
                        sig_key = _canonicalize_sig(sig)
                        if sec_for_sig == "P":
                            current["cf_deployer"].add(sig_key)
                        elif sec_for_sig == "S":
                            current["cf_simple"].add(sig_key)
                        elif sec_for_sig == "O":
                            current["cf_another"].add(sig_key)
                        elif sec_for_sig == "MEV":
                            current["cf_mev"].add(sig_key)
                        elif sec_for_sig == "USER":
                            current["cf_user"].add(sig_key)
                        elif sec_for_sig == "HACK":
                            current["cf_hack"].add(sig_key)
                    pending_list = None
                continue

            if stripped.startswith("benchmark:"):
                bench = stripped.split(":", 1)[1].strip()
                _ensure_current(bench)
                section = None
                continue

            if current is None:
                continue

            if stripped.startswith("Deployer Transaction (1):"):
                current["deployer_tx"] = int(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Simple Txs to Same Protocol (2):"):
                current["simple_tx"] = int(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Another Famous DeFi Protocol Call Flows (3):"):
                current["another_tx"] = int(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("MEV (4):"):
                current["mev_tx"] = int(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("User-assisted Contract (5):"):
                current["user_tx"] = int(stripped.split(":", 1)[1].strip())
            elif stripped.startswith("Hack (6):"):
                current["hack_tx"] = int(stripped.split(":", 1)[1].strip())

            # Section headers can appear multiple times on one physical line.
            # We'll track all headers on this line and keep the last one as the
            # carried-over section for following lines.
            headers = []
            header_specs = [
                ("== Deployer Transactions", "P"),
                ("== Simple Txs to Same Protocol", "S"),
                ("== Another Famous DeFi Protocol Call Flows", "O"),
                ("== MEV Call Flows", "MEV"),
                ("== User-assisted Contract Call Flows", "USER"),
                ("== Hack Call Flows", "HACK"),
            ]
            for token, code in header_specs:
                idx = stripped.find(token)
                if idx >= 0:
                    headers.append((idx, code))
            headers.sort(key=lambda x: x[0])
            if headers:
                section = headers[-1][1]


            if stripped.startswith("False positive ratio"):
                # Example: False positive ratio 3.5699 %
                try:
                    val = float(stripped.split("ratio", 1)[1].split("%", 1)[0].strip())
                except Exception:
                    val = None
                current["fp_ratio_percent"] = val

            if stripped.startswith("Total gas overhead:"):
                try:
                    val = float(stripped.split("overhead:", 1)[1].split("%", 1)[0].strip())
                except Exception:
                    val = None
                current["gas_overhead_percent"] = val

            # Capture control-flow signature list literals that may appear anywhere in the line.
            if section in {"P", "S", "O", "MEV", "USER", "HACK"}:
                # First, detect whether this line starts an incomplete list literal.
                depth = 0
                saw_open = False
                for ch in stripped:
                    if ch == "[":
                        depth += 1
                        saw_open = True
                    elif ch == "]":
                        depth -= 1

                lits = _extract_list_literals_with_pos(stripped)
                if lits:
                    for lit_start, _, sig in lits:
                        sec_for_sig = section
                        # Prefer the closest preceding header on the same line.
                        if headers:
                            for hpos, hsec in reversed(headers):
                                if hpos < lit_start:
                                    sec_for_sig = hsec
                                    break

                        sig_key = _canonicalize_sig(sig)
                        if sec_for_sig == "P":
                            current["cf_deployer"].add(sig_key)
                        elif sec_for_sig == "S":
                            current["cf_simple"].add(sig_key)
                        elif sec_for_sig == "O":
                            current["cf_another"].add(sig_key)
                        elif sec_for_sig == "MEV":
                            current["cf_mev"].add(sig_key)
                        elif sec_for_sig == "USER":
                            current["cf_user"].add(sig_key)
                        elif sec_for_sig == "HACK":
                            current["cf_hack"].add(sig_key)
                elif saw_open and depth > 0:
                    # Wrapped list literal: start accumulating until brackets balance.
                    pending_list = {
                        "buf": stripped,
                        "depth": depth,
                        "section": section,
                        "headers": headers,
                    }

    return records



def parse_trace2inv_compared_log(path):
    records = {}
    current = None
    section = None
    pending_list = None

    def _ensure_current(benchmark: str):
        nonlocal current
        if benchmark not in records:
            records[benchmark] = {
                "benchmark": benchmark,
                "fp_ratio_percent": None,
                "cf_hack": set(),
                # Number of non-empty content lines after '== Hack Call Flows:' and
                # before 'False positives:' (per user, used to decide whether hack is blocked).
                "hack_section_lines": 0,
            }
        current = records[benchmark]
        return current

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            stripped = raw_line.strip()

            def _add_hack_sigs_from_list_literal(list_literal: str) -> None:
                """Parse a Python list literal and add each element as a hack call-flow signature.

                Compared logs often print hack call flows as a Python list of strings (with many
                duplicates). We want the unique call-flow *elements*, not the whole list as one value.
                """
                try:
                    val = ast.literal_eval(list_literal)
                except Exception:
                    # Fallback: treat the literal string as a single signature token.
                    sig_key = re.sub(r"\s+", "", list_literal)
                    current["cf_hack"].add(sig_key)
                    return

                if isinstance(val, list):
                    for item in val:
                        s = str(item).strip()
                        if not s:
                            continue
                        current["cf_hack"].add(re.sub(r"\s+", "", s))
                else:
                    s = str(val).strip()
                    if s:
                        current["cf_hack"].add(re.sub(r"\s+", "", s))

            if pending_list is not None:
                pending_list["buf"] += stripped
                for ch in stripped:
                    if ch == "[":
                        pending_list["depth"] += 1
                    elif ch == "]":
                        pending_list["depth"] -= 1
                if pending_list["depth"] <= 0:
                    text = pending_list["buf"]

                    def _extract(text2: str):
                        out = []
                        i = 0
                        n = len(text2)
                        while i < n:
                            if text2[i] != "[":
                                i += 1
                                continue
                            start = i
                            depth = 0
                            while i < n:
                                ch2 = text2[i]
                                if ch2 == "[":
                                    depth += 1
                                elif ch2 == "]":
                                    depth -= 1
                                    if depth == 0:
                                        out.append(text2[start : i + 1])
                                        break
                                i += 1
                            i += 1
                        return out

                    for sig in _extract(text):
                        _add_hack_sigs_from_list_literal(sig.strip())
                    pending_list = None
                continue

            if stripped.startswith("benchmark:"):
                bench = stripped.split(":", 1)[1].strip()
                _ensure_current(bench)
                section = None
                continue

            if current is None:
                continue

            # Note: we already used .strip(), so section headers start with '==' (no leading space).
            if stripped.startswith("== Hack Call Flows"):
                section = "HACK"
                # Reset for this benchmark section.
                current["hack_section_lines"] = 0
                continue
            if stripped.startswith("== "):
                section = None
                continue

            # Count hack-section content lines (for Table 3 blocked criterion).
            if section == "HACK":
                if stripped.startswith("False positives"):
                    section = None
                elif stripped:
                    current["hack_section_lines"] += 1

            if stripped.startswith("False positive ratio"):
                try:
                    val = float(stripped.split("ratio", 1)[1].split("%", 1)[0].strip())
                except Exception:
                    val = None
                current["fp_ratio_percent"] = val

            if section == "HACK" and "[" in stripped and "]" in stripped:
                # Compared logs sometimes place content on the same line; extract all list literals.
                # We only care about hack CF signatures for Table 3.
                def _extract(text: str):
                    out = []
                    i = 0
                    n = len(text)
                    while i < n:
                        if text[i] != "[":
                            i += 1
                            continue
                        start = i
                        depth = 0
                        while i < n:
                            ch = text[i]
                            if ch == "[":
                                depth += 1
                            elif ch == "]":
                                depth -= 1
                                if depth == 0:
                                    out.append(text[start : i + 1])
                                    break
                            i += 1
                        i += 1
                    return out

                for sig in _extract(stripped):
                    _add_hack_sigs_from_list_literal(sig.strip())
            elif section == "HACK" and "[" in stripped and "]" not in stripped:
                depth = 0
                for ch in stripped:
                    if ch == "[":
                        depth += 1
                    elif ch == "]":
                        depth -= 1
                if depth > 0:
                    pending_list = {"buf": stripped, "depth": depth}

    return records




def load_expected_outputs(expected_path=None):
    if expected_path is None:
        expected_path = os.path.join(SCRIPT_DIR, "Expected_Outputs.txt")
    return _read_text(expected_path)


def load_latex_tables(latex_path=None):
    # Backward compatibility: accept LaTeX tables or Expected_Outputs.txt.
    return load_expected_outputs(latex_path)


def load_ae_final_logs(log_dir=None):


    paths = {key: _resolve_path(log_dir, name) for key, name in AE_LOG_FILES.items()}
    _ensure_paths(list(paths.values()), "AE log files")
    return {key: parse_final_like_log(path) for key, path in paths.items()}


def load_ae_trace2inv_logs(log_dir=None):
    wo_path = _resolve_path(log_dir, AE_TRACE_FILES["trace2inv_wo_ts"])
    w_path = _resolve_path(log_dir, AE_TRACE_FILES["trace2inv_w_ts"])
    _ensure_paths([wo_path, w_path], "trace2inv logs")
    wo_records = parse_trace2inv_compared_log(wo_path)
    w_records = parse_trace2inv_compared_log(w_path)
    return wo_records, w_records


def _fmt_num(value, digits=2):
    if value is None:
        return MARK_NA
    rounded = round(float(value), digits)
    s = f"{rounded:.{digits}f}"
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def _fmt_int(value):
    if value is None:
        return MARK_NA
    return str(int(value))


def _fmt_mark(value):
    if value is None:
        return MARK_NA
    return MARK_YES if value else MARK_NO


def _normalize_protocol_name(name):
    name = name.strip()
    name = name.replace("\\_", "_")

    # Map log benchmark keys to the LaTeX table display names.
    replacements = {
        # LaTeX typo: DFOX should be GFOX.
        "DFOX": "GFOX",
        "bZx2": "bZx",
        "Warp_interface": "Warp",
        "CheeseBank_1": "CheeseBank",
        "CreamFi1_1": "CreamFi1",
        "CreamFi2_4": "CreamFi2",
        "RariCapital2_3": "RariCapital2",
        "Harvest1_fUSDT": "Harvest",
        "Yearn1_interface": "Yearn",
        "Punk_1": "Punk",
        "BeanstalkFarms_interface": "BeanstalkFarms",
        "AAVE2": "AAVE",
        "Lido2": "Lido",
        "Uniswap2": "Uniswap",
    }
    if name in replacements:
        return replacements[name]
    return name


_ROW_END_RE = re.compile(r"\\\\\s*(?:\\hline|\\Xhline\{.*?\}|\\bottomrule)?\s*$")


def _strip_latex_tokens(s):
    s = s.strip()
    if not s:
        return s

    # Unwrap common tabular wrappers.
    # These typically contain a simple scalar (Yes/No/N/A/number).
    for _ in range(10):
        if "\\multicolumn{" not in s and "\\multirow{" not in s:
            break
        new_s = s
        new_s = re.sub(r"\\multicolumn\{[^{}]*\}\{[^{}]*\}\{([^{}]*)\}", r"\1", new_s)
        new_s = re.sub(r"\\multirow\{[^{}]*\}\{[^{}]*\}\{([^{}]*)\}", r"\1", new_s)
        if new_s == s:
            break
        s = new_s

    # Remove \revisionhl{...} wrappers (repeat, but never loop forever).
    for _ in range(10):
        if "\\revisionhl{" not in s:
            break
        new_s = re.sub(r"\\revisionhl\{([^{}]*)\}", r"\1", s)
        if new_s == s:
            # Unbalanced/nested braces: stop trying to peel further.
            break
        s = new_s

    # Remove \cellcolor... prefix attached to a value.
    s = re.sub(r"\\cellcolor\[[^\]]*\]\{[^}]*\}", "", s)
    s = re.sub(r"\\cellcolor\{[^}]*\}", "", s)

    # Common wrappers.
    s = re.sub(r"\\makecell\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\$", "", s)
    s = s.replace("$", "")

    # Marks.
    s = s.replace("\\cmark$\\ast$", "Yes*")
    s = s.replace("\\cmark\\ast", "Yes*")
    s = s.replace("\\cmark", "Yes")
    s = s.replace("\\xmark", "No")
    s = s.replace("\\halfmark", "Half")

    # Remove citations.
    s = re.sub(r"\\cite\{[^}]*\}", "", s)

    # Unescape LaTeX underscores.
    s = s.replace("\\_", "_")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _is_latex_expected(text):
    return "\\caption{" in text or "\\begin{table" in text


def _split_csv_blocks(text):
    blocks = []
    current = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if not line.strip():
            if current:
                blocks.append("\n".join(current))
                current = []
            continue
        current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _parse_csv_block(block_text):
    rows = []
    reader = csv.reader(io.StringIO(block_text))
    for row in reader:
        if not row:
            continue
        rows.append([cell.strip() for cell in row])
    return rows


def _find_csv_block(text, required_cols):
    for block in _split_csv_blocks(text):
        rows = _parse_csv_block(block)
        if not rows:
            continue
        header = [h.strip() for h in rows[0]]
        if all(col in header for col in required_cols):
            return rows
    return None


def _parse_latex_table_rows(latex_text):
    rows = []
    for raw_line in latex_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("%"):
            continue
        if "&" not in line or "\\\\" not in line:
            continue
        if line.startswith("\\multicolumn") or line.startswith("\\rowcolor"):
            continue

        # Trim trailing LaTeX row markers.
        line = _ROW_END_RE.sub("", line)
        parts = [p.strip() for p in line.split("&")]
        parts = [_strip_latex_tokens(p) for p in parts]
        rows.append(parts)
    return rows


def _extract_table_blocks(latex_text):
    # Minimal splitting based on captions.
    # We assume Latex_Tables.txt contains exactly these captions in order.
    def _find_block(start_marker, end_marker, start_pos=0):
        start = latex_text.find(start_marker, start_pos)
        if start < 0:
            raise ValueError(f"Could not find marker: {start_marker}")
        end = latex_text.find(end_marker, start)
        if end < 0:
            raise ValueError(f"Could not find end marker: {end_marker}")
        return latex_text[start : end + len(end_marker)], end + len(end_marker)

    block1, pos1 = _find_block("\\caption{Summary of Benchmarks", "\\end{table*}")
    block2, pos2 = _find_block("\\caption{Ablation study", "\\end{table*}", pos1)
    block3, _ = _find_block("\\caption{Comparison of", "\\end{table}", pos2)
    return block1, block2, block3


def _csv_string(rows):
    buf = io.StringIO()
    writer = csv.writer(buf)
    for row in rows:
        writer.writerow(row)
    return buf.getvalue().rstrip("\n")


def _parse_expected_table1_latex(latex_text):
    block1, _, _ = _extract_table_blocks(latex_text)
    rows = _parse_latex_table_rows(block1)

    order = []
    expected = {}
    for parts in rows:
        # Table 1 has 16 columns in the LaTeX row.
        if len(parts) < 16:
            continue
        proto = _strip_latex_tokens(parts[0])
        if proto.strip().lower() == "victim protocol":
            continue
        if proto.lower().startswith("avg."):
            continue
        proto = _normalize_protocol_name(proto)
        order.append(proto)
        expected[proto] = {
            "Unique CF in Hack?": parts[5],
            "Total #Txs": parts[6],
            "Total #nCF": parts[7],
            "P-Tx": parts[8],
            "P-nCF": parts[9],
            "S-Tx": parts[10],
            "S-nCF": parts[11],
            "O-Tx": parts[12],
            "O-nCF": parts[13],
            "E-Tx": parts[14],
            "E-nCF": parts[15],
        }
    return order, expected


def _parse_expected_table1_csv(expected_text):
    rows = _find_csv_block(expected_text, ["Victim Protocol", "Unique CF in Hack?"])
    if not rows:
        raise ValueError("Could not find Table 1 CSV block in Expected_Outputs.txt")

    header = rows[0]
    col_idx = {name: idx for idx, name in enumerate(header)}
    col_map = {
        "Unique CF in Hack?": ["Unique CF in Hack?"],
        "Total #Txs": ["Total #Txs"],
        "Total #nCF": ["Total #nCF"],
        "P-Tx": ["#P-Tx", "P-Tx"],
        "P-nCF": ["#P-nCF", "P-nCF"],
        "S-Tx": ["#S-Tx", "S-Tx"],
        "S-nCF": ["#S-nCF", "S-nCF"],
        "O-Tx": ["#O-Tx", "O-Tx"],
        "O-nCF": ["#O-nCF", "O-nCF"],
        "E-Tx": ["#E-Tx", "E-Tx"],
        "E-nCF": ["#E-nCF", "E-nCF"],
    }

    def _get_col(row, names):
        for name in names:
            idx = col_idx.get(name)
            if idx is not None and idx < len(row):
                return row[idx].strip()
        return ""

    order = []
    expected = {}
    for row in rows[1:]:
        proto_raw = row[0].strip() if row else ""
        if not proto_raw:
            continue
        if proto_raw.lower().startswith("avg"):
            continue
        proto = _normalize_protocol_name(proto_raw)
        order.append(proto)
        expected[proto] = {
            key: _get_col(row, names) for key, names in col_map.items()
        }
    return order, expected


def _parse_expected_table1(expected_text):
    if _is_latex_expected(expected_text):
        return _parse_expected_table1_latex(expected_text)
    return _parse_expected_table1_csv(expected_text)


def _parse_expected_table2_latex(latex_text):
    _, block2, _ = _extract_table_blocks(latex_text)
    rows = _parse_latex_table_rows(block2)

    order = []
    expected = {}
    for parts in rows:
        if len(parts) < 18:
            continue
        proto = _strip_latex_tokens(parts[0])
        if proto.lower().startswith("summary"):
            continue
        proto = _normalize_protocol_name(proto)
        order.append(proto)

        # Columns per LaTeX table 2.
        expected[proto] = {
            "Baseline Block?": parts[1],
            "Baseline FP%": parts[2],
            "RR Block?": parts[3],
            "RR FP%": parts[4],
            "RR+RE Block?": parts[5],
            "RR+RE FP%": parts[6],
            "RR+RE+ERC20 Block?": parts[7],
            "RR+RE+ERC20 FP%": parts[8],
            "CrossGuard Block?": parts[9],
            "CrossGuard FP%": parts[10],
            "Gas OH%": parts[11],
            "Feedback Block?": parts[12],
            "3 days FP%": parts[13],
            "1 day FP%": parts[14],
            "1 hour FP%": parts[15],
        }
    return order, expected


def _parse_expected_table2_csv(expected_text):
    rows = _find_csv_block(expected_text, ["Victim Protocol", "Baseline Block?"])
    if not rows:
        raise ValueError("Could not find Table 2 CSV block in Expected_Outputs.txt")

    header = rows[0]
    col_idx = {name: idx for idx, name in enumerate(header)}
    col_map = {
        "Baseline Block?": ["Baseline Block?"],
        "Baseline FP%": ["Baseline FP%"],
        "RR Block?": ["Baseline+RR Block?", "RR Block?"],
        "RR FP%": ["Baseline+RR FP%", "RR FP%"],
        "RR+RE Block?": ["Baseline+RR+RE Block?", "RR+RE Block?"],
        "RR+RE FP%": ["Baseline+RR+RE FP%", "RR+RE FP%"],
        "RR+RE+ERC20 Block?": ["Baseline+RR+RE+ERC20 Block?", "RR+RE+ERC20 Block?"],
        "RR+RE+ERC20 FP%": ["Baseline+RR+RE+ERC20 FP%", "RR+RE+ERC20 FP%"],
        "CrossGuard Block?": ["CrossGuard Block?"],
        "CrossGuard FP%": ["CrossGuard FP%"],
        "Gas OH%": ["Gas OH%", "Gas OH(%)"],
        "Feedback Block?": ["CrossGuard+Feedback Block?", "Feedback Block?"],
        "3 days FP%": ["3 days FP%"],
        "1 day FP%": ["1 day FP%"],
        "1 hour FP%": ["1 hour FP%"],
    }

    def _get_col(row, names):
        for name in names:
            idx = col_idx.get(name)
            if idx is not None and idx < len(row):
                return row[idx].strip()
        return ""

    order = []
    expected = {}
    for row in rows[1:]:
        proto_raw = row[0].strip() if row else ""
        if not proto_raw:
            continue
        if proto_raw.lower().startswith("summary"):
            continue
        proto = _normalize_protocol_name(proto_raw)
        order.append(proto)
        expected[proto] = {
            key: _get_col(row, names) for key, names in col_map.items()
        }
    return order, expected


def _parse_expected_table2(expected_text):
    if _is_latex_expected(expected_text):
        return _parse_expected_table2_latex(expected_text)
    return _parse_expected_table2_csv(expected_text)


def _parse_expected_table3_latex(latex_text):
    _, _, block3 = _extract_table_blocks(latex_text)
    rows = _parse_latex_table_rows(block3)
    expected = {}
    for parts in rows:
        if len(parts) < 5:
            continue
        metric = parts[0]
        expected[metric] = {
            "CrossGuard (w/o TS)": parts[1],
            "CrossGuard (w TS)": parts[2],
        }
    return expected


def _parse_expected_table3_csv(expected_text):
    rows = _find_csv_block(expected_text, ["Metric", "CrossGuard (w/o TS)", "CrossGuard (w TS)"])
    if not rows:
        raise ValueError("Could not find Table 3 CSV block in Expected_Outputs.txt")

    expected = {}
    for row in rows[1:]:
        if len(row) < 3:
            continue
        metric = row[0].strip()
        if metric in ("# Table 3 Details: Calculation Inputs", "Definition", "Variant", "Victim Protocol"):
            break
        if metric not in ("# Hacks Blocked", "Avg. FP%"):
            continue
        expected[metric] = {
            "CrossGuard (w/o TS)": row[1].strip(),
            "CrossGuard (w TS)": row[2].strip(),
        }
    return expected


def _parse_expected_table3(expected_text):
    if _is_latex_expected(expected_text):
        return _parse_expected_table3_latex(expected_text)
    return _parse_expected_table3_csv(expected_text)


def _print_mismatches(
    table_name,
    mismatches,
    missing,
) -> None:
    if not mismatches and not missing:
        print(f"[OK] {table_name}: no mismatches detected", file=sys.stderr)
        return

    print(f"[REPORT] {table_name}", file=sys.stderr)
    if missing:
        print("  Missing:", file=sys.stderr)
        for item in missing:
            print(f"    - {item}", file=sys.stderr)
    if mismatches:
        print("  Mismatches:", file=sys.stderr)
        for row_id, col, expected, actual in mismatches:
            print(f"    - {row_id} | {col}: expected={expected} actual={actual}", file=sys.stderr)


def _compare_numericish(expected, actual):
    if expected == actual:
        return True
    if expected == MARK_NA or actual == MARK_NA:
        return expected == actual
    try:
        e = float(expected)
        a = float(actual)
        return abs(e - a) <= 0.01
    except Exception:
        return False


def _compare_csv_blocks(expected_text, actual_text, table_labels):
    exp_blocks = _split_csv_blocks(expected_text)
    act_blocks = _split_csv_blocks(actual_text)
    mismatches = []
    missing = []
    extra = []

    if len(exp_blocks) < len(table_labels):
        missing.append("Expected output missing one or more table blocks")
    if len(act_blocks) < len(table_labels):
        missing.append("Generated output missing one or more table blocks")
    if len(act_blocks) > len(table_labels):
        extra.append(f"Generated output has {len(act_blocks) - len(table_labels)} extra block(s)")

    for idx, label in enumerate(table_labels):
        if idx >= len(exp_blocks) or idx >= len(act_blocks):
            continue
        exp_rows = _parse_csv_block(exp_blocks[idx])
        act_rows = _parse_csv_block(act_blocks[idx])
        row_count = max(len(exp_rows), len(act_rows))
        col_count = 0
        for row in exp_rows + act_rows:
            if len(row) > col_count:
                col_count = len(row)

        for r in range(row_count):
            exp_row = exp_rows[r] if r < len(exp_rows) else []
            act_row = act_rows[r] if r < len(act_rows) else []
            row_id = exp_row[0] if exp_row else (act_row[0] if act_row else f"row {r}")
            for c in range(col_count):
                exp_val = exp_row[c].strip() if c < len(exp_row) else ""
                act_val = act_row[c].strip() if c < len(act_row) else ""
                if exp_val == act_val:
                    continue
                if _compare_numericish(exp_val, act_val):
                    continue
                col = exp_rows[0][c] if exp_rows and c < len(exp_rows[0]) else f"col {c}"
                mismatches.append((f"{label}:{row_id}", col, exp_val, act_val))

    return mismatches, missing, extra


def compute_study_row_from_final4(rec):
    p_tx = rec.get("deployer_tx") or 0
    s_tx = rec.get("simple_tx") or 0
    o_tx = rec.get("another_tx") or 0
    mev_tx = rec.get("mev_tx") or 0
    user_tx = rec.get("user_tx") or 0
    hack_tx = rec.get("hack_tx") or 0
    e_tx = mev_tx + user_tx + hack_tx
    total_tx = p_tx + s_tx + o_tx + e_tx

    # Table 1's #nCF values are derived from the printed unique call-flow signatures.
    # Important: in final4.txt, a category may have many transactions but print *no* signatures
    # (e.g., when it has zero false positives). In that case, the correct #nCF is 0 (not missing).
    p_cf = set(rec.get("cf_deployer") or set())
    s_cf = set(rec.get("cf_simple") or set())
    o_cf = set(rec.get("cf_another") or set())
    mev_cf = set(rec.get("cf_mev") or set())
    user_cf = set(rec.get("cf_user") or set())
    hack_cf = set(rec.get("cf_hack") or set())

    # E is union of (MEV, user-assisted, hack).
    e_cf = mev_cf | user_cf | hack_cf

    # Total is union over categories.
    total_cf = p_cf | s_cf | o_cf | e_cf

    # Unique CF in Hack? compares hack CF signatures vs *all* other categories.
    # Table 1 does not have N/A for this column; if a hack exists but no hack CF signatures are
    # printed, we conservatively mark it as No (cannot show uniqueness).
    unique_in_hack = compute_unique_in_hack_from_record(rec)

    return {
        "Unique CF in Hack?": unique_in_hack,
        "Total #Txs": total_tx,
        "Total #nCF": len(total_cf),
        "P-Tx": p_tx,
        "P-nCF": len(p_cf),
        "S-Tx": s_tx,
        "S-nCF": len(s_cf),
        "O-Tx": o_tx,
        "O-nCF": len(o_cf),
        "E-Tx": e_tx,
        "E-nCF": len(e_cf),
    }


def compute_unique_in_hack_from_record(rec):
    hack_tx = rec.get("hack_tx") or 0
    if hack_tx <= 0:
        return MARK_NA

    hack_cf = set(rec.get("cf_hack") or set())
    if not hack_cf:
        return MARK_NO

    p_cf = set(rec.get("cf_deployer") or set())
    s_cf = set(rec.get("cf_simple") or set())
    o_cf = set(rec.get("cf_another") or set())
    mev_cf = set(rec.get("cf_mev") or set())
    user_cf = set(rec.get("cf_user") or set())

    non_hack_cf = p_cf | s_cf | o_cf | mev_cf | user_cf
    unique_hack_cf = hack_cf - non_hack_cf
    if len(unique_hack_cf) == 0:
        return MARK_NO
    return MARK_YES


def compute_blocked_from_record(rec):
    # Block? definition (per user): block is true iff hack call-flows are unique,
    # i.e., there exists at least one hack call-flow signature not present in any
    # other category call-flows.
    hack_tx = rec.get("hack_tx")
    if hack_tx is not None and hack_tx == 0:
        return None
    if hack_tx is None:
        return None

    hack_cf = set(rec.get("cf_hack") or set())
    # Some logs have an empty '== Hack Call Flows:' section even when hack_tx > 0.
    # In that case we treat it as not blockable (No) rather than unknown, because
    # we cannot establish uniqueness from printed data.
    if hack_tx > 0 and not hack_cf:
        return False

    # Note: these logs only print non-hack call-flow signatures when there are false
    # positives (FP>0). If a category prints none, we treat it as an empty set.
    non_hack_cf = (
        set(rec.get("cf_deployer") or set())
        | set(rec.get("cf_simple") or set())
        | set(rec.get("cf_another") or set())
        | set(rec.get("cf_mev") or set())
        | set(rec.get("cf_user") or set())
    )

    # If any hack CF signature is not present elsewhere, the hack is blockable.
    return len(hack_cf - non_hack_cf) > 0


def generate_table1_csv(
    final4_records,
    latex_text,
    unique_in_hack_records=None,
):
    order, expected = _parse_expected_table1(latex_text)

    header = [
        "Victim Protocol",
        "Unique CF in Hack?",
        "Total #Txs",
        "Total #nCF",
        "#P-Tx",
        "#P-nCF",
        "#S-Tx",
        "#S-nCF",
        "#O-Tx",
        "#O-nCF",
        "#E-Tx",
        "#E-nCF",
    ]
    rows = [header]

    mismatches = []
    missing = []
    missing_counts = {}
    missing_examples = {}

    sum_total_tx = 0
    sum_total_ncf = 0
    sum_p_tx = sum_s_tx = sum_o_tx = sum_e_tx = 0
    sum_p_ncf = sum_s_ncf = sum_o_ncf = sum_e_ncf = 0
    ncf_complete = True

    # Pre-normalize keys for quick lookup.
    norm_map = {_normalize_protocol_name(k): k for k in final4_records.keys()}
    rr_norm_map = None
    if unique_in_hack_records is not None:
        rr_norm_map = {_normalize_protocol_name(k): k for k in unique_in_hack_records.keys()}

    for proto in order:
        log_key = norm_map.get(proto)
        if log_key is None:
            missing.append(f"{proto} not found in final4 log")
            data = {
                "Unique CF in Hack?": MARK_NA,
                "Total #Txs": None,
                "Total #nCF": None,
                "P-Tx": None,
                "P-nCF": None,
                "S-Tx": None,
                "S-nCF": None,
                "O-Tx": None,
                "O-nCF": None,
                "E-Tx": None,
                "E-nCF": None,
            }
        else:
            rec = final4_records[log_key]
            data = compute_study_row_from_final4(rec)

        if rr_norm_map is not None:
            rr_key = rr_norm_map.get(proto)
            if rr_key is None:
                data["Unique CF in Hack?"] = MARK_NA
                missing.append(f"{proto} not found in RR log for Unique CF in Hack?")
            else:
                rr_rec = unique_in_hack_records[rr_key]
                data["Unique CF in Hack?"] = compute_unique_in_hack_from_record(rr_rec)

        actual_row = {
            "Unique CF in Hack?": str(data.get("Unique CF in Hack?", MARK_NA)),
            "Total #Txs": _fmt_int(data.get("Total #Txs")),
            "Total #nCF": _fmt_int(data.get("Total #nCF")),
            "P-Tx": _fmt_int(data.get("P-Tx")),
            "P-nCF": _fmt_int(data.get("P-nCF")),
            "S-Tx": _fmt_int(data.get("S-Tx")),
            "S-nCF": _fmt_int(data.get("S-nCF")),
            "O-Tx": _fmt_int(data.get("O-Tx")),
            "O-nCF": _fmt_int(data.get("O-nCF")),
            "E-Tx": _fmt_int(data.get("E-Tx")),
            "E-nCF": _fmt_int(data.get("E-nCF")),
        }

        exp = expected.get(proto, {})
        for col, actual in actual_row.items():
            exp_val = _strip_latex_tokens(exp.get(col, ""))
            if not exp_val:
                continue
            if actual == MARK_NA and exp_val != MARK_NA:
                missing_counts[col] = missing_counts.get(col, 0) + 1
                if col not in missing_examples:
                    missing_examples[col] = []
                if len(missing_examples[col]) < 3:
                    missing_examples[col].append(proto)
                continue
            if col == "Unique CF in Hack?":
                if exp_val != actual:
                    mismatches.append((proto, col, exp_val, actual))
            else:
                if not _compare_numericish(exp_val, actual):
                    mismatches.append((proto, col, exp_val, actual))

        rows.append(
            [
                proto,
                actual_row["Unique CF in Hack?"],
                actual_row["Total #Txs"],
                actual_row["Total #nCF"],
                actual_row["P-Tx"],
                actual_row["P-nCF"],
                actual_row["S-Tx"],
                actual_row["S-nCF"],
                actual_row["O-Tx"],
                actual_row["O-nCF"],
                actual_row["E-Tx"],
                actual_row["E-nCF"],
            ]
        )

        # Summary totals: compute Tx ratios whenever Tx counts exist.
        try:
            if data.get("Total #Txs") is not None:
                sum_total_tx += int(data.get("Total #Txs") or 0)
                sum_p_tx += int(data.get("P-Tx") or 0)
                sum_s_tx += int(data.get("S-Tx") or 0)
                sum_o_tx += int(data.get("O-Tx") or 0)
                sum_e_tx += int(data.get("E-Tx") or 0)
        except Exception:
            pass

        # nCF ratios require that all nCF values are available.
        if any(data.get(k) is None for k in ["Total #nCF", "P-nCF", "S-nCF", "O-nCF", "E-nCF"]):
            ncf_complete = False
        else:
            sum_total_ncf += int(data.get("Total #nCF") or 0)
            sum_p_ncf += int(data.get("P-nCF") or 0)
            sum_s_ncf += int(data.get("S-nCF") or 0)
            sum_o_ncf += int(data.get("O-nCF") or 0)
            sum_e_ncf += int(data.get("E-nCF") or 0)

    # Summary row: Avg Ratio (percent of totals).
    def pct(n, d):
        if d == 0:
            return MARK_NA
        return _fmt_num((n / d) * 100.0, 2)

    rows.append(
        [
            "Avg Ratio",
            "",
            "100",
            "100",
            pct(sum_p_tx, sum_total_tx),
            (pct(sum_p_ncf, sum_total_ncf) if ncf_complete else MARK_NA),
            pct(sum_s_tx, sum_total_tx),
            (pct(sum_s_ncf, sum_total_ncf) if ncf_complete else MARK_NA),
            pct(sum_o_tx, sum_total_tx),
            (pct(sum_o_ncf, sum_total_ncf) if ncf_complete else MARK_NA),
            pct(sum_e_tx, sum_total_tx),
            (pct(sum_e_ncf, sum_total_ncf) if ncf_complete else MARK_NA),
        ]
    )

    # Report.
    for col, count in sorted(missing_counts.items(), key=lambda x: (-x[1], x[0])):
        ex = ", ".join(missing_examples.get(col, []))
        if ex:
            missing.append(f"{col} not derivable from final4 log for {count} benchmarks (e.g., {ex})")
        else:
            missing.append(f"{col} not derivable from final4 log for {count} benchmarks")
    _print_mismatches("Table 1 (Study)", mismatches, missing)
    return _csv_string(rows)


def generate_table2_csv(final_logs, latex_text):
    order, expected = _parse_expected_table2(latex_text)

    header = [
        "Victim Protocol",
        "Baseline Block?",
        "Baseline FP%",
        "Baseline+RR Block?",
        "Baseline+RR FP%",
        "Baseline+RR+RE Block?",
        "Baseline+RR+RE FP%",
        "Baseline+RR+RE+ERC20 Block?",
        "Baseline+RR+RE+ERC20 FP%",
        "CrossGuard Block?",
        "CrossGuard FP%",
        "Gas OH(%)",
        "CrossGuard+Feedback Block?",
        "3 days FP%",
        "1 day FP%",
        "1 hour FP%",
    ]
    rows = [header]

    mismatches = []
    missing = []

    def _new_summary_acc():
        return {
            "block_counts": {
                "baseline": 0,
                "rr": 0,
                "rr_re": 0,
                "rr_re_erc20": 0,
                "crossguard": 0,
                "fb": 0,
            },
            "block_seen": {
                "baseline": False,
                "rr": False,
                "rr_re": False,
                "rr_re_erc20": False,
                "crossguard": False,
                "fb": False,
            },
            "fp_values": {
                "baseline": [],
                "rr": [],
                "rr_re": [],
                "rr_re_erc20": [],
                "crossguard": [],
                "fb_3d": [],
                "fb_1d": [],
                "fb_1h": [],
            },
            "gas_values": [],
        }

    def _avg(vals):
        if not vals:
            return MARK_NA
        return _fmt_num(sum(vals) / len(vals), 2)

    def _summary_row(acc):
        def _block_cell(key):
            if not acc["block_seen"].get(key, False):
                return MARK_NA
            return str(acc["block_counts"].get(key, 0))

        return [
            "Summary",
            _block_cell("baseline"),
            _avg(acc["fp_values"]["baseline"]),
            _block_cell("rr"),
            _avg(acc["fp_values"]["rr"]),
            _block_cell("rr_re"),
            _avg(acc["fp_values"]["rr_re"]),
            _block_cell("rr_re_erc20"),
            _avg(acc["fp_values"]["rr_re_erc20"]),
            _block_cell("crossguard"),
            _avg(acc["fp_values"]["crossguard"]),
            _avg(acc["gas_values"]),
            _block_cell("fb"),
            _avg(acc["fp_values"]["fb_3d"]),
            _avg(acc["fp_values"]["fb_1d"]),
            _avg(acc["fp_values"]["fb_1h"]),
        ]

    acc = _new_summary_acc()

    # LaTeX Table 2 has two Summary rows: one before AAVE, one after Uniswap.
    # We use 'AAVE' as the split marker (benchmark suite vs large-scale suite).
    split_marker = "AAVE"
    split_inserted = False

    def _get_record(config_key: str, proto: str):
        records = final_logs.get(config_key, {})
        if "_norm" not in records:
            records["_norm"] = {_normalize_protocol_name(k): k for k in records.keys() if k != "_norm"}
        key = records["_norm"].get(proto)
        return records.get(key) if key else None

    for proto in order:
        if (not split_inserted) and proto == split_marker:
            rows.append(_summary_row(acc))
            acc = _new_summary_acc()
            split_inserted = True

        r0 = _get_record("baseline", proto)
        r1 = _get_record("rr", proto)
        r2 = _get_record("rr_re", proto)
        r3 = _get_record("rr_re_erc20", proto)
        r4 = _get_record("crossguard", proto)
        r3d = _get_record("fb_3d", proto)
        r1d = _get_record("fb_1d", proto)
        r1h = _get_record("fb_1h", proto)

        if r0 is None or r1 is None or r2 is None or r3 is None or r4 is None:
            missing.append(f"{proto}: missing one or more final*.txt records")

        def bval(r) -> str:
            if r is None:
                return MARK_NA
            return _fmt_mark(compute_blocked_from_record(r))

        def fpval(r) -> str:
            if r is None or r.get("fp_ratio_percent") is None:
                return MARK_NA
            return _fmt_num(r.get("fp_ratio_percent"), 2)

        baseline_block = bval(r0)
        rr_block = bval(r1)
        rr_re_block = bval(r2)
        rr_re_erc20_block = bval(r3)
        crossguard_block = bval(r4)

        baseline_fp = fpval(r0)
        rr_fp = fpval(r1)
        rr_re_fp = fpval(r2)
        rr_re_erc20_fp = fpval(r3)
        crossguard_fp = fpval(r4)

        gas_oh = MARK_NA
        if r4 is not None and r4.get("gas_overhead_percent") is not None:
            gas_oh = _fmt_num(r4.get("gas_overhead_percent"), 2)
            acc["gas_values"].append(r4.get("gas_overhead_percent"))

        fb_block = bval(r3d)
        fp_3d = fpval(r3d)
        fp_1d = fpval(r1d)
        fp_1h = fpval(r1h)

        # Update summary accumulators.
        def _acc(config_key: str, block_str: str, fp_str: str) -> None:
            if block_str != MARK_NA:
                acc["block_seen"][config_key] = True
            if block_str == MARK_YES:
                acc["block_counts"][config_key] += 1
            if fp_str not in (MARK_NA, ""):
                try:
                    acc["fp_values"][config_key].append(float(fp_str))
                except Exception:
                    pass

        _acc("baseline", baseline_block, baseline_fp)
        _acc("rr", rr_block, rr_fp)
        _acc("rr_re", rr_re_block, rr_re_fp)
        _acc("rr_re_erc20", rr_re_erc20_block, rr_re_erc20_fp)
        _acc("crossguard", crossguard_block, crossguard_fp)
        if fb_block != MARK_NA:
            acc["block_seen"]["fb"] = True
        if fb_block == MARK_YES:
            acc["block_counts"]["fb"] += 1
        if fp_3d not in (MARK_NA, ""):
            acc["fp_values"]["fb_3d"].append(float(fp_3d))
        if fp_1d not in (MARK_NA, ""):
            acc["fp_values"]["fb_1d"].append(float(fp_1d))
        if fp_1h not in (MARK_NA, ""):
            acc["fp_values"]["fb_1h"].append(float(fp_1h))

        # Compare to LaTeX expected.
        exp = expected.get(proto, {})
        comparisons = {
            "Baseline Block?": baseline_block,
            "Baseline FP%": baseline_fp,
            "RR Block?": rr_block,
            "RR FP%": rr_fp,
            "RR+RE Block?": rr_re_block,
            "RR+RE FP%": rr_re_fp,
            "RR+RE+ERC20 Block?": rr_re_erc20_block,
            "RR+RE+ERC20 FP%": rr_re_erc20_fp,
            "CrossGuard Block?": crossguard_block,
            "CrossGuard FP%": crossguard_fp,
            "Gas OH%": gas_oh,
            "Feedback Block?": fb_block,
            "3 days FP%": fp_3d,
            "1 day FP%": fp_1d,
            "1 hour FP%": fp_1h,
        }
        for col, actual in comparisons.items():
            exp_val = _strip_latex_tokens(exp.get(col, MARK_NA))
            if col.endswith("Block?"):
                if exp_val != actual:
                    mismatches.append((proto, col, exp_val, actual))
            else:
                if not _compare_numericish(exp_val, actual):
                    mismatches.append((proto, col, exp_val, actual))

        rows.append(
            [
                proto,
                baseline_block,
                baseline_fp,
                rr_block,
                rr_fp,
                rr_re_block,
                rr_re_fp,
                rr_re_erc20_block,
                rr_re_erc20_fp,
                crossguard_block,
                crossguard_fp,
                gas_oh,
                fb_block,
                fp_3d,
                fp_1d,
                fp_1h,
            ]
        )

    # If we never saw the split marker, keep the original single-summary behavior.
    if not split_inserted:
        rows.append(_summary_row(acc))
    else:
        # Second Summary row (large-scale block) appears after Uniswap.
        rows.append(_summary_row(acc))

    _print_mismatches("Table 2 (Ablation)", mismatches, missing)
    return _csv_string(rows)


def generate_table3_csv(
    wo_ts_records,
    w_ts_records,
    latex_text,
):
    expected = _parse_expected_table3(latex_text)

    header = [
        "Metric",
        "CrossGuard (w/o TS)",
        "CrossGuard (w TS)",
    ]
    rows = [header]

    def _collect_details(records):
        details = []
        fp_vals = []
        fp_missing = []
        for proto, rec in sorted(records.items(), key=lambda kv: _normalize_protocol_name(kv[0])):
            hack_cf_count = len(rec.get("cf_hack") or set())
            hack_section_lines = rec.get("hack_section_lines")
            # Table 3 rule (per user): blocked iff there are >=2 lines below
            # '== Hack Call Flows:' and above 'False positives:'.
            blocked = (hack_section_lines is not None) and (int(hack_section_lines) >= 2)
            fp = rec.get("fp_ratio_percent")
            if fp is None:
                fp_missing.append(proto)
            else:
                try:
                    fp_vals.append(float(fp))
                except Exception:
                    fp_missing.append(proto)
                    fp = None
            details.append(
                {
                    "proto": proto,
                    "blocked": blocked,
                    "hack_cf_count": hack_cf_count,
                    "hack_section_lines": hack_section_lines,
                    "fp": fp,
                }
            )
        blocked_count = sum(1 for d in details if d["blocked"])
        fp_sum = sum(fp_vals)
        fp_n = len(fp_vals)
        fp_avg = (fp_sum / fp_n) if fp_n else float("nan")
        return {
            "details": details,
            "blocked_count": blocked_count,
            "total": len(details),
            "fp_vals": fp_vals,
            "fp_sum": fp_sum,
            "fp_n": fp_n,
            "fp_avg": fp_avg,
            "fp_missing": fp_missing,
        }

    wo = _collect_details(wo_ts_records)
    w = _collect_details(w_ts_records)

    wo_blocked, wo_avg_fp = wo["blocked_count"], wo["fp_avg"]
    w_blocked, w_avg_fp = w["blocked_count"], w["fp_avg"]

    # Compare with LaTeX.
    mismatches = []
    missing = []

    exp_blocked = _strip_latex_tokens(expected.get("# Hacks Blocked", {}).get("CrossGuard (w/o TS)", MARK_NA))
    if exp_blocked != MARK_NA and exp_blocked != str(wo_blocked):
        mismatches.append(("# Hacks Blocked", "CrossGuard (w/o TS)", exp_blocked, str(wo_blocked)))

    exp_blocked2 = _strip_latex_tokens(expected.get("# Hacks Blocked", {}).get("CrossGuard (w TS)", MARK_NA))
    if exp_blocked2 != MARK_NA and exp_blocked2 != str(w_blocked):
        mismatches.append(("# Hacks Blocked", "CrossGuard (w TS)", exp_blocked2, str(w_blocked)))

    exp_fp = _strip_latex_tokens(expected.get("Avg. FP%", {}).get("CrossGuard (w/o TS)", MARK_NA))
    wo_fp_str = _fmt_num(wo_avg_fp, 2) if wo_avg_fp == wo_avg_fp else MARK_NA
    if exp_fp != MARK_NA and not _compare_numericish(exp_fp, wo_fp_str):
        mismatches.append(("Avg. FP%", "CrossGuard (w/o TS)", exp_fp, wo_fp_str))

    exp_fp2 = _strip_latex_tokens(expected.get("Avg. FP%", {}).get("CrossGuard (w TS)", MARK_NA))
    w_fp_str = _fmt_num(w_avg_fp, 2) if w_avg_fp == w_avg_fp else MARK_NA
    if exp_fp2 != MARK_NA and not _compare_numericish(exp_fp2, w_fp_str):
        mismatches.append(("Avg. FP%", "CrossGuard (w TS)", exp_fp2, w_fp_str))

    _print_mismatches("Table 3 (Comparison)", mismatches, missing)

    # Detailed calculation explanation.
    # This is intentionally verbose because Table 3 is otherwise hard to audit.
    print("[DETAIL] Table 3 (Comparison): how values are calculated", file=sys.stderr)
    print(
        "  # Hacks Blocked = count(benchmark where hack_section_lines >= 2) (from compared logs)",
        file=sys.stderr,
    )
    print(
        "  Avg. FP% = mean(fp_ratio_percent) over benchmarks where fp_ratio_percent is present",
        file=sys.stderr,
    )

    def _fmt_fp(v):
        return MARK_NA if v is None else _fmt_num(v, 2)

    def _variant_summary(label, coll):
        avg_str = _fmt_num(coll["fp_avg"], 2) if coll["fp_avg"] == coll["fp_avg"] else MARK_NA
        print(
            f"  {label}: total_benchmarks={coll['total']} blocked_count={coll['blocked_count']}",
            file=sys.stderr,
        )
        if coll["fp_n"]:
            print(
                f"  {label}: fp_avg = fp_sum/fp_n = {coll['fp_sum']:.6f}/{coll['fp_n']} = {avg_str}",
                file=sys.stderr,
            )
        else:
            print(
                f"  {label}: fp_avg = N/A (no fp_ratio_percent values present)",
                file=sys.stderr,
            )
        if coll["fp_missing"]:
            sample = ", ".join(coll["fp_missing"][:10])
            more = "" if len(coll["fp_missing"]) <= 10 else f" (+{len(coll['fp_missing']) - 10} more)"
            print(f"  {label}: fp_ratio_percent missing for {len(coll['fp_missing'])}: {sample}{more}", file=sys.stderr)

    _variant_summary("CrossGuard (w/o TS)", wo)
    _variant_summary("CrossGuard (w TS)", w)

    all_protos = sorted(
        set(wo_ts_records.keys()) | set(w_ts_records.keys()),
        key=_normalize_protocol_name,
    )
    wo_by = {d["proto"]: d for d in wo["details"]}
    w_by = {d["proto"]: d for d in w["details"]}

    print("  Per-benchmark inputs (blocked/hack_section_lines/|cf_hack|/fp_ratio_percent):", file=sys.stderr)
    max_lines = 250
    for i, proto in enumerate(all_protos):
        if i >= max_lines:
            print(f"    ... truncated ({len(all_protos) - max_lines} more benchmarks)", file=sys.stderr)
            break
        d1 = wo_by.get(proto)
        d2 = w_by.get(proto)
        wo_block = MARK_NA if d1 is None else _fmt_mark(d1["blocked"])
        wo_hack_lines = (
            MARK_NA
            if d1 is None or d1.get("hack_section_lines") is None
            else str(d1["hack_section_lines"])
        )
        wo_hack = MARK_NA if d1 is None else str(d1["hack_cf_count"])
        wo_fp = MARK_NA if d1 is None else _fmt_fp(d1["fp"])
        w_block_s = MARK_NA if d2 is None else _fmt_mark(d2["blocked"])
        w_hack_lines = (
            MARK_NA
            if d2 is None or d2.get("hack_section_lines") is None
            else str(d2["hack_section_lines"])
        )
        w_hack = MARK_NA if d2 is None else str(d2["hack_cf_count"])
        w_fp_s = MARK_NA if d2 is None else _fmt_fp(d2["fp"])
        print(
            f"    - {_normalize_protocol_name(proto)} | w/o TS: blocked={wo_block} hack_lines={wo_hack_lines} |cf_hack|={wo_hack} fp%={wo_fp} | w TS: blocked={w_block_s} hack_lines={w_hack_lines} |cf_hack|={w_hack} fp%={w_fp_s}",
            file=sys.stderr,
        )

    rows.append(["# Hacks Blocked", str(wo_blocked), str(w_blocked)])
    rows.append(["Avg. FP%", wo_fp_str, w_fp_str])

    # Also append a detailed breakdown to the CSV output (stdout) so users don't have
    # to inspect stderr to understand how Table 3 was derived.
    rows.append(["# Table 3 Details: Calculation Inputs"])  # section marker row
    rows.append([
        "Definition",
        "# Hacks Blocked = count(hack_section_lines >= 2)",
        "Avg. FP% = mean(fp_ratio_percent over present values)",
    ])
    rows.append([
        "Variant",
        "total_benchmarks",
        "blocked_count",
        "fp_sum",
        "fp_n",
        "fp_avg(%)",
    ])
    rows.append([
        "CrossGuard (w/o TS)",
        str(wo["total"]),
        str(wo["blocked_count"]),
        _fmt_num(wo["fp_sum"], 6) if wo["fp_n"] else MARK_NA,
        str(wo["fp_n"]),
        wo_fp_str,
    ])
    rows.append([
        "CrossGuard (w TS)",
        str(w["total"]),
        str(w["blocked_count"]),
        _fmt_num(w["fp_sum"], 6) if w["fp_n"] else MARK_NA,
        str(w["fp_n"]),
        w_fp_str,
    ])
    if wo["fp_missing"] or w["fp_missing"]:
        rows.append([
            "Missing FP%",
            f"w/o TS missing={len(wo['fp_missing'])}",
            f"w TS missing={len(w['fp_missing'])}",
        ])

    rows.append([
        "Victim Protocol",
        "w/o TS blocked",
        "w/o TS hack_lines",
        "w/o TS |cf_hack|",
        "w/o TS FP%",
        "w TS blocked",
        "w TS hack_lines",
        "w TS |cf_hack|",
        "w TS FP%",
    ])
    for proto in all_protos:
        d1 = wo_by.get(proto)
        d2 = w_by.get(proto)
        wo_block = MARK_NA if d1 is None else _fmt_mark(d1["blocked"])
        wo_hack_lines = (
            MARK_NA
            if d1 is None or d1.get("hack_section_lines") is None
            else str(d1["hack_section_lines"])
        )
        wo_hack = MARK_NA if d1 is None else str(d1["hack_cf_count"])
        wo_fp = MARK_NA if d1 is None else _fmt_fp(d1["fp"])
        w_block_s = MARK_NA if d2 is None else _fmt_mark(d2["blocked"])
        w_hack_lines = (
            MARK_NA
            if d2 is None or d2.get("hack_section_lines") is None
            else str(d2["hack_section_lines"])
        )
        w_hack = MARK_NA if d2 is None else str(d2["hack_cf_count"])
        w_fp_s = MARK_NA if d2 is None else _fmt_fp(d2["fp"])
        rows.append([
            _normalize_protocol_name(proto),
            wo_block,
            wo_hack_lines,
            wo_hack,
            wo_fp,
            w_block_s,
            w_hack_lines,
            w_hack,
            w_fp_s,
        ])
    return _csv_string(rows)


def _write_output(text, out_path):
    if not out_path or out_path == "-":
        print(text)
        return
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate AE tables from renamed logs in artifact_evaluation.",
    )
    parser.add_argument(
        "--log-dir",
        default=SCRIPT_DIR,
        help="Directory containing baseline.txt, RR.txt, RR_RE.txt, RR_RE_ERC20.txt, and CrossGuard logs.",
    )
    parser.add_argument(
        "--latex",
        default=os.path.join(SCRIPT_DIR, "Expected_Outputs.txt"),
        help="Path to Expected_Outputs.txt (CSV) or Latex_Tables.txt.",
    )
    parser.add_argument(
        "--table",
        choices=["study", "ablation", "comparison", "all"],
        default="all",
        help="Which table(s) to generate.",
    )
    parser.add_argument(
        "--out",
        default="-",
        help="Output CSV path, or '-' for stdout.",
    )
    args = parser.parse_args(argv)

    latex_text = load_latex_tables(args.latex)

    outputs = []
    final_logs = None
    if args.table in ("study", "ablation", "all"):
        final_logs = load_ae_final_logs(args.log_dir)

    if args.table in ("study", "all"):
        outputs.append(
            generate_table1_csv(
                final_logs["crossguard"],
                latex_text,
                unique_in_hack_records=final_logs.get("rr_re_erc20"),
            )
        )
    if args.table in ("ablation", "all"):
        outputs.append(generate_table2_csv(final_logs, latex_text))
    if args.table in ("comparison", "all"):
        wo_records, w_records = load_ae_trace2inv_logs(args.log_dir)
        outputs.append(generate_table3_csv(wo_records, w_records, latex_text))

    output_text = "\n\n".join(outputs)
    _write_output(output_text, args.out)

    if not _is_latex_expected(latex_text):
        table_labels = []
        if args.table in ("study", "all"):
            table_labels.append("Table 1 (Study)")
        if args.table in ("ablation", "all"):
            table_labels.append("Table 2 (Ablation)")
        if args.table in ("comparison", "all"):
            table_labels.append("Table 3 (Comparison)")
        mismatches, missing, extra = _compare_csv_blocks(
            latex_text, output_text, table_labels
        )
        missing_all = list(missing)
        if extra:
            missing_all.extend(extra)
        expected_path = os.path.abspath(args.latex)
        if not mismatches and not missing_all:
            print(
                f"[OK] Compared with the expected outputs at {expected_path}",
                file=sys.stderr,
            )
        _print_mismatches(
            "Generated Output vs Expected_Outputs.txt",
            mismatches,
            missing_all,
        )
        if mismatches or missing_all:
            raise SystemExit(1)


__all__ = [
    "MARK_YES",
    "MARK_NO",
    "MARK_HALF",
    "MARK_NA",
    "_csv_string",
    "generate_table1_csv",
    "generate_table2_csv",
    "generate_table3_csv",
    "load_expected_outputs",
    "load_latex_tables",
    "load_ae_final_logs",
    "load_ae_trace2inv_logs",
]


if __name__ == "__main__":
    main()
