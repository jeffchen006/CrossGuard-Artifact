// // SPDX-License-Identifier: UNLICENSED
// pragma solidity ^0.8.13;

// import {Test} from "forge-std/Test.sol";
// import {CrossGuardEngine} from "../src/CrossGuardEngine.sol";
// import {Contract2Protect} from "../src/Instrumented_Contract.sol";


// contract Contract2ProtectTest is Test {

//     CrossGuardEngine public crossGuardEngine1;
//     Contract2Protect public Contract2Protect1;

//     CrossGuardEngine public crossGuardEngine2;
//     Contract2Protect public Contract2Protect2;

//     CrossGuardEngine public crossGuardEngine3;
//     Contract2Protect public Contract2Protect3;

//     CrossGuardEngine public crossGuardEngine4;
//     Contract2Protect public Contract2Protect4;

//     CrossGuardEngine public crossGuardEngine5;
//     Contract2Protect public Contract2Protect5;

//     CrossGuardEngine public crossGuardEngine6;
//     Contract2Protect public Contract2Protect6;

//     CrossGuardEngine public crossGuardEngine7;
//     Contract2Protect public Contract2Protect7;

//     CrossGuardEngine public crossGuardEngine8;
//     Contract2Protect public Contract2Protect8;


//     function setUp() public {
//         crossGuardEngine1 = new CrossGuardEngine();
//         Contract2Protect1 = new Contract2Protect(
//             address(crossGuardEngine1)
//         );
//         // Add contracts as operators
//         crossGuardEngine1.addOperator(address(Contract2Protect1));

//         crossGuardEngine2 = new CrossGuardEngine();
//         Contract2Protect2 = new Contract2Protect(
//            address(crossGuardEngine2) 
//         );
//         crossGuardEngine2.addOperator(address(Contract2Protect2));

//         crossGuardEngine3 = new CrossGuardEngine();
//         Contract2Protect3 = new Contract2Protect(
//             address(crossGuardEngine3)
//         );
//         crossGuardEngine3.addOperator(address(Contract2Protect3));

//         crossGuardEngine4 = new CrossGuardEngine();
//         Contract2Protect4 = new Contract2Protect(
//             address(crossGuardEngine4)
//         );
//         crossGuardEngine4.addOperator(address(Contract2Protect4));

//         crossGuardEngine5 = new CrossGuardEngine();
//         Contract2Protect5 = new Contract2Protect(
//             address(crossGuardEngine5)
//         );
//         crossGuardEngine5.addOperator(address(Contract2Protect5));

//         crossGuardEngine6 = new CrossGuardEngine();
//         Contract2Protect6 = new Contract2Protect(
//             address(crossGuardEngine6)
//         );
//         crossGuardEngine6.addOperator(address(Contract2Protect6));

//         crossGuardEngine7 = new CrossGuardEngine();
//         Contract2Protect7 = new Contract2Protect(
//             address(crossGuardEngine7)
//         );
//         crossGuardEngine7.addOperator(address(Contract2Protect7));

//         crossGuardEngine8 = new CrossGuardEngine();
//         Contract2Protect8 = new Contract2Protect(
//             address(crossGuardEngine8)
//         );
//         crossGuardEngine8.addOperator(address(Contract2Protect8));
//     }

//     // function test_updateCurrentTimestampCF() public {
//     //         uint times = 4;
//     //         for (uint i = 0; i < 10; i++) {
//     //             times ++;
//     //             Contract2Protect1.updateCurrentTimestampBare();
//     //             Contract2Protect2.updateCurrentTimestampTopDown(times);
//     //             Contract2Protect3.updateCurrentTimestampTopDownSload(times);
//     //             Contract2Protect4.updateCurrentTimestampTopDownSstore(times);
//     //         }
//     // }

//     // Comprehensive gas measurement tests
//     function test_GasConsumption_SingleCall() public {
//         emit log_string("=== Gas Consumption Analysis - Single Function Call ===");
        
//         uint gasBefore;
//         uint gasAfter;
//         uint gasUsed;
//         uint times = 1;

//         // Test 1: Bare function (baseline)
//         gasBefore = gasleft();
//         Contract2Protect1.updateCurrentTimestampBare();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("Bare function gas used", gasUsed);

//         // Test 2: Top-down instrumentation (basic)
//         gasBefore = gasleft();
//         Contract2Protect2.updateCurrentTimestampTopDown(times);
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("TopDown instrumentation gas used", gasUsed);

