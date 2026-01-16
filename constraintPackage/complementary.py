
complementary = {
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
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"]),
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
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
        "fallback": ("fallback", None, None, True),
    },
    "0xfa6de2697d59e88ed7fc4dfe5a33dac43565ea41": {
        "0x255de7bb": ("swapExactAmountIn", ["address", "address", "uint", "address", "uint", "uint"], [], False)
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
        # The following is from https://app.dedaub.com/ethereum/address/0x7d8bb0dcfb4f20115883050f45b517459735181b/abi
        "0x0a90b578": ("guessed_0a90b578", None, None, True),
        "0xf8b2cb4f": ("getBalance", ["address"], ["uint"], True),
        "0x093983bd": ("guessed_093983bd", None, None, True),
        "0x13e97c71": ("guessed_13e97c71", None, None, True),
        "0x16a6bff6": ("guessed_16a6bff6", None, None, True),
        "0x2035d73b": ("guessed_2035d73b", None, None, True),
        "0x2274346b": ("guessed_2274346b", None, None, True),
        "0x42ad3526": ("guessed_42ad3526", None, None, True),
        "0x4780eac1": ("guessed_4780eac1", None, None, True),
        "0x4a7c3d50": ("guessed_4a7c3d50", None, None, True),
        "0x4b4056c5": ("guessed_4b4056c5", None, None, True),
        "0x5c445c86": ("guessed_5c445c86", None, None, True),
        "0x64a71040": ("guessed_64a71040", None, None, True),
        "0x71eb125e": ("guessed_71eb125e", None, None, True),
        "0x779dec5b": ("guessed_779dec5b", None, None, True),
        "0x7955f60f": ("guessed_7955f60f", None, None, True),
        "0x7b8e3514": ("guessed_7b8e3514", None, None, True),
        "0x82c174d0": ("guessed_82c174d0", None, None, True),
        "0x86042ec6": ("guessed_86042ec6", None, None, True),
        "0x8638aa65": ("guessed_8638aa65", None, None, True),
        "0x8da5cb5b": ("guessed_8da5cb5b", None, None, True),
        "0x9048617a": ("guessed_9048617a", None, None, True),
        "0x9437d0ea": ("guessed_9437d0ea", None, None, True),
        "0x9ae6b186": ("guessed_9ae6b186", None, None, True),
        "0x9c3f1e90": ("guessed_9c3f1e90", None, None, True),
        "0x9e312dac": ("guessed_9e312dac", None, None, True),
        "0xa72480ae": ("guessed_a72480ae", None, None, True),
        "0xb7a025f9": ("guessed_b7a025f9", None, None, True),
        "0xcce37f3e": ("guessed_cce37f3e", None, None, True),
        "0xd9fd7341": ("guessed_d9fd7341", None, None, True),
        "0xde3f26eb": ("guessed_de3f26eb", None, None, True),
        "0xf4fb9b2f": ("guessed_f4fb9b2f", None, None, True),
    },
    "0x77f973fcaf871459aa58cd81881ce453759281bc": {
        "0x031d2db8": ("guessed_031d2db8", None, None, False),   
        "0x66fa576f": ("flashBorrowToken", None, None, False),
    },
    "0xda6fe40e8310dc4cdb1795c724944175f18eb2f3": {
        "0x1e202240": ("liquidatePosition", ["uint256", "address", "uint256"], [], False),
    },
    "0xffde4785e980a99fe10e6a87a67d243664b91b25": {
        "fallback": ("fallback", [], [], True),
    },
    "0x2db6c82ce72c8d7d770ba1b5f5ed0b6e075066d6": {
        "0x0a087903": ("sushi", [], [], True),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"])
    },

    
    # below is what I'm not sure, but I would love to have a try:
    # Extremely important for CreamFi
    # implementation at 0x1cc6Cf8455f7783980B1ee06ecD4ED9acd94e1c7, should be read-only but not view modifier is added
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258": {
        "0x36bdd087": ("_supportMarket", ["address", "uint"], ["bool"], False),
        "0x3d98a1e5": ("isMarketListed", None, None, True),
        "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
        "0x24008a62": ("repayBorrowAllowed", [], []),
        "0xd02f7351": ("seizeAllowed", [], []),
        "0xda3d454c": ("borrowAllowed", [], []),
        "0x4ef4c3e1": ("mintAllowed", [], []),
        "0xeabe7d91": ("redeemAllowed", [], []),
        "0xbdcdc258": ("transferAllowed", [], []),
        "0x1ededc91": ("repayBorrowVerify", [], []),
        "0x6d35bf91": ("seizeVerify", [], []),
        "0x6a56947e": ("transferVerify", [], []),
        "0x5c778605": ("borrowVerify", [], []),
        "0x41c728b9": ("mintVerify", [], []),
        "0x51dff989": ("redeemVerify", [], []),
        "0x47ef3b3b": ("liquidateBorrowVerify", [], []),
        # implementation at 0x9ac75fc3cb8a631f4ecf4c16a89ee95d847b64a7

    },
    "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f": {
        "0xeabe7d91": ("redeemAllowed", [], []),
        "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
        "0xc90c20b1": ("_beforeNonReentrant", [], [], True), # re-entrancy
        "0x632e5142": ("_afterNonReentrant", [], [], True), # re-entrancy
        "0x24008a62": ("repayBorrowAllowed", [], []),
        "0xd02f7351": ("seizeAllowed", [], []),
        "0x4ef4c3e1": ("mintAllowed", [], []),
        "0xda3d454c": ("borrowAllowed", [], []),
        "0x51dff989": ("redeemVerify", [], []),
        "0x41c728b9": ("mintVerify", [], []),
        "0x5d72de62": ("_becomeImplementation", [], [], False), # implementation at 0xe16db319d9da7ce40b666dd2e365a4b8b3c18217
        "0x5384949d": ("_becomeImplementation", [], [], False), # implementation at 0x1a1e7b69348b22b304428a07a7ffa1c6347f8ef6
        
        "0x18c882a5": ("_setBorrowPaused", [], [], False), # implementation at 0xe16db319d9da7ce40b666dd2e365a4b8b3c18217
        "0xdd5cd22c": ("autoImplementation", [], [], True), 

    
    },
    # balanceOfUnderlying should be read-only
    "0x7fcb7dac61ee35b3d4a51117a7c58d53f0a8a670": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"])
    },
    "0x697b4acaa24430f254224eb794d2a85ba1fa1fb8": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"]),
        "0x6f307dc3": ("0x6f307dc3", [], []),  # very weird, do not match any function selector, could be underlying() but is not pure/view
    },
    "0xfd609a03b393f1a1cfcacedabf068cad09a924e2": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"])
    },
    "0x8379baa817c5c5ab929b03ee8e3c48e45018ae41": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"])
    },
    "0x44fbebd2f576670a6c33f6fc0b00aa8c5753b322": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"]),
        "0xe0232b42": ("flashLoan", [], [], False), # 0xcc44572b57372dac502bcd784705e083779b2afc
        "0x8897bd85": ("registerCollateral", [], [], False), # 0x3c710b981f5ef28da1807ce7ed3f2a28580e0754
    },
    "0xe89a6d0509faf730bd707bf868d9a2a744a363c7": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"])
    },
    "0x2a537fa9ffaea8c1a41d3c2b68a9cb791529366d": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"]),
        "0x8897bd85": ("registerCollateral", [], [], False), # 0x3c710b981f5ef28da1807ce7ed3f2a28580e0754

    },
    "0x797aab1ce7c01eb727ab980762ba88e7133d2157": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"]),
        "0x8897bd85": ("registerCollateral", [], [], False), # 0x3c710b981f5ef28da1807ce7ed3f2a28580e0754
    },
    "0x10fdbd1e48ee2fd9336a482d746138ae19e649db": {
        "0x17bfdfbc": ("borrowBalanceCurrent", [], []),
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"])
    },
    "0xeff039c3c1d668f408d09dd7b63008622a77532c": {
        "0x3af9e669": ("balanceOfUnderlying", ["address"], ["uint"]),
    },
    "0xb14b3b9682990ccc16f52eb04146c3ceab01169a": {  # proxy - implementation pattern
                                                     # directly got from EtherScan write as a proxy
        "0xe3333ae9": ("pledgeAndBorrow", [], [], False),
        "0x150b7a02": ("onERC721Received", [], [], False),
        "0x61bc221a": ("counter", [], [], True),
        "0x023245d7": ("withdrawNFT", [], [], False),
    },
    "0xb7e2300e77d81336307e36ce68d6909e43f4d38a": {  # proxy - implementation pattern
                                                     # directly got from EtherScan write as a proxy
        "0xaf13fe93": ("getOrderBorrowBalanceCurrent", [], [], False),
        "0x8f63a482": ("borrowAllowed", [], []), # 0x34ca24ddcdaf00105a3bf10ba5aae67953178b85
    },
    "0xb38707e31c813f832ef71c70731ed80b45b85b2d":{   # proxy - implementation pattern
                                                    # directly got from EtherScan write as a proxy
        "0x0c28d13e": ("borrow", [], [], False)
    },
    "0x222d7b700104c91a2ebbf689ff7b2a35f2541f98": { # get it from Phalcon
        "0xac41865a": ("getPrice", [], [], True)
    },
    "0x5e5186d21cbddc8765c4558dbda0bf20b90bf118": { # proxy - implementation pattern
                                                    # get it from Phalcon
        "0x39726239": ("updateBorrow", [], [], False),
    },
    "0x1b0284391fdf905222b6174ef2cde60ba58d9529": { # get it from Phalcon
        "0x15f24053": ("getBorrowRate", [], [], True),
    },
    "0xf289b48636f6a66f8aea4c2d422a88d4f73b3894": { # get it from Phalcon
        "0x15f24053": ("getBorrowRate", [], [], True),
    },
    "0x4e9a87ce601618fbf0c5bc415e35a4ac012d3863": { # get it from Phalcon
        "0x15f24053": ("getBorrowRate", [], [], True),
    },
    "0x5bd628141c62a901e0a83e630ce5fafa95bbdee4": { # get it from Phalcon
        "0x255de7bb": ("swapExactAmountIn", [], [], False),
    },
    "0xd6e194af3d9674b62d1b30ec676030c23961275e": { # proxy - implementation pattern
                                                    # implementation at 0xec260f5a7a729bb3d0c42d292de159b4cb1844a3
        "0xd0e30db0": ("deposit", [], [], False),  # without arguments
        "0x2e1a7d4d": ("withdraw", [], [], False),
        "0xec815e1b": ("rariFundToken", [], [], True),
        "0x8e27d719": ("deposit", [], [], False),  # with arguments
        "0xdae9e379": ("getFundBalance", [], [], True), 
        "0x70a08231": ("balanceOf", ["address"], ["uint"], True),
    },
    "0xa731585ab05fc9f83555cf9bff8f58ee94e18f85": { # proxy - implementation pattern
                                                    # implementation at 0xec260f5a7a729bb3d0c42d292de159b4cb1844a3
                                                    # get from EtherScan
        "0xb01b86fd": ("_callPool", [], [], False),
        "0xdd86fea1": ("interestFeeRate", [], [], True),
        "0x9c7be708": ("maxSupplyEth", [], [], True),
        "0xfdb25fb1": ("minBorrowEth", [], [], True),
        "0xdfcb48bd": ("maxUtilizationRate", [], [], True),
        "0x2acbff39": ("_callPool", [], [], False), # 0x650fcbc52e37631b4f40e0c4f660e6ac03b77db2
        "0x3465b6e1": ("_withdrawAssets", [], [], False), # 0x650fcbc52e37631b4f40e0c4f660e6ac03b77db2
        "0x5d72de62": ("_becomeImplementation", [], [], False), # 0xe16db319d9da7ce40b666dd2e365a4b8b3c18217
        "0x01758fc2": ("_editCErc20DelegateWhitelist", [], [], False), # 0x50ce132ebe395d35b8cf6df6ce5f817107707583
        "0x2f876d32": ("_setPoolLimits", [], [], False), # 0x650fcbc52e37631b4f40e0c4f660e6ac03b77db2
        "0x2f8a3da0": ("0x2f8a3da0", [], [], False), # 0x650fcbc52e37631b4f40e0c4f660e6ac03b77db2
        "0x8d3bb8ef": ("_editComptrollerImplementationWhitelist", [], [], False), # 0x83728b5ba733b849bc35b4aa8544cfbfb814b814
        "0xd64517b2": ("_editCEtherDelegateWhitelist", [], [], False), # 0x83728b5ba733b849bc35b4aa8544cfbfb814b814
        "0x06bc4611": ("_setCustomInterestFeeRate", [], [], False), # 0x50ce132ebe395d35b8cf6df6ce5f817107707583
        "0x8754e4fd": ("deployCErc20", [], [], False), # implementation at 0x50ce132ebe395d35b8cf6df6ce5f817107707583
        "0x9b86a9b5": ("deployCEther", [], [], False), # implementation at 0x83728b5ba733b849bc35b4aa8544cfbfb814b814
        "0x45cc9705": ("latestCErc20Delegate", [], [], True), # 
        "0xbbcdd6d3": ("latestComptrollerImplementation", [], [], True), # 
        

    },
    "0x8164cc65827dcfe994ab23944cbc90e0aa80bfcb": {
        "0xcbcbb507": ("EMISSION_MANAGER", None, None, True),
        "0xdde43cba": ("REVISION", None, None, True),
        "0x4c0369c3": ("getAllUserRewards", None, None, True),
        "0x9efd6f72": ("getAssetDecimals", None, None, True),
        "0x886fe70b": ("getAssetIndex", None, None, True),
        "0x74d945ec": ("getClaimer", None, None, True),
        "0x1b839c77": ("getDistributionEnd", None, None, True),
        "0x92074b08": ("getEmissionManager", None, None, True),
        "0x6657732f": ("getRewardsByAsset", None, None, True),
        "0x7eff4ba8": ("getRewardsData", None, None, True),
        "0xb45ac1a9": ("getRewardsList", None, None, True),
        "0x5f130b24": ("getTransferStrategy", None, None, True),
        "0xb022418c": ("getUserAccruedRewards", None, None, True),
        "0x533f542a": ("getUserAssetIndex", None, None, True),
        "0x70674ab9": ("getUserRewards", None, None, True),
    }, 
    "0x3a70dfa7d2262988064a2d051dd47521e43c9bdd": {
        "0x313ce567": ("decimals", None, None, True),
        "0xd96c7fce": ("get_previous_balances", None, None, True),
        "0x14f05979": ("get_balances", None, None, True),
        "0x0f6ba8e3": ("get_twap_balances", None, None, True),
        "0x4469e30e": ("get_price_cumulative_last", None, None, True),
        "0xfee3f7f9": ("admin_fee", None, None, True),
        "0xf446c1d0": ("A", None, None, True),
        "0x76a2f0f0": ("A_precise", None, None, True),
        "0xbb7b8b80": ("get_virtual_price", None, None, True),
        "0xed8e84f3": ("calc_token_amount", None, None, True),
        "0xe47e6b9e": ("calc_token_amount", None, None, True),
        "0x5e0d443f": ("get_dy", None, None, True),
        "0x7e42fc0c": ("get_dy", None, None, True),
        "0x07211ef7": ("get_dy_underlying", None, None, True),
        "0xe36fd501": ("get_dy_underlying", None, None, True),
        "0xcc2b27d7": ("calc_withdraw_one_coin", None, None, True),
        "0xc532a774": ("calc_withdraw_one_coin", None, None, True),
        "0xe2e7d264": ("admin_balances", None, None, True),
        "0xf851a440": ("admin", None, None, True),
        "0xc6610657": ("coins", None, None, True),
        "0x4903b0d1": ("balances", None, None, True),
        "0xddca3f43": ("fee", None, None, True),
        "0x63543f06": ("block_timestamp_last", None, None, True),
        "0x5409491a": ("initial_A", None, None, True),
        "0xb4b577ad": ("future_A", None, None, True),
        "0x2081066c": ("initial_A_time", None, None, True),
        "0x14052288": ("future_A_time", None, None, True),
        "0x06fdde03": ("name", None, None, True),
        "0x95d89b41": ("symbol", None, None, True),
        "0x70a08231": ("balanceOf", ["address"], ["uint"], True),
        "0xdd62ed3e": ("allowance", ["address", "address"], ["uint"], True),
        "0x18160ddd": ("totalSupply", None, ["uint"], True),

    },

    "0xec260f5a7a729bb3d0c42d292de159b4cb1844a3": {
        "0x8e27d719": ("deposit", [], [], False),
    },
    "0x8922c1147e141c055fddfc0ed5a119f3378c8ef8": { # get it from Phalcon
        "0xc37f68e2": ("getAccountSnapshot", [], [], True),
        "0x6f307dc3": ("underlying", [], [], True),
        "0xac784ddc": ("isCEther", [], [], True),
    },
    "0xebe0d1cb6a0b8569929e062d67bfbc07608f0a47": { # get it from Phalcon
        "0x6f307dc3": ("underlying", [], [], True),
        "0xac784ddc": ("isCEther", [], [], True),
    },
    "0x26267e41ceca7c8e0f143554af707336f27fa051": { # get it from Phalcon
        "0x6f307dc3": ("underlying", [], [], True),
        "0xac784ddc": ("isCEther", [], [], True),
    },
    "0x4ef29407a8dbca2f37b7107eab54d6f2a3f2ad60": {
        "0x2191f92a": ("isInterestRateModel", [], [], True),
        "0xe85426f6": ("0xe85426f6", [], [], False),
        "0xbdfa0466": ("0xbdfa0466", [], [], False),
        "0xd9822816": ("0xd9822816", [], [], False),
    },
    "0xfea425f0baadf191546cf6f2dbf72357d631ae46": {
        "0x1c9161e0": ("flywheelPreSupplierAction", [], [], False),
        "0xe6e162e8": ("flywheelPreBorrowerAction", [], [], False),
        "0x4e081c95": ("flywheelPreTransferAction", [], [], False),
        "0xef5cfb8c": ("claimRewards", [], [], False),
    },
    "0xe097783483d1b7527152ef8b150b99b9b2700c8d": {
        "0xc37f68e2": ("getAccountSnapshot", [], [], True),
        "0x6f307dc3": ("underlying", [], [], True),
        "0xac784ddc": ("isCEther", [], [], True),
    },
    "0x228619cca194fbe3ebeb2f835ec1ea5080dafbb2": {
        "0x0a087903": ("sushi", [], [], True),

    },
    "0x4112a717edd051f77d834a6703a1ef5e3d73387f": {
        "0x8897bd85": ("registerCollateral", [], [], False),
    },
    "0x299e254a8a165bbeb76d9d69305013329eea3a3b": {
        "0x8897bd85": ("registerCollateral", [], [], False),
    },
    "0x8c3b7a4320ba70f8239f83770c4015b5bc4e6f91": {
        "0xc5ebeaec": ("borrow", [], [], False),
        "0x8897bd85": ("registerCollateral", [], [], False),
        "0xa7af467a": ("flashloan", [], [], False),
        "0x5cffe9de": ("flashFee", [], [], True),
    },
    "0x523effc8bfefc2948211a05a905f761cba5e8e9e": {
        "0x8897bd85": ("registerCollateral", [], [], False),
    },
    "0x1f9b4756b008106c806c7e64322d7ed3b72cb284": {
        "0x0a087903": ("sushi", [], [], True),
    },
    "0x4baa77013ccd6705ab0522853cb0e9d453579dd4": {
        "0x0a087903": ("sushi", [], [], True),
    },

    "0xc1e088fc1323b20bcbee9bd1b9fc9546db5624c5": {
        "0xfc06d2a6": ("sunrise", [], [], False),
        "0xd4a3e9d7": ("capture", [], ["uint", "uint"], False),
        "0xa856f359": ("commit", [], [], False),
        "0x73015684": ("emergencyCommit", [], [], False),
        "0x69d9120d": ("transferPlot", [], [], False), # implementation: 0xdfc0a75109abe81adcc02f3c00df167fcbda557c
        "0x75ce258d": ("depositBeans", [], [], False), # implementation: 0x47e9910a1eb01d6453a57d2329d616cb0c8061a6
        "0xc50b0fb0": ("season", [], [], True), # implementation: 0x5C2DB111FCDfc24ec3fDD3263C585BDf95B55880, not reflected in Phalcon
        "0xcf13c9d3": ("buyAndDepositBeans", [], [], False), # implementation: 0x448d330affa0ad31264c2e6a7b5d2bf579608065
        "0x47e7ef24": ("deposit", [], [], False), # implementation: 0x23d231f37c8f5711468c8abbfbf1757d1f38fda2
        "0xf984019b": ("curveToBDV", [], [], True), # implementation: 0xc1e088fc1323b20bcbee9bd1b9fc9546db5624c5
        "0x9f88e20d": ("buyBeansAndFillPodListing", [], [], False), # implementation: 0xdefcf58e20520466c2f023ab94a526184f534a6a
        "0x9094c763": ("vote", [], [], False), # implementation: 0xf480ee81a54e21be47aa02d0f9e29985bc7667c4
        "0x3bcbd6fc": ("lusdToBDV", [], [], True), # implementation: 0xc1e088fc1323b20bcbee9bd1b9fc9546db5624c5
        "0xaa0742a4": ("convertDepositedBeans", [], [], False), # implementation: 0x649d4b21278a1771c0b196614e2c21b4c73fe801
        "0x8bee5499": ("updateSilo", [], [], False), # implementation: 0x448d330affa0ad31264c2e6a7b5d2bf579608065

    },
    "0x55bf8304c78ba6fe47fd251f37d7beb485f86d26": { # get it from Phalcon
        "0x70a08231": ("balanceOf", ["address"], ["uint"], True),
        # proxy - implementation pattern
        # implementation at 0xe7f0c51d8faf239a1cf65db79e5e0fc64d148424
        "0x39bb96a8": ("withdrawFor", [], [], False),
        # implementation at 0xddd7df28b1fb668b77860b473af819b03db61101
        "0x4a042674": ("depositFor", [], [], False),

    },
    "0xffde4785e980a99fe10e6a87a67d243664b91b25": { # get it from Phalcon
        "fallback": ("fallback", [], [], True), 
    },
    "0x4dcf7407ae5c07f8681e1659f626e114a7667339": { # get it from Phalcon
        "0xeabe7d91": ("redeemAllowed", [], []),
        "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
        "0x4ef4c3e1": ("mintAllowed", [], []),
        "0x24008a62": ("repayBorrowAllowed", [], []),
        "0x1ededc91": ("repayBorrowVerify", [], []),
        "0x6d35bf91": ("seizeVerify", [], []),
        "0x6a56947e": ("transferVerify", [], []),
        "0x5c778605": ("borrowVerify", [], []),
        "0x41c728b9": ("mintVerify", [], []),
        "0x51dff989": ("redeemVerify", [], []),

        "0xcc7ebdc4": ("compAccrued", [], [], True),
        "0xabfceffc": ("getAssetsIn", [], [], True),
        "0x8e8f294b": ("markets", [], [], True),
        "0x7dc0d1d0": ("oracle", [], [], True),
        "0x5ec88c79": ("getAccountLiquidity", [], [], True),
        # implementation from 0x2c0edf1f7dbcdb347ed8ce626d4de2221f1d76a2
        "0x5fc7e71e": ("liquidateBorrowAllowed", [], [], True),
        "0xe9af0292": ("claimComp", [], [], False),
        "0x1c3db2e0": ("claimComp", [], [], False), # implementation from 0x731b65a993c7a4ff10d304d5204afc51033cda4c

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
        "0x229e0b16": ("guess_229e0b16", None, None, False), # 0x0ef7115da1269aad60f9ed7ded5aaeabacc7c08d
        "0x95eb84c0": ("guess_95eb84c0", None, None, False), # 0x9f9eaeda74b2580a566ebcb2fb80d307b38a8bc4
        "0x473ac3ed": ("guess_473ac3ed", None, None, False), # 0x1c5eb39dbb6dfe74699d4dfdc6dc17b47234b3bb
        "0xa1e93482": ("withdrawCollateral", None, None, False), # 0xef8e5a79c9fa05ab234a1844e7f4899858932775
        # get it from Phalcon
        "0x9dcf71d9": ("0x9dcf71d9", [], [], True),
        "0xf7a8c508": ("0xf7a8c508", [], [], True),
        "0xf3d75a9c": ("0xf3d75a9c", [], [], True),  # 0xb83a4095ba5d87334a82384253180a25efae5466
        "0x0a90b578": ("0x0a90b578", [], [], True),
        "0xb1fd9e05": ("0xb1fd9e05", [], [], True),

        "0x6826bad9": ("0x6826bad9", [], [], False),
        "0x7267ea86": ("0x7267ea86", [], [], False),
        "0x8dca78c8": ("0x8dca78c8", [], [], False),
        "0x30501fd1": ("0x30501fd1", [], [], False),
        "0xb1eac3ad": ("0xb1eac3ad", [], [], False),
    },

    "0x222412af183bceadefd72e4cb1b71f1889953b1c": {
        "0x0d453efb": ("hasVault", [], [], True),
    },
    "0x893411580e590d62ddbca8a703d61cc4a8c7b2b9": {
        "fallback": ("fallback", None, None, True),
    },
    "0x464c71f6c2f760dda6093dcb91c24c39e5d6e18c": {
         "fallback": ("fallback", None, None, True),
    },
    "0x388c818ca8b9251b393131c08a736a67ccb19297": {
         "fallback": ("fallback", None, None, True),
    },
    "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": {
        "fallback": ("fallback", None, None, False),
    },
    "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad": {
        "fallback": ("fallback", None, None, True),
    },
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": {
        "fallback": ("fallback", None, None, True),
    },
    "0xe592427a0aece92de3edee1f18e0157c05861564": {
        "fallback": ("fallback", None, None, True),
    },
    "0xc36442b4a4522e871399cd717abdd847ab11fe88": {
        "fallback": ("fallback", None, None, True),
    },
    "0xa2cd3d43c775978a96bdbf12d733d5a1ed94fb18": {
        "fallback": ("fallback", None, None, True),
    },
    "0x2ccb7d00a9e10d0c3408b5eefb67011abfacb075": {
        "fallback": ("fallback", None, None, True),
    },
    "0x8f1cece048cade6b8a05dfa2f90ee4025f4f2662": {
        "fallback": ("fallback", None, None, True),
    },

    "0x004e9c3ef86bc1ca1f0bb5c7662861ee93350568": {
        "0xa9059cbb": ("transfer", ["address", "uint256"], ["bool"], False),
        "0x23b872dd": ("transferFrom", ["address", "address", "uint256"], ["bool"], False),
        "0x30e0789e": ("_transfer", ["address", "address", "uint256"], [], False),
        "0x095ea7b3": ("approve", ["address", "uint256"], ["bool"], False),
        "0xa457c2d7": ("decreaseAllowance", ["address", "uint256"], ["bool"], False),
        "0x39509351": ("increaseAllowance", ["address", "uint256"], ["bool"], False),
        "0x70a08231": ("balanceOf", ["address"], ["uint256"], True),

    },

    "0x9536a78440f72f5e9612949f1848fe5e9d4934cc": {
        "0x23b872dd": ("transferFrom", ["address", "address", "uint256"], ["bool"]),
        "0xa9059cbb": ("transfer", ["address", "uint256"], ["bool"]),
        "0xd505accf": ("permit", ["address", "address", "uint256", "uint256", "bytes"], ["bool"]),
        "0x0902f1ac": ("getReserves", [], [], True),  # get it from Phalcon
        "0x0dfe1681": ("token0", [], [], True),  # get it from Phalcon
        "0xd21220a7": ("token1", [], [], True),  # get it from Phalcon
    },

    "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": {
        "0x35ea6a75": ("getReserveData", ["address"], [], True), 
    },

    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": {
        "0x70a08231": ("balanceOf", ["address"], ["uint256"], True),
        "0x7a28fb88": ("getPooledEthByShares", ["uint256"], ["uint256"], True),
    },

    "0x889edc2edab5f40e902b864ad4d7ade8e412f9b1": {
        "0xb8c4b85a": ("getWithdrawalStatus", [], [], True),  # get it from Phalcon
        "0x7d031b65": ("getWithdrawalRequests", [], [], True),  # get it from Phalcon
    },

    "0xebe72cdafebc1abf26517dd64b28762df77912a9": {
        "0xaeaa4ae6": ("supplyERC721", [], []), 
        "0x1ba91d46": ("liquidationERC721", [], []),
        "0xa415bcad": ("borrow", [], []),
        "0x3786ddfc": ("withdrawERC721", [], []),
    },

    "0x218615c78104e16b5f17764d35b905b638fe4a92": {
        "0xea70ed94": ("burn", [], []),
    },

    "0xb8919522331c59f5c16bdfaa6a121a6e03a91f62": {
        "0xa6aa57ce": ("lend", [], []),
    },

    "0xe7597f774fd0a15a617894dc39d45a28b97afa4f": {
        "fallback": ("fallback", None, None, True),  # get it from Phalcon
    },


    "0xeb7e15b4e38cbee57a98204d05999c3230d36348": {
        "0x552079dc":  ("fallback", None, None, True),
    }



}


