// SPDX-License-Identifier: UNLICENSED
// (c) Zhiyang Chen 2024

pragma solidity ^0.8.17;

import {console} from "forge-std/console.sol";
import "./TransientStorageUtils.sol";


contract CrossGuardEngine {
    constructor() {
        admins[msg.sender] = true;
        operators[msg.sender] = true;
        _allowedCFHashes[0] = true; // Allow the zero CFHash by default
    }

    // Admin and operator mappings
    mapping(address => bool) public operators; // operators are the contracts inside the same protocol
    mapping(address => bool) public admins; // approved senders are the contracts that can call the validate functions
    
    // show always be transient storage
    // a sum is a summation
    // when a function enters, it adds +X
    // when a function exits, it subtracts X
    // so the sum should be 0, when a new invocation starts

    // Transient storage slots for CFHash, sum, invCount, and isRAWDependent
    bytes32 private constant SLOT_CFHASH = bytes32(uint256(0));
    bytes32 private constant SLOT_SUM = bytes32(uint256(1));
    bytes32 private constant SLOT_INVCOUNT = bytes32(uint256(2));
    bytes32 private constant SLOT_ISRAWDEPENDENT = bytes32(uint256(3));
    bytes32 private constant SLOT_ISCF_RAW = bytes32(uint256(4));
    bytes32 private constant SLOT_ISCF_REENTRANCY = bytes32(uint256(5));

    mapping(uint216 => bool) internal _allowedCFHashes;



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


    // Admin functions to add operators and configure rules
    function addOperator(address operator) external onlyAdmin {
        operators[operator] = true;
    }

    modifier onlyOperator() {
        require(operators[msg.sender], "CrossGuard error: operator required");
        _;
    }

    modifier onlyAdmin() {
        require(admins[msg.sender], "CrossGuard error: admin required");
        _;
    }

    function configureRules(uint216 _CFHash) external onlyAdmin {
        _allowedCFHashes[_CFHash] = true;
    }

    function Enter_Func(uint256 funcID)
        public
        returns (uint times)
    {
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


    function Exit_Func(uint256 funcID, bool isRR, bool isRAW)
        external
        onlyOperator
    {   
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




}
    

