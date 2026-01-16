// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import "forge-std/Test.sol";
import "../src/CrossGuardEngine.sol";
import "../src/Instrumented_Contract.sol";
import "../src/MergedCrossGuardContract.sol";

contract CrossGuardGasComparisonTest is Test {
    CrossGuardEngine public engine;
    Contract2Protect public instrumentedContract;
    MergedCrossGuardContract public mergedContract;
    uint numIterations = 10;

    function setUp() public {

        // Deploy CrossGuardEngine
        engine = new CrossGuardEngine();
        
        // Deploy instrumented contract with engine reference
        instrumentedContract = new Contract2Protect(address(engine));
        
        // Add the instrumented contract as an operator to the engine
        engine.addOperator(address(instrumentedContract));
        
        // Deploy merged contract
        mergedContract = new MergedCrossGuardContract();
    }

    function testGasComparisonBareFunction() public {
        emit log_string("=== Gas Comparison: Bare Function ===");
        uint gasBefore;
        uint gasAfter;
        uint gasUsed;

        // Test separate contracts
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            instrumentedContract.updateCurrentTimestampBare();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("instrumentedContract Bare function total gas", gasUsed);
        emit log_named_uint("instrumentedContract Bare function gas per call", gasUsed / numIterations);

        // Test merged contract
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            mergedContract.updateCurrentTimestampBare();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("mergedContract Bare function total gas", gasUsed);
        emit log_named_uint("mergedContract Bare function gas per call", gasUsed / numIterations);
    }

    function testGasComparisonTopDownFunction() public {
        emit log_string("=== Gas Comparison: TopDown Function ===");

        uint gasBefore;
        uint gasAfter;
        uint gasUsed;

        // Test separate contracts
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            instrumentedContract.updateCurrentTimestampTopDown();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("instrumentedContract Bare function total gas", gasUsed);
        emit log_named_uint("instrumentedContract Bare function gas per call", gasUsed / numIterations);

        // Test merged contract
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            mergedContract.updateCurrentTimestampTopDown();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("mergedContract Bare function total gas", gasUsed);
        emit log_named_uint("mergedContract Bare function gas per call", gasUsed / numIterations);
    }



    function testGasComparisonTopDownSloadFunction() public {
        emit log_string("=== Gas Comparison: TopDownSload Function ===");
        
        uint gasBefore;
        uint gasAfter;
        uint gasUsed;

        // Test separate contracts
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            instrumentedContract.updateCurrentTimestampTopDownSload();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("instrumentedContract Bare function total gas", gasUsed);
        emit log_named_uint("instrumentedContract Bare function gas per call", gasUsed / numIterations);

        // Test merged contract
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            mergedContract.updateCurrentTimestampTopDownSload();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("mergedContract Bare function total gas", gasUsed);
        emit log_named_uint("mergedContract Bare function gas per call", gasUsed / numIterations);
    }



    function testGasComparisonTopDownSstoreFunction() public {
        emit log_string("=== Gas Comparison: TopDownSload Function ===");
        
        uint gasBefore;
        uint gasAfter;
        uint gasUsed;

        // Test separate contracts
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            instrumentedContract.updateCurrentTimestampTopDownSstore();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("instrumentedContract Bare function total gas", gasUsed);
        emit log_named_uint("instrumentedContract Bare function gas per call", gasUsed / numIterations);

        // Test merged contract
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            mergedContract.updateCurrentTimestampTopDownSstore();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("mergedContract Bare function total gas", gasUsed);
        emit log_named_uint("mergedContract Bare function gas per call", gasUsed / numIterations);

    }

    function testGasComparisonTopDownSloadSstoreFunction() public {
        emit log_string("=== Gas Comparison: TopDownSloadSstore Function ===");

        uint gasBefore;
        uint gasAfter;
        uint gasUsed;

        // Test separate contracts
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            instrumentedContract.updateCurrentTimestampTopDownSloadSstore();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("instrumentedContract Bare function total gas", gasUsed);
        emit log_named_uint("instrumentedContract Bare function gas per call", gasUsed / numIterations);

        // Test merged contract
        gasBefore = gasleft();
        for (uint i = 0; i < numIterations; i++) {
            mergedContract.updateCurrentTimestampTopDownSloadSstore();
        }
        gasAfter = gasleft();
        gasUsed = gasBefore - gasAfter;
        emit log_named_uint("mergedContract Bare function total gas", gasUsed);
        emit log_named_uint("mergedContract Bare function gas per call", gasUsed / numIterations);

    }




} 