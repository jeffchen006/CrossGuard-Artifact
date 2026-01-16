import os
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from crawlPackage.crawlEtherscan import CrawlEtherscan
from crawlPackage.crawlQuicknode import CrawlQuickNode
# from crawlPackage.crawlTrueBlocks import CrawlTrueBlocks
from staticAnalyzer.slitherAnalyzer import slitherAnalyzer
from staticAnalyzer.vyperAnalyzer import vyperAnalyzer

import subprocess
import ujson as json 
import time
import random
import pickle
import copy
import sqlite3
from crawlPackage.cacheDatabase import _save_transaction_receipt, _load_transaction_receipt, _save_contract, _load_contract



# Solidity starts from 0.4.11 to 0.8.17
# Vyper starts from 0.1.0-beta.16 to 0.3.7
# Vyper starts to support storage layout option from 0.2.16


def save_object(obj, filename: str):
    # print("filename: ", filename)
    try:
        with open(SCRIPT_DIR + "/cache/" + "{}.pickle".format(filename), "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print("Error during pickling object (Possibly unsupported):", ex)
    finally:
        pass
 

def load_object(filename: str):
    # print("read filename: ", filename)
    try:
        with open(SCRIPT_DIR + "/cache/" + "{}.pickle".format(filename), "rb") as f:
            value = pickle.load(f)
            return value
    except Exception as ex:
        return None
    finally:
        pass



class Analyzer:

    
    def __init__(self) -> None:
        self.crawlEtherscan = CrawlEtherscan()
        self.slitherAnalyzer = slitherAnalyzer()
        self.vyperAnalyzer = vyperAnalyzer()
        self.isVyperCache = {}
        self.storageMappingMapping = {}
        self.funcSigMapMapping = {}
        self.unableCompileAddresses = []

        SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
        etherScanDatabase = SCRIPT_DIR + "/../crawlPackage/database/etherScan.db"
        if os.path.exists(etherScanDatabase):
            self.conn = sqlite3.connect(etherScanDatabase)
            self.cur = self.conn.cursor()

            self.slitherAnalyzer.cur = self.cur
            self.vyperAnalyzer.cur = self.cur
            

    
    # def contract2storageLayout(self, contractAddress: str) -> dict:
    #     """Given a contract address, return a map (<func selector> -> <func signature>)"""
    #     filename = "{}_storageLayout".format(contractAddress.lower())
    #     storage_layout = load_object(filename)
    #     if storage_layout is not None:
    #         return storage_layout
    #     if self.isVyper(contractAddress):
    #         storage_layout = self.vyperAnalyzer.Contract2storageLayout(contractAddress)
    #     else:
    #         storage_layout = self.slitherAnalyzer.Contract2storageLayout(contractAddress)
    #     if storage_layout == None:
    #         sys.exit("Error: cannot read storage layout of {}!".format(contractAddress))
            
    #     save_object(storage_layout, filename)
    #     return storage_layout

    def contract2storageMapping(self, contractAddress: str) -> dict:
        """Given a contract, return a map (<position in bytes> -> <variables and its properties>)"""
        if contractAddress in self.storageMappingMapping:
            return self.storageMappingMapping[contractAddress]

        if contractAddress in self.unableCompileAddresses:
            return None

        anotherFileName = "UnableCompileAddresses"
        UnableCompileAddresses = load_object(anotherFileName)
        if UnableCompileAddresses is None:
            self.unableCompileAddresses = []
        else:
            self.unableCompileAddresses = UnableCompileAddresses
            
        filename = "{}_storageMapping".format(contractAddress.lower())
        storage_mapping = load_object(filename)
        if storage_mapping is not None and storage_mapping != {}:
            self.storageMappingMapping[contractAddress] = storage_mapping
            return storage_mapping
        
        try:
            if not self.isVyper(contractAddress):
                storage_mapping = self.slitherAnalyzer.Contract2storageMapping(contractAddress)
                self.storageMappingMapping[contractAddress] = storage_mapping
            else:
                storage_mapping = self.vyperAnalyzer.Contract2storageMapping(contractAddress)
                self.storageMappingMapping[contractAddress] = storage_mapping
        except:
            storage_mapping = None

        if storage_mapping == None:
            # print("Error: cannot read storage mapping of {}!".format(contractAddress))
            # print("possible reason: the contract is written in Vyper < 0.2.16")
            self.unableCompileAddresses.append(contractAddress)
            save_object(self.unableCompileAddresses, anotherFileName)
            pass
        save_object(storage_mapping, filename)
        return storage_mapping

    def imple2funcSigMap(self, contractAddress: str, implementationAddress: str):
        filename = "{}_funcSigMap".format(contractAddress.lower())
        funcSigMap2 = load_object(filename)

        funcSigMap = self.contract2funcSigMap(implementationAddress)
        for funcSelector in funcSigMap:
            if funcSelector not in funcSigMap2:
                funcSigMap2[funcSelector] = funcSigMap[funcSelector]
        save_object(funcSigMap2, filename)
        # print(funcSigMap2)
        return funcSigMap2



    def contract2funcSigMap(self, contractAddress: str):
        """Given a contract address, return a list of function selectors"""
        """{selector: (name, input_types, output_types)}"""
        """eg. {'0x771602f7': ('add', ['uint256', 'uint256'], ['uint256'], readOnly?)...}"""
        if contractAddress in self.funcSigMapMapping:
            return self.funcSigMapMapping[contractAddress]
        
        filename = "{}_funcSigMap".format(contractAddress.lower())
        funcSigMap2 = load_object(filename)
        if funcSigMap2 is None:
            funcSigMap2 = {}

        else:
            # print(len(funcSigMap2.keys()))
            self.funcSigMapMapping[contractAddress] = funcSigMap2
            return funcSigMap2
        
        funcSigMap2 = {}
        
        anotherFileName = "UnverifiedAddresses"
        UnverifiedAddresses = load_object(anotherFileName)
        if UnverifiedAddresses is None:
            self.UnverifiedAddresses = []
        else:
            self.UnverifiedAddresses = UnverifiedAddresses
        
        if contractAddress in self.UnverifiedAddresses:
            return {}
        
        # try it until it succeeds:
        while True:
            try:
                # func sig map from public ABI
                funcSigMap = self.crawlEtherscan.Contract2funcSigMap(contractAddress)
                break
            except Exception as ex:
                print("etherscan error: ", contractAddress)
                time.sleep(2)
                pass

        # # func sig map from public ABI
        # try:
        #     funcSigMap = self.crawlEtherscan.Contract2funcSigMap2(contractAddress)
        # except Exception as ex:
        #     print("etherscan error: ", contractAddress)
        #     return funcSigMap2
        
        if len(funcSigMap.keys()) == 0: # means the contract is not verified on etherscan
            self.funcSigMapMapping[contractAddress] = {}
            self.UnverifiedAddresses.append(contractAddress)
            save_object(self.UnverifiedAddresses, anotherFileName)
            return {}
        
        funcSigMap2 = None
        try: 
            self.crawlEtherscan.Contract2Sourcecode(contractAddress)
            if not self.isVyper(contractAddress):
                # func sig map from slither
                funcSigMap2 = self.slitherAnalyzer.Contract2funcSigMap(contractAddress)
            else:
                # func sig map from vyper compile results
                funcSigMap2 = self.vyperAnalyzer.Contract2funcSigMap(contractAddress)
        except Exception as ex:
            return funcSigMap
        
        # merge two maps
        for funcSelector in funcSigMap:
            # <funcSelector not in funcSigMap2> means it is a read-only function, in every case, it's a public variable query function. 
            funcSigMap2[funcSelector] = funcSigMap[funcSelector]

        switch_filename = "switchMap"
        switchMap = load_object(switch_filename)
        if switchMap is None:
            switchMap = {}
        keys = list(switchMap.keys())
        for key in keys:
            if "0x" in key:
                switchMap.pop(key)

        # convert non primitive types to address
        for funcSelector in funcSigMap2:
            for jj in [1, 2]:
                if jj == 2 and funcSelector == "constructor":
                    continue
                for ii in range(len(funcSigMap2[funcSelector][jj])):
                    if  funcSigMap2[funcSelector][jj][ii] in switchMap:
                        funcSigMap2[funcSelector][jj][ii] = switchMap[ funcSigMap2[funcSelector][jj][ii] ]
            

        # check if there is a function selector collision
        for funcSelector in funcSigMap:
            if funcSelector == "constructor":
                continue

            if funcSelector in funcSigMap2:
                if ( len(funcSigMap[funcSelector]) != len(funcSigMap2[funcSelector]) \
                or len(funcSigMap[funcSelector][1]) != len(funcSigMap2[funcSelector][1]) \
                or len(funcSigMap[funcSelector][2]) != len(funcSigMap2[funcSelector][2]) \
                or funcSigMap[funcSelector][0] != funcSigMap2[funcSelector][0] ):

                    funcSigMap2[funcSelector] = funcSigMap[funcSelector]
                    # print(funcSigMap[funcSelector])
                    # print(funcSigMap2[funcSelector])
                    # sys.exit("Error: function selector different lengths !")

                for ii in [1, 2]:
                    for jj in range(len(funcSigMap[funcSelector][ii])):
                        if funcSigMap[funcSelector][ii][jj] != funcSigMap2[funcSelector][ii][jj]:
                           switchMap[ copy.deepcopy(funcSigMap2[funcSelector][ii][jj]) ] = funcSigMap[funcSelector][ii][jj]
                           funcSigMap2[funcSelector][ii][jj] = funcSigMap[funcSelector][ii][jj]


        self.funcSigMapMapping[contractAddress] = funcSigMap2
        save_object(switchMap, switch_filename)        
        save_object(funcSigMap2, filename)

        return funcSigMap2


    def contract2funcSelectors(self, contractAddress: str) -> list:
        """Given a contract address, return a list of function selectors"""
        funcSigMap = self.contract2funcSigMap(contractAddress)
        funcSelectors = list(funcSigMap.keys())
        print(funcSelectors)
        return funcSelectors

    def isVyper(self, contractAddress: str):
        """Given a contract address, return True if the contract is Vyper"""
        if contractAddress in self.isVyperCache:
            return self.isVyperCache[contractAddress]
            
        CompilerVersion, _ = self.vyperAnalyzer.contract2Sourcecode(contractAddress)
        if CompilerVersion is None or (not CompilerVersion.startswith("vyper")):
            self.isVyperCache[contractAddress] = False
            return False
        self.isVyperCache[contractAddress] = True
        return True





if __name__ == "__main__":
    analyzer = Analyzer()
    # analyzer.contract2storageMapping("0x15fda9f60310d09fea54e3c99d1197dff5107248")

    # analyzer.imple2funcSigMap("0x2069043d7556b1207a505eb459d18d908df29b55", "0xc68bf77e33f1df59d8247dd564da4c8c81519db6")
    # analyzer.imple2funcSigMap("0x44fbebd2f576670a6c33f6fc0b00aa8c5753b322", "0x3c710b981f5ef28da1807ce7ed3f2a28580e0754")

    contract = "0x51a7f889480c57cbeea81614f7d0be2b70db6c5e"
    map = analyzer.contract2funcSigMap(contract)
    print(map)

    sys.exit(0)


    map = {
        "Uniswap2": ["0x1f98415757620b543a52e61c46b32eb19261f984" , "0x5ba1e12693dc8f9c48aad8770482f4739beed696", "0xb753548f6e010e7e680ba186f9ca1bdab2e90cf2", "0xbfd8137f7d1516d3ea5ca83523914859ec47f573", "0xb27308f9f90d607463bb33ea1bebb41c27ce5ab6", "0xe592427a0aece92de3edee1f18e0157c05861564", "0x42b24a95702b9986e82d421cc3568932790a48ec", "0x91ae842a5ffd8d12023116943e72a606179294f3", "0xee6a57ec80ea46401049e92587e52f5ec1c24785", "0xc36442b4a4522e871399cd717abdd847ab11fe88", "0xa5644e29708357803b5a882d272c41cc0df92b34", "0x61ffe014ba17989e743c5f6cb21bf9697530b21e", "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45", "0x000000000022d473030f116ddee9f6b43ac78ba3", "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad", "0xe34139463ba50bd61336e0c446bd8c0867c6fe65"],
        "AAVE2": ["0xc2aacf6553d20d1e9d78e365aaba8032af9c85b0","0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2","0x64b761d848206f447fe2dd461b0c635ec39ebb27","0x8164cc65827dcfe994ab23944cbc90e0aa80bfcb","0x2f39d218133afab8f2b819b1066c7e434ad94e9e","0xbaa999ac55eace41ccae355c77809e68bb345170","0x7b4eb56e7cd4b454ba8ff71e4518426369a138a3","0x162a7ac02f547ad796ca549f757e2b8d1d9b10a6","0x91c0ea31b49b69ea18607702c5d9ac360bf3de7d","0x893411580e590d62ddbca8a703d61cc4a8c7b2b9","0xc7be5307ba715ce89b152f3df0658295b3dba8e2","0x54586be62e3c3580375ae3723c145253060ca0c2","0x464c71f6c2f760dda6093dcb91c24c39e5d6e18c","0x3d569673daa0575c936c7c67c4e6aeda69cc630c","0xadc0a53095a0af87f3aa29fe0715b5c28016364e","0x02e7b8511831b1b02d9018215a0f8f500ea5c6b3","0x8761e0370f94f68db8eaa731f4fc581f6ad0bd68","0x78f8bd884c3d738b74b420540659c82f392820e0","0xb748952c7bc638f31775245964707bcc5ddfabfc"], 
        "Lido2": ["0xc1d0b3de6792bf6b4b37eccdcc24e45978cfd2eb","0xae7ab96520de3a18e5e111b5eaab095312d7fe84","0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0","0x8f73e4c2a6d852bb4ab2a45e6a9cf5715b3228b7","0xfddf38947afb03c621c71b06c9c70bce73f12999","0x55032650b14df07b85bf18a3a3ec8e0af2e028d5","0xae7b191a31f627b4eb1d4dac64eab9976995b433","0xc77f8768774e1c9244beed705c4354f2113cfc09","0x388c818ca8b9251b393131c08a736a67ccb19297","0x889edc2edab5f40e902b864ad4d7ade8e412f9b1","0xb9d7934878b5fb9610b3fe8a5e441e8fad7e293f","0xd15a672319cf0352560ee76d9e89eab0889046d3","0xf95f069f9ad107938f6ba802a3da87892298610e"]
    }

    for benchmark in map:
        for contract in map[benchmark]:
            print(contract)
            analyzer.contract2funcSigMap(contract)
            print("")


    # funcMap = analyzer.contract2funcSigMap(contract)
    # print(funcMap)
    
    sys.exit(0)

    unique_contracts = [
        "0x026c6ac0179d34e4488f40c52c1486355ce4e755",
        "0x051ebd717311350f1684f89335bed4abd083a2b6",
        "0x053c80ea73dc6941f518a68e2fc52ac45bde7c9c",
        "0x10fdbd1e48ee2fd9336a482d746138ae19e649db",
        "0x13db1cb418573f4c3a2ea36486f0e421bc0d2427",
        "0x1637e4e9941d55703a7a5e7807d6ada3f7dcd61b",
        "0x16f6664c16bede5d70818654defef11769d40983",
        "0x17786f3813e6ba35343211bd8fe18ec4de14f28b",
        "0x1887118e49e0f4a78bd71b792a49de03504a764d",
        "0x1b0284391fdf905222b6174ef2cde60ba58d9529",
        "0x1c47343ea7135c2ba3b2d24202ad960adafaa81c",
        "0x1cf226e9413addaf22412a2e182f9c0de44af002",
        "0x1f9b4756b008106c806c7e64322d7ed3b72cb284",
        "0x210ac53b27f16e20a9aa7d16260f84693390258f",
        "0x222412af183bceadefd72e4cb1b71f1889953b1c",
        "0x222d7b700104c91a2ebbf689ff7b2a35f2541f98",
        "0x226124e83868812d3dae87eb3c5f28047e1070b7",
        "0x228619cca194fbe3ebeb2f835ec1ea5080dafbb2",
        "0x2427da81376a0c0a0c654089a951887242d67c92",
        "0x26267e41ceca7c8e0f143554af707336f27fa051",
        "0x299e254a8a165bbeb76d9d69305013329eea3a3b",
        "0x2a537fa9ffaea8c1a41d3c2b68a9cb791529366d",
        "0x2db6c82ce72c8d7d770ba1b5f5ed0b6e075066d6",
        "0x338eee1f7b89ce6272f302bdc4b952c13b221f1d",
        "0x3756fa458880fa8fe53604101cf31c542ef22f6f",
        "0x39b1df026010b5aea781f90542ee19e900f2db15",
        "0x3a70dfa7d2262988064a2d051dd47521e43c9bdd",
        "0x3a84ad5d16adbe566baa6b3dafe39db3d5e261e5",
        "0x3c37f97f7d8f705cc230f97a0668f77a0e05d0aa",
        "0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258",
        "0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f",
        "0x4112a717edd051f77d834a6703a1ef5e3d73387f",
        "0x41d5d79431a913c4ae7d69a668ecdfe5ff9dfb68",
        "0x44fbebd2f576670a6c33f6fc0b00aa8c5753b322",
        "0x467e9f2caa9b7678ddc29b248cb9fb181907bf3e",
        "0x4baa77013ccd6705ab0522853cb0e9d453579dd4",
        "0x4c2a8a820940003cfe4a16294b239c8c55f29695",
        "0x4dcf7407ae5c07f8681e1659f626e114a7667339",
        "0x4e9a87ce601618fbf0c5bc415e35a4ac012d3863",
        "0x4ef29407a8dbca2f37b7107eab54d6f2a3f2ad60",
        "0x523effc8bfefc2948211a05a905f761cba5e8e9e",
        "0x55bf8304c78ba6fe47fd251f37d7beb485f86d26",
        "0x57cda125d0c7b146a8320614ccd6c55999d15bf2",
        "0x5ade7ae8660293f2ebfcefaba91d141d72d221e8",
        "0x5e181bdde2fa8af7265cb3124735e9a13779c021",
        "0x6847259b2b3a4c17e7c43c54409810af48ba5210",
        "0x6949bb624e8e8a90f87cd2058139fcd77d2f3f87",
        "0x697b4acaa24430f254224eb794d2a85ba1fa1fb8",
        "0x7623a53cbc779dbf44b706a00d4adf1be7e358ec",
        "0x77f973fcaf871459aa58cd81881ce453759281bc",
        "0x797aab1ce7c01eb727ab980762ba88e7133d2157",
        "0x7e4956688367fb28de3c0a62193f59b1526a00e7",
        "0x7f26337348cbaffd3368ab1aad1d111711a0617d",
        "0x7fcb7dac61ee35b3d4a51117a7c58d53f0a8a670",
        "0x812c0b2a2a0a74f6f6ed620fbd2b67fec7db2190",
        "0x833e440332caa07597a5116fbb6163f0e15f743d",
        "0x8379baa817c5c5ab929b03ee8e3c48e45018ae41",
        "0x85191476022593a408c472455b57b8346756f144",
        "0x851a040fc0dcbb13a272ebc272f2bc2ce1e11c4d",
        "0x865377367054516e17014ccded1e7d814edc9ce4",
        "0x8922c1147e141c055fddfc0ed5a119f3378c8ef8",
        "0x8c2f33b3a580baeb2a1f2d34bcc76e020a54338d",
        "0x8c3b7a4320ba70f8239f83770c4015b5bc4e6f91",
        "0x8f0439382359c05ed287acd5170757b76402d93f",
        "0x951d51baefb72319d9fbe941e1615938d89abfe2",
        "0x98595670e97aa2ec229f366806b37745ad6e92b5",
        "0x9a3a03c614dc467acc3e81275468e033c98d960e",
        "0x9a975fe93cff8b0387b958adb9082b0ed0659ad2",
        "0x9c211bfa6dc329c5e757a223fb72f5481d676dc1",
        "0x9ca85572e6a3ebf24dedd195623f188735a5179f",
        "0x9e65ad11b299ca0abefc2799ddb6314ef2d91080",
        "0xa04bdb1f11413a84d1f6c1d4d4fed0208f2e68bf",
        "0xa422890cbbe5eaa8f1c88590fbab7f319d7e24b6",
        "0xa731585ab05fc9f83555cf9bff8f58ee94e18f85",
        "0xa80e737ded94e8d2483ec8d2e52892d9eb94cf1f",
        "0xa81bd16aa6f6b25e66965a2f842e9c806c0aa11f",
        "0xaa6198fe597dfc331471ae7deba026fb299297fc",
        "0xacd43e627e64355f1861cec6d3a6688b31a6f952",
        "0xae465fd39b519602ee28f062037f7b9c41fdc8cf",
        "0xb0602af43ca042550ca9da3c33ba3ac375d20df4",
        "0xb14b3b9682990ccc16f52eb04146c3ceab01169a",
        "0xb38707e31c813f832ef71c70731ed80b45b85b2d",
        "0xb387e90367f1e621e656900ed2a762dc7d71da8c",
        "0xb43f0707b2719a5b8ab905d253022c6073a63926",
        "0xb54acff1ff7c7de9b0e30ad6d58b941ed22bbb44",
        "0xb64dfae5122d70fa932f563c53921fe33967b3e0",
        "0xba5d28f4ecee5586d616024c74e4d791e01adee7",
        "0xbadac56c9aca307079e8b8fc699987aac89813ee",
        "0xbd0e1bc09ae52072a9f5d3343b98643ae585e339",
        "0xc08f38f43adb64d16fe9f9efcc2949d9eddec198",
        "0xc1e088fc1323b20bcbee9bd1b9fc9546db5624c5",
        "0xc59601f0cc49baa266891b7fc63d2d5fe097a79d",
        "0xc95cbe4ca30055c787cb784be99d6a8494d0d197",
        "0xcbc1065255cbc3ab41a6868c22d1f1c573ab89fd",
        "0xcd892a97951d46615484359355e3ed88131f829d",
        "0xcda4770d65b4211364cb870ad6be19e7ef1d65f4",
        "0xcdb97f4c32f065b8e93cf16bb1e5d198bcf8ca0d",
        "0xd06527d5e56a3495252a528c4987003b712860ee",
        "0xd55ada00494d96ce1029c201425249f9dfd216cc",
        "0xd652c40fbb3f06d6b58cb9aa9cff063ee63d465d",
        "0xd6e194af3d9674b62d1b30ec676030c23961275e",
        "0xd721a90dd7e010c8c5e022cc0100c55ac78e0fc4",
        "0xd77c2ab1cd0faa4b79e16a0e7472cb222a9ee175",
        "0xd8d6ab3d2094d3a0258f4193c5c85fadd44d589a",
        "0xdc59ac4fefa32293a95889dc396682858d52e5db",
        "0xde2af899040536884e062d3a334f2dd36f34b4a4",
        "0xe097783483d1b7527152ef8b150b99b9b2700c8d",
        "0xe102421a85d9c0e71c0ef1870dac658eb43e1493",
        "0xe4ffd682380c571a6a07dd8f20b402412e02830e",
        "0xe7db46742c51a7bd64b8d83b8201239d759786be",
        "0xe8929afd47064efd36a7fb51da3f8c5eb40c4cb4",
        "0xe89a6d0509faf730bd707bf868d9a2a744a363c7",
        "0xe952bda8c06481506e4731c4f54ced2d4ab81659",
        "0xe980efb504269ff53f7f4bc92a2bd1e31b43f632",
        "0xea48b3f50f3cf2216e34e2e868abc810b729f0e3",
        "0xebe0d1cb6a0b8569929e062d67bfbc07608f0a47",
        "0xed2cd60c0000a990a5ffaf0e7ddc70a37d7c623f",
        "0xeff039c3c1d668f408d09dd7b63008622a77532c",
        "0xf00a38376c8668fc1f3cd3daeef42e0e44a7fcdb",
        "0xf0358e8c3cd5fa238a29301d0bea3d63a17bedbe",
        "0xf289b48636f6a66f8aea4c2d422a88d4f73b3894",
        "0xf2b223eb3d2b382ead8d85f3c1b7ef87c1d35f3a",
        "0xf938424f7210f31df2aee3011291b658f872e91e",
        "0xfa5a44d3ba93d666bf29c8804a36e725ecac659a",
        "0xfa6de2697d59e88ed7fc4dfe5a33dac43565ea41",
        "0xfca4416d9def20ac5b6da8b8b322b6559770efbf",
        "0xfd609a03b393f1a1cfcacedabf068cad09a924e2",
        "0xfea425f0baadf191546cf6f2dbf72357d631ae46"
    ]



    for contract in unique_contracts:

        # contract = "0xD533a949740bb3306d119CC777fa900bA034cd52"
        funcMap = analyzer.contract2funcSigMap(contract)
        print(funcMap)


#     # EMN contract
#     contractAddress = "0x5ade7aE8660293F2ebfcEfaba91d141d72d221e8"

#     # Yearn contract
#     contractAddress = "0xacd43e627e64355f1861cec6d3a6688b31a6f952"
# #  KeyError: '0xf8897945'

#     funcSigMap = analyzer.contract2funcSigMap(contractAddress)

#     # StrategyDAI3pool
#     contractAddress = "0x9c211bfa6dc329c5e757a223fb72f5481d676dc1"
#     funcSigMap = analyzer.contract2funcSigMap(contractAddress)

#     # test isVyper
#     # EMN contract
#     contractAddress = "0x5ade7aE8660293F2ebfcEfaba91d141d72d221e8"
#     print(analyzer.isVyper(contractAddress))

    # contractAddress = "0x6b175474e89094c44da98b954eedeac495271d0f"
    # funcSigMap = analyzer.contract2funcSigMap(contractAddress)
    # import pprint
    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(funcSigMap)


    # # test contract2storageMapping
    # contractAddress = "0xd77e28a1b9a9cfe1fc2eee70e391c05d25853cbf"
    # storageMapping = analyzer.contract2storageMapping(contractAddress)
    # print(storageMapping)

    
    # ('0x85ca13d8496b2d22d6...1e096dd7e0', 'Mapping', '00000000000000000000...0000000019', 'CALLER', '0x195f9f44489b43e04', 5527)


    





