#!/bin/bash

# forge test --gas-report --evm-version cancun -vvv \
#     --match-contract helperContract > helperContract_2.txt

# forge test --evm-version cancun -vvv \
#     --match-contract CrossGuardGasComparisonTest > gasComparison_2.txt

# forge test --gas-report --evm-version cancun -vvv \
#     --match-contract Contract2ProtectTest > InstrumentationResults_2.txt



forge test --gas-report --evm-version cancun -vvv --match-contract CrossGuardGasComparisonTest --optimizer-runs 10000
