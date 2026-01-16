import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from crawlPackage.crawlEtherscan import *
from crawlPackage.crawlQuicknode import *
from utilsPackage.compressor import *
from constraintPackage.macros import *
from constraintPackage.utils import *
# import multiprocessing
# import matplotlib.pyplot as plt
# from parserPackage.parser import analyzeOneTxGlobal
from staticAnalyzer.analyzer import Analyzer
import copy
from labelPackage.readLabels import Labeler
from constraintPackage.complementary import complementary, reEntrancyGuard, revertedTransactions, arbitrary_external_call
from constraintPackage.RAWTree import RAWTree





pruneReadOnly = False
pruneERC20 = False
pruneTrivialControlFlow = False

pruneRuntimeReadOnly = False
pruneCache = False
pruneRAW = False

pruneParametric2 = None



reEntrancyName = ["flashBorrowToken", "flashLoan", "0xd065-borrow", "0xeb7e-borrow", "0x2db6-borrow", \
                  "0x77f9-0x66fa576f", "0xc9f2-deposit"]

reEntrancyFunctions = []


def extract_name(callnode):
    """Extract the name from the callnode tuple."""
    contract, funcName, status, structLogsStart, structLogsEnd, type, storageAccesses = callnode
    return contract[0:6] + "-" + funcName

globalisReEntrancy = False    

class callTree:
    def __init__(self, node) -> None:
        self.node = node
        self.children = []
    
    def addChildren(self, child, depth = 0):
        if depth == 0:
            self.children.append(child)
        else:
            self.children[-1].addChildren(child, depth - 1)

    def add_child(self, child):
        self.children.append(child)

    def toResult(self):
        results = []
        for child in self.children:
            results.append(child.__str__())
        return results
    
    def toResultStorage(self):
        results = []    
        for child in self.children:
            results.append(child.node[6])
        return results
    
    def __str__(self) -> str:
        returnStr = ""
        isReEntrancy = False
        for name in reEntrancyName:
            extracted = extract_name(self.node)
            if extracted.endswith("-" + name) or "-" + name + "-" in extracted:
                isReEntrancy = True
                global globalisReEntrancy
                globalisReEntrancy = True

                key = [self.node[0], self.node[1]]
                if key not in reEntrancyFunctions:
                    reEntrancyFunctions.append(key)
                break
        returnStr += " <" + extract_name(self.node) + "-start,"
        if isReEntrancy:
            for child in self.children:
                func = child.node[0] + "-" + child.node[1]
                func0 = self.node[0] + "-" + self.node[1]
                if func0 in arbitrary_external_call and func in arbitrary_external_call[func0]:
                    pass
                else:
                    returnStr += str(child)
        returnStr += extract_name(self.node) + "-end> "
        return returnStr
    
def can_be_parent(parent, child):
    if parent.node == None:
        return True
    a1, a2 = parent.node[3], parent.node[4]
    b1, b2 = child.node[3], child.node[4]
    return a1 < b1 and a2 > b2

def insert_node(root, node):
    # Try to insert the node in the subtree of root
    inserted = False
    for child in root.children:
        if can_be_parent(child, node):
            if isinstance(node, callTree):
                insert_node(child, node )
            else:
                insert_node(child, callTree(node) )
            inserted = True
            break
    if not inserted:
        # If not inserted in any child, check if it should be a child of root
        if can_be_parent(root, node):
            root.add_child(node)
            # # check whether your storageAccesses is a subset of the parent's storageAccesses
            # if root.node is not None and root.node[5] != "delegatecall" and root.node[6] != None and node.node[6] != None:
            #     for contract in node.node[6]:
            #         if contract not in root.node[6]:
            #             sys.exit("storageAccesses is not a subset of the parent's storageAccesses")
            #         for key in node.node[6][contract]:
            #             if key not in root.node[6][contract]:
            #                 sys.exit("storageAccesses is not a subset of the parent's storageAccesses")

        else:
            # Else, it is a sibling of root, to be handled by the caller
            return False
    return True

