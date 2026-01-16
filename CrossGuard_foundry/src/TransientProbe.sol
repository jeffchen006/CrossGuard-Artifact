// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.24;

import {TransientStorageUtils} from "./TransientStorageUtils.sol";

/// @notice Minimal probe for EIP-1153 transient storage behavior.
contract TransientProbe {
    uint256 private constant SLOT = 0xBEEF;

    function set(uint256 value) external {
        assembly {
            tstore(SLOT, value)
        }
    }

    function get() external view returns (uint256 value) {
        assembly {
            value := tload(SLOT)
        }
    }

    function setThenGet(uint256 value) external returns (uint256 readValue) {
        assembly {
            tstore(SLOT, value)
            readValue := tload(SLOT)
        }
    }

    function clear() external {
        assembly {
            tstore(SLOT, 0)
        }
    }
}

/// @notice Same as TransientProbe but uses TransientStorageUtils (bytes32 slot) like CrossGuardEngine.
contract TransientProbeViaLib {
    bytes32 private constant SLOT = bytes32(uint256(0xBEEF));

    function set(uint256 value) external {
        TransientStorageUtils.Tstore(SLOT, bytes32(value));
    }

    function get() external view returns (uint256) {
        return uint256(TransientStorageUtils.Tload(SLOT));
    }

    function setThenGet(uint256 value) external returns (uint256) {
        TransientStorageUtils.Tstore(SLOT, bytes32(value));
        return uint256(TransientStorageUtils.Tload(SLOT));
    }
}
