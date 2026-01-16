import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from Benchmarks_Traces.listBenchmark import *
from Benchmarks_Traces.filterTx import *
from Benchmarks_Traces.detectTrace import *
from parserPackage.locator import *
from parserPackage.parser import *
from parserPackage.parserRunnerUtils import *
from crawlPackage.crawlEtherscan import *
from crawlPackage.crawlQuicknode import *

import pickle
import gc
import multiprocessing






def main(benchmark):
    ce = CrawlEtherscan()
    cq = CrawlQuickNode()
    # # iterate Benchmarks_Traces/SLS/
    # txList = []
    # path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs".format(benchmark)

    # txHashes = os.listdir(path)
    # for txHash in txHashes:
    #     txHash = txHash.split(".")[0]
    #     txList.append(txHash)

    txList = []
    filePath = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/combined.txt".format(benchmark)
    with open (filePath, 'r') as f:
        for line in f:
            entries = line.split(" ")
            Tx = entries[0]
            Tx = Tx.strip()
            contracts = entries[1:]
            txList.append(Tx)

    # if benchmark == "CreamFi1_1":
    #     txList = ["0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec"]
    # elif benchmark == "IndexFi":
    #     txList = ["0x52a0541deff2373e1098881998b60af4175d75c410d67c86fcee850b23e61fc2"]
    # elif benchmark == "RevestFi":
    #     txList = ["0xca13006944e6eba2ccee0b2d96a131204491641014622ef2a3df3db3e6939062"]
    # elif benchmark == "Yearn1_interface":
    #     txList = ["0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec"]


    NumOfProcesses = 1
    processes = []
    processStats = []
    for _ in range(NumOfProcesses):
        processStats.append(0)
    ProcessesRunning = 0

    startTime = time.time()
    lockMap = {}


    isStart = False
    for ii in range(0, len(txList)):
        # 118404
        # 120000
        # if ii < 100000 or ii > 120000:
        #     continue

        # if ii < 53022:
        #     continue
        
        tx = txList[ii]
        tx = tx.strip()

        if tx == "0x79ca606d2b370965928021b671b0619f618f4b8869cceb9ec08f1be885e10ca6":
            print("now is the time")


        # if tx == "0x206f6d5dc93976f7576beb51372d720318f8f62c88fc2cce3bc623d5e4010fcc":
        #     print("now is the time")


        # if not tx.startswith("0x"):
        #     continue

        # if tx != "0x23eaeaeadaa81135d57577a4e335997488cdab772ed048cd4b8eca50324aa319" and not isStart:
        #     continue
        # else:
        #     isStart = True

        block = cq.Tx2Block(tx)
        jsonGzPath = SCRIPT_DIR + "/../parserPackage/cache/{}/{}.json.gz".format(benchmark, block)
        txMapping = {}

        # # print(jsonGzPath, "read")   
        try:
            if os.path.exists(jsonGzPath):
                txMapping = readCompressedJson(jsonGzPath)
                # currentTxMapping[0] = block
                # currentTxMapping[1] = {}
                # currentTxMapping[1][block] = txMapping
        except Exception as e:
            print("ran out of input for tx: ", tx, "benchmark: ", benchmark)
            continue

        if tx in txMapping and txMapping[tx] is not None:
            # print("tx {} already analyzed".format(tx))
            continue
        # else:
        #     print("tx {} not analyzed".format(tx))
        #     continue

        if block not in lockMap:
            lock = multiprocessing.Lock()
            lockMap[block] = lock

        if ProcessesRunning < NumOfProcesses:
            print("working on tx: {}  block: {}".format(tx, block))
            p = multiprocessing.Process(target=analyzeOneTxGlobal, args=(benchmark, block, tx, lockMap[block] ))
            p.start()
            processes.append(p)
            processStats[ProcessesRunning] = [tx, ii, time.time()]
            ProcessesRunning += 1
            if ProcessesRunning == NumOfProcesses:
                print("From now on, all processes are running")
        else:
            # spinning wait
            ifbreak = False
            while True:
                for jj in range(NumOfProcesses):
                    if not processes[jj].is_alive():
                        processes[jj].join()
                        # print("Process {} finished for {}(progress: {}/{}), takes time {} s".format(jj, processStats[jj][0], processStats[jj][1], len(txList), time.time() - processStats[jj][2]))
                        # checkFileSize(logPath)
                        p = multiprocessing.Process(target=analyzeOneTxGlobal, args=(benchmark, block, tx, lockMap[block] ))
                        p.start()
                        processes[jj] = p
                        processStats[jj] = [tx, ii, time.time()]
                        ifbreak = True
                        break
                if ifbreak:
                    break
                # sleep 100 ms
                # time.sleep(1)
        
        print("now analyze {}/{} tx: {}  block: {}".format(ii+1,  len(txList), tx, block))
        gc.collect()
        
    endTime = time.time()
    print("time: {}".format(endTime - startTime))
    return




if __name__ == "__main__":
    benchmark = "Harvest1_fUSDT"
    # bZx2, CheeseBank_1, CreamFi1_1, DODO, Eminence, Harvest1_fUSDT, 
    # IndexFi, Opyn, PickleFi, Punk_1, RariCapital1, RevestFi, VisorFi
    # Yearn1_interface
    listBenchmark = [
        # "bZx2", # confirmed to be finish completely
        # "CheeseBank_1", # confirmed to be finish completely
        # "CreamFi1_1", # confirmed to be finish completely
        # "DODO", # confirmed to be finish completely
        # "Eminence", # confirmed to be finish completely
        # "Harvest1_fUSDT", # confirmed to be finish completely
        # "IndexFi",# confirmed to be finish completely
        # "Opyn", # confirmed to be finish completely
        # "PickleFi", # confirmed to be finish completely
        # "Punk_1", # confirmed to be finish completely
        # "RariCapital1", # confirmed to be finish completely
        # "RevestFi", # confirmed to be finish completely   has a very long transaction, give up
        # "VisorFi", # confirmed to be finish completely
        # "Yearn1_interface", # confirmed to be finish completely   has a very long transaction, give up

        # "BeanstalkFarms_interface", # newly added, need to fetch trace
        # "ValueDeFi",
        # "XCarnival",
        # "RariCapital2_3",
        # "Warp_interface",
        # "InverseFi",
        # "CreamFi2_4"

        # "UmbrellaNetwork",


        # "Bedrock_DeFi",
        # "DoughFina",
        # "OnyxDAO",
        # "UwULend",
        # "GFOX",
        # "PikeFinance",
        # "PrismaFi",
        # "BlueberryProtocol"


        # "Audius",
        # "OmniNFT",
        # "MetaSwap",
        # "Auctus",
        # "BaconProtocol",
        # "MonoXFi",
        # "NowSwap",
        # "PopsicleFi"


        "SphereX"
    ]

    for benchmark in listBenchmark:
        print("benchmark: ", benchmark)
        main(benchmark)


# DoughFina
# 0xf4ea87c3e33fc8dc5775c3b29ce209efefe913f0a64988c5e92f55da9b88271e Airdrop 1
# 0x9434d4dbb1b559ff541fceb9e8b3709762d38ee227195a7949118b0e00526418 Airdrop 2

