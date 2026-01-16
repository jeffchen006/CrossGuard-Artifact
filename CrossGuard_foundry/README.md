<!-- forge test --gas-report --evm-version cancun -vvv --optimizer-runs 0


forge test --gas-report --evm-version cancun -vvv --optimizer-runs 0 --match-contract CrossGuardGasComparisonTest > report0713.txt


forge test --gas-report --evm-version cancun -vvv --optimizer-runs 0 --match-contract AdvancedSecurityTest > report1223.txt

 -->


forge test --gas-report --evm-version cancun -vvv --match-contract CrossGuardGasComparisonTest --optimizer-runs 10000




Build + run:

Build: docker build -t crossguard-gas --build-arg FOUNDRY_COMMIT=fdf5732d08ce1c67aa0aaf047c3fb86614caf5ae --build-arg SOLC_VERSION=0.8.26 .
Run: docker run --rm -t crossguard-gas



Remove the container(s) (only needed if you ran without --rm):

docker ps -a --filter ancestor=crossguard-gas
docker rm -f $(docker ps -aq --filter ancestor=crossguard-gas)




cleanup:

docker rmi -f crossguard-gas
docker builder prune -af
docker system prune -af