//         // Test 3: SLOAD tracking
//         gasBefore = gasleft();
//         Contract2Protect3.updateCurrentTimestampTopDownSload(times);
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("TopDown + SLOAD tracking gas used", gasUsed);

//         // Test 4: SSTORE tracking
//         gasBefore = gasleft();
//         Contract2Protect4.updateCurrentTimestampTopDownSstore(times);
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("TopDown + SSTORE tracking gas used", gasUsed);

//         // Test 5: Full instrumentation (SLOAD + SSTORE)
//         gasBefore = gasleft();
//         Contract2Protect5.updateCurrentTimestampTopDownSloadSstore(times);
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("Full instrumentation (SLOAD + SSTORE) gas used", gasUsed);

//         // Test 6: CrossGuard wrapper versions
//         gasBefore = gasleft();
//         Contract2Protect6.updateCurrentTimestampTopDown();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard wrapped TopDown gas used", gasUsed);

//         gasBefore = gasleft();
//         Contract2Protect7.updateCurrentTimestampTopDownSload();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard wrapped TopDown + SLOAD gas used", gasUsed);

//         gasBefore = gasleft();
//         Contract2Protect8.updateCurrentTimestampTopDownSstore();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard wrapped TopDown + SSTORE gas used", gasUsed);
//     }

//     function test_GasConsumption_MultipleCall() public {
//         emit log_string("=== Gas Consumption Analysis - Multiple Function Calls (10 iterations) ===");
        
//         uint gasBefore;
//         uint gasAfter;
//         uint gasUsed;
//         uint times = 1;

//         // Test with multiple calls to see scaling
//         gasBefore = gasleft();
//         for (uint i = 0; i < 10; i++) {
//             Contract2Protect1.updateCurrentTimestampBare();
//         }
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("Bare function (10 calls) total gas", gasUsed);
//         emit log_named_uint("Bare function avg gas per call", gasUsed / 10);

//         gasBefore = gasleft();
//         for (uint i = 0; i < 10; i++) {
//             times++;
//             Contract2Protect2.updateCurrentTimestampTopDown(times);
//         }
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("TopDown instrumentation (10 calls) total gas", gasUsed);
//         emit log_named_uint("TopDown instrumentation avg gas per call", gasUsed / 10);

//         times = 1;
//         gasBefore = gasleft();
//         for (uint i = 0; i < 10; i++) {
//             times++;
//             Contract2Protect3.updateCurrentTimestampTopDownSload(times);
//         }
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("SLOAD tracking (10 calls) total gas", gasUsed);
//         emit log_named_uint("SLOAD tracking avg gas per call", gasUsed / 10);

//         times = 1;
//         gasBefore = gasleft();
//         for (uint i = 0; i < 10; i++) {
//             times++;
//             Contract2Protect4.updateCurrentTimestampTopDownSstore(times);
//         }
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("SSTORE tracking (10 calls) total gas", gasUsed);
//         emit log_named_uint("SSTORE tracking avg gas per call", gasUsed / 10);

//         times = 1;
//         gasBefore = gasleft();
//         for (uint i = 0; i < 10; i++) {
//             times++;
//             Contract2Protect5.updateCurrentTimestampTopDownSloadSstore(times);
//         }
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("Full instrumentation (10 calls) total gas", gasUsed);
//         emit log_named_uint("Full instrumentation avg gas per call", gasUsed / 10);
//     }



//     function test_GasConsumption_WithCrossGuardEngine() public {
//         emit log_string("=== Gas Consumption Analysis - With CrossGuard Engine Integration ===");
        
//         uint gasBefore;
//         uint gasAfter;
//         uint gasUsed;

//         // Test functions that integrate with CrossGuardEngine
//         gasBefore = gasleft();
//         Contract2Protect1.updateCurrentTimestampTopDown();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard Enter/Exit + TopDown gas used", gasUsed);

//         gasBefore = gasleft();
//         Contract2Protect2.updateCurrentTimestampTopDownSload();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard Enter/Exit + SLOAD tracking gas used", gasUsed);

//         gasBefore = gasleft();
//         Contract2Protect3.updateCurrentTimestampTopDownSstore();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard Enter/Exit + SSTORE tracking gas used", gasUsed);

//         gasBefore = gasleft();
//         Contract2Protect4.updateCurrentTimestampTopDownSloadSstore();
//         gasAfter = gasleft();
//         gasUsed = gasBefore - gasAfter;
//         emit log_named_uint("CrossGuard Enter/Exit + Full instrumentation gas used", gasUsed);
//     }