# readOnlyAlike = {
#     "transferAllowed", "exchangeRateCurrent", "mintAllowed", "balanceOfUnderlying", "borrowBalanceCurrent", \
#     "balanceOfUnderlying", "repayBorrowAllowed", "seizeAllowed", "borrowAllowed", "mintAllowed", "redeemAllowed", "repayBorrowVerify", \
#     "seizeVerify", "transferVerify", "borrowVerify", "mintVerify", "redeemVerify", "liquidateBorrowVerify"
# }



reEntrancyGuard = {
    "0x697b4acaa24430f254224eb794d2a85ba1fa1fb8": ["0x0"],
    "0xd06527d5e56a3495252a528c4987003b712860ee": ["0x0"],
    "0x2db6c82ce72c8d7d770ba1b5f5ed0b6e075066d6": ["0x0"],
    "0x7fcb7dac61ee35b3d4a51117a7c58d53f0a8a670": ["0x0"],
    "0xfd609a03b393f1a1cfcacedabf068cad09a924e2": ["0x0"],
    "0x44fbebd2f576670a6c33f6fc0b00aa8c5753b322": ["0x0"],
    "0x797aab1ce7c01eb727ab980762ba88e7133d2157": ["0x0"],
    "0xe89a6d0509faf730bd707bf868d9a2a744a363c7": ["0x0"],
    "0x10fdbd1e48ee2fd9336a482d746138ae19e649db": ["0x0"],
    "0x2a537fa9ffaea8c1a41d3c2b68a9cb791529366d": ["0x0"],
    "0x8379baa817c5c5ab929b03ee8e3c48e45018ae41": ["0x0"],
    "0xeff039c3c1d668f408d09dd7b63008622a77532c": ["0x0"],

    # "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258": ["0x0"], potentially sstore the same value back to sload


}


