// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {CrossGuardEngine} from "../src/CrossGuardEngine.sol";

/**
 * Advanced CrossGuard Security Tests
 * 
 * These tests validate the security detection capabilities including:
 * - Reentrancy attacks via external contract callbacks
 * - RAW dependency detection through instrumentation
 * - Mixed attack scenarios
 * - Edge cases and access control
 */

contract AdvancedSecurityTest is Test {
    CrossGuardEngine public crossGuardEngine;

    function setUp() public {
        crossGuardEngine = new CrossGuardEngine();
        // Add this contract as an operator
        crossGuardEngine.addOperator(address(this));
    }

    // Test that legitimate protocol patterns are allowed
    function test_LegitimateProtocolPatterns() public {
        console.log("=== Testing Legitimate Protocol Patterns ===");
        
        // Test normal protocol execution (internal calls don't trigger Enter/Exit)
        uint funcID_A = 1000;
        
        // Pattern: A -> B -> C -> D (all internal) -> exit A
        crossGuardEngine.Enter_Func(funcID_A);
        // B, C, D are internal function calls within the protocol
        // They don't call Enter_Func/Exit_Func, just pass info up the stack
        crossGuardEngine.Exit_Func(funcID_A, false, false);
        
        console.log("Normal protocol pattern without violations: PASSED");
        
        // Test multiple separate protocol calls
        uint funcID_B = 2000;
        uint funcID_C = 3000;
        
        crossGuardEngine.Enter_Func(funcID_B);
        crossGuardEngine.Exit_Func(funcID_B, false, false);
        
        crossGuardEngine.Enter_Func(funcID_C);
        crossGuardEngine.Exit_Func(funcID_C, true, false); // Read-only
        
        console.log("Multiple separate protocol calls: PASSED");
    }

    // Test that read-only patterns never fail regardless of complexity
    function test_ReadOnlyComplexPatterns() public {
        console.log("=== Testing Read-Only Complex Patterns ===");
        
        // Even with potential reentrancy pattern, read-only should pass
        uint funcID = 5000;
        
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Enter_Func(funcID);
        
        // All read-only, should pass even with reentrancy
        crossGuardEngine.Exit_Func(funcID, true, false);
        crossGuardEngine.Exit_Func(funcID, true, false);
        crossGuardEngine.Exit_Func(funcID, true, false);
        
        console.log("Read-only pattern with reentrancy structure: PASSED");
        
        // Test read-only with RAW indicators (should still pass)
        funcID = 5001;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, true, true); // Read-only with RAW should pass
        
        console.log("Read-only with RAW indicators: PASSED");
    }

    // Test CFHash calculation and whitelist functionality
    function test_CFHashWhitelisting() public {
        console.log("=== Testing CFHash Whitelisting ===");
        
        // First, let's create a specific pattern and see its CFHash
        uint funcID = 6000;
        crossGuardEngine.Enter_Func(funcID);
        
        // This should fail initially (not whitelisted + has violation)
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Pattern correctly blocked before whitelisting");
        }
        
        // Note: In real scenario, admin would extract the CFHash from logs
        // and add it to whitelist using configureRules()
    }

    // Test various reentrancy attack patterns
    function test_ReentrancyAttackPatterns() public {
        console.log("=== Testing Reentrancy Attack Patterns ===");
        
        // Pattern 1: Simple reentrancy (A -> external -> A)
        uint funcID = 7000;
        crossGuardEngine.Enter_Func(funcID);      // A starts
        crossGuardEngine.Enter_Func(funcID);      // External contract calls back to A
        
        crossGuardEngine.Exit_Func(funcID, false, false);  // Inner A exits
        try crossGuardEngine.Exit_Func(funcID, false, false) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Simple reentrancy attack: BLOCKED");
        }
        

    }


    // Test various reentrancy attack patterns
    function test_ReentrancyAttackPatterns1() public {
        // Pattern 2: Cross-function reentrancy (A -> external -> B)
        uint funcID_A = 7001;
        uint funcID_B = 7002;
        
        crossGuardEngine.Enter_Func(funcID_A);   // A starts
        crossGuardEngine.Enter_Func(funcID_B);   // External contract calls B
        
        crossGuardEngine.Exit_Func(funcID_B, false, false);  // B exits
        try crossGuardEngine.Exit_Func(funcID_A, false, false) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Cross-function reentrancy attack: BLOCKED");
        }
        

    }


    // Test various reentrancy attack patterns
    function test_ReentrancyAttackPatterns2() public {
        // Pattern 3: Multiple external reentrancy calls
        uint funcID_A = 7003;
        uint funcID_B = 7004;
        uint funcID_C = 7005;
        
        crossGuardEngine.Enter_Func(funcID_A);   // A starts
        crossGuardEngine.Enter_Func(funcID_B);   // External calls B
        crossGuardEngine.Enter_Func(funcID_C);   // External calls C
        
        crossGuardEngine.Exit_Func(funcID_C, false, false);  // C exits
        crossGuardEngine.Exit_Func(funcID_B, false, false);  // B exits
        try crossGuardEngine.Exit_Func(funcID_A, false, false) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Multiple external reentrancy calls: BLOCKED");
        }
    }



    // Test RAW dependency detection patterns
    function test_RAWDependencyPatterns() public {
        console.log("=== Testing RAW Dependency Patterns ===");
        
        // Single function with RAW dependency
        uint funcID = 8000;
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false);

        // Function with internal calls that have RAW dependency
        uint funcID_A = 8001;
        crossGuardEngine.Enter_Func(funcID_A);
        // Internal protocol functions detect RAW dependency and pass it up
        // The final Exit_Func gets the aggregated RAW dependency info
        try crossGuardEngine.Exit_Func(funcID_A, false, true) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Protocol function with internal RAW dependency: BLOCKED");
        }
    }

    // Test mixed violation scenarios
    function test_MixedViolationScenarios() public {
        console.log("=== Testing Mixed Violation Scenarios ===");
        
        // Reentrancy + RAW dependency
        uint funcID = 9000;
        crossGuardEngine.Enter_Func(funcID);      // A starts
        crossGuardEngine.Enter_Func(funcID);      // External calls A again (reentrancy)
        
        crossGuardEngine.Exit_Func(funcID, false, true); // Inner A exits with RAW dependency
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Reentrancy + RAW dependency: BLOCKED");
        }
        
    }

    // Test state isolation between transactions
    function test_StateIsolation() public {
        console.log("=== Testing State Isolation Between Transactions ===");
        
        // First transaction with violation
        uint funcID = 10000;
        crossGuardEngine.Enter_Func(funcID);
        
        try crossGuardEngine.Exit_Func(funcID, false, true) {
            revert("Expected revert did not happen");
        } catch {
            console.log("First transaction with violation: BLOCKED");
        }
        
        // Second transaction should start fresh (same funcID, but no violation)
        crossGuardEngine.Enter_Func(funcID);
        crossGuardEngine.Exit_Func(funcID, false, false); // Should pass
        
        console.log("Second transaction with same funcID: PASSED");
        
        // Third transaction with different pattern
        uint funcID_A = 10001;
        uint funcID_B = 10002;
        
        crossGuardEngine.Enter_Func(funcID_A);
        crossGuardEngine.Enter_Func(funcID_B);
        crossGuardEngine.Exit_Func(funcID_B, false, false);
        crossGuardEngine.Exit_Func(funcID_A, false, false);
        
        console.log("Third transaction with different pattern: PASSED");
    }



    // Test performance with many nested calls
    function test_PerformanceWithNestedCalls() public {
        console.log("=== Testing Performance with Many Nested Calls ===");
        
        uint depth = 10;
        uint startGas = gasleft();
        crossGuardEngine.Enter_Func(12000);
        
        // Enter many functions
        for (uint i = 1; i < depth; i++) {
            crossGuardEngine.Enter_Func(i + 12000);
        }
        
        // Exit in reverse order
        for (uint i = depth; i > 1; i--) {
            crossGuardEngine.Exit_Func((i - 1) + 12000, false, false);
        }

        // Expect revert
        try crossGuardEngine.Exit_Func(12000, false, false) {
            revert("Expected revert did not happen");
        } catch {
            console.log("Nested calls: PASSED");
        }
        
        
        uint gasUsed = startGas - gasleft();
        console.log("Gas used for", depth, "nested calls:", gasUsed);
        console.log("Average gas per call:", gasUsed / (depth * 2));
    }
} 