import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from parserPackage.parser import *
from parserPackage.parserRunnerUtils import *
from constraintPackage.macros import benchmark2targetContracts

import pickle
import cProfile
import multiprocessing




def testHarvest1_fUSDT():
    p = VmtraceParserGlobal()
    # changeLoggingUpperBound(1000) 
    # hack = "0x0fc6d2ca064fc841bc9b1c1fad1fbb97bcea5c9a1b2b66ef837f1227e06519a6" # 11129500

    block = 11129474
    hackTx = "0x35f8d2f572fceaac9288e5d462117850ef2694786992a8c3f6d02612277b0877" # 11129474
    
    # block = 11113743
    # hackTx = "0x9323fc02580eb49481eddf4b6bf40a9236eff20dc81ee4bfde992e85fbdef4f3"

    # block = 10996107
    # hackTx = "0x1db08713129990704b88b43a4161ddb433a2c13a7e2cd28c9d9feb18c31969dc"

    targetContracts = benchmark2targetContracts["Harvest1_fUSDT"]
    lock = multiprocessing.Lock()
    analyzeOneTxGlobal("Harvest1_fUSDT", block, hackTx, lock, isDecode=True, decodeAddresses=targetContracts)

    

    # path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/Harvest1_fUSDT/Txs/{}.json.gz".format(hackTx)
    # trace = readCompressedJson(path)

    # metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)
    # print(metaTraceTree)

    
    pass


def testRevestFi():
    pass


def testYearn1():
    pass


def testBeanstalkFarms():
    pass


def testCreamFi1_1():

    hackTx = "0xc57f708386bf7a6c33d478dc24b45c567004770f407d458ac676a71074751054"

    lock = multiprocessing.Lock()
    # analyzeOneTxGlobal("CreamFi1_1", block, hackTx, lock)

    hackTx = "0x61c5501d8e7fadf5af26ba359cbfaddd58c9c416b0b037c11892a0a301833731"

    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("CreamFi1_1", hackTx)

    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()

    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)

    print(metaTraceTree)


    pass

def testEminence():

    hackTx = "0x42bc0ef33367e7b80563ba6172cbb6c7c75a4239a124b640edf055a281b7a240"

    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("Eminence", hackTx)

    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()

    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)

    print(metaTraceTree)

    pass

def testOpyn():

    hackTx = "0x82a91acf660d3f19b593490041fa9763597fe400f552e447caa63cf3a980c261"

    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("Opyn", hackTx)

    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()

    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)

    print(metaTraceTree)


    pass


def testCheeseBank_1():
    hackTx = "0x4784f5f8e111544c74313c5fc58fabe6786d9e12373705545ed22cc0de60321e"

    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("CheeseBank_1", hackTx)

    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()

    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)

    print(metaTraceTree)
    pass


def testPunk_1():
    pass

def testPickleFi():
    pass


def testbZx2():
    hackTx = "0x217e2587df465ca6cf95a662d757494b18a005c2f652d874dab47ce6aa3593aa" # 11129474
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("bZx2", hackTx)
    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()
    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)
    print(metaTraceTree)
    # lock = multiprocessing.Lock()
    # analyzeOneTxGlobal("bZx2", block, hackTx, lock)
    pass

def testVisor():
    pass


def testDODO():

    block = 11984769
    hackTx = "0xe6b8d409f914661329f438e823cdfdea3abecc91a4ab30dbaeb8a17431817f1c" # 11129474

    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("DODO", hackTx)

    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()

    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)

    print(metaTraceTree)



def testIndexFi():

    hackTx = "0x3408e8e8145a0ccc2877df2e70f4dea1f0b090c0d7bedd7b2cd008eef7cd42d4" # 11129474

    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("IndexFi", hackTx)

    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()

    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)

    print(metaTraceTree)

    pass


def testRariCapital1():
    pass


def testPrismaFi():
    hackTx = ""
    hackTx = "0x25cd7731af04fd7440804f6fc50f794c2866ed154f00336c0230ad06db1ae7d5"
    # fe = fetcher()
    # fe.storeTraceCross("CreamFi1_1", hackTx, False)
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("PrismaFi", hackTx)
    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()
    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)
    print(metaTraceTree)


def testOnyxDAO():
    hackTx = "0xcc3248a860f7b18eb00ab023fcd84f6e41b0d3b8a748922bf6904115c791799c"
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("OnyxDAO", hackTx)
    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()
    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)
    print(metaTraceTree)


def testPrismaFi():
    hackTx = "0xe25bd58e06769e9d4b6ef423855d2df7cb5d09e7ca11ab13420c41a585378b9a"
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("PrismaFi", hackTx)
    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()
    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)
    print(metaTraceTree)


def testMonoXFi():
    hackTx = "0xf4dbe0dd1cc6700691550702460ce96c37b66fecc4534898c6d90f6dc0c4e2e6"
    path = SCRIPT_DIR + "/../Benchmarks_Traces/CrossContract/{}/Txs/{}.json.gz".format("MonoXFi", hackTx)
    trace = readCompressedJson(path)
    # changeLoggingUpperBound(1000)
    p = VmtraceParserGlobal()
    metaTraceTree = None
    metaTraceTree = p.parseLogsGlobal(None, hackTx, trace)
    print(metaTraceTree)



if __name__ == "__main__":
    # testIndexFi()
    # testCheeseBank_1()
    # testCreamFi1_1()
    # testOpyn()
    # testEminence()
    # testHarvest1_fUSDT()
    # testPrismaFi()
    # testOnyxDAO()
    testMonoXFi()

    # # run Profiler
    # # ranked by cum time
    # cProfile.run('testHarvest()', sort='cumtime')

