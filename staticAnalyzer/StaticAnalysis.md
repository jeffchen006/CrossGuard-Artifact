# This file is critically important 


It records everything we need to get from the static analysis of the bytecode!



# a few macro labels: 

# 0: potential arbitrary external call
# 1: read-only [in Solidity code] x, this part we can ignore, it is the most correct one
# 2. read-only, by reasoning about the bytecode (no sstore)
# 3. read-only like, one branch is read-only, the other is not 
#           (for these functions we also need to check their runtime behavior)
#           Assumption: one branch with only read operations, another branch with write operations, we can simply insert guard on read operations.
#           Assumption: not all executions will collect interest
#           
# 4. which two functions are behaving having RAW dependency and which functions are bahaving without 
# 5. common ERC20 operations ... this is ignored ... very hard to say ... how to make sense of this?

# which proxy contract uses which implementations?




"0xed2cd60c0000a990a5ffaf0e7ddc70a37d7c623f":{
    "0x12065fe0": ("getBalance", [], ["uint"], True),
    "0x2e1a7d4d": ("withdraw", ["uint"], [], False),
    "0xb6b55f25": ("deposit", ["uint"], [], False),
},
"0xfca4416d9def20ac5b6da8b8b322b6559770efbf": {
    "0x8c92b130": ("yCrvToUnderlying", ["uint", "uint"], ["uint"], True),
},
"0xd8d6ab3d2094d3a0258f4193c5c85fadd44d589a": {
    "0x8c92b130": ("yCrvToUnderlying", ["uint", "uint"], ["uint"], True),
},
"0xffde4785e980a99fe10e6a87a67d243664b91b25": {
    "0x00000000": ("execute_44g58pv", [], [], False),
},
"0xf00a38376c8668fc1f3cd3daeef42e0e44a7fcdb": {
    "0x00000000": ("execute_44g58pv", [], [], False),
    "0xc6acb34f": ("delegateCompLikeTokenFromPool", ["address", "address", "address"], [], False)
},
"0xd06527d5e56a3495252a528c4987003b712860ee": {
    "0x0a087903": ("sushi", [], [], True),
    "0x6f307dc3": ("underlying", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True),
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
},
"0xaa6198fe597dfc331471ae7deba026fb299297fc": {
    "0x06599aa0": ("getTradeData", ["address", "address", "uint"], ["uint", "uint", "uint"], True),
    "0x5e19a6eb": ("guessed_5e19a6eb", ["address[]"], [], False), # store decimals of a list of tokens in the contract
    "0x50c9b1fb": ("guessed_50c9b1fb", ["address[]", "uint[]"], [], False),  # store these values into the contract, only called by the owner
    "0x72e98a79": ("transferBZxOwnership", ["address"], [], False), 
    "0xdaebc33e": ("guessed_daebc33e", ["address", "address", "uint", "uint"], None, False), # priviledged function, transfer DAI to bZx DAI token
    "0xaccdeccc": ("setSaneRate", ["address", "address"], [], False),
    "0x4849b6c8": ("trade", ["address", "address", "uint", "uint"], ["uint"], False),
    "0xff8a2640": ("guessed_ff8a2640", None, None, True),
    "0xe54699c1": ("clearSaneRate", ["address", "address"], [], False),
    "0x565ebfed": ("getCurrentMarginAndCollateralSize", ["address", "address", "address", "uint", "uint", "uint"], ["uint"], True),
    "0xc3feec61": ("guessed_c3feec61", None, None, False), # looks like a trade
    "0x79356a91": ("guessed_79356a91", None, None, False), # looks like a trade
    "0x369308ce": ("guessed_369308ce", None, None, False), # looks like close and withdraw
    "0x051c8a8d": ("tradeUserAsset", ["address","address","address","address","uint","uint","uint"], [], False),
    "0x00432cf3": ("getCurrentMarginAmount", ["address","address","address","uint","uint","uint"], ["uint"], True),
    "0x5e3f4b3c": ("guessed_5e3f4b3c", None, None, True),
    "0xf5537ede": ("transferToken", ["address", "address", "uint"], ["bool"], False),
    "0x7dbe6df8": ("guessed_7dbe6df8", None, None, False), # (1) check priviledged, (2) update a few storage slots from 0 to 1
},
"0x1cf226e9413addaf22412a2e182f9c0de44af002": {
    "0x327ab639": ("payInterestForOracle", ["address", "address"], [], False),
    "0x17815f1d": ("guessed_17815f1d", None, None, False), # update oracle
    "0x17815F1D": ("guessed_17815f1d", None, None, False), # update oracle
    "0x1E202240": ("liquidatePosition", ["bytes32","address","uint256"], None, False),
    "0x0a90b578": ("getLenderInterestForOracle", ["address","address","address"], None, True),
    "0xb1fd9e05": ("getTotalEscrowWithRate", ["bytes32","address","uint256","uint256"], None, True),
    "0x34cf5561": ("guess_34cf5561", None, None, False),
    "0x8b851665": ("guess_8b851665", None, None, False),
    "0x178F416F": ("guess_178F416F", None, None, False),
    "0x3ad97167": ("guess_3ad97167", None, None, False),
    "0xc4d66de8": ("guess_c4d66de8", None, None, False),
},
"0xfa6de2697d59e88ed7fc4dfe5a33dac43565ea41": {
    "0x255de7bb": ("swapExactAmountIn", ["address", "address", "uint", "address", "uint", "uint"], [], False)
},
"0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258": {
    "0x36bdd087": ("_supportMarket", ["address", "uint"], ["bool"], False),
    "0x3d98a1e5": ("isMarketListed", None, None, True)
},
"0x3756fa458880fa8fe53604101cf31c542ef22f6f": {
    "0xc4d66de8": ("initialize", ["address"], None, False), # update oracle
    "0xb1eac3ad": ("guessed_b1eac3ad", None, None, False), # withdraw token + trade
    "0xf3d75a9c": ("getBorrowAmount", ["address","address","address","uint256","uint256"], ["uint"], True),
},
"0x7d8bb0dcfb4f20115883050f45b517459735181b": {
    "0xc4d66de8": ("guessed_c4d66de8", None, None, False), 
    "0x327ab639": ("guessed_327ab639", None, None, False),
    "0x0a90b578": ("guessed_0a90b578", None, None, False),
},
"0x77f973fcaf871459aa58cd81881ce453759281bc": {
    "0x031d2db8": ("guessed_031d2db8", None, None, False),   
},
"0xda6fe40e8310dc4cdb1795c724944175f18eb2f3": {
    "0x1e202240": ("liquidatePosition", ["uint256", "address", "uint256"], [], False),
},
"0xffde4785e980a99fe10e6a87a67d243664b91b25": {
    "fallback": ("fallback", [], [], True),
},
"0x2db6c82ce72c8d7d770ba1b5f5ed0b6e075066d6": {
    "0x0a087903": ("sushi", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},


# below is what I'm not sure, but I would love to have a try:
# Extremely important for CreamFi
# implementation at 0x1cc6Cf8455f7783980B1ee06ecD4ED9acd94e1c7, should be read-only but not view modifier is added
"0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258": {
    "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
    "0x24008a62": ("repayBorrowAllowed", [], [], True),
    "0xd02f7351": ("seizeAllowed", [], [], True),
    "0xda3d454c": ("borrowAllowed", [], [], True),
    "0x4ef4c3e1": ("mintAllowed", [], [], True),
    "0xeabe7d91": ("redeemAllowed", [], [], True),
    "0xbdcdc258": ("transferAllowed", [], [], True),
    "0x1ededc91": ("repayBorrowVerify", [], [], True),
    "0x6d35bf91": ("seizeVerify", [], [], True),
    "0x6a56947e": ("transferVerify", [], [], True),
    "0x5c778605": ("borrowVerify", [], [], True),
    "0x41c728b9": ("mintVerify", [], [], True),
    "0x51dff989": ("redeemVerify", [], [], True),
    "0x47ef3b3b": ("liquidateBorrowVerify", [], [], True),
},
"0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f": {
    "0xeabe7d91": ("redeemAllowed", [], [], True),
    "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
    "0xc90c20b1": ("_beforeNonReentrant", [], [], True),
    "0x632e5142": ("_afterNonReentrant", [], [], True),
    "0x24008a62": ("repayBorrowAllowed", [], [], True),
    "0xd02f7351": ("seizeAllowed", [], [], True),
    "0x4ef4c3e1": ("mintAllowed", [], [], True),
    "0xda3d454c": ("borrowAllowed", [], [], True),

    "0x51dff989": ("redeemVerify", [], [], True),
    "0x41c728b9": ("mintVerify", [], [], True),

},
"0x4dcf7407ae5c07f8681e1659f626e114a7667339": {
    "0xeabe7d91": ("redeemAllowed", [], [], True),
    "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
    "0x4ef4c3e1": ("mintAllowed", [], [], True),
    "0x24008a62": ("repayBorrowAllowed", [], [], True),
    "0x1ededc91": ("repayBorrowVerify", [], [], True),
    "0x6d35bf91": ("seizeVerify", [], [], True),
    "0x6a56947e": ("transferVerify", [], [], True),
    "0x5c778605": ("borrowVerify", [], [], True),
    "0x41c728b9": ("mintVerify", [], [], True),
    "0x51dff989": ("redeemVerify", [], [], True),
},

# balanceOfUnderlying should be read-only
"0x7fcb7dac61ee35b3d4a51117a7c58d53f0a8a670": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0x697b4acaa24430f254224eb794d2a85ba1fa1fb8": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0xfd609a03b393f1a1cfcacedabf068cad09a924e2": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0x8379baa817c5c5ab929b03ee8e3c48e45018ae41": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0x44fbebd2f576670a6c33f6fc0b00aa8c5753b322": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0xe89a6d0509faf730bd707bf868d9a2a744a363c7": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0x2a537fa9ffaea8c1a41d3c2b68a9cb791529366d": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0x797aab1ce7c01eb727ab980762ba88e7133d2157": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},
"0x10fdbd1e48ee2fd9336a482d746138ae19e649db": {
    "0x17bfdfbc": ("borrowBalanceCurrent", [], [], True),
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True)
},

"0xeff039c3c1d668f408d09dd7b63008622a77532c": {
    "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"], True),
}