arbitrary_external_call = {
    "0xeb7e15b4e38cbee57a98204d05999c3230d36348-borrow-0x6e2246a7": ["0x82151ca501c81108d032c490e25f804787bef3b8-lend-0xd5badabc"],
    # "0x051ebd717311350f1684f89335bed4abd083a2b6-flashLoan-0xd0a494e4": ["0x2bbd66fc4898242bdbd2583bbe1d76e8b8f71445-flashLoan-0xd0a494e4"]
}


# sstore_same_value_on_the_fly = {
#     # CreamFi1_1
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-mintAllowed-0x4ef4c3e1", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-redeemAllowed-0xeabe7d91", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-transferAllowed-0xbdcdc258", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-borrowAllowed-0xda3d454c", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-seizeAllowed-0xd02f7351", \
    
#     # RariCapital2_3
#     "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-mintVerify-0x41c728b9", \
#     "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-redeemAllowed-0xeabe7d91", \
#     "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-seizeAllowed-0xd02f7351", \
#     "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-mintAllowed-0x4ef4c3e1", 

#     # CreamFi2_4
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-redeemAllowed-0xeabe7d91", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-transferAllowed-0xbdcdc258", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-mintAllowed-0x4ef4c3e1", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-repayBorrowAllowed-0x24008a62", \
#     "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-seizeAllowed-0xd02f7351", \
# }


