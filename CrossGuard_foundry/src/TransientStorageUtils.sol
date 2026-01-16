

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

library TransientStorageUtils {
    // Function to Tload from transient storage
    function Tload(bytes32 slot) internal view returns (bytes32 result) {
        assembly {
            result := tload(slot)
        }
    }

    // Function to Tstore into transient storage
    function Tstore(bytes32 slot, bytes32 value) internal {
        assembly {
            tstore(slot, value)
        }
    }

    // Helper function to calculate the storage slot for a single key mapping
    function getMappingSlot(bytes32 baseSlot, uint256 key) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(key, baseSlot));
    }

    // Helper function to calculate the storage slot for a nested mapping
    function getNestedMappingSlot(bytes32 baseSlot, uint256 outerKey, uint256 innerKey) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(innerKey, keccak256(abi.encodePacked(outerKey, baseSlot))));
    }

    // Set value in transient storage mapping (single key)
    function setTransientUint(bytes32 baseSlot, uint256 key, uint256 value) internal {
        bytes32 storageSlot = getMappingSlot(baseSlot, key);
        Tstore(storageSlot, bytes32(value));
    }

    // Get value from transient storage mapping (single key)
    function getTransientUint(bytes32 baseSlot, uint256 key) internal view returns (uint256) {
        bytes32 storageSlot = getMappingSlot(baseSlot, key);
        return uint256(Tload(storageSlot));
    }

    // Set boolean in transient nested mapping (double key)
    function setTransientBoolNested(bytes32 baseSlot, uint256 outerKey, uint256 innerKey, bool value) internal {
        bytes32 storageSlot = getNestedMappingSlot(baseSlot, outerKey, innerKey);
        Tstore(storageSlot, bytes32(uint256(value ? 1 : 0)));
    }

    // Get boolean from transient nested mapping (double key)
    function getTransientBoolNested(bytes32 baseSlot, uint256 outerKey, uint256 innerKey) internal view returns (bool) {
        bytes32 storageSlot = getNestedMappingSlot(baseSlot, outerKey, innerKey);
        return uint256(Tload(storageSlot)) != 0;
    }
}