//     function test_GasConsumption_Overhead() public {
//         emit log_string("=== Gas Consumption Overhead Analysis ===");
        
//         uint gasBefore;
//         uint gasAfter;
//         uint bareGas;
//         uint instrumentedGas;
//         uint overhead;
//         uint times = 1;

//         // Measure baseline
//         gasBefore = gasleft();
//         Contract2Protect1.updateCurrentTimestampBare();
//         gasAfter = gasleft();
//         bareGas = gasBefore - gasAfter;

//         // Measure each instrumentation level and calculate overhead
//         gasBefore = gasleft();
//         Contract2Protect2.updateCurrentTimestampTopDown(times);
//         gasAfter = gasleft();
//         instrumentedGas = gasBefore - gasAfter;
//         overhead = instrumentedGas - bareGas;
//         emit log_named_uint("TopDown instrumentation overhead (gas)", overhead);
//         emit log_named_uint("TopDown overhead percentage", (overhead * 100) / bareGas);

//         gasBefore = gasleft();
//         Contract2Protect3.updateCurrentTimestampTopDownSload(times);
//         gasAfter = gasleft();
//         instrumentedGas = gasBefore - gasAfter;
//         overhead = instrumentedGas - bareGas;
//         emit log_named_uint("SLOAD tracking overhead (gas)", overhead);
//         emit log_named_uint("SLOAD tracking overhead percentage", (overhead * 100) / bareGas);

//         gasBefore = gasleft();
//         Contract2Protect4.updateCurrentTimestampTopDownSstore(times);
//         gasAfter = gasleft();
//         instrumentedGas = gasBefore - gasAfter;
//         overhead = instrumentedGas - bareGas;
//         emit log_named_uint("SSTORE tracking overhead (gas)", overhead);
//         emit log_named_uint("SSTORE tracking overhead percentage", (overhead * 100) / bareGas);

//         gasBefore = gasleft();
//         Contract2Protect5.updateCurrentTimestampTopDownSloadSstore(times);
//         gasAfter = gasleft();
//         instrumentedGas = gasBefore - gasAfter;
//         overhead = instrumentedGas - bareGas;
//         emit log_named_uint("Full instrumentation overhead (gas)", overhead);
//         emit log_named_uint("Full instrumentation overhead percentage", (overhead * 100) / bareGas);

//         // Test CrossGuard wrapper overhead
//         gasBefore = gasleft();
//         Contract2Protect6.updateCurrentTimestampTopDown();
//         gasAfter = gasleft();
//         instrumentedGas = gasBefore - gasAfter;
//         overhead = instrumentedGas - bareGas;
//         emit log_named_uint("CrossGuard integration overhead (gas)", overhead);
//         emit log_named_uint("CrossGuard integration overhead percentage", (overhead * 100) / bareGas);
//     }

//     function test_GasConsumption_Scaling() public {
//         emit log_string("=== Gas Consumption Scaling Analysis ===");
        
//         // Test how gas consumption scales with different numbers of operations
//         uint[] memory iterations = new uint[](4);
//         iterations[0] = 1;
//         iterations[1] = 5;
//         iterations[2] = 10;
//         iterations[3] = 20;

//         for (uint j = 0; j < iterations.length; j++) {
//             uint numIterations = iterations[j];
//             emit log_string("--- Scaling case ---");
//             emit log_named_uint("Iterations", numIterations);
            
//             uint gasBefore;
//             uint gasAfter;
//             uint gasUsed;
//             uint times = 1;

//             // Bare function scaling
//             gasBefore = gasleft();
//             for (uint i = 0; i < numIterations; i++) {
//                 Contract2Protect1.updateCurrentTimestampBare();
//             }
//             gasAfter = gasleft();
//             gasUsed = gasBefore - gasAfter;
//             emit log_named_uint("Bare function total gas", gasUsed);
//             emit log_named_uint("Bare function gas per call", gasUsed / numIterations);

//             // Full instrumentation scaling
//             times = 1;
//             gasBefore = gasleft();
//             for (uint i = 0; i < numIterations; i++) {
//                 times++;
//                 Contract2Protect2.updateCurrentTimestampTopDownSloadSstore(times);
//             }
//             gasAfter = gasleft();
//             gasUsed = gasBefore - gasAfter;
//             emit log_named_uint("Full instrumentation total gas", gasUsed);
//             emit log_named_uint("Full instrumentation gas per call", gasUsed / numIterations);
//         }
//     }
// }