read_only_on_the_fly = {
    # CreamFi1_1
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-mintAllowed-0x4ef4c3e1-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-redeemAllowed-0xeabe7d91-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-transferAllowed-0xbdcdc258-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-repayBorrowAllowed-0x24008a62-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-seizeAllowed-0xd02f7351-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-borrowAllowed-0xda3d454c-read-only", \

    # RariCapital2_3
    "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-redeemAllowed-0xeabe7d91-read-only", \
    "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-seizeAllowed-0xd02f7351-read-only", \
    "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f-mintAllowed-0x4ef4c3e1-read-only", \
    
    # CreamFi2_4
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-mintAllowed-0x4ef4c3e1-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-transferAllowed-0xbdcdc258-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-redeemAllowed-0xeabe7d91-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-repayBorrowAllowed-0x24008a62-read-only", \
    "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258-seizeAllowed-0xd02f7351-read-only"
}


# part of the transaction are reverted
revertedTransactions = [
    "0x01a80e3bfa5e0d18dc267ea25c5504dcca93a7742d09764524766d5f9eb880dc",
    "0xff7256da245269a3211cdb88c031f43900f6855285e4749b41ddc4a8269923f0",
    "0x223a1d70ba9ab7dcc153ec484170f4802548436cb60a0fc33e9acafa539e71a3",
    "0xfe99081571cbc8ae2bfc32aae3c7971eb810c2f13062cb433f8797126856b3b8",
    "0x98103ccc94e179b22ab850a7d77f2c2f7bb2ac08570bf2e8e783bb24c48e5290",
    "0xfbb2b0acdef46ecd11e61ccbcae678dee537bd699049250afaf1640ab9f7021d",
    "0xcabb556333b378f503c9cb2c48c45f2c970a9b6eadab780b5913605813f0a2fe",
    "0xd9d05a1ed40e981761825f84bb208d134a4e0e192f5fcd67308068d9da2550d4",
    "0x0c601a6e726dd25a68887a7585fb4608d9f7338e2e490c5d31867a82d633461e",
    "0x34d6de209b34bf926445adb7c93da539b08b8fa4c089447a967743baab66961e",
    "0x3ca21a13846184378c4c15376eb6628b9c210f91b259610a7a214370e00db3da",
    "0xdb21cf74115056afcd0ce38c0c5fb56029545ec5e24f1c6018245547e68d14b6",
    "0xf4bf51dd8eb38d95339867b0b1b31317c73c3ace7b5df6692db4e784e122cf5d",
    "0xaf9ef0d7b223d55025a2983e5c69cae546f0112d70d5aecee0ee478e493bda85",
    "0x45e8a3ebbf3ce6b1b6a36fbea9266cda79273d4924b3dc8b2d79f657a1731f77",
    "0x1b203dd83f92a55319acd129ada4a0505613d88e7728c38fae3c62ffdc9227ef",
    "0xffa6a934d5895ddeb6392e334d45d2d36265d545e4dc8ba10639c2e98e3e1039",
    "0xa719932500af55b28c73114856b8c8474a57d557265df53fb660fa4cf644d6b3",
    "0xd9fef32db25521719d8ed1125171a86ef8b46ec6dd91169c321472adeb6bf5e9",
    "0xe6c508e5b8c73356acd8fcffa998b2de8667297b60d8c9bc5bdb193968610b25",
    "0x27668fcbb33c5d60cc511b25deca8a29aff12e3cac29c535abdfa3cb3403973f",
    "0xe404d4a4be9fe3b30e8135af925a81799d9906bb79fcfde4d4388dbc1961c3bc",
    "0x44c846f6214c3850caf32b491c664fd9dada81308a1c3b0cfe4dc634ac192e7a",
    "0x9caf6093d782e4d66a2b91168b7007243e05882cd01d23a2283ac6cd5968849f",
    '0x95b18b46e489f98c8dd2fa5bb57e53702a9e09d034bcc7f2974f609a32d753a2', 
    '0x0092314d8f348afcd6226c573b8c8f8421c7d3d219a3e1f3eb667d9015e44de9', 
    '0xb4ba543c8c47955ec928eb9e8a833983a1b03578f097ebda09fb76dcedc19445', 
    '0x36c360beb31c208f41f322d26b069adb9c18d1facbb73493c0caaf3fb6b468cd', 
    '0x12c319e60db3d8c2d2606291faf4ed31cee8eff21675b36b800384090a97f598', 
    '0xdf80fd1df2197a14146fa836fd8eabb5bdc4bd1a1c851bca85f4ab43804c8043', 
    '0x1ff3c0dac595b23a280d378c322e1f94d54ced462849b236fc885422359f0ce6', 
    '0xd767ee5c0020ff360f15775d311cec02d74088d07b832b1f2526a565de1dc0e3', 
    '0xafafbb54250104c440e63ed4f2237684e05d2d7bb8d908261a684203faae6e56', 
    '0x40f3c826276bdef25d3bd2ddff8932d82a09c12849f31ef7b0a33d7a99ceefcd', 
    '0xaa53dd547e88358df4c6de5c9a13ffa5a916b5b2e3155de3f91bcf8141c1ede4', 
    '0x30058f5d89697c5c0dd74d1500ed4a23a3ef72f0c89b52e6860d26c314d7f349', 
    '0xe623f8c91c84445f714bcba6ab6623be166ae1c84f58ab553fd41180d367efe5', 
    '0x1984e8ad3010bd66ccc8e190bc4531a1bbda9b975058a9c003a7000343836459', 
    '0x2823c1ad8e71bf602ed5ea433be7f7a7489975f53617e98c08dbb7a6bff236b1', 
    '0x5fa230bc5afadc878123a5ad1d82d500daf3d72ed7301b3571c3280197b44105', 
    '0xa0707aea5dbbbbf77bc473ac0b249bda145e26183fb0df647ba37503cb548470', 
    '0xc395054b304db2969da05c20d4ae841847b11acf2fb8d2e142d412116171cba3', 
    '0x658ea7390a5f7cfba381c619b95ca3c807bf7e386668ee4c281777ab46b7ab8e', 
    '0x37a947ad9441c2fbb0dd3bece037503a0fc5aaa8a7202cf592a9405a6ab68d48', 
    '0xde6e220794cb5246dbe9d5ccbee28b64843092fd24a140f5dc0cb425e3030bd7', 
    '0x890d87c7518303c14e31784f7c10b9268d23fab197c102f068486d5245728323', 
    '0xe967d03ede2264a0c61a6aad974c29a98864a9baaa204fc971c2542159f7934f', 
    '0xdc01a0f24beb62546edf25396b29e4e1f329eb46889b33edb77c4bb4e2d27ecb', 
    '0xd626d3b9adce6c2c6f997e4c17a8bc8a301231f764904fdda2cc0a0b8bf53b3a', 
    '0x7d5c01988ab256ca43379d04745c40094e6490ccc8223913ac765fc9c3e0d1e1', 
    '0x0ba62db55d4db43fa2010b1df3b85176fb3ebecb12867f07894115a27e81ce01', 
    '0x0a59a0252842490128510f7cd202a21159fceb954b459dbc40c3b3a05310bb5a', 
    '0x4552229f9665c6cde270e05573e6af5d76db767a36aaa444d7e5d1b52451f039'
]



knownTxsNotCollected = [
    "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec",
    "0x52a0541deff2373e1098881998b60af4175d75c410d67c86fcee850b23e61fc2",
    "0xca13006944e6eba2ccee0b2d96a131204491641014622ef2a3df3db3e6939062",
    "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec",
    "0x9ef7a35012286fef17da12624aa124ebc785d9e7621e1fd538550d1209eb9f7d",
    "0xd770356649f1e60e7342713d483bd8946f967e544db639bd056dfccc8d534d8e",
    "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec"
]