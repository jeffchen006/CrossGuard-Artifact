// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {TransientProbe, TransientProbeViaLib} from "../src/TransientProbe.sol";

contract TransientStorageProbeTest is Test {
    TransientProbe internal probe;
    TransientProbeViaLib internal probeViaLib;

    function setUp() public {
        probe = new TransientProbe();
        probeViaLib = new TransientProbeViaLib();
    }

    /// Within a single call, tstore then tload should return the same value.
    function test_setThenGet_sameCall() public {
        uint256 v = 123;
        uint256 readValue = probe.setThenGet(v);
        assertEq(readValue, v, "tload did not read back value in same call");
    }

    function test_setThenGet_sameCall_viaLib() public {
        uint256 v = 124;
        uint256 readValue = probeViaLib.setThenGet(v);
        assertEq(readValue, v, "viaLib: tload did not read back value in same call");
    }

    /// Across two external calls within the same transaction, transient storage should persist.
    function test_persists_acrossExternalCalls_sameTx() public {
        uint256 v = 456;
        probe.set(v);
        uint256 readValue = probe.get();
        assertEq(readValue, v, "transient value did not persist across external calls");
    }

    function test_persists_acrossExternalCalls_sameTx_viaLib() public {
        uint256 v = 457;
        probeViaLib.set(v);
        uint256 readValue = probeViaLib.get();
        assertEq(readValue, v, "viaLib: transient value did not persist across external calls");
    }

    /// Sanity: a fresh test starts with empty transient storage.
    function test_freshTx_startsZero() public {
        uint256 readValue = probe.get();
        assertEq(readValue, 0, "expected transient slot to start as 0");
    }
}
