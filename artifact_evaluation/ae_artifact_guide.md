# Artifact Evaluation Guide

This guide is a step-by-step, PC-friendly walkthrough to reproduce tables and key statistics in `artifact_evaluation/ae_validation_targets.md` using the new `runFullExperiments.py` pipeline and the AE extraction script.

## 0. Prerequisites

### 0.1 Python packages
Verify required Python packages:
```bash
python3 -c "import ujson, numpy, pandas, matplotlib, tqdm"
```
Expected result: no ImportError.

### 0.2 Network and API access
The experiment scripts call RPC endpoints and Etherscan APIs configured in `settings.toml`. Ensure these endpoints are reachable and keys are valid.

### 0.3 Caches and traces
The experiment requires `constraintPackage/cache/functionAccess/<benchmark>/<block>.json` and decoded traces in `parserPackage/cache/<benchmark>_decoded/`. If missing, experiments will fail or skip benchmarks.

## 1. Run the full experiment suite

Command (from repo root):
```bash
python3 runFullExperiments.py
```

What it does:
- Runs CrossGuard configurations (baseline, RR, RR+RE, RR+RE+ERC20, RR+RE+ERC20+RAW, and three feedback windows).
- Runs Trace2Inv comparison variants (w/o training and w/ training).
- Executes all tasks in parallel and writes logs under `artifact_evaluation/`.

Expected log outputs (all under `artifact_evaluation/`):
- CrossGuard logs:
  - `baseline.txt`
  - `RR.txt`
  - `RR_RE.txt`
  - `RR_RE_ERC20.txt`
  - `RR_RE_ERC20_RAW.txt`
  - `RR_RE_ERC20_RAW_3days.txt`
  - `RR_RE_ERC20_RAW_1day.txt`
  - `RR_RE_ERC20_RAW_1hour.txt`
- Trace2Inv logs:
  - `trace2inv0_CrossGuard_woTS_compared.txt`
  - `trace2inv1_CrossGuard_wTS_compared.txt`

Expected runtime: long (multiple hours), depending on RPC speed and cache coverage.

## 2. Extract tables and key statistics

Command:
```bash
python3 artifact_evaluation/ae_extract_and_compare.py --log-dir artifact_evaluation
```

What it does:
- Parses the log files above.
- Generates CSV tables matching `Latex_Tables.txt`.
- Computes key statistics listed in `ae_validation_targets.md` and compares them to expected values.

Outputs:
- `artifact_evaluation/tables_generated.csv`
- `artifact_evaluation/ae_key_stats_report.md`
- `artifact_evaluation/table_mismatch_report.txt`

Note: The script uses `Latex_Tables.txt` for table expectations and `ae_validation_targets.md` values for key-stat comparisons. Table mismatches (per-protocol) are written to `artifact_evaluation/table_mismatch_report.txt`.

## 3. Compare results to expected targets

### 3.1 Table 1 (Study)
Check `artifact_evaluation/ae_key_stats_report.md` section “Table 1 (Study)”:
- Unique CF counts (expected 32/37 unique; exceptions set = bZx, VisorFi, Opyn, DODO, Bedrock_DeFi).
- Protocols with <=9 nCF (expected 27).
- Ratio summary (P-Tx, P-nCF, S-Tx, S-nCF, O-Tx, O-nCF, E-Tx, E-nCF).

If any comparison is marked FAIL, inspect:
- `artifact_evaluation/tables_generated.csv` (Table 1 block).
- Original log `artifact_evaluation/RR_RE_ERC20_RAW.txt`.

### 3.2 Table 2 (Ablation + Gas + Feedback)
Check `artifact_evaluation/ae_key_stats_report.md` section “Table 2 (Ablation + Gas)”:
- Summary row (37 protocols): CrossGuard blocked count and FP%, average gas overhead, feedback FP%.
- Summary row (AAVE/Lido/Uniswap): average gas overhead.

Bypassability (Not-Bypassable / Flash-Loan / bypassable list) is not auto-derived from logs; manual validation is required.

### 3.3 Table 3 (Comparison)
Check `artifact_evaluation/ae_key_stats_report.md` section “Table 3 (Comparison)”:
- CrossGuard w/o TS and w TS values derived by the table generator (based on compared logs).
- Trace2Inv values computed directly from `trace2inv0_...` and `trace2inv1_...` logs (assumed to map to EOA^GC^DFU and EOA^(OB|DFU)).

### 3.4 Other key statistics
Check `artifact_evaluation/ae_key_stats_report.md` “Other key statistics”:
- SphereX overhead and tx breakdown (166 total, 127 simple, 38 deployer).
- AAVE/Lido/Uniswap total tx counts (expected 100,000 each).
- Dataset split 21/8/8 by source: not derivable from logs (manual check).
- Heuristic limitation only Bedrock_DeFi: not derivable from logs (manual check).

## 4. Troubleshooting

Common issues:
- Missing logs: rerun `runFullExperiments.py` and confirm all files are produced.
- Mismatches in tables: open `tables_generated.csv` and compare against `Latex_Tables.txt`.
- RPC/API failures: check `settings.toml` for valid keys/endpoints and rerun.

## 5. Files to include in AE submission

- `artifact_evaluation/ae_validation_targets.md` (targets/claims)
- `artifact_evaluation/ae_extract_and_compare.py` (extraction + comparison script)
- `artifact_evaluation/tables_generated.csv` (generated tables)
- `artifact_evaluation/ae_key_stats_report.md` (comparison report)
- Experiment logs under `artifact_evaluation/` (listed above)