class recorder:
    def __init__(self, targetContracts):
        self.targetContracts = targetContracts
        self.functionAccess = []
        self.benchmark = None
        self.tx = None
        self.block = None
        self.tokenTransfers = []
        self.tokens = []
        self.storageAccesses = {}

    def reset(self, tx = None, block = None):
        self.tx = tx
        self.block = block
        self.functionAccess = []
        self.tokenTransfers = []

    def getStorageAccesses(self, tree, parentAddrList, delegateCallList, depth):
        if depth == 0:
            self.storageAccesses = {}
            if "type" in tree.info and tree.info["type"] == "delegatecall":
                return []
        counter = 0
        if "type" in tree.info and tree.info["type"] == "delegatecall":
            counter += 1
            for delegateCall in delegateCallList[::-1]:
                if delegateCall:
                    counter += 1
                else:
                    break

        contract = tree.info["addr"]
        if counter > 0:
            contract = parentAddrList[- counter]
        if "sload/sstore" in tree.info:
            if contract not in self.storageAccesses:
                self.storageAccesses[contract] = tree.info["sload/sstore"]
            else:
                self.storageAccesses[contract] += tree.info["sload/sstore"]
        isDelegateCall = False
        if "type" in tree.info and tree.info["type"] == "delegatecall":
            isDelegateCall = True
        for internalCall in tree.internalCalls:
            self.getStorageAccesses(internalCall, parentAddrList + [contract], delegateCallList + [isDelegateCall], depth + 1)

        return self.storageAccesses

    def traverseTree(self, tree, parentAddrList, delegateCallList):
        if "meta" in tree.info:
            for internalCall in tree.internalCalls:
                self.traverseTree(internalCall, parentAddrList, delegateCallList)
            return
        else:
            contract = tree.info["addr"]
            if contract in self.targetContracts:
                node = None
                if tree.info["type"] == "create" or tree.info["type"] == "create2":

                    storageAccesses = self.getStorageAccesses(tree, parentAddrList, delegateCallList, 0)
                    node = (contract, "constructor", "complete", tree.info["structLogsStart"], tree.info["structLogsEnd"], tree.info["type"].lower(), storageAccesses)
                    self.functionAccess.append( node )

                elif "call" in tree.info["type"].lower():
                    # Step 1: get selector
                    selector = ""
                    if "Raw calldata" in tree.info and tree.info["Raw calldata"] != "" and "type" in tree.info and tree.info["type"] != "firstCall":
                        calldata = tree.info["Raw calldata"]
                        # remove 0x prefix from calldata if exists
                        if calldata[:2] == "0x":
                            calldata = calldata[2:]
                        selector = '0x' + calldata[:8]
                    elif "calldata" in tree.info and tree.info["calldata"] != "":
                        calldata = tree.info["calldata"]
                        # remove 0x prefix from calldata if exists
                        if calldata[:2] == "0x":
                            calldata = calldata[2:]
                        selector = '0x' + calldata[:8]
                    else:
                        selector = tree.info["Selector"] if "Selector" in tree.info else ''

                    status = "complete"
                    if "gasless" in tree.info and tree.info["gasless"] :
                        status = "gasless"

                    if len(selector) != 10 and selector != "0x" and selector != "":
                        sys.exit("selector length is not 10: {}".format(selector))
                    
                    
                    # Step 1.1: get storage accesses:
                    storageAccesses = []
                    if "type" in tree.info and tree.info["type"] != "delegatecall":
                        storageAccesses = self.getStorageAccesses(tree, parentAddrList, delegateCallList, 0)

                    # Step 2: handle fallback
                    if selector == "0x" or selector == "":
                        # Step 2.1: handle staticcall to fallback
                        if tree.info["type"] == "staticcall" and "Raw returnvalue" in tree.info and tree.info["Raw returnvalue"] != "":
                            self.functionAccess.append( (contract, "fallback", status, tree.info["structLogsStart"], tree.info["structLogsEnd"], tree.info["type"].lower(), storageAccesses) )
                        elif tree.info["type"] == "staticcall" and "Raw returnvalue" in tree.info and tree.info["Raw returnvalue"] == "":
                            sys.exit("empty return value for a staticcall")

                        # Step 2.2: handle call to fallback
                        if 'msg.value' not in tree.info and "type" in tree.info and tree.info["type"] != "staticcall":
                            print(tree.info)
                            sys.exit("msg.value not found")
                        else:
                            msgValue = int(tree.info['msg.value'], 16) if 'msg.value' in tree.info else 0
                            self.functionAccess.append( (contract, "fallback", status, tree.info["structLogsStart"], tree.info["structLogsEnd"], tree.info["type"].lower(), storageAccesses) )
                            # if msgValue > 0:
                            #     self.functionAccess.append( (contract, "fallback", msgValue) )

                    # step 3: handle normal function call
                    else:
                        # funcName = self.contractSelector2functions[contract][selector]
                        # print(funcName)
                        self.functionAccess.append( (contract, selector, status, tree.info["structLogsStart"], tree.info["structLogsEnd"], tree.info["type"].lower(), storageAccesses) )
                        # pass

                else:
                    print("unknown type: {}".format(tree.info["type"]))
                    sys.exit("unknown type: {}".format(tree.info["type"]))

            counter = 0
            if "type" in tree.info and tree.info["type"] == "delegatecall":
                counter += 1
                for delegateCall in delegateCallList[::-1]:
                    if delegateCall:
                        counter += 1
                    else:
                        break
            if counter > 0:
                contract = parentAddrList[- counter]

            isDelegateCall = False
            if "type" in tree.info and tree.info["type"] == "delegatecall":
                isDelegateCall = True

            for internalCall in tree.internalCalls:
                self.traverseTree(internalCall, parentAddrList + [contract], delegateCallList + [isDelegateCall])
            return

    def getRealSender(self, tree, parentAddrList, delegateCallList):
        sender2 = None
        for ii in range(-1, -5, -1):
            if not delegateCallList[ii]:
                sender2 = parentAddrList[ii]
                break
        # if sender1 != sender2:
        #     sys.exit("sender1 != sender2")
        return sender2
    
    def decodeTransferFrom(self, calldata):
        if not calldata.startswith("23b872dd"):
            sys.exit("calldata not start with 23b872dd")
        # Remove the function selector (first 4 bytes)
        data = calldata[8:]
        # Decode the data
        from_address = ('0x' + data[24:64])
        to_address = ('0x' + data[88:128])
        amount = int(data[128:], 16)
        return (from_address, to_address, amount)
    
    def decodeTransfer(self, calldata):
        if not calldata.startswith("a9059cbb"):
            sys.exit("calldata not start with a9059cbb")
        # Remove the function selector (first 4 bytes)
        data = calldata[8:]
        # Decode the data
        to_address = ('0x' + data[24:64])
        amount = int(data[64:], 16)
        return (to_address, amount)

    def traverseTreeToken(self, tree, parentAddrList, delegateCallList):
        if "meta" in tree.info:
            for internalCall in tree.internalCalls:
                self.traverseTreeToken(internalCall, parentAddrList, delegateCallList)
            return
        else:
            contract = tree.info["addr"]
            
            if "msg.value" in tree.info and int(tree.info["msg.value"], 16) != 0:
                receiver = contract
                # if "type" in tree.info and tree.info["type"] == "delegatecall":
                #     print("interesting! delegatecall with msg.value != 0")
                    # sys.exit(1)
                sender = parentAddrList[-1]
                if "type" in tree.info and tree.info["type"] == "delegatecall":
                    sender = self.getRealSender(tree, parentAddrList, delegateCallList)
                
                if sender in self.targetContracts or receiver in self.targetContracts:
                    self.tokenTransfers.append( ("ether", sender, receiver, int(tree.info["msg.value"], 16)) )
            
            # if contract in self.targetContracts:

            # There are cases that the proxy is one of our targetContract but the implementation is not
            for internalCall in tree.internalCalls:
                if "Selector" in internalCall.info:
                    tokenAddr = internalCall.info["addr"]

                    if internalCall.info["Raw calldata"][0:8] == "a9059cbb": # transfer(address,uint256)
                        calldata = internalCall.info["Raw calldata"]
                        (to_address, amount) = self.decodeTransfer(calldata)
                        sender = contract
                        if "type" in tree.info and tree.info["type"] == "delegatecall":
                            sender = parentAddrList[-1]
                        
                        if sender in self.targetContracts or to_address in self.targetContracts:
                            self.tokenTransfers.append( (tokenAddr, sender, to_address, amount) )

                    elif internalCall.info["Raw calldata"][0:8] == "23b872dd": # transferFrom(address,address,uint256)
                        calldata = internalCall.info["Raw calldata"]
                        (from_address, to_address, amount) = self.decodeTransferFrom(calldata)

                        if from_address in self.targetContracts or to_address in self.targetContracts:
                            self.tokenTransfers.append( (tokenAddr, from_address, to_address, amount) )
                
                 
            counter = 0
            if "type" in tree.info and tree.info["type"] == "delegatecall":
                counter += 1
                for delegateCall in delegateCallList[::-1]:
                    if delegateCall:
                        counter += 1
                    else:
                        break
            if counter > 0:
                contract = parentAddrList[- counter]

            isDelegateCall = False
            if "type" in tree.info and tree.info["type"] == "delegatecall":
                isDelegateCall = True

            for internalCall in tree.internalCalls:
                self.traverseTreeToken(internalCall, parentAddrList + [contract], delegateCallList + [isDelegateCall])
            return






knownTxsNotCollected = [
    "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec",
    "0x52a0541deff2373e1098881998b60af4175d75c410d67c86fcee850b23e61fc2",
    "0xca13006944e6eba2ccee0b2d96a131204491641014622ef2a3df3db3e6939062",
    "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec",
    "0x9ef7a35012286fef17da12624aa124ebc785d9e7621e1fd538550d1209eb9f7d",
    "0xd770356649f1e60e7342713d483bd8946f967e544db639bd056dfccc8d534d8e",
    "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec"
]

commonERC20Functions = ["transfer", "transferFrom", "approve", "increaseAllowance", "decreaseAllowance", "permit"]
# 0x23b872dd is the selector of transferFrom
commonERC20Selectors = ["0xa9059cbb", "0x23b872dd", "0x095ea7b3", "0x39509351", "0xa457c2d7", "0xd505accf"]



staticcall_functions = []
complementary_functions_nonReadOnly2ReadOnly = []
complementary_functions_close_source = []
complementary_functions_readOnlySideEffect = []

