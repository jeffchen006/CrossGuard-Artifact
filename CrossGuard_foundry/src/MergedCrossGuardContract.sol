// SPDX-License-Identifier: MIT
// (c) Zhiyang Chen 2024

pragma solidity ^0.8.26;
pragma abicoder v2;

import {console} from "forge-std/console.sol";
import "./TransientStorageUtils.sol";

/// @notice Merged contract combining CrossGuardEngine and Contract2Protect functionality
contract MergedCrossGuardContract {
    uint256 emptyUint; // Placeholder for empty uint to ensure all storage slots are bigger than 0, 
                       // which is required for transient storage to work correctly
    uint256 storedTimestamp;
    uint256 storedBlockNumber;

    constructor() {
        admins[msg.sender] = true;
        operators[msg.sender] = true;
        _allowedCFHashes[0] = true; // Allow the zero CFHash by default
    }

    // Admin and operator mappings (from CrossGuardEngine)
    mapping(address => bool) public operators; // operators are the contracts inside the same protocol
    mapping(address => bool) public admins; // approved senders are the contracts that can call the validate functions
    
    // Transient storage slots for CFHash, sum, invCount, and isRAWDependent (from CrossGuardEngine)
    bytes32 private constant SLOT_CFHASH = bytes32(uint256(0));
    bytes32 private constant SLOT_SUM = bytes32(uint256(1));
    bytes32 private constant SLOT_INVCOUNT = bytes32(uint256(2));
    bytes32 private constant SLOT_ISRAWDEPENDENT = bytes32(uint256(3));
    bytes32 private constant SLOT_ISCF_RAW = bytes32(uint256(4));
    bytes32 private constant SLOT_ISCF_REENTRANCY = bytes32(uint256(5));

    mapping(uint216 => bool) internal _allowedCFHashes;

    // Base slots for mappings (from Contract2Protect)
    bytes32 private constant SLOT_STORAGE_WRITES = keccak256("CrossGuardEngine.storageWrites");
    bytes32 private constant SLOT_TEMP_STORAGE_READS = keccak256("CrossGuardEngine.tempStorageReads");
    bytes32 private constant SLOT_TEMP_STORAGE_WRITES = keccak256("CrossGuardEngine.tempStorageWrites");

    // ========================== Begin of Transient Array Functions ==========================
    // Transient Array for callTrace
    uint constant TRANSIENT_ARRAY_LENGTH_SLOT = 0x6;
    uint constant TRANSIENT_ARRAY_BASE_SLOT = 0x7;

    // Push an element to the transient array
    function push(uint256 value) internal {
        assembly {
            // Load the current length from transient storage
            let len := tload(TRANSIENT_ARRAY_LENGTH_SLOT)
            // Store value at slot (BASE_SLOT + len)
            tstore(add(TRANSIENT_ARRAY_BASE_SLOT, len), value)
            // Increment length and store it back
            tstore(TRANSIENT_ARRAY_LENGTH_SLOT, add(len, 1))
        }
    }

    // Pop an element from the transient array and return it
    function pop() internal returns (uint256 value) {
        assembly {
            let len := tload(TRANSIENT_ARRAY_LENGTH_SLOT)
            // Ensure array is not empty
            if iszero(len) {
                revert(0, 0)
            }
            // Decrement length
            len := sub(len, 1)
            // Read value from the last slot
            value := tload(add(TRANSIENT_ARRAY_BASE_SLOT, len))
            // Update length back
            tstore(TRANSIENT_ARRAY_LENGTH_SLOT, len)
        }
    }

    // Get element at index
    function get(uint256 index) internal view returns (uint256 value) {
        assembly {
            let len := tload(TRANSIENT_ARRAY_LENGTH_SLOT)
            // Ensure index < len
            if iszero(lt(index, len)) {
                revert(0, 0)
            }
            value := tload(add(TRANSIENT_ARRAY_BASE_SLOT, index))
        }
    }

    // Get current length of the transient array
    function length() internal view returns (uint256 len) {
        assembly {
            len := tload(TRANSIENT_ARRAY_LENGTH_SLOT)
        }
    }

    // Clear the transient array (reset length to 0)
    function clear() internal {
        assembly {
            // Simply set length to 0
            tstore(TRANSIENT_ARRAY_LENGTH_SLOT, 0)
        }
    }
    // ========================== End of Transient Array Functions ==========================

    // Modifiers
    modifier onlyOperator() {
        require(operators[msg.sender], "CrossGuard error: operator required");
        _;
    }

    modifier onlyAdmin() {
        require(admins[msg.sender], "CrossGuard error: admin required");
        _;
    }

    // Admin functions to add operators and configure rules
    function addOperator(address operator) external onlyAdmin {
        operators[operator] = true;
    }

    function configureRules(uint216 _CFHash) external onlyAdmin {
        _allowedCFHashes[_CFHash] = true;
    }

    // CrossGuardEngine functions - now public instead of external
    function Enter_Func(uint256 funcID) public returns (uint times) {
        // Load sum using Tload
        uint256 sum = uint256(TransientStorageUtils.Tload(SLOT_SUM));
        // Load invCount using Tload
        uint256 invCount = uint256(TransientStorageUtils.Tload(SLOT_INVCOUNT));
        if (sum == 0) {
            invCount += 1;
            // Store the updated invCount using Tstore
            TransientStorageUtils.Tstore(SLOT_INVCOUNT, bytes32(invCount));
        } else {
            // Set isCF_ReEntrancy to true
            TransientStorageUtils.Tstore(SLOT_ISCF_REENTRANCY, bytes32(uint(1)));
        }
        sum += funcID;
        // Store the updated sum using Tstore
        TransientStorageUtils.Tstore(SLOT_SUM, bytes32(sum));
        push(funcID);
        return invCount;
    }

    function Exit_Func(uint256 funcID, bool isRR, bool isRAW) public {   
        // Load sum 
        uint sum = uint256(TransientStorageUtils.Tload(SLOT_SUM));
        sum -= funcID;

        // store the updated sum using Tstore
        TransientStorageUtils.Tstore(SLOT_SUM, bytes32(sum));

        if (isRR) {
            pop();
        } else {
            push( type(uint256).max - funcID);
        } 
        uint216 CFHash = 0;
        if (sum == 0) {
            uint len = length();
            for (uint i = 0; i < len; i++) {
                uint256 id = get(i);
                CFHash = uint216(bytes27(keccak256(abi.encode(id, CFHash))));
            }
            clear();
        }
        if (isRAW) {
            // Store the updated isCF_RAW using Tstore
            TransientStorageUtils.Tstore(SLOT_ISCF_RAW, bytes32(uint(1)));
        }
        bool isCFReEntrancy = (TransientStorageUtils.Tload(SLOT_ISCF_REENTRANCY) != bytes32(0));
        bool isCFRAW = (TransientStorageUtils.Tload(SLOT_ISCF_RAW) != bytes32(0));

        // print out the CFHash
        console.log("CFHash: ", CFHash);

        if (!_allowedCFHashes[CFHash] && (isCFReEntrancy || isCFRAW))  {
            revert("Unsafe pattern detected");
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

    // ********** storageWrites (mapping(uint256 => mapping(uint256 => bool))) **********
    // Set value in storageWrites mapping
    function setStorageWrites(uint256 slot, uint256 times, bool value) internal {
        bytes32 storageSlot = getNestedMappingSlot(SLOT_STORAGE_WRITES, slot, times);
        Tstore(storageSlot, bytes32(uint256(value ? 1 : 0)));  // Store boolean as 0 or 1
    }

    // Get value from storageWrites mapping
    function getStorageWrites(uint256 slot, uint256 times) internal view returns (bool) {
        bytes32 storageSlot = getNestedMappingSlot(SLOT_STORAGE_WRITES, slot, times);
        return uint256(Tload(storageSlot)) != 0;  // Return true if non-zero, false otherwise
    }

    // ********** tempStorageReads (mapping(uint256 => uint256)) **********
    // Set value in tempStorageReads mapping
    function setTempStorageReads(uint256 key, uint256 value) internal {
        bytes32 storageSlot = getMappingSlot(SLOT_TEMP_STORAGE_READS, key);
        Tstore(storageSlot, bytes32(value));
    }

    // Get value from tempStorageReads mapping
    function getTempStorageReads(uint256 key) internal view returns (uint256) {
        bytes32 storageSlot = getMappingSlot(SLOT_TEMP_STORAGE_READS, key);
        return uint256(Tload(storageSlot));
    }

    // ********** tempStorageWrites (mapping(uint256 => uint256)) **********
    // Set value in tempStorageWrites mapping
    function setTempStorageWrites(uint256 key, uint256 value) internal {
        bytes32 storageSlot = getMappingSlot(SLOT_TEMP_STORAGE_WRITES, key);
        Tstore(storageSlot, bytes32(value));
    }

    // Get value from tempStorageWrites mapping
    function getTempStorageWrites(uint256 key) internal view returns (uint256) {
        bytes32 storageSlot = getMappingSlot(SLOT_TEMP_STORAGE_WRITES, key);
        return uint256(Tload(storageSlot));
    }

    // Instrumented contract functions - modified to use internal calls instead of external CrossGuardEngine calls
    function updateCurrentTimestampTopDownSloadSstore() public  {
        uint invNum = Enter_Func(1); // Now internal call
        // Call the top-down function
        (bool isReadOnly, bool hasRAWDependency) = updateCurrentTimestampTopDownSloadSstore(invNum);
        Exit_Func(1, isReadOnly, hasRAWDependency); // Now internal call
    }

    function updateCurrentTimestampTopDownSloadSstore(uint invNum) internal returns (bool, bool) {
        // ********** define the read and write sets **********
        uint256[] memory readElements = new uint256[](3);
        uint256[] memory writeElements = new uint256[](3);
        uint readElementsIndex = 0;
        uint writeElementsIndex = 0;

        // ********** every sload instrumentation **********
        // Append the read element
        readElements[readElementsIndex] = 0x1; // 0x1 represents the storage slot of storedTimestamp
        readElementsIndex ++;
        // Check if the temp storage has been written to
        if (getTempStorageWrites(0x1) == 0 && getTempStorageReads(0x1) == 0) {
            setTempStorageReads(0x1, storedTimestamp);
        }

        // ********** every sstore instrumentation **********
        setTempStorageWrites(0x1, 7028);
        // Append the write element
        writeElements[writeElementsIndex] = 0x1; // 0x1 represents the storage slot of storedTimestamp
        writeElementsIndex ++;

        // ================= original code start =================
        storedTimestamp = storedTimestamp + 7028;
        // ================= original code end ===================

        // ********** check runtime read only **********
        bool isReadOnly = true;
        for (uint256 i = 0; i < writeElementsIndex; i++) {
            uint slot = writeElements[i];
            // ********** check if it's a cached **********
            if ( getTempStorageWrites(slot) != getTempStorageReads(slot)) {
                // it is a cache, used for RAW analysis but does not count towards readOnly
                setStorageWrites(slot, invNum, true);
                isReadOnly = false;
            } else {
                // fake write 
            }
        }

        // ********** check RAW dependency **********
        bool hasRAWDependency = false;
        for (uint256 i = 0; i < readElementsIndex; i++) {
            uint slot = readElements[i];
            for (uint256 j = 0; j < invNum; j++) {
                if (getStorageWrites(slot, j)) {
                    hasRAWDependency = true;
                    break;
                }
            }
        }
        return (isReadOnly, hasRAWDependency);
    }

    function updateCurrentTimestampTopDownSload() public {
        uint invNum = Enter_Func(1); // Now internal call
        // Call the top-down function
        (bool isReadOnly, bool hasRAWDependency) = updateCurrentTimestampTopDownSload(invNum);
        Exit_Func(1, isReadOnly, hasRAWDependency); // Now internal call
    }

    function updateCurrentTimestampTopDownSload(uint invNum) internal returns (bool, bool) {
        // ********** define the read and write sets **********
        uint256[] memory readElements = new uint256[](3);
        uint256[] memory writeElements = new uint256[](3);
        uint readElementsIndex = 0;
        uint writeElementsIndex = 0;

        // ********** every sload instrumentation **********
        // Append the read element
        readElements[readElementsIndex] = 0x1; // 0x1 represents the storage slot of storedTimestamp
        readElementsIndex ++;
        // Check if the temp storage has been written to
        if (getTempStorageWrites(0x1) == 0 && getTempStorageReads(0x1) == 0) {
            setTempStorageReads(0x1, storedTimestamp);
        }
        
        // ================= original code start =================
        storedTimestamp = storedTimestamp + 7028;
        // ================= original code end ===================

        // ********** check runtime read only **********
        bool isReadOnly = true;
        for (uint256 i = 0; i < writeElementsIndex; i++) {
            uint slot = writeElements[i];
            // ********** check if it's a cached **********
            if ( getTempStorageWrites(slot) != getTempStorageReads(slot)) {
                // it is a cache, used for RAW analysis but does not count towards readOnly
                setStorageWrites(slot, invNum, true);
                isReadOnly = false;
            } else {
                // fake write 
            }
        }

        // ********** check RAW dependency **********
        bool hasRAWDependency = false;
        for (uint256 i = 0; i < readElementsIndex; i++) {
            uint slot = readElements[i];
            for (uint256 j = 0; j < invNum; j++) {
                if (getStorageWrites(slot, j)) {
                    hasRAWDependency = true;
                    break;
                }
            }
        }
        return (isReadOnly, hasRAWDependency);
    }

    function updateCurrentTimestampTopDownSstore() public {
        uint invNum = Enter_Func(1); // Now internal call
        // Call the top-down function
        (bool isReadOnly, bool hasRAWDependency) = updateCurrentTimestampTopDownSstore(invNum);
        Exit_Func(1, isReadOnly, hasRAWDependency); // Now internal call
    }
    
    function updateCurrentTimestampTopDownSstore(uint invNum) internal returns (bool, bool) {
        // ********** define the read and write sets **********
        uint256[] memory readElements = new uint256[](3);
        uint256[] memory writeElements = new uint256[](3);
        uint readElementsIndex = 0;
        uint writeElementsIndex = 0;
        
        // ********** every sstore instrumentation **********
        setTempStorageWrites(0x1, 7028);
        // Append the write element
        writeElements[writeElementsIndex] = 0x1; // 0x1 represents the storage slot of storedTimestamp
        writeElementsIndex ++;

        // ================= original code start =================
        storedTimestamp = storedTimestamp + 7028;
        // ================= original code end ===================

        // ********** check runtime read only **********
        bool isReadOnly = true;
        for (uint256 i = 0; i < writeElementsIndex; i++) {
            uint slot = writeElements[i];
            // ********** check if it's a cached **********
            if ( getTempStorageWrites(slot) != getTempStorageReads(slot)) {
                // it is a cache, used for RAW analysis but does not count towards readOnly
                setStorageWrites(slot, invNum, true);
                isReadOnly = false;
            } else {
                // fake write 
            }
        }

        // ********** check RAW dependency **********
        bool hasRAWDependency = false;
        for (uint256 i = 0; i < readElementsIndex; i++) {
            uint slot = readElements[i];
            for (uint256 j = 0; j < invNum; j++) {
                if (getStorageWrites(slot, j)) {
                    hasRAWDependency = true;
                    break;
                }
            }
        }

        return (isReadOnly, hasRAWDependency);
    }

    function updateCurrentTimestampTopDown() public {
        uint invNum = Enter_Func(1); // Now internal call
        // Call the top-down function
        (bool isReadOnly, bool hasRAWDependency) = updateCurrentTimestampTopDown(invNum);
        Exit_Func(1, isReadOnly, hasRAWDependency); // Now internal call
    }

    function updateCurrentTimestampTopDown_bare() public {
        // Call the top-down function
        uint invNum = 1; 
        (bool isReadOnly, bool hasRAWDependency) = updateCurrentTimestampTopDown(invNum);
    }


    function updateCurrentTimestampTopDown(uint invNum) internal returns (bool, bool) {
        // ********** define the read and write sets **********
        uint256[] memory readElements = new uint256[](3);
        uint256[] memory writeElements = new uint256[](3);
        uint readElementsIndex = 0;
        uint writeElementsIndex = 0;
        
        // ================= original code start =================
        storedTimestamp = storedTimestamp + 7028;
        // ================= original code end ===================

        // ********** check runtime read only **********
        bool isReadOnly = true;
        for (uint256 i = 0; i < writeElementsIndex; i++) {
            uint slot = writeElements[i];
            // ********** check if it's a cached **********
            if ( getTempStorageWrites(slot) != getTempStorageReads(slot)) {
                // it is a cache, used for RAW analysis but does not count towards readOnly
                setStorageWrites(slot, invNum, true);
                isReadOnly = false;
            } else {
                // fake write 
            }
        }

        // ********** check RAW dependency **********
        bool hasRAWDependency = false;
        for (uint256 i = 0; i < readElementsIndex; i++) {
            uint slot = readElements[i];
            for (uint256 j = 0; j < invNum; j++) {
                if (getStorageWrites(slot, j)) {
                    hasRAWDependency = true;
                    break;
                }
            }
        }
        return (isReadOnly, hasRAWDependency);
    }

    // Bare function for comparison
    function updateCurrentTimestampBare() public {
        storedTimestamp = storedTimestamp + 7028;
    }

    // Getter functions for testing
    function getStoredTimestamp() public view returns (uint256) {
        return storedTimestamp;
    }
} 