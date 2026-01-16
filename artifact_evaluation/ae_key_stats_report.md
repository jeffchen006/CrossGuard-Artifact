# AE Key-Stats Report

## Inputs
- baseline: `artifact_evaluation/baseline.txt` (2867238 bytes)
- rr: `artifact_evaluation/RR.txt` (2693091 bytes)
- rr_re: `artifact_evaluation/RR_RE.txt` (2616437 bytes)
- rr_re_erc20: `artifact_evaluation/RR_RE_ERC20.txt` (827412 bytes)
- crossguard: `artifact_evaluation/RR_RE_ERC20_RAW.txt` (768718 bytes)
- fb_3d: `artifact_evaluation/RR_RE_ERC20_RAW_3days.txt` (588701 bytes)
- fb_1d: `artifact_evaluation/RR_RE_ERC20_RAW_1day.txt` (579548 bytes)
- fb_1h: `artifact_evaluation/RR_RE_ERC20_RAW_1hour.txt` (530867 bytes)
- trace2inv_wo_ts: `artifact_evaluation/trace2inv0_CrossGuard_woTS_compared.txt` (233895 bytes)
- trace2inv_w_ts: `artifact_evaluation/trace2inv1_CrossGuard_wTS_compared.txt` (104186 bytes)

## Table 1 (Study)
- Unique CF counts: Yes=34, Half=1, No=2
- Exceptions (Unique CF != Yes): Auctus, Bedrock_DeFi, CreamFi2
- Protocols with <=9 nCF: 27

### Comparisons
- Expected Yes count: 32 -> actual 34 (FAIL)
- Expected exceptions: Bedrock_DeFi, DODO, Opyn, VisorFi, bZx -> actual Auctus, Bedrock_DeFi, CreamFi2 (FAIL)
- Expected <=9 nCF count: 27 -> actual 27 (PASS)
- Avg Ratio P-Tx: expected 6.11 -> actual 0.73 (FAIL)
- Avg Ratio P-nCF: expected 18.35 -> actual 18.99 (FAIL)
- Avg Ratio S-Tx: expected 70.14 -> actual 67.28 (FAIL)
- Avg Ratio S-nCF: expected 20.01 -> actual 29.91 (FAIL)
- Avg Ratio O-Tx: expected 10.58 -> actual 17.9 (FAIL)
- Avg Ratio O-nCF: expected 5.97 -> actual 12.03 (FAIL)
- Avg Ratio E-Tx: expected 13.17 -> actual 14.08 (FAIL)
- Avg Ratio E-nCF: expected 65.64 -> actual 58.39 (FAIL)
- First external nCF is hack: NOT DERIVABLE from current logs

## Table 2 (Ablation + Gas)
- Summary (37 protocols): CrossGuard blocked=35.0, FP%=0.26, Gas OH%=3.53
- Summary feedback FP%: 3d=0.06, 1d=0.05, 1h=0.03
### Comparisons
- Expected CrossGuard blocked 35 -> actual 35.0 (PASS)
- Expected CrossGuard FP 0.26 -> actual 0.26 (PASS)
- Expected feedback FP [0.06, 0.05, 0.03] -> actual [0.06, 0.05, 0.03] (PASS)
- Expected avg gas OH 3.53 -> actual 3.53 (PASS)
- Summary (AAVE/Lido/Uniswap): Gas OH%=7.52
- Expected large-suite avg gas OH 7.52 -> actual 7.52 (PASS)
- Bypassability counts/list: NOT DERIVABLE from current logs

## Table 3 (Comparison)
- CSV (CrossGuard w/o TS / w TS): blocked=['35', '35'], avg FP%=['1.19', '0.15']
- Expected CrossGuard w/o TS blocked 35 FP 1.19
- Expected CrossGuard w TS blocked 35 FP 0.15

### Trace2Inv (from trace2inv logs)
- trace2inv0 (assumed EOA^GC^DFU): blocked=35, avg FP=1.19, total=38
- Expected blocked 34 FP 3.14
- trace2inv1 (assumed EOA^(OB|DFU)): blocked=35, avg FP=0.15, total=38
- Expected blocked 29 FP 0.23

## Other key statistics
- SphereX gas overhead: 0.2247476694878895 (expected 0.22)
- SphereX tx breakdown: simple=127, deployer=38, total=166 (expected simple=127, deployer=38)
- AAVE/Lido/Uniswap total tx counts (from logs): {'AAVE2': 71405, 'Lido2': 94703, 'Uniswap2': 75715} (expected 100000 each)
- Dataset composition 21/8/8 by source: NOT DERIVABLE from current logs (expected 21/8/8)
- Heuristic limitation only Bedrock_DeFi: NOT DERIVABLE from current logs