def sort_callnodes(callnodes, targetContracts, tx_category, extraEnterExits, benchmark ):
    global globalisReEntrancy
    globalisReEntrancy = False

    """Sort callnodes based on the structLogsStart and structLogsEnd values and handle nested inclusions."""
    sorted_nodes = sorted(callnodes, key=lambda x: (x[3], -x[4]))  # Sort by structLogsStart and descending structLogsEnd for nested inclusions
    root = callTree(None)
    for ii, node in enumerate(sorted_nodes):
        if ii == 0:
            root.addChildren(callTree(node))
            continue
        if not insert_node(root, callTree(node) ):
            new_root = callTree(node)
            if can_be_parent(new_root, root):
                new_root.addChildren(root)
                root = new_root
            else:
                sys.exit("root node is not parent of the new node")

    for child in root.children:
        if child.node[5] == "staticcall":
            key =  [child.node[0], child.node[1]] 
            if key not in staticcall_functions:
                staticcall_functions.append( key )

    if pruneReadOnly:
        # filter out staticcalls
        root.children = [child for child in root.children if child.node[5] != "staticcall"]
    root.children = [child for child in root.children if child.node[5] != "delegatecall"]

    if pruneERC20:
        root.children = [child for child in root.children if child.node[1] not in commonERC20Functions]
    

    if tx_category != 1 and tx_category != 2 and tx_category != 6:
        results = root.toResult()
        callFlow0 = str(results)

        global contract2invGas
        global contractFunc2InstrumentationGas
        global totalGas
        global totalGasWithGuard
        
        # counter number of -start and -end
        numEntries = callFlow0.count("-start")
        numExits = callFlow0.count("-end")
        if numEntries != numExits:
            sys.exit("numEntries != numExits")
        
        # totalGasWithGuard += (numEntries + extraEnterExits) * gasConsumptionGuard["ValidatePre"]
        # totalGasWithGuard += (numExits + extraEnterExits) * gasConsumptionGuard["ValidatePost"] 

        import re
        if len(results) > 0:
            pass
            # print("now is the time")
        pattern = r'<(0x[a-fA-F0-9]+)-'
        matches = re.findall(pattern, callFlow0)
        # unique_addresses = []
        # for address in matches:
        #     if address not in unique_addresses:
        #         unique_addresses.append(address)

        countTemp = 0
        for address in matches:
            isFound = False
            FoundAddress = ""
            for contract in targetContracts:
                if contract.startswith(address):
                    isFound = True
                    FoundAddress = contract
                    break
            if not isFound:
                print("FoundAddress not found in targetContracts, tx: ", tx)
                print("callFlow0: ", callFlow0)
                print("matches: ", matches)
                print("targetContracts: ", targetContracts)
                sys.exit("FoundAddress not found in targetContracts")

            if FoundAddress not in contract2invGas:
                contract2invGas[FoundAddress] = 0
            contract2invGas[FoundAddress] = contract2invGas[FoundAddress] + gasConsumptionGuard["ValidatePre"]  + gasConsumptionGuard["ValidatePost"]
            countTemp += 1

            if FoundAddress.lower() == benchmark2mostUsedContract[benchmark].lower():
                contract2invGas[FoundAddress] -= (gasConsumptionGuard["ValidatePre"] + gasConsumptionGuard["ValidatePost"])
                contract2invGas[FoundAddress] -= (gasConsumptionGuard["Instrument_prepost"])
                contract2invGas[FoundAddress] += gasConsumptionGuard["merge_instrument_prepost"]

                # totalGasWithGuard -= (gasConsumptionGuard["ValidatePre"] + gasConsumptionGuard["ValidatePost"])
                # totalGasWithGuard -= (gasConsumptionGuard["Instrument_prepost"])
                # totalGasWithGuard += gasConsumptionGuard["merge_instrument_prepost"]

        # if countTemp != numEntries:
        #     sys.exit("countTemp != numEntries, countTemp: {}, numEntries: {}".format(countTemp, numEntries))



    return root.toResult(), root.toResultStorage(), globalisReEntrancy
            
     



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
#    ==> the way to make sense of it: 




