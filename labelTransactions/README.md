# labelTransactions

This folder contains the transaction-level labeling scripts. They combine the benchmark trace lists with contract labels (and Etherscan metadata) to assign categories to transactions.

## What these scripts do

- `labelTransactions.py`: the entry point that runs the labeling workflow end to end.
- `transactionLabeling.py`: the core logic used for categorization.
- `toLabels2_argmented5.md`: the resulting label definitions used by downstream experiments.

## How it fits in the pipeline

- It reads the benchmark lists from `Benchmarks_Traces/`.
- It uses labels from `labelPackage/` and data from `crawlPackage/` to resolve categories.
- The output is a markdown label file that other scripts consume.

## Notes

- If you update the benchmark lists or labels, re-run this stage to keep everything in sync.
- Some logic assumes certain benchmark names or categories; keep file names stable when possible.
