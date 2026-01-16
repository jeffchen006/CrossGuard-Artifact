# artifact_evaluation

This folder is the checkpoint for the artifact evaluation. It is where we explain how to run the experiments, how those runs map to figures/tables in the paper, and how we verify the outputs against expected results.

If you only want to run the experiments, you can mostly ignore this folder. If you want to validate the reproduction or understand how a number in the paper is produced, start here.

## How this folder is used

1. Run the experiments (see the top-level README).
2. The experiment scripts write logs under `artifact_evaluation/logs/`.
3. Run `table_printers.py` to parse those logs into `tables_generated.csv` and compare against `Expected_Outputs.txt`.

## Files you will probably open

- `ae_artifact_guide.md`: the main evaluation guide, written for reviewers.
- `ae_reproduction_mapping.md`: a map from each experiment to the specific table/figure entries in the paper.
- `ae_validation_targets.md`: what we consider a successful reproduction (targets and thresholds).
- `ae_key_stats_report.md`: summary statistics referenced by the paper.
- `Expected_Outputs.txt`: the canonical expected table outputs for comparison.
- `table_printers.py`: the script that turns logs into tables and checks against expected outputs.
- `tables_generated.csv`: the last generated table output (overwritten each run).
- `logs/`: experiment logs parsed by `table_printers.py`.

## Notes

- `table_printers.py` expects specific log filenames inside `artifact_evaluation/logs/`. If a log is missing, it will stop with a missing-file error.
- `Expected_Outputs.txt` is plain text. If you change any experiment or inputs, you may need to regenerate or update it.
- The `tables_generated.csv` file is mainly for inspection and debugging; it is not treated as a source of truth.