def classify(benchmark):
    ##########################################################################
    ################### Step 1: Classification 
    ##########################################################################
    c = classifier()
    # preparation
    ce = CrawlEtherscan()
    targetContracts = benchmark2targetContracts[benchmark]
    hack = benchmark2hack[benchmark]
    # categories given by the classifier
    # -1 represents not collected
    # 1: privileged txs
    # 2: simple txs to same protocols
    # 3: another famous DeFi protocol
    # 4: MEV
    # 5: User-assisted contract
    # 6: Hack
    categoryCounts = {-1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    # collect deployers of the target contracts
    # Whitelist Policy 1: txs initiated by deployers can be considered as benign
    deployers = set()
    for contract in targetContracts:
        deployer = ce.Contract2Deployer(contract)
        deployers.add(deployer)
    from labelTransactions.transactionLabeling import knownPriviledgedTxOrigin
    if benchmark in knownPriviledgedTxOrigin:
        deployers = deployers.union(knownPriviledgedTxOrigin[benchmark])

    # iterate all tx in txList:
    txList = []
    filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/combined2.txt".format(benchmark)
    isPopular = False
    if "AAVE" in benchmark or "Lido" in benchmark or "Uniswap" in benchmark:
        filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract_study/{}/combined2.txt".format(benchmark)
        isPopular = True

    if benchmark not in ["DODO", "Opyn", "PickleFi", "Punk_1", "Harvest1_fUSDT", "Eminence", "CheeseBank_1", "RevestFi", \
                         "VisorFi", "BeanstalkFarms_interface", "ValueDeFi", "XCarnival", "Warp_interface", "UmbrellaNetwork", \
                         "IndexFi", "RariCapital1", "Yearn1_interface", "InverseFi", "bZx2", "CreamFi1_1", "RariCapital2_3", "CreamFi2_4", \
                         "AAVE2", "Lido2", "Uniswap2"]:
        filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/combined.txt".format(benchmark)


    with open (filePath, 'r') as f:
        for line in f:
            entries = line.split(" ")
            Tx = entries[0]
            # contracts = entries[1:]
            txList.append(Tx)

    if isPopular:
        txList = txList[-100000: ]

    cq = CrawlQuickNode()

    an = Analyzer()
    contractSelector2functions = {}
    for tx in txList:
        tx = tx.strip()
        block = cq.Tx2Block(tx)
        receipt = cq.Tx2Receipt(tx)
        to = receipt["to"]
        status = receipt["status"]
        if not isinstance(status, int):
            status = int(status, 16)
        if status == 0:
            categoryCounts[-1].append(tx)
            tx_category = -1
            continue
        if to is None:
            to = receipt["contractAddress"]
        if to is None:
            sys.exit("to is None")

        to = to.lower() if to is not None else None

        tx_category = None

        # Category -1: Reverted
        if tx in revertedTransactions:
            categoryCounts[-1].append(tx)
            tx_category = -1
            continue
        
        # Category 2: Simple Transactions, directly sent from one of the functions of router contracts
        if to in targetContracts or to.lower() in targetContracts:
            tx_category = 2

        # Category X: if we have classified the contract
        category = c.benchmark_contract2Category(benchmark, to)
        if category != None:
            if category.lower() == "hack":
                tx_category = 6
            else:
                tx_category = int(category)
        
        if tx_category == 2 and receipt["to"] != None:
            sig = ""
            if receipt["input"] is not None:
                _selector = receipt["input"][0:10]
                _contract = receipt["to"]
                if _contract not in contractSelector2functions:
                    contractSelector2functions[_contract] = an.contract2funcSigMap(_contract)

                sig = None
                if _selector in contractSelector2functions[_contract]:
                    sig = contractSelector2functions[_contract][_selector]
                else:
                    sig = ""

            key = _contract + "-" + _selector + "-" + str(sig)
            
            if key not in simple_txs_to_simple_function:
                simple_txs_to_simple_function[key] = [ tx ]
            else:
                simple_txs_to_simple_function[key].append(tx)

        
        # Category 1: Transactions from deployers
        details = ce.Tx2Details(tx)
        if "from" in details and (details["from"] in deployers or details["from"].lower() in deployers):
            tx_category = 1
        if tx == hack:
            tx_category = 6

        jsonGzPath = SCRIPT_DIR + "/../constraintPackage/cache/functionAccess/{}/{}.json".format(benchmark,block)
        if not os.path.exists(jsonGzPath):
            if tx in knownTxsNotCollected:
                categoryCounts[-1].append(tx)
                continue
            else:
                # print("{} not exists".format(jsonGzPath))
                continue

        txResultMapping = readJson(jsonGzPath)
        functionAccess = []
        for txHash in txResultMapping:
            if txHash == tx:
                if len(txResultMapping[txHash]) == 0:
                    functionAccess = []
                else:
                    functionAccess = txResultMapping[txHash][0]
                break

        if len(functionAccess) == 0:
            tx_category = 0

        if tx_category == None:
            print(functionAccess)
            sys.exit("tx_category is None for tx " + tx + "  to is " + to)

        categoryCounts[tx_category].append(tx)

    print("Category Counts: ")
    print("Txs not collected or reverted (-1): ", len(categoryCounts[-1]))
    print("No Func Access (0): ", len(categoryCounts[0]))
    print("Deployer Transaction (1): ", len(categoryCounts[1]))
    print("Simple Txs to Same Protocol (2): ", len(categoryCounts[2]))
    print("Another Famous DeFi Protocol Call Flows (3): " , len(categoryCounts[3]))
    print("MEV (4): ", len(categoryCounts[4]))
    print("User-assisted Contract (5): ", len(categoryCounts[5]))
    print("Hack (6): ", len(categoryCounts[6]))

    print("all classified tx: ", sum(len(v) for v in categoryCounts.values()), "/", len(txList))

    return categoryCounts, contractSelector2functions



potential_reentrancy_guard = {}
potential_cache = {}

read_after_write_no_dependency_functions = {}
simple_txs_to_simple_function = {}
ERC20Functions = []

contract2invGas = {}
contractFunc2InstrumentationGas = {}

totalGas = 0
totalGasWithGuard = 0

def readAndAnalyze(categoryCounts, contractSelector2functions, benchmark):
    global contract2invGas
    contract2invGas.clear()
    global contractFunc2InstrumentationGas
    contractFunc2InstrumentationGas.clear()

    global totalGas
    global totalGasWithGuard
    totalGas = 0
    totalGasWithGuard = 0

    targetContracts = benchmark2targetContracts[benchmark]

    # iterate all tx in txList:
    txList = []
    filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/combined2.txt".format(benchmark)
    isPopular = False
    if "AAVE" in benchmark or "Lido" in benchmark or "Uniswap" in benchmark:
        filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract_study/{}/combined2.txt".format(benchmark)
        isPopular = True

    if benchmark not in ["DODO", "Opyn", "PickleFi", "Punk_1", "Harvest1_fUSDT", "Eminence", "CheeseBank_1", "RevestFi", \
                         "VisorFi", "BeanstalkFarms_interface", "ValueDeFi", "XCarnival", "Warp_interface", "UmbrellaNetwork", \
                         "IndexFi", "RariCapital1", "Yearn1_interface", "InverseFi", "bZx2", "CreamFi1_1", "RariCapital2_3", "CreamFi2_4", \
                         "AAVE2", "Lido2", "Uniswap2"]:
        filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/combined.txt".format(benchmark)

    with open (filePath, 'r') as f:
        for line in f:
            entries = line.split(" ")
            Tx = entries[0]
            # contracts = entries[1:]
            txList.append(Tx)

    if isPopular:
        txList = txList[-100000: ]
        
    ##########################################################################
    ################### Step 2: Call Flow Analysis
    ##########################################################################
    an = Analyzer()
    ce = CrawlEtherscan()
    for contract in targetContracts:
        funcSigMap2 = an.contract2funcSigMap(contract)
        contractSelector2functions[contract] = funcSigMap2

    callFlowMap = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    callFlowExampleMaps = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}

    approvedCallFlow = {
        # callflow: validBlock
    }

    for tx_category in categoryCounts:
        if tx_category == -1 or tx_category == 0:
            continue


        
        if tx_category == 6:
            print("hack")

        for tx in categoryCounts[tx_category]:
            # if tx == "0xe3f062768a42da6954d144b63c424bd9dcebcd3c4ca06532b94c1d50275c6b4d":
            #     print("now is the time:", tx)

            receipt = ce.Tx2Receipt(tx)
            block = receipt["blockNumber"]
            if isinstance(block, str):  # it might be a hex string
                block = int(block, 16) # convert hex to int

            gasUsed = receipt["gasUsed"]
            
            if tx_category != 6:
                totalGas += gasUsed
                totalGasWithGuard += gasUsed

            if tx_category == 2:
                totalGasWithGuard += gasConsumptionGuard["EOA"]
                # continue            

            if tx_category == 1:
                receipt = ce.Tx2Receipt(tx)
                gasUsed = receipt["gasUsed"]
                totalGas += gasUsed
                totalGasWithGuard += gasUsed
                totalGasWithGuard += gasConsumptionGuard["checkAdmin"]
                


            jsonGzPath = SCRIPT_DIR + "/../constraintPackage/cache/functionAccess/{}/{}.json".format(benchmark,block)
            if not os.path.exists(jsonGzPath):
                if tx in knownTxsNotCollected:
                    categoryCounts[-1].append(tx)
                    continue
                else:
                    print("{} not exists".format(jsonGzPath))
                    continue

            txResultMapping = readJson(jsonGzPath)
            functionAccess = []
            for txHash in txResultMapping:
                if txHash == tx:
                    if len(txResultMapping[txHash]) == 0:
                        functionAccess = []
                    else:
                        functionAccess = txResultMapping[txHash][0]
                    break
            
            functionAccess2 = []

            hasOneReEntrancy = False
            # convert selector to function name
            for node in functionAccess:
                contract = node[0]
                selector = node[1]

                if len(node) == 2:
                    sys.exit("len(node) == 2")

                funcName = selector
                isReadOnly = False
                isRuntimeReadOnly = False
                isRestoreOnExit = False
                extraEnterExits = 0

                if funcName.startswith("0x"):
                    if contract in complementary and selector in complementary[contract] and len(complementary[contract][selector]) == 3:
                        node[1] = complementary[contract][selector][0] + "-" + selector
                        funcName = complementary[contract][selector][0]
                        key = [contract, funcName, selector]

                    elif contract in contractSelector2functions and selector not in contractSelector2functions[contract] and contract in complementary and selector not in complementary[contract]:
                        node[1] = selector
                        funcName = selector
                        key = [contract, funcName, selector]
                        complementary_functions_readOnlySideEffect.append(key)

                        if pruneRuntimeReadOnly:
                            isRuntimeReadOnly = True
                            # check sstore
                            for address in node[6]:
                                # delete re-entrancy sload and sstore from node[6]
                                temp = []
                                for ii in range(len(node[6][address])):
                                    opcode = node[6][address][ii][0]
                                    slot = str(node[6][address][ii][1])
                                    value = node[6][address][ii][2]
                                    if address in reEntrancyGuard and slot in reEntrancyGuard[address]:
                                        continue
                                    else:
                                        temp.append(node[6][address][ii])
                                node[6][address] = temp
                                    
                                for ii in range(len(node[6][address])):
                                    opcode = node[6][address][ii][0]
                                    slot = str(node[6][address][ii][1])
                                    value = node[6][address][ii][2]

                                    isRuntimeReadOnly = False

 

                    elif contract in contractSelector2functions and selector not in contractSelector2functions[contract] and contract in complementary and selector not in complementary[contract]:
                        node[1] = selector
                        funcName = selector
                        # these functions are not that important, as they 
                        # are not the first function called, instead, they are internal function calls
                        # key = [contract, funcName, selector]
                        # if key not in temp:
                        #     temp.append(key)
                        #     print("contract in contractSelector2functions and selector not in contractSelector2functions[contract]")
                        #     print("tx: ", tx)
                        #     print("contract: ", contract)
                        #     print("selector: ", selector
                    elif contract in contractSelector2functions and selector in contractSelector2functions[contract] and contract in complementary and selector in complementary[contract]:
                        node[1] = complementary[contract][selector][0] + "-" + selector
                        funcName = complementary[contract][selector][0]
                        if complementary[contract][selector][3]:
                            isReadOnly = True

                        if complementary[contract][selector][3] != contractSelector2functions[contract][selector][3]:
                            if  complementary[contract][selector][3] and not contractSelector2functions[contract][selector][3]:
                                # normal
                                key = [contract, funcName, selector, complementary[contract][selector][3]]
                                if key not in complementary_functions_nonReadOnly2ReadOnly:
                                    complementary_functions_nonReadOnly2ReadOnly.append(key)
                            else:
                                sys.exit("complementary[contract][selector][3] != contractSelector2functions[contract][3]")
                    elif contract in contractSelector2functions and selector not in contractSelector2functions[contract] and contract in complementary and selector in complementary[contract]:
                        node[1] = complementary[contract][selector][0] + "-" + selector
                        funcName = complementary[contract][selector][0]
                        if complementary[contract][selector][3]:
                            isReadOnly = True                        
                        
                        key = [contract, funcName, selector, complementary[contract][selector][3]]
                        if str(key) not in complementary_functions_close_source and complementary[contract][selector][3]:
                            complementary_functions_close_source.append(str(key))
                    else:
                        if contract not in contractSelector2functions or selector not in contractSelector2functions[contract]:
                            # print("tx: ", tx)
                            # print("contract: ", contract)
                            # print("selector: ", selector)
                            isReadOnly = False
                        else:
                            node[1] = contractSelector2functions[contract][selector][0] + "-" + selector
                            funcName = contractSelector2functions[contract][selector][0]
                            if contractSelector2functions[contract][selector][3]:
                                isReadOnly = True

                elif funcName == "fallback":
                    selector = "0x552079dc"
                    
                    if contract in contractSelector2functions and selector in contractSelector2functions[contract]:
                        if contractSelector2functions[contract][selector][3]:
                            isReadOnly = True
                    elif contract in complementary and funcName in complementary[contract]:
                        if complementary[contract][funcName][3]:
                            isReadOnly = True

                        key = [contract, "fallback", "0x", complementary[contract][funcName][3]]
                        if complementary[contract][funcName][3] and str(key) not in complementary_functions_close_source:
                            complementary_functions_close_source.append(key)
                    else:
                        sys.exit("fallback not in contractSelector2functions[contract] and not in complementary[contract], contract = {}, tx = {}".format(contract, tx))
                    

                # Now measure the gas consumption of the function before checking runtime read-only, Restore-on-Exit and RAW
                # But apply Read-Only, 
                if tx_category != 1 and tx_category != 2 and tx_category != 6:
                    if not isReadOnly:
                        if node[5] != "delegatecall" and node[5] != "staticcall":
                            if pruneERC20 and selector in commonERC20Selectors:
                                pass
                            else:

                                if contract not in contractFunc2InstrumentationGas:
                                    contractFunc2InstrumentationGas[contract] = {}
                                if selector not in contractFunc2InstrumentationGas[contract]:
                                    contractFunc2InstrumentationGas[contract][selector] = 0

                                
                                if contract.lower() != benchmark2mostUsedContract[benchmark].lower():
                                    # totalGasWithGuard += gasConsumptionGuard["Instrument_prepost"]
                                    contractFunc2InstrumentationGas[contract][selector] += gasConsumptionGuard["Instrument_prepost"]
                                else:
                                    # totalGasWithGuard += gasConsumptionGuard["merge_instrument_prepost"]
                                    contractFunc2InstrumentationGas[contract][selector] += gasConsumptionGuard["merge_instrument_prepost"]
                                    

                                # print("now is the time:", tx)
                                # print("isReadOnly: ", isReadOnly, "contract: ", contract, "selector: ", selector, "funcName: ", funcName, "node[5]: ", node[5])
                            
                        for address in node[6]:
                            if address not in targetContracts:
                                continue
                            else:
                                for ii in range(len(node[6][address])):
                                    opcode = node[6][address][ii][0]

                                    if pruneERC20 and selector in commonERC20Selectors:
                                        pass
                                    else:
                                        if contract not in contractFunc2InstrumentationGas:
                                            contractFunc2InstrumentationGas[contract] = {}
                                        if selector not in contractFunc2InstrumentationGas[contract]:
                                            contractFunc2InstrumentationGas[contract][selector] = 0
                                        

                                        if opcode == "sload":
                                            if contract.lower() != benchmark2mostUsedContract[benchmark].lower():
                                                # totalGasWithGuard += gasConsumptionGuard["Instrument_sload"]
                                                contractFunc2InstrumentationGas[contract][selector] += gasConsumptionGuard["Instrument_sload"]
                                            else:
                                                # totalGasWithGuard += gasConsumptionGuard["merge_instrument_sload"]
                                                contractFunc2InstrumentationGas[contract][selector] += gasConsumptionGuard["merge_instrument_sload"]

                                            
                                        elif opcode == "sstore":
                                            if contract.lower() != benchmark2mostUsedContract[benchmark].lower():
                                                # totalGasWithGuard += gasConsumptionGuard["Instrument_sstore"]
                                                contractFunc2InstrumentationGas[contract][selector] += gasConsumptionGuard["Instrument_sstore"]
                                            else:
                                                # totalGasWithGuard += gasConsumptionGuard["merge_instrument_sstore"]
                                                contractFunc2InstrumentationGas[contract][selector] += gasConsumptionGuard["merge_instrument_sstore"]
                                                

                                            

                if pruneRuntimeReadOnly and isRuntimeReadOnly:
                    isReadOnly = True

                if pruneCache and not isReadOnly and node[1] != "constructor":
                    for address in node[6]:
                        set0x0 = []
                        for ii in range(len(node[6][address])):
                            opcode = node[6][address][ii][0]
                            slot = str(node[6][address][ii][1])
                            value = node[6][address][ii][2]
                            if opcode == "sstore" and value == "0x0":
                                set0x0.append(slot)
                            if opcode == "sstore" and value == "0x1":
                                if slot in set0x0 and address not in potential_reentrancy_guard:
                                    # print("Potential re-entrancy guard", key, "in", tx)
                                    potential_reentrancy_guard[address] = tx
                                    break


                    isAllAllMatches = True
                    numberOfSstores = 0
                    for address in node[6]:
                        # search for the obvious re-entrancy pattern
                        # contains two sstore, one set it to 0x0 and later set it to 0x1
                        firstSloads = {}
                        lastSstores = {}

                        for ii in range(len(node[6][address])):
                            opcode = node[6][address][ii][0]
                            slot = str(node[6][address][ii][1])
                            value = node[6][address][ii][2]
                            if opcode == "sload" and slot not in firstSloads and slot not in lastSstores:
                                firstSloads[slot] = value
                            elif opcode == "sstore":
                                lastSstores[slot] = value
                                numberOfSstores += 1
                            
                        # check whether all lastSstores are in firstSloads and be equal 
                        for slot in lastSstores:                                    
                            if slot not in firstSloads or firstSloads[slot] != lastSstores[slot]:
                                isAllAllMatches = False
                            elif slot in firstSloads and firstSloads[slot] == lastSstores[slot]:
                                # remove sstore from node[6]
                                temp = []
                                for ii in range(len(node[6][address])):
                                    opcode = node[6][address][ii][0]
                                    _slot = str(node[6][address][ii][1])
                                    value = node[6][address][ii][2]
                                    if opcode == "sstore" and _slot == slot:
                                        continue
                                    temp.append(node[6][address][ii])
                                node[6][address] = temp

                    if isAllAllMatches:
                        if numberOfSstores > 1 and contract not in potential_cache:
                            potential_cache[contract] = lastSstores.keys()
                        isRestoreOnExit = True
                        isReadOnly = True



                # prune 1: discard the read-only functions
                if not isReadOnly:
                    if not pruneERC20:
                        functionAccess2.append(node)
                    else:
                        if funcName not in commonERC20Functions:
                            functionAccess2.append(node)
                        else:
                            contract = node[0]
                            funName = node[1] + "-" + selector
                            key = [contract, funName]
                            if key not in ERC20Functions:
                                ERC20Functions.append(key)
                elif ( (pruneRuntimeReadOnly and isRuntimeReadOnly) or (pruneCache and isRestoreOnExit) ) and (tx_category != 1 and tx_category != 2 and tx_category != 6):
                    extraEnterExits += 1
                    if contract not in contract2invGas:
                        contract2invGas[contract] = 0

                    # if contract == "0x7d8bb0dcfb4f20115883050f45b517459735181b":
                    #     print("now is the time:", tx)

                    contract2invGas[contract] += gasConsumptionGuard["ValidatePre"] + gasConsumptionGuard["ValidatePost"]

                    if contract.lower() == benchmark2mostUsedContract[benchmark].lower():
                        # totalGasWithGuard -= (gasConsumptionGuard["ValidatePre"] + gasConsumptionGuard["ValidatePost"])
                        contract2invGas[contract] -= (gasConsumptionGuard["ValidatePre"] + gasConsumptionGuard["ValidatePost"])

                    

            functionAccess = copy.deepcopy(functionAccess2)
            
            len1 = len(staticcall_functions)
            results, resultStorages, hasOneReEntrancy = sort_callnodes(functionAccess, targetContracts, tx_category, extraEnterExits, benchmark)
            len2 = len(staticcall_functions)

            if pruneRuntimeReadOnly:
                # remove results that only read but never write
                indexes2Remove = []
                for i in range(len(resultStorages)):
                    resultStorage = resultStorages[i]
                    isWrite = False
                    for contract in resultStorage:
                        for storageAccess in resultStorage[contract]:
                            if storageAccess[0] == "sstore":
                                isWrite = True
                                break
                    if not isWrite:
                        indexes2Remove.append(i)
                
                results = [results[i] for i in range(len(results)) if i not in indexes2Remove]
                resultStorages = [resultStorages[i] for i in range(len(resultStorages)) if i not in indexes2Remove]
            
            

            # if len2 != len1:
            #     print("staticcall_functions is updated at tx ", tx)
            
            if len(results) != len(resultStorages):
                sys.exit("results and resultStorages have different lengths")




            # ignore pruning for now
            if len(results) == 0:
                continue
            elif len(results) == 1 and (results[0].count("-start") == 1 and results[0].count("-end") == 1) :
                continue


            if len(results) == 1 and hasOneReEntrancy:
                # get the full name:
                # <0x051e-sellBase-start,0x051e-sellBase-end>
                contractStart = results[0].split("-")[0]
                contractStart = contractStart[2:]
                funcName = results[0].split("-")[1].split("-")[0]
                for contract, func, _, _, _, _, _ in functionAccess:
                    if contract.startswith(contractStart) and func.startswith( funcName ):
                        key = contract + "-" + func
                        if key not in simple_txs_to_simple_function:
                            simple_txs_to_simple_function[key] = [tx]
                        else:
                            simple_txs_to_simple_function[key].append(tx)
                        break

            # Prune Hard: Read-After-Write. 
            elif len(results) > 1:
                # 0x2e7d7e7a6eb157b98974c8687fbd848d0158d37edc1302ea08ee5ddb376befea 
                # is a special transaction which has a read-after-write 
                # dependency not on storage but on ether balance. 
                if pruneRAW:
                    # first we need to identify read and write operations
                    resultsStorageReads = []
                    resultsStorageWrites = []
                    for resultStorage in resultStorages:
                        resultsStorageReads.append({})
                        resultsStorageWrites.append({})
                        for contract in resultStorage:
                            if contract not in targetContracts:
                                continue
                            for storageAccess in resultStorage[contract]:
                                key = contract + "-" + str(storageAccess[1])
                                if storageAccess[0] == "sload":
                                    resultsStorageReads[-1][key] = 1
                                else:
                                    resultsStorageWrites[-1][key] = 1
                    rawTree = RAWTree(resultsStorageReads, resultsStorageWrites, results)
                    isReadAfterWriteOnce = False  # at least one action is reading some states that are written by previous actions
                    for i in range(1, len(results)):
                        currentStorageReads = resultsStorageReads[i]
                        for j in range(0, i):
                            previousStorageWrites = resultsStorageWrites[j]
                            for key in previousStorageWrites:
                                if key in currentStorageReads:
                                    isReadAfterWriteOnce = True
                                    break
                            if isReadAfterWriteOnce:
                                break
                        if isReadAfterWriteOnce:
                            break

                    if isReadAfterWriteOnce != rawTree.isReadAfterWriteOnce():
                        print("isReadAfterWriteOnce is not consistent")
                        rawTree.isReadAfterWriteOnce()
                        sys.exit("isReadAfterWriteOnce is not consistent")

                    if not isReadAfterWriteOnce and not hasOneReEntrancy:
                        if str(results) not in read_after_write_no_dependency_functions:
                            read_after_write_no_dependency_functions[str(results)] = [tx]
                        else:
                            read_after_write_no_dependency_functions[str(results)].append(tx)
                        continue
            
                


            callFlow = str(results)
            # if (tx_category == 4 or tx_category == 5 or tx_category == 6) and len(results) == 0:
            #     print("now is the time")
            # print("catgeory", tx_category, "tx:", tx) 
            # print(callFlow)


            if callFlow in approvedCallFlow and block >= approvedCallFlow[callFlow]:
                continue
                
            if callFlow not in callFlowMap[tx_category]:
                callFlowMap[tx_category][callFlow] = 1

                if pruneParametric2 is not None:
                    for index in range(1, len(results) + 1):
                        subCallFlow = str(results[0:index])
                        approvedCallFlow[subCallFlow] = block + pruneParametric2
                        # 267 is the average block time for 1 hour
                        # 6400 is the average block time for 24 hours
                        # 19200 is the average block time for 3 days
            else:
                callFlowMap[tx_category][callFlow] += 1
            
            if callFlow not in callFlowExampleMaps[tx_category]:
                receipt = ce.Tx2Receipt(tx)
                to = receipt["to"]
                callFlowExampleMaps[tx_category][callFlow] = (to, tx)




    # sort it based on invGas
    contract2invGas = {k: v for k, v in sorted(contract2invGas.items(), key=lambda item: item[1], reverse=True)}
    sum_temp = sum(contract2invGas.values())

    # sort it based on instrumentation for each selector for each contract
    contractFunc2InstrumentationGas = {k: v for k, v in sorted(contractFunc2InstrumentationGas.items(), key=lambda item: sum(item[1].values()), reverse=True)}
    for contract in contractFunc2InstrumentationGas:
        for selector in contractFunc2InstrumentationGas[contract]:
            invGas = contractFunc2InstrumentationGas[contract][selector]
    instrumentation_gas = sum([sum(v.values()) for v in contractFunc2InstrumentationGas.values()])
    totalGasWithGuard += sum_temp + instrumentation_gas
    if instrumentation_gas + totalGas + sum_temp > totalGasWithGuard:
        print("Instrumentation gas is larger than total gas with guard")
        print(tx)
        sys.exit("Instrumentation gas is larger than total gas with guard")



    falsePositives = 0
    falsePositivesAppproval = []



    sums = sum(callFlowMap[1].values())
    print(" == Deployer Transactions: ")
    Asorted = {k: v for k, v in sorted(callFlowMap[1].items(), key=lambda item: item[1], reverse=True)}

    for callFlow in Asorted:
        if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
            continue
        print(callFlow, Asorted[callFlow])
        print(callFlowExampleMaps[1][callFlow])


    sums = sum(callFlowMap[2].values())
    print(" == Simple Txs to Same Protocol: ")
    Asorted = {k: v for k, v in sorted(callFlowMap[2].items(), key=lambda item: item[1], reverse=True)}
    
    for callFlow in Asorted:
        if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
            continue
        print(callFlow, Asorted[callFlow])
        print(callFlowExampleMaps[2][callFlow])

    # allowedControlFlow = []
    # if pruneParametric:
    #     for callFlow in Asorted:
    #         allowedControlFlow.append(callFlow)

    sums = sum(callFlowMap[3].values())
    print(" == Another Famous DeFi Protocol Call Flows: ", "False Positives: ", sums, "respective FP Rate:", sums / ( len(txList) - len(categoryCounts[-1]) - len(categoryCounts[0]) ) * 100, "%")
    Asorted = {k: v for k, v in sorted(callFlowMap[3].items(), key=lambda item: item[1], reverse=True)}
    
    for callFlow in Asorted:
        if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
            continue
        print(callFlow, Asorted[callFlow])
        falsePositives += Asorted[callFlow]
        if callFlow not in falsePositivesAppproval:
            falsePositivesAppproval.append(callFlow)
        print(callFlowExampleMaps[3][callFlow])


    sums = sum(callFlowMap[4].values())
    print(" == MEV Call Flows: ", "False Positives: ", sums, "respective FP Rate:", sums / ( len(txList) - len(categoryCounts[-1]) - len(categoryCounts[0]) ) * 100, "%")
    Asorted = {k: v for k, v in sorted(callFlowMap[4].items(), key=lambda item: item[1], reverse=True)}
    
    for callFlow in Asorted:
        if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
            continue
        print(callFlow, Asorted[callFlow])
        falsePositives += Asorted[callFlow]
        if callFlow not in falsePositivesAppproval:
            falsePositivesAppproval.append(callFlow)
        print(callFlowExampleMaps[4][callFlow])

    sums = sum(callFlowMap[5].values())
    print(" == User-assisted Contract Call Flows: ", "False Positives: ", sums, "respective FP Rate:", sums / ( len(txList) - len(categoryCounts[-1]) - len(categoryCounts[0]) ) * 100, "%")
    Asorted = {k: v for k, v in sorted(callFlowMap[5].items(), key=lambda item: item[1], reverse=True)}
    
    for callFlow in Asorted:
        if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
            continue
        print(callFlow, Asorted[callFlow])
        falsePositives += Asorted[callFlow]
        if callFlow not in falsePositivesAppproval:
            falsePositivesAppproval.append(callFlow)
        print(callFlowExampleMaps[5][callFlow])


    # # merge 4, 5
    # temp = {}
    # for callFlow in callFlowMap[4]:
    #     if callFlow not in temp:
    #         temp[callFlow] = callFlowMap[4][callFlow]
    #     else:
    #         temp[callFlow] += callFlowMap[4][callFlow]

    # for callFlow in callFlowMap[5]:
    #     if callFlow not in temp:
    #         temp[callFlow] = callFlowMap[5][callFlow]
    #     else:
    #         temp[callFlow] += callFlowMap[5][callFlow]

    # Asorted = {k: v for k, v in sorted(temp.items(), key=lambda item: item[1], reverse=True)}
    # for callFlow in Asorted:
    #     if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
    #         continue
    #     print(callFlow, Asorted[callFlow])

    #     if callFlow != "[]":
    #         falsePositives += Asorted[callFlow]
    #         if callFlow not in falsePositivesAppproval:
    #             falsePositivesAppproval.append(callFlow)

    #     if callFlow in callFlowExampleMaps[4]:
    #         print(callFlowExampleMaps[4][callFlow])
    #     else:
    #         print(callFlowExampleMaps[5][callFlow])

    print(" == Hack Call Flows: ")
    for callFlow in callFlowMap[6]:
        if callFlow.count("-start") <= 1 and callFlow.count("-end") <= 1:
            continue
        print(callFlow, callFlowMap[6][callFlow])
        print(callFlowExampleMaps[6][callFlow])


    #     isHack = False
    #     if tx == hack:
    #         # print("now is the time")
    #         isHack = True
    #         pass
    
    print("False positives: ", falsePositives, " out of ", len(txList) - len(categoryCounts[-1]) - len(categoryCounts[0]))

    print("False positive ratio", falsePositives / ( len(txList) - len(categoryCounts[-1]) - len(categoryCounts[0]) ) * 100, "%")



    # no need anymore
    # print("False positive after user approval ", len(falsePositivesAppproval) / ( len(txList) - len(categoryCounts[-1]) - len(categoryCounts[0]) ) * 100, "%")

    if pruneERC20 and pruneRuntimeReadOnly and pruneCache and pruneRAW and pruneParametric2 is None:
        print("Total gas: ", totalGas)
        print("Total gas with guard: ", totalGasWithGuard)
        print("Total gas overhead: ", (totalGasWithGuard - totalGas) / totalGas * 100, "%")
        # sort it based on invGas
        contract2invGas = {k: v for k, v in sorted(contract2invGas.items(), key=lambda item: item[1], reverse=True)}
        print("Contract invGas: ")
        for contract in contract2invGas:
            print("Contract: ", contract, "invGas: ", contract2invGas[contract])
        sum_temp = sum(contract2invGas.values())

        # sort it based on instrumentation for each selector for each contract
        contractFunc2InstrumentationGas = {k: v for k, v in sorted(contractFunc2InstrumentationGas.items(), key=lambda item: sum(item[1].values()), reverse=True)}
        print("")
        print("Contract Func2InstrumentationGas: ")
        for contract in contractFunc2InstrumentationGas:
            print("Contract: ", contract)
            for selector in contractFunc2InstrumentationGas[contract]:
                invGas = contractFunc2InstrumentationGas[contract][selector]
                print("\tSelector: ", selector, "invGas: ", invGas)
        instrumentation_gas = sum([sum(v.values()) for v in contractFunc2InstrumentationGas.values()])

        print("Sum Gas:", instrumentation_gas)
        TotalGas = instrumentation_gas + totalGas
        print("Total Gas with Instrumentation: ", TotalGas)
        print("Total Gas with Instrumentation with Inv: ", TotalGas + sum_temp)





def executeOnce(listBenchmark, local_pruneERC20, local_pruneRuntimeReadOnly,  local_pruneCache,  local_pruneRAW, local_pruneParametric2):
    global pruneERC20
    pruneERC20 = local_pruneERC20
    global pruneRuntimeReadOnly 
    pruneRuntimeReadOnly = local_pruneRuntimeReadOnly
    global pruneCache
    pruneCache = local_pruneCache
    global pruneRAW
    pruneRAW = local_pruneRAW
    global pruneParametric2
    pruneParametric2 = local_pruneParametric2

    print("pruneERC20: ", local_pruneERC20)
    print("pruneRuntimeReadOnly: ", pruneRuntimeReadOnly)
    print("pruneCache: ", pruneCache)
    print("pruneRAW: ", pruneRAW)
    print("pruneParametric2: ", pruneParametric2)

    global reEntrancyName
    for benchmark in listBenchmark:

        if benchmark == "DODO":
            reEntrancyName = ["flashLoan", ]
        elif benchmark == "Opyn":
            reEntrancyName = ["borrow", "withdraw"]
        elif benchmark == "PickleFi":
            reEntrancyName = ["swapExactJarForJar", "execute"]
        elif benchmark == "Punk_1":
            reEntrancyName = []
        elif benchmark == "Harvest1_fUSDT":
            reEntrancyName = []
        elif benchmark == "Eminence":
            reEntrancyName = []
        elif benchmark == "CheeseBank_1":
            reEntrancyName = []
        elif benchmark == "RevestFi":
            reEntrancyName = ["mintAddressLock", ]
        elif benchmark == "VisorFi":
            reEntrancyName = ["deposit", ]
        elif benchmark == "BeanstalkFarms_interface":
            reEntrancyName = []
        elif benchmark == "ValueDeFi":
            reEntrancyName = ["executeTransaction", ]
        elif benchmark == "XCarnival":
            reEntrancyName = ["upgradeTo", "upgradeToAndCall", ]
        elif benchmark == "Warp_interface":
            reEntrancyName = []
        # elif benchmark == "UmbrellaNetwork":
        #     reEntrancyName = []
        elif benchmark == "IndexFi":
            reEntrancyName = []
        elif benchmark == "RariCapital1":
            reEntrancyName = []
        elif benchmark == "Yearn1_interface":
            reEntrancyName = []
        elif benchmark == "InverseFi":
            reEntrancyName = []
        elif benchmark == "bZx2":
            reEntrancyName = ["flashBorrowToken"]
        elif benchmark == "CreamFi1_1":
            reEntrancyName = ["borrow"]
        elif benchmark == "RariCapital2_3":
            reEntrancyName = ["borrow"]
        elif benchmark == "CreamFi2_4":
            reEntrancyName = ["borrow"]

        elif benchmark == "DoughFina":
            reEntrancyName = ["flashloanReq", "executeOperation"]
        elif benchmark == "Bedrock_DeFi":
            reEntrancyName = []
        elif benchmark == "OnyxDAO":
            reEntrancyName = []
        elif benchmark == "BlueberryProtocol":
            reEntrancyName = []
        elif benchmark == "PrismaFi":
            reEntrancyName = []
        elif benchmark == "PikeFinance":
            reEntrancyName = []
        elif benchmark == "GFOX":
            reEntrancyName = []
        elif benchmark == "UwULend":
            reEntrancyName = []

        elif benchmark == "AAVE2":
            reEntrancyName = []
        elif benchmark == "Lido2":
            reEntrancyName = ["_upgradeToAndCallSecure", ]
        elif benchmark == "Uniswap2":
            reEntrancyName = ["exactOutput", "exactOutputSingle", ]

        elif benchmark == "Audius":
            reEntrancyName = []
        elif benchmark == "OmniNFT":
            reEntrancyName = ["liquidationERC721", "withdrawERC721", "burn"]
        elif benchmark == "MetaSwap":
            reEntrancyName = []
        elif benchmark == "Auctus":
            reEntrancyName = []
        elif benchmark == "BaconProtocol":
            reEntrancyName = ["lend"]
        elif benchmark == "MonoXFi":
            reEntrancyName = []
        elif benchmark == "NowSwap":
            reEntrancyName = []
        elif benchmark == "PopsicleFi":
            reEntrancyName = []

        print("\n\n\n\nbenchmark: ", benchmark)
        print("reEntrancyName: ", reEntrancyName)

        categoryCounts, contractSelector2functions = classify(benchmark)
        readAndAnalyze(categoryCounts, contractSelector2functions, benchmark)



        

if __name__ == "__main__":
    import argparse
    # read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pruneERC20", action='store_true', help="prune common ERC20 functions")
    parser.add_argument("--pruneRuntimeReadOnly", action='store_true', help="prune runtime read-only functions")
    parser.add_argument("--pruneCache", action='store_true', help="prune cache")
    parser.add_argument("--pruneRAW", action='store_true', help="prune RAW dependency")
    parser.add_argument("--pruneParametric2", type=int, help="parametric with user assistance, expects an integer value")

    args = parser.parse_args()

    # pruneCache = True


    # study
    pruneReadOnly = True
    # pruneERC20 = True
    pruneTrivialControlFlow = True
    
    # new rules
    pruneERC20 = True
    pruneRuntimeReadOnly = True
    pruneCache = True
    pruneRAW = True
    pruneParametric2 = None
                        # 267 is the average block time for 1 hour
                        # 6400 is the average block time for 24 hours
                        # 19200 is the average block time for 3 days


    listBenchmark = [
        "DODO",  # Easy
        "Opyn",  # Easy
        "PickleFi",  # Easy
        "Punk_1",  # Easy
        "Harvest1_fUSDT", # Easy
        "Eminence", # Easy
        "CheeseBank_1", # Easy
        "RevestFi", # Easy
        "VisorFi", # Easy
        "BeanstalkFarms_interface", # Easy
        "ValueDeFi", # Easy
        "XCarnival", # Easy
        "Warp_interface", # Easy
        "IndexFi", # Medium
        "RariCapital1", # Medium
        "Yearn1_interface", # Medium
        "InverseFi", # Medium
        "bZx2", # a lot of routers on top of main functions # Hard
        "CreamFi1_1", # Hard
        "RariCapital2_3", # Hard
        "CreamFi2_4", # Hard

        "DoughFina",  # Easy
        "Bedrock_DeFi",  # 15.44 %
        "OnyxDAO", # Easy 0.01%
        "BlueberryProtocol", # Easy
        "PrismaFi", # Medium 1.2%
        "PikeFinance", # Easy
        "GFOX", # Easy
        "UwULend",

        "AAVE2", 
        "Lido2",
        "Uniswap2",

        # Major Revision
        "Audius",
        "OmniNFT",
        "MetaSwap",
        "Auctus",
        "BaconProtocol",
        "MonoXFi",
        "NowSwap",
        "PopsicleFi",

        "SphereX"
    ]

    # executeOnce(listBenchmark, True, True, True, True, None)
    executeOnce(listBenchmark, args.pruneERC20, args.pruneRuntimeReadOnly, args.pruneCache, args.pruneRAW, args.pruneParametric2)


    # for benchmark in listBenchmark:
    #     staticcall_functions = []
    #     complementary_functions_nonReadOnly2ReadOnly = []
    #     complementary_functions_close_source = []
    #     potential_reentrancy_guard = {}
    #     potential_cache = {}
    #     read_after_write_no_dependency_functions = {}
    #     ERC20Functions = []
    #     reEntrancyFunctions = []
    #     simple_txs_to_simple_function = {}
    #     print("\n\n\n\nbenchmark: ", benchmark)
    #     categoryCounts, contractSelector2functions = classify(benchmark)
    #     readAndAnalyze(categoryCounts, contractSelector2functions, benchmark)
    #     # print("staticcall_functions")
    #     # for key in staticcall_functions:
    #     #     print(key)    
    #     print("")
    #     print("complementary_functions_nonReadOnly2ReadOnly")
    #     for key in complementary_functions_nonReadOnly2ReadOnly:
    #         print(key)

    #     print("")
    #     print("complementary_functions_close_source")
    #     for key in complementary_functions_close_source:
    #         print(key)

    #     print("")
    #     print("potential_reentrancy_guard")
    #     for key in potential_reentrancy_guard:
    #         if key not in reEntrancyGuard:
    #             print(key)

    #     print("")
    #     print("potential_cache")
    #     for key in potential_cache:
    #         print(key, potential_cache[key])
    #     # print("")
    #     # print("read_after_write_no_dependency_functions")
    #     # for key in read_after_write_no_dependency_functions:
    #     #     print(key, len(read_after_write_no_dependency_functions[key]), read_after_write_no_dependency_functions[key])
        
    #     # print("")
    #     # print("ERC20Functions")
    #     # for key in ERC20Functions:
    #     #     print(key)

    #     print("")
    #     print("reEntrancyFunctions")
    #     for key in reEntrancyFunctions:
    #         print(key)

    #     # print("")
    #     # print("simple_txs_to_simple_function")
    #     # for key in simple_txs_to_simple_function:
    #     #     print(key, len(simple_txs_to_simple_function[key]), simple_txs_to_simple_function[key])



