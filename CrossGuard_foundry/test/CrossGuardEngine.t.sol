// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {CrossGuardEngine} from "../src/CrossGuardEngine.sol";

/**
 * CrossGuard System Understanding:
 * 
 * 1. INTERNAL CALLS: When protocol function A calls protocol function B directly,
 *    only A calls Enter_Func/Exit_Func. B just does instrumentation and passes
 *    isReadOnly/hasRAWDependency info back to A.
 * 
 * 2. REENTRANCY: Only occurs when external contracts call back into the protocol.
 *    Example: A calls external contract → external calls protocol function B
 *    This creates: Enter_Func(A) → Enter_Func(B) (reentrancy detected!)
 * 
 * 3. RAW DEPENDENCIES: Detected through instrumentation within protocol functions
 *    and reported via the hasRAWDependency flag in Exit_Func.
 */




contract helperContract {
    CrossGuardEngine public crossGuardEngine;

    constructor() {
        crossGuardEngine = new CrossGuardEngine();
        // Add this contract as an operator so it can call Exit_Func
        crossGuardEngine.addOperator(address(this));
    }

    function refresh() public {
        crossGuardEngine = new CrossGuardEngine();
        // Add this contract as an operator so it can call Exit_Func
        crossGuardEngine.addOperator(address(this));
    }

    function functionalTest() public {
        refresh();
        // a (run-time) read only function should always pass
        uint funcID = 1;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, true, false);

        // a single function call should always pass
        funcID = 2;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false);

        // two consecutive function call with RAW dependency should revert
        funcID = 3;
        crossGuardEngine.Enter_Func(funcID);

        // expect revert
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }

    }

    function functionalTest2() public {
        refresh();
        // a re-entrant function call should revert 
        uint funcID = 4;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Enter_Func(funcID);

        crossGuardEngine.Exit_Func(funcID, false, false);
        // Expect revert
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }
    }

    // Test actual reentrancy patterns (external contract calls back)
    function testActualReentrancy() public {
        refresh();
        // Test A -> (external) -> A pattern 
        // This simulates: A calls external contract, external calls back to A
        uint funcID_A = 10;
        
        crossGuardEngine.Enter_Func(funcID_A);  // A starts
        crossGuardEngine.Enter_Func(funcID_A);  // External contract calls back to A (reentrancy!)
        
        crossGuardEngine.Exit_Func(funcID_A, false, false);  // Inner A exits
        
        // Should revert due to reentrancy
        try crossGuardEngine.Exit_Func(funcID_A, false, false) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }
    }

    // Test cross-function reentrancy (A -> external -> B)
    function testCrossFunctionReentrancy() public {
        refresh();
        // This simulates: A calls external contract, external calls protocol function B
        uint funcID_A = 100;
        uint funcID_B = 200;
        
        crossGuardEngine.Enter_Func(funcID_A);  // A starts
        crossGuardEngine.Enter_Func(funcID_B);  // External contract calls B (reentrancy!)
        
        crossGuardEngine.Exit_Func(funcID_B, false, false);  // B exits
        
        // Should revert due to reentrancy
        try crossGuardEngine.Exit_Func(funcID_A, false, false) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }
    }

    // Test mixed reentrancy and RAW dependency
    function testReentrancyWithRAW() public {
        refresh();
        uint funcID = 500;
        
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Enter_Func(funcID); // Reentrancy
        
        crossGuardEngine.Exit_Func(funcID, false, false);
        
        // Should revert due to both reentrancy and RAW
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }
    }

    // Test that read-only functions never trigger security violations
    function testReadOnlyAlwaysPasses() public {
        refresh();
        // Single read-only call
        uint funcID = 600;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, true, false); // Should always pass

        // Read-only with potential RAW (shouldn't matter for read-only)
        funcID = 601;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, true, true); // Should pass because it's read-only

        // Read-only in reentrancy context
        funcID = 602;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, true, false); // Read-only, should pass
        crossGuardEngine.Exit_Func(funcID, true, false); // Should pass
    }

    // Test normal protocol function (no external calls)
    function testNormalProtocolFlow() public {
        refresh();
        // A -> B -> C (internal calls) -> exit A
        // Only A calls Enter_Func/Exit_Func, B and C are internal
        uint funcID_A = 700;
        
        crossGuardEngine.Enter_Func(funcID_A);
        // Internal calls to B and C happen here (no Enter_Func/Exit_Func)
        // They just pass isReadOnly and hasRAWDependency info up
        crossGuardEngine.Exit_Func(funcID_A, false, false);
        // Should pass - normal execution
    }

    // Test RAW dependency without reentrancy
    function testRAWDependencyOnly() public {
        refresh();
        uint funcID = 1000;
        crossGuardEngine.Enter_Func(funcID);
        
        // Should revert due to RAW dependency
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }
    }

    // Test multiple separate invocations (should reset state)
    function testMultipleSeparateInvocations() public {
        refresh();
        // First invocation
        uint funcID = 1100;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false); // Should pass
        
        // Second invocation (state should be reset)
        funcID = 1200;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false); // Should pass
        
        // Third invocation with different pattern
        funcID = 1300;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, true, false); // Read-only, should pass
    }

    // Test multiple separate transactions (should pass)
    function testSeparateTransactions() public {
        refresh();
        // First transaction: A calls external, external calls B
        uint funcID_A = 1400;
        uint funcID_B = 1500;
        
        crossGuardEngine.Enter_Func(funcID_A);
        crossGuardEngine.Enter_Func(funcID_B); // External calls B (reentrancy)
        crossGuardEngine.Exit_Func(funcID_B, false, false);
        
        // This should fail due to reentrancy
        try crossGuardEngine.Exit_Func(funcID_A, false, false) {
            revert("Expected revert did not happen");
        } catch {
            // expected revert
        }
    }

    function atomicTest() public {
        refresh();
        uint funcID = 1;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false);

        funcID = 2;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false);

        funcID = 3;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false);

        funcID = 4;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false);
    }
}




contract CrossGuardEngineTest is Test {
    helperContract public helper;

    function setUp() public {
        helper = new helperContract();
    }

    function test_Functional() public {
        helper.functionalTest();
    }

    function test_Functional2() public {
        helper.functionalTest2();
    }

    function test_ActualReentrancy() public {
        helper.testActualReentrancy();
    }

    function test_CrossFunctionReentrancy() public {
        helper.testCrossFunctionReentrancy();
    }

    function test_ReentrancyWithRAW() public {
        helper.testReentrancyWithRAW();
    }

    function test_ReadOnlyAlwaysPasses() public {
        helper.testReadOnlyAlwaysPasses();
    }

    function test_NormalProtocolFlow() public {
        helper.testNormalProtocolFlow();
    }

    function test_RAWDependencyOnly() public {
        helper.testRAWDependencyOnly();
    }

    function test_MultipleSeparateInvocations() public {
        helper.testMultipleSeparateInvocations();
    }

    function test_SeparateTransactions() public {
        helper.testSeparateTransactions();
    }

    function test_Validate2() public {
        
        helper.atomicTest();
    }
}