import sys
import os
import gzip

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
# print(SCRIPT_DIR)

from crawlPackage.crawl import Crawler
from fetchPackage.fetchTrace import fetcher
from utilsPackage.compressor import *
from benchmarkPackage.readFiles import *

import multiprocessing
import time
from eth_utils import to_checksum_address



def file2Txlist(fileName: str):
    txlist = []
    with open(fileName, 'r') as f:
        for line in f:
            Tx = line.strip()
            if Tx.startswith('0x') and len(Tx) == 66:
                txlist.append(Tx)
    return txlist


def checkFileSize(logPath: str, sizeLimit = 100):
    """Given a log path, check if the file size is larger than the size limit(MB)"""
    fileSize = os.path.getsize(logPath) / 1024 / 1024
    if fileSize >= sizeLimit * 1024 * 1024:
        print("=======================================")
        print("File size >= {}MB, please check !!!", sizeLimit)
        print("=======================================")
        return
    else:
        print("File size: {}MB".format(fileSize))
        pass


def getTxBlockIndexes(incident, contract):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    filePath = SCRIPT_DIR + '/CrossContract/{}/{}.txt'.format(incident, contract)
    print(filePath)
    if not os.path.exists(filePath):
        print("No such file: {}".format(filePath))
        return
    blockIndexes = []
    with open (filePath, 'r') as f:
        for line in f:
            if any(char.isalpha() for char in line):
                continue
            # line = 14465357 4
            # parse it to block and index
            entries = line.split(" ")
            block = int(entries[0])
            index = entries[1]
            # delete \n from index
            index = int(index.strip())
            if not isinstance(block, int) or not isinstance(index, int):
                print("Invalid block or index: {} {}".format(block, index))
                sys.exit(1)
            blockIndexes.append((block, index))
    return blockIndexes



def getTxBlockIndexes2(incident, contract):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    filePath = SCRIPT_DIR + '/CrossContract_study/{}/{}.txt'.format(incident, contract)
    print(filePath)
    if not os.path.exists(filePath):
        print("No such file: {}".format(filePath))
        return []
    blockIndexes = []
    with open (filePath, 'r') as f:
        for line in f:
            if any(char.isalpha() for char in line):
                continue
            # line = 14465357 4
            # parse it to block and index
            entries = line.split(" ")
            block = int(entries[0])
            index = entries[1]
            # delete \n from index
            index = int(index.strip())
            if not isinstance(block, int) or not isinstance(index, int):
                print("Invalid block or index: {} {}".format(block, index))
                sys.exit(1)
            blockIndexes.append((block, index))
    return blockIndexes





def getTxContracts(incident):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    filePath = SCRIPT_DIR + '/CrossContract/{}/combined.txt'.format(incident)
    print(filePath)
    if not os.path.exists(filePath):
        print("No such file: {}".format(filePath))
        return
    TxContracts = []
    # Txs = []
    with open (filePath, 'r') as f:
        for line in f:
            entries = line.split(" ")
            Tx = entries[0]
            contracts = entries[1:]
            for ii in range(len(contracts)):
                # remove \n from contracts[ii]
                contracts[ii] = contracts[ii].strip()
            TxContracts.append((Tx, contracts))
            # Txs.append(Tx)
    return TxContracts


contractsNotInHack = ["0xb387e90367f1e621e656900ed2a762dc7d71da8c", "0xd77c2ab1cd0faa4b79e16a0e7472cb222a9ee175", "0xe4ffd682380c571a6a07dd8f20b402412e02830e"]

    



def rerankTransactions(contracts: list, incident: str, hack: str):
    # category must be CrossContract
    hack2Contract = Hack2Contract()

    # assertion 1: hack must be in hack2Contract
    if hack not in hack2Contract:
        print("No such hack: {}".format(hack))
        return
    
    # assertion 2: contracts must be in hack2Contract[hack]
    trace2invContract2Txs = {}
    for category, interface, implementation, benchmark in hack2Contract[hack]:
        if interface.lower() not in contracts and \
                interface.lower() != "0xddd7df28b1fb668b77860b473af819b03db61101" and \
                    interface.lower() != "0x5417da20ac8157dd5c07230cfc2b226fdcfc5663":
            print(incident)
            print("No such contract: {}".format(interface))
            sys.exit(1)
        trainingSet = benchmark['trainingSet']
        testingSet = benchmark['testingSet']
        trace2invContract2Txs[interface] = trainingSet + testingSet
    
    # assertion 3: TxHistory of interface contract must be equal to Trace2Inv
        # ignored because Trace2Inv ignores some transactions like create
    # list all files under CrossContract/{incident} folder
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    folderPath = SCRIPT_DIR + '/CrossContract/{}'.format(incident)
    if not os.path.exists(folderPath):
        print("No such folder: {}".format(folderPath))
        sys.exit(1)
    
    combinedBlockIndexes = []
    contract2BlockIndexes = {}
    for contract in contracts:
        blockIndexes = getTxBlockIndexes(incident, contract)
        contract2BlockIndexes[contract] = blockIndexes
        combinedBlockIndexes += blockIndexes
    # eliminate duplicates
    combinedBlockIndexes = list(set(combinedBlockIndexes))
    # sort combinedBlockIndexes by block number and then by index
    combinedBlockIndexes.sort(key=lambda x: (x[0], x[1]))
    print("In total, {} txs".format(len(combinedBlockIndexes)))
    # print(combinedBlockIndexes)
    crawler = Crawler()
    txHashes = crawler.blockIndexes2Txs(combinedBlockIndexes)

    if len(txHashes) != len(combinedBlockIndexes):
        print("Length of txHashes and combinedBlockIndexes must be equal")
        sys.exit(1)

    if hack not in txHashes:
        print("hackTx must be in txHashes but not found")
        sys.exit(1)
    # prune all txs after hack
    index = txHashes.index(hack)
    txHashes = txHashes[: index + 1]



    combinedFilePath = SCRIPT_DIR + '/CrossContract/{}/combined.txt'.format(incident)
    with open(combinedFilePath, 'w') as f:
        for ii in range(len(txHashes)):
            tx = txHashes[ii]
            line = tx
            block, index = combinedBlockIndexes[ii]
            for contract in contract2BlockIndexes:
                if (block, index) in contract2BlockIndexes[contract]:
                    line += " " + contract
            f.write(line + '\n')

        # for tx in txHashes:
        #     f.write(tx + '\n')
    print("Combined txs are written to {}".format(combinedFilePath))





def rerankTransactionsStudy(contracts: list, incident: str):
    # assertion 3: TxHistory of interface contract must be equal to Trace2Inv
        # ignored because Trace2Inv ignores some transactions like create
    # list all files under CrossContract/{incident} folder
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    folderPath = SCRIPT_DIR + '/CrossContract_study/{}'.format(incident)
    if not os.path.exists(folderPath):
        print("No such folder: {}".format(folderPath))
        sys.exit(1)
    
    combinedBlockIndexes = []
    contract2BlockIndexes = {}
    for contract in contracts:
        blockIndexes = getTxBlockIndexes2(incident, contract)
        blockIndexes2 = []
        for block, index in blockIndexes:
            if index < 1000:
                blockIndexes2.append((block, index))
        contract2BlockIndexes[contract] = blockIndexes2
        combinedBlockIndexes += blockIndexes2
    # eliminate duplicates
    combinedBlockIndexes = list(set(combinedBlockIndexes))
    # sort combinedBlockIndexes by block number and then by index
    combinedBlockIndexes.sort(key=lambda x: (x[0], x[1]))
    print("In total, {} txs".format(len(combinedBlockIndexes)))
    # print(combinedBlockIndexes)
    crawler = Crawler()
    combinedBlockIndexes = combinedBlockIndexes[-100000: ]
    # txHashes = crawler.blockIndexes2Txs(combinedBlockIndexes)

    txHashes = []
    for block, index in combinedBlockIndexes:
        try:
            tx = crawler.BlockIndex2Tx(block, index)
            txHashes.append(tx)
        except:
            print("Block {} index {} not found".format(block, index))

    if len(txHashes) != len(combinedBlockIndexes):
        print("Length of txHashes", len(txHashes))
        print("Length of combinedBlockIndexes", len(combinedBlockIndexes))
        # sys.exit(1)

    combinedFilePath = SCRIPT_DIR + '/CrossContract_study/{}/combined.txt'.format(incident)
    with open(combinedFilePath, 'w') as f:
        for ii in range(len(txHashes)):
            tx = txHashes[ii]
            line = tx
            block, index = combinedBlockIndexes[ii]
            for contract in contract2BlockIndexes:
                if (block, index) in contract2BlockIndexes[contract]:
                    line += " " + contract
            f.write(line + '\n')

        # for tx in txHashes:
        #     f.write(tx + '\n')
    print("Combined txs are written to {}".format(combinedFilePath))



def rerankTransactionsStudy_SphereX(contracts: list):
    # assertion 3: TxHistory of interface contract must be equal to Trace2Inv
        # ignored because Trace2Inv ignores some transactions like create
    # Locate study folder relative to this script
    SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    folder_path: str = os.path.join(SCRIPT_DIR, "CrossContract_study", "SphereX")

    if not os.path.exists(folder_path):
        sys.exit(f"[ERROR] Folder not found: {folder_path}")

    # (block, index, tx_hash) for every hash we encounter
    tx_records: List[Tuple[int, int, str]] = []
    seen: set[str] = set()

    crawler = Crawler()
    # Walk all *.txt files
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".txt"):
            continue

        file_path = os.path.join(folder_path, file_name)
        print(f"[INFO] Processing {file_path}")

        with open(file_path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line.startswith("0x"):
                    # ignore comments / empty lines
                    continue
                if line in seen:
                    # skip duplicates so the final combined.txt has unique hashes
                    continue
                block = crawler.Tx2Block(line)
                index = crawler.Tx2BlockIndex(line)
                if block is None or index is None:
                    sys.exit(f"[ERROR] Could not find (block, index) for {line}")

                tx_records.append((block, index, line))
                seen.add(line)

    if not tx_records:
        print("[WARN] No transactions found – nothing to write.")
        return

    # Sort: older first = lower block number; within the block, lower index first
    tx_records.sort(key=lambda rec: (rec[0], rec[1]))

    combined_path = os.path.join(folder_path, "combined.txt")
    with open(combined_path, "w", encoding="utf-8") as out_fh:
        for _, _, tx_hash in tx_records:
            out_fh.write(tx_hash + " \n")

    print(f"[SUCCESS] Wrote {len(tx_records)} ordered txs to {combined_path}")








def rerankTransactionsNew(contracts: list, incident: str, hack: str):


    # list all files under CrossContract/{incident} folder
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    folderPath = SCRIPT_DIR + '/CrossContract/{}'.format(incident)
    if not os.path.exists(folderPath):
        print("No such folder: {}".format(folderPath))
        sys.exit(1)
    
    combinedBlockIndexes = []
    contract2BlockIndexes = {}
    for contract in contracts:
        blockIndexes = getTxBlockIndexes(incident, contract)
        contract2BlockIndexes[contract] = blockIndexes
        combinedBlockIndexes += blockIndexes
    # eliminate duplicates
    combinedBlockIndexes = list(set(combinedBlockIndexes))
    # sort combinedBlockIndexes by block number and then by index
    combinedBlockIndexes.sort(key=lambda x: (x[0], x[1]))
    print("In total, {} txs".format(len(combinedBlockIndexes)))
    # print(combinedBlockIndexes)
    crawler = Crawler()
    txHashes = crawler.blockIndexes2Txs(combinedBlockIndexes)

    if len(txHashes) != len(combinedBlockIndexes):
        print("Length of txHashes and combinedBlockIndexes must be equal")
        sys.exit(1)

    if hack not in txHashes:
        print("hackTx must be in txHashes but not found")
        sys.exit(1)
    # prune all txs after hack
    index = txHashes.index(hack)
    txHashes = txHashes[: index + 1]


    combinedFilePath = SCRIPT_DIR + '/CrossContract/{}/combined.txt'.format(incident)
    with open(combinedFilePath, 'w') as f:
        for ii in range(len(txHashes)):
            tx = txHashes[ii]
            line = tx
            block, index = combinedBlockIndexes[ii]
            for contract in contract2BlockIndexes:
                if (block, index) in contract2BlockIndexes[contract]:
                    line += " " + contract
            f.write(line + '\n')

        # for tx in txHashes:
        #     f.write(tx + '\n')
    print("Combined txs are written to {}".format(combinedFilePath))








# def to_checksum_address(address):
#     # Remove the '0x' prefix
#     address = address.lower().replace('0x', '')
#     # Hash the address using Keccak-256
#     address_hash = sha3.keccak_256(address.encode('utf-8')).hexdigest()
#     checksum_address = '0x'
#     for i in range(len(address)):
#         # If the ith character in the hash is 8 or higher, uppercase the corresponding address character
#         if int(address_hash[i], 16) >= 8:
#             checksum_address += address[i].upper()
#         else:
#             checksum_address += address[i]
#     return checksum_address



def getStatsMoveFilesCache(incident: str, contracts: str, hack: str):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    combinedFilePath = SCRIPT_DIR + '/CrossContract/{}/combined.txt'.format(incident)
    if not os.path.exists(combinedFilePath):
        print("No such file: {}".format(combinedFilePath))
        sys.exit(1)
    
    TxContracts = getTxContracts(incident)

    # if tx collected in Trace2Inv, then just copy and paste
    hack2Contract = Hack2Contract()

    # assertion 2: contracts must be in hack2Contract[hack]
    trace2invContract2Txs = {}
    for category, interface, implementation, benchmark in hack2Contract[hack]:
        if interface.lower() not in contracts and \
                interface.lower() != "0xddd7df28b1fb668b77860b473af819b03db61101" and \
                    interface.lower() != "0x5417da20ac8157dd5c07230cfc2b226fdcfc5663":
            print("No such contract: {}".format(interface))
            sys.exit(1)
        trainingSet = benchmark['trainingSet']
        testingSet = benchmark['testingSet']
        trace2invContract2Txs[interface.lower()] = (category, trainingSet + testingSet)
    
    # check how many transactions to collect
    # check if contract collected before in Trace2Inv, if yes, just copy and paste
    countCollected = 0
    countToCopy = 0
    countToCollect = 0
    Txs2Collect = []
    for tx, contracts in TxContracts:
        isCollect = False
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        newLogPath = SCRIPT_DIR + '/CrossContract/{}/Txs/{}.json.gz'.format(incident, tx)
        if os.path.exists(newLogPath) and os.path.getsize(newLogPath) > 0:
            countCollected += 1
            isCollect = True
            continue
        for contract in contracts:
            if contract.lower() in trace2invContract2Txs:
                countToCopy += 1
                logPath = SCRIPT_DIR + '/{}/Txs/{}/{}.json.gz'.format(category, contract, tx)
                if os.path.exists(logPath) and os.path.getsize(logPath) > 0:
                    print("cp {} {}".format(logPath, newLogPath))
                    os.system("cp {} {}".format(logPath, newLogPath))
                    countCollected += 1
                    isCollect = True
                    break
                anotherLogPath = SCRIPT_DIR + '/{}/Txs/{}/{}.json.gz'.format(category, to_checksum_address(contract), tx)
                if os.path.exists(anotherLogPath) and os.path.getsize(anotherLogPath) > 0:
                    print("cp {} {}".format(anotherLogPath, newLogPath))
                    os.system("cp {} {}".format(anotherLogPath, newLogPath))
                    countCollected += 1
                    isCollect = True
                    break
                print("{} should be collected in trace2inv but not found".format(tx))
                print("\tpossible causes: 1. trace too long. ")

        if isCollect:
            continue
        countToCollect += 1
        Txs2Collect.append(tx)

    print("Collected: {}/{}".format(countCollected, len(TxContracts)))
    print("To copy: {}/{}".format(countToCopy, len(TxContracts)))
    print("To collect: {}/{}".format(countToCollect, len(TxContracts)))

    # store Txs2Collect to a temp file
    path = SCRIPT_DIR + '/CrossContract/{}/Txs2Collect.txt'.format(incident)
    with open(path, 'w') as f: 
        for tx in Txs2Collect:
            f.write(tx + '\n')




def FetchTxs(incident: str):
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    # read Txs2Collect from temp file
    path = SCRIPT_DIR + '/CrossContract/{}/combined.txt'.format(incident)
    Txs2Collect = []

    with open(path, 'r') as f:
        for line in f:
            tx = line.split(" ")[0]
            Txs2Collect.append(tx)

    fe = fetcher()
    NumOfProcesses = 2
    processes = []
    processStats = []
    # An entry in processStats is a list of [Tx, Index, start time]
    for _ in range(NumOfProcesses):
        processStats.append(0)
    ProcessesRunning = 0
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    for ii, tx in enumerate(Txs2Collect):
        tx = tx.strip()
        if tx == "0x52a0541deff2373e1098881998b60af4175d75c410d67c86fcee850b23e61fc2" or \
            tx == "0xca13006944e6eba2ccee0b2d96a131204491641014622ef2a3df3db3e6939062" or \
            tx == "0xc8d138a6190459db20542a6ddec692cbf176c9825bdccd79f06d65c9c3509a86" or \
            tx == "0xdfe08f532df2cc89707a65400e65edc9b9d108de02875b8043f845915ab884fe" or \
            tx == "0x43921dc3d070263678d84abb262d0eedb06d38fed840d6308f228a03610c312d" or \
            tx == "0xc651aeeaea2a25cc530dbeaecded933572af070565be911e3b624097faecd2df" or \
            tx == "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec":
            # this tx trace is too big
            continue

        path = SCRIPT_DIR + '/CrossContract/{}/Txs/{}.json.gz'.format(incident, tx)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print("Trace exists for {}(progress: {}/{}) - incident {}".format(tx, ii + 1, len(Txs2Collect), incident))
            continue


        if ProcessesRunning < NumOfProcesses:
            p = multiprocessing.Process(target=fe.storeTraceCross, args=(incident, tx, False))
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
                        logPath = SCRIPT_DIR + '/CrossContract/{}/Txs/{}.json.gz'.format(incident, processStats[jj][0])
                        print("Process {} finished for {}(progress: {}/{}), takes time {} s - incident {}".format(jj, processStats[jj][0], processStats[jj][1], len(Txs2Collect), time.time() - processStats[jj][2], incident))
                        # checkFileSize(logPath)
                        p = multiprocessing.Process(target=fe.storeTraceCross, args=(incident, tx, False))
                        p.start()
                        processes[jj] = p
                        processStats[jj] = [tx, ii, time.time()]
                        ifbreak = True
                        time.sleep(0.05)
                        break
                if ifbreak:
                    break
                # sleep 100 ms
                time.sleep(0.1)




    


    



def categoryContract2File(category: str, contract: str):
    # start = time.time()
    path = SCRIPT_DIR + '/{}/Txs/{}'.format(category, contract)
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    filePath = SCRIPT_DIR + '/{}/{}.txt'.format(category, contract)

    # filePath = SCRIPT_DIR + "/../constraintPackage/ReFetchedTxs/{}.pickle".format(contract.lower())
    txList = file2Txlist(filePath)
    # txList = readList(filePath)[0]
    # if contract == "0x8407dc57739bcda7aa53ca6f12f82f9d51c2f21e":
    #     txList = txList[-100000:]

    fe = fetcher()

    NumOfProcesses = 16
    processes = []
    processStats = []
    # An entry in processStats is a list of [Tx, Index, start time]
    for _ in range(NumOfProcesses):
        processStats.append(0)

    ProcessesRunning = 0

    for ii in range(len(txList)):
        # if ii < len(txList) - 1:
        #     continue
        # if ii < 400:
        #     continue
        Tx = txList[ii]
        logPath = SCRIPT_DIR + '/{}/Txs/{}/{}.json.gz'.format(category, contract, Tx)

        # # if Tx != "0x7903e4d558c81c457f96c754fc8c23bc105c46b281a9ea80d15ab1d4945d4fc2":
        if os.path.exists(logPath) and os.path.getsize(logPath) > 0:
            print("Trace exists for {}(progress: {}/{})".format(Tx, ii + 1, len(txList)))
            continue

        if Tx == "0x52a0541deff2373e1098881998b60af4175d75c410d67c86fcee850b23e61fc2" or \
            Tx == "0xca13006944e6eba2ccee0b2d96a131204491641014622ef2a3df3db3e6939062" or \
            Tx == "0xc8d138a6190459db20542a6ddec692cbf176c9825bdccd79f06d65c9c3509a86" or \
            Tx == "0xdfe08f532df2cc89707a65400e65edc9b9d108de02875b8043f845915ab884fe" or \
            Tx == "0x43921dc3d070263678d84abb262d0eedb06d38fed840d6308f228a03610c312d" or \
            Tx == "0xc651aeeaea2a25cc530dbeaecded933572af070565be911e3b624097faecd2df" or \
            Tx == "0xed7efd5bf771ae1e115fb59b9f080c2f66d74bf3c9234a89acb0e91e48181aec":
            # this tx trace is too big
            continue

        if ProcessesRunning < NumOfProcesses:
            p = multiprocessing.Process(target=fe.storeTrace, args=(category, contract, Tx, False))
            p.start()
            processes.append(p)
            processStats[ProcessesRunning] = [Tx, ii, time.time()]
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
                        logPath = SCRIPT_DIR + '/{}/Txs/{}/{}.json.gz'.format(category, contract, processStats[jj][0])
                        print("Process {} finished for {}(progress: {}/{}), takes time {} s".format(jj, processStats[jj][0], processStats[jj][1], len(txList), time.time() - processStats[jj][2]))
                        # checkFileSize(logPath)
                        p = multiprocessing.Process(target=fe.storeTrace, args=(category, contract, Tx, False))
                        p.start()
                        processes[jj] = p
                        processStats[jj] = [Tx, ii, time.time()]
                        ifbreak = True
                        time.sleep(0.05)
                        break
                if ifbreak:
                    break
                # sleep 100 ms
                time.sleep(0.1)

        # print("Trace fetch started for {}(progress: {}/{})".format(Tx, ii, len(txList)))

    




    # temp = []
    # batchsize = 100 # Batch Size
    # for ii in range(len(txList)):
    #     if len(temp) == batchsize or ii == len(txList) - 1:

    #         # traces = fe.batch_getTrace(temp)
    #         # for jj in range(len(temp)):
    #         #     trace = traces[jj]
    #         #     tx = temp[jj]
    #         #     logPath = SCRIPT_DIR + '/{}/Txs/{}/{}.json.gz'.format(category, contract, tx)
    #         #     writeCompressedJson(logPath, trace)
    #         #     checkFileSize(logPath)
    #         fe.batch_storeTrace2(category=category, contract=contract, Txs=temp)   # 2 is faster
    #         temp = []
    #         print("Batch Fetching Done")
    #     Tx = txList[ii]
    #     logPath = SCRIPT_DIR + '/{}/Txs/{}/{}.json.gz'.format(category, contract, Tx)
    #     if os.path.exists(logPath) and os.path.getsize(logPath) > 0:
    #         print("Trace exists for {}(progress: {}/{})".format(Tx, ii, len(txList)))
    #         continue
    #     temp.append(Tx)
    #     print("Collecting trace for {}(progress: {}/{})".format(Tx[: 7], ii, len(txList)))
    # end = time.time()
    # print("=======================================")
    # print("Total time: {}s".format(end - start))
    # print("=======================================")


def main():
# # # After FSE submission:
# # category = 'CrossContract'
#     # getTxBlockIndexes("RevestFi", "0xa81bd16aa6f6b25e66965a2f842e9c806c0aa11f")

#     # Revest Finance
#     incident = "RevestFi"
#     hack = "0xe0b0c2672b760bef4e2851e91c69c8c0ad135c6987bbf1f43f5846d89e691428"
#     contracts = []
#     contracts.append("0xa81bd16aa6f6b25e66965a2f842e9c806c0aa11f")
#     contracts.append("0xe952bda8c06481506e4731c4f54ced2d4ab81659")
#     contracts.append("0x2320a28f52334d62622cc2eafa15de55f9987ed9")
#     contracts.append("0xd721a90dd7e010c8c5e022cc0100c55ac78e0fc4")
#     contracts.append("0x226124e83868812d3dae87eb3c5f28047e1070b7")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)

   
#     # Eminence
#     incident = "Eminence"
#     hack = "0x3503253131644dd9f52802d071de74e456570374d586ddd640159cf6fb9b8ad8"
#     contracts = []
#     contracts.append("0x16f6664c16bede5d70818654defef11769d40983")
#     contracts.append("0x5ade7ae8660293f2ebfcefaba91d141d72d221e8")
#     contracts.append("0xc08f38f43adb64d16fe9f9efcc2949d9eddec198")
#     contracts.append("0xb387e90367f1e621e656900ed2a762dc7d71da8c")
#     contracts.append("0xd77c2ab1cd0faa4b79e16a0e7472cb222a9ee175")
#     contracts.append("0xe4ffd682380c571a6a07dd8f20b402412e02830e")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)

#     # BeanstalkFarms_interface
#     incident = "BeanstalkFarms_interface"
#     hack = "0xcd314668aaa9bbfebaf1a0bd2b6553d01dd58899c508d4729fa7311dc5d33ad7"
#     contracts = []
#     contracts.append("0x23d231f37c8f5711468c8abbfbf1757d1f38fda2")
#     contracts.append("0x3a70dfa7d2262988064a2d051dd47521e43c9bdd")
#     contracts.append("0x448d330affa0ad31264c2e6a7b5d2bf579608065")
#     contracts.append("0xf480ee81a54e21be47aa02d0f9e29985bc7667c4")
#     contracts.append("0xdc59ac4fefa32293a95889dc396682858d52e5db")
#     contracts.append("0xd652c40fbb3f06d6b58cb9aa9cff063ee63d465d")
#     contracts.append("0xc1e088fc1323b20bcbee9bd1b9fc9546db5624c5")
#     contracts.append("0x33b63042865242739ba410ac32ab68723e6cf4b9")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # CreamFi1_1
#     incident = "CreamFi1_1"
#     hack = "0x0016745693d68d734faa408b94cdf2d6c95f511b50f47b03909dc599c1dd9ff6"
#     contracts = []
#     contracts.append("0xd06527d5e56a3495252a528c4987003b712860ee")
#     contracts.append("0x338eee1f7b89ce6272f302bdc4b952c13b221f1d")
#     contracts.append("0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258")
#     contracts.append("0x2db6c82ce72c8d7d770ba1b5f5ed0b6e075066d6")
#     contracts.append("0xbadac56c9aca307079e8b8fc699987aac89813ee")
#     contracts.append("0x812c0b2a2a0a74f6f6ed620fbd2b67fec7db2190")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)




#     # Yearn
#     incident = "Yearn1_interface"
#     hack = "0x59faab5a1911618064f1ffa1e4649d85c99cfd9f0d64dcebbc1af7d7630da98b"
#     contracts = []
#     contracts.append("0xf147b8125d2ef93fb6965db97d6746952a133934")
#     contracts.append("0xc59601f0cc49baa266891b7fc63d2d5fe097a79d")
#     contracts.append("0x9ca85572e6a3ebf24dedd195623f188735a5179f")
#     contracts.append("0xacd43e627e64355f1861cec6d3a6688b31a6f952")
#     contracts.append("0x9a3a03c614dc467acc3e81275468e033c98d960e")
#     contracts.append("0x9c211bfa6dc329c5e757a223fb72f5481d676dc1")
#     contracts.append("0x9e65ad11b299ca0abefc2799ddb6314ef2d91080")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)



#     # Opyn
#     incident = "Opyn"
#     hack = "0xa858463f30a08c6f3410ed456e59277fbe62ff14225754d2bb0b4f6a75fdc8ad"
#     contracts = []
#     contracts.append("0x951d51baefb72319d9fbe941e1615938d89abfe2")
#     contracts.append("0x82151ca501c81108d032c490e25f804787bef3b8")
#     contracts.append("0x7623a53cbc779dbf44b706a00d4adf1be7e358ec")
#     contracts.append("0xeb7e15b4e38cbee57a98204d05999c3230d36348")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)



#     # CheeseBank_1
#     incident = "CheeseBank_1"
#     hack = "0x600a869aa3a259158310a233b815ff67ca41eab8961a49918c2031297a02f1cc"
#     contracts = []
#     contracts.append("0x026c6ac0179d34e4488f40c52c1486355ce4e755")
#     contracts.append("0xb54acff1ff7c7de9b0e30ad6d58b941ed22bbb44")
#     contracts.append("0x7e4956688367fb28de3c0a62193f59b1526a00e7")
#     contracts.append("0xa04bdb1f11413a84d1f6c1d4d4fed0208f2e68bf")
#     contracts.append("0xde2289695220531dfcf481fe3554d1c9c3156ba3")
#     contracts.append("0xa80e737ded94e8d2483ec8d2e52892d9eb94cf1f")
#     contracts.append("0x833e440332caa07597a5116fbb6163f0e15f743d")
#     contracts.append("0x4c2a8a820940003cfe4a16294b239c8c55f29695")
#     contracts.append("0x7f26337348cbaffd3368ab1aad1d111711a0617d")
#     contracts.append("0x85191476022593a408c472455b57b8346756f144")
#     contracts.append("0x3c7274679ff9d090889ed8131218bdc871020391")
#     contracts.append("0x5e181bdde2fa8af7265cb3124735e9a13779c021")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)



#     # Punk_1
#     incident = "Punk_1"
#     hack = "0x597d11c05563611cb4ad4ed4c57ca53bbe3b7d3fefc37d1ef0724ad58904742b"
#     contracts = []
#     contracts.append("0x1f3b04c8c96a31c7920372ffa95371c80a4bfb0d")
#     contracts.append("0x3bc6aa2d25313ad794b2d67f83f21d341cc3f5fb")
#     contracts.append("0x929cb86046e421abf7e1e02de7836742654d49d6")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)



#     # PickleFi
#     incident = "PickleFi"
#     hack = "0xe72d4e7ba9b5af0cf2a8cfb1e30fd9f388df0ab3da79790be842bfbed11087b0"
#     contracts = []
#     contracts.append("0x6949bb624e8e8a90f87cd2058139fcd77d2f3f87")
#     contracts.append("0x6186e99d9cfb05e1fdf1b442178806e81da21dd8")
#     contracts.append("0xcd892a97951d46615484359355e3ed88131f829d")
#     contracts.append("0x6847259b2b3a4c17e7c43c54409810af48ba5210")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # bZx2
#     incident = "bZx2"
#     hack = "0x762881b07feb63c436dee38edd4ff1f7a74c33091e534af56c9f7d49b5ecac15"
#     contracts = []
#     contracts.append("0x1cf226e9413addaf22412a2e182f9c0de44af002")
#     contracts.append("0x8b3d70d628ebd30d4a2ea82db95ba2e906c71633")
#     contracts.append("0xaa6198fe597dfc331471ae7deba026fb299297fc")
#     contracts.append("0x77f973fcaf871459aa58cd81881ce453759281bc")
#     contracts.append("0x85ca13d8496b2d22d6518faeb524911e096dd7e0")
#     contracts.append("0x3756fa458880fa8fe53604101cf31c542ef22f6f")
#     contracts.append("0x7d8bb0dcfb4f20115883050f45b517459735181b")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)

#     # VisorFi
#     incident = "VisorFi"
#     hack = "0x69272d8c84d67d1da2f6425b339192fa472898dce936f24818fda415c1c1ff3f"
#     contracts = []
#     contracts.append("0x3a84ad5d16adbe566baa6b3dafe39db3d5e261e5")
#     contracts.append("0xf938424f7210f31df2aee3011291b658f872e91e")
#     contracts.append("0xc9f27a50f82571c1c8423a42970613b8dbda14ef")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # DODO
#     incident = "DODO"
#     hack = "0x395675b56370a9f5fe8b32badfa80043f5291443bd6c8273900476880fb5221e"
#     contracts = []
#     contracts.append("0x2bbd66fc4898242bdbd2583bbe1d76e8b8f71445")
#     contracts.append("0x051ebd717311350f1684f89335bed4abd083a2b6")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # IndexFi
#     incident = "IndexFi"
#     hack = "0x44aad3b853866468161735496a5d9cc961ce5aa872924c5d78673076b1cd95aa"
#     contracts = []
#     contracts.append("0xf00a38376c8668fc1f3cd3daeef42e0e44a7fcdb")
#     contracts.append("0x120c6956d292b800a835cb935c9dd326bdb4e011")
#     contracts.append("0x5bd628141c62a901e0a83e630ce5fafa95bbdee4")
#     contracts.append("0xffde4785e980a99fe10e6a87a67d243664b91b25")
#     contracts.append("0xfa5a44d3ba93d666bf29c8804a36e725ecac659a")
#     contracts.append("0xfa6de2697d59e88ed7fc4dfe5a33dac43565ea41")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # RariCapital1
#     incident = "RariCapital1"
#     hack = "0x4764dc6ff19a64fc1b0e57e735661f64d97bc1c44e026317be8765358d0a7392"
#     contracts = []
#     contracts.append("0x9c0caeb986c003417d21a7daaf30221d61fc1043")
#     contracts.append("0xcda4770d65b4211364cb870ad6be19e7ef1d65f4")
#     contracts.append("0xd6e194af3d9674b62d1b30ec676030c23961275e")
#     contracts.append("0xec260f5a7a729bb3d0c42d292de159b4cb1844a3")
#     contracts.append("0xed2cd60c0000a990a5ffaf0e7ddc70a37d7c623f")
#     contracts.append("0xa422890cbbe5eaa8f1c88590fbab7f319d7e24b6")
#     contracts.append("0xc7a89d73606379f108752bfe4795b69ab4abb94f")
#     contracts.append("0xb849daff8045fc295af2f6b4e27874914b5911c6")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # Harvest1_fUSDT
#     incident = "Harvest1_fUSDT"
#     hack = "0x0fc6d2ca064fc841bc9b1c1fad1fbb97bcea5c9a1b2b66ef837f1227e06519a6"
#     contracts = []
#     contracts.append("0x053c80ea73dc6941f518a68e2fc52ac45bde7c9c")
#     contracts.append("0xd8d6ab3d2094d3a0258f4193c5c85fadd44d589a")
#     contracts.append("0x1c47343ea7135c2ba3b2d24202ad960adafaa81c")
#     contracts.append("0xf2b223eb3d2b382ead8d85f3c1b7ef87c1d35f3a")
#     contracts.append("0x2427da81376a0c0a0c654089a951887242d67c92")
#     contracts.append("0x9b3be0cc5dd26fd0254088d03d8206792715588b")
#     contracts.append("0x222412af183bceadefd72e4cb1b71f1889953b1c")
#     contracts.append("0xc95cbe4ca30055c787cb784be99d6a8494d0d197")
#     contracts.append("0xd55ada00494d96ce1029c201425249f9dfd216cc")
#     contracts.append("0xfca4416d9def20ac5b6da8b8b322b6559770efbf")
#     contracts.append("0xf0358e8c3cd5fa238a29301d0bea3d63a17bedbe")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


    # # Umbrella Network
    # incident = "UmbrellaNetwork"
    # hack = "0x33479bcfbc792aa0f8103ab0d7a3784788b5b0e1467c81ffbed1b7682660b4fa"
    # contracts = []
    # contracts.append("0xb3fb1d01b07a706736ca175f827e4f56021b85de")
    # # rerankTransactions(contracts, incident, hack)
    # # getStatsMoveFilesCache(incident, contracts, hack)
    # FetchTxs(incident)




# def main2():

#     # ValueDeFi
#     incident = "ValueDeFi"
#     hack = "0x46a03488247425f845e444b9c10b52ba3c14927c687d38287c0faddc7471150a"
#     contracts = []
#     contracts.append("0x8c2f33b3a580baeb2a1f2d34bcc76e020a54338d")
#     contracts.append("0x55bf8304c78ba6fe47fd251f37d7beb485f86d26")
#     contracts.append("0x57cda125d0c7b146a8320614ccd6c55999d15bf2")
#     contracts.append("0xea48b3f50f3cf2216e34e2e868abc810b729f0e3")
#     contracts.append("0xb43f0707b2719a5b8ab905d253022c6073a63926")
#     contracts.append("0xba5d28f4ecee5586d616024c74e4d791e01adee7")
#     contracts.append("0x8764f2c305b79680cfcc3398a96aedea9260f7ff")
#     contracts.append("0x98595670e97aa2ec229f366806b37745ad6e92b5")
#     contracts.append("0x467e9f2caa9b7678ddc29b248cb9fb181907bf3e")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)




#     # XCarnival
#     incident = "XCarnival"
#     hack = "0x51cbfd46f21afb44da4fa971f220bd28a14530e1d5da5009cfbdfee012e57e35"
#     contracts = []
#     contracts.append("0x5e5186d21cbddc8765c4558dbda0bf20b90bf118")
#     contracts.append("0xb38707e31c813f832ef71c70731ed80b45b85b2d")
#     contracts.append("0xb7e2300e77d81336307e36ce68d6909e43f4d38a")
#     contracts.append("0xbd0e1bc09ae52072a9f5d3343b98643ae585e339")
#     contracts.append("0x222d7b700104c91a2ebbf689ff7b2a35f2541f98")
#     contracts.append("0xb14b3b9682990ccc16f52eb04146c3ceab01169a")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)




#     # RariCapital2_3
#     incident = "RariCapital2_3"
#     hack = "0xab486012f21be741c9e674ffda227e30518e8a1e37a5f1d58d0b0d41f6e76530"
#     contracts = []
#     contracts.append("0xb0602af43ca042550ca9da3c33ba3ac375d20df4")
#     contracts.append("0xe980efb504269ff53f7f4bc92a2bd1e31b43f632")
#     contracts.append("0x4ef29407a8dbca2f37b7107eab54d6f2a3f2ad60")
#     contracts.append("0xe102421a85d9c0e71c0ef1870dac658eb43e1493")
#     contracts.append("0xfea425f0baadf191546cf6f2dbf72357d631ae46")
#     contracts.append("0xe097783483d1b7527152ef8b150b99b9b2700c8d")
#     contracts.append("0xa731585ab05fc9f83555cf9bff8f58ee94e18f85")
#     contracts.append("0x8922c1147e141c055fddfc0ed5a119f3378c8ef8")
#     contracts.append("0xebe0d1cb6a0b8569929e062d67bfbc07608f0a47")
#     contracts.append("0x1887118e49e0f4a78bd71b792a49de03504a764d")
#     contracts.append("0x3f2d1bc6d02522dbcdb216b2e75edddafe04b16f")
#     contracts.append("0x26267e41ceca7c8e0f143554af707336f27fa051")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)


#     # Warp_interface
#     incident = "Warp_interface"
#     hack = "0x8bb8dc5c7c830bac85fa48acad2505e9300a91c3ff239c9517d0cae33b595090"
#     contracts = []
#     contracts.append("0x4a224cd0517f08b26608a2f73bf390b01a6618c8")
#     contracts.append("0x2261a20c1aa9a73bc35bdb36cd5830d94f2f7ddb")
#     contracts.append("0xdadd9ba311192d360df13395e137f1e673c91deb")
#     contracts.append("0x4e9a87ce601618fbf0c5bc415e35a4ac012d3863")
#     contracts.append("0xf289b48636f6a66f8aea4c2d422a88d4f73b3894")
#     contracts.append("0x6046c3ab74e6ce761d218b9117d5c63200f4b406")
#     contracts.append("0xae465fd39b519602ee28f062037f7b9c41fdc8cf")
#     contracts.append("0x13db1cb418573f4c3a2ea36486f0e421bc0d2427")
#     contracts.append("0x3c37f97f7d8f705cc230f97a0668f77a0e05d0aa")
#     contracts.append("0x496b5607e6ef186d5de849a2791fb186e2e94982")
#     contracts.append("0x97dbf244c17a667d93e29a70b961d7ab9b72d7ed")
#     contracts.append("0x1b0284391fdf905222b6174ef2cde60ba58d9529")
#     contracts.append("0x48772565845872fc65c43eccc44d33b25598ca81")
#     contracts.append("0xba539b9a5c2d412cb10e5770435f362094f9541c")
#     contracts.append("0x320380c4e463ea9427b49118ddf57f51672743e0")
#     contracts.append("0xcdb97f4c32f065b8e93cf16bb1e5d198bcf8ca0d")
#     contracts.append("0xb64dfae5122d70fa932f563c53921fe33967b3e0")
#     # rerankTransactions(contracts, incident, hack)
#     getStatsMoveFilesCache(incident, contracts, hack)
#     # FetchTxs(incident)




    # # InverseFi
    # incident = "InverseFi"
    # hack = "0x600373f67521324c8068cfd025f121a0843d57ec813411661b07edc5ff781842"
    # contracts = []
    # contracts.append("0x1637e4e9941d55703a7a5e7807d6ada3f7dcd61b")
    # contracts.append("0x697b4acaa24430f254224eb794d2a85ba1fa1fb8")
    # contracts.append("0x39b1df026010b5aea781f90542ee19e900f2db15")
    # contracts.append("0x4dcf7407ae5c07f8681e1659f626e114a7667339")
    # contracts.append("0x17786f3813e6ba35343211bd8fe18ec4de14f28b")
    # contracts.append("0x865377367054516e17014ccded1e7d814edc9ce4")
    # contracts.append("0xe8929afd47064efd36a7fb51da3f8c5eb40c4cb4")
    # contracts.append("0x7fcb7dac61ee35b3d4a51117a7c58d53f0a8a670")
    # contracts.append("0x41d5d79431a913c4ae7d69a668ecdfe5ff9dfb68")
    # contracts.append("0x210ac53b27f16e20a9aa7d16260f84693390258f")
    # contracts.append("0x8f0439382359c05ed287acd5170757b76402d93f")
    # contracts.append("0xde2af899040536884e062d3a334f2dd36f34b4a4")
    # # rerankTransactions(contracts, incident, hack)
    # getStatsMoveFilesCache(incident, contracts, hack)
    # # FetchTxs(incident)



    # # CreamFi2_4
    # incident = "CreamFi2_4"
    # hack = "0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92"
    # contracts = []
    # contracts.append("0x8379baa817c5c5ab929b03ee8e3c48e45018ae41")
    # contracts.append("0xd06527d5e56a3495252a528c4987003b712860ee")
    # contracts.append("0x44fbebd2f576670a6c33f6fc0b00aa8c5753b322")
    # contracts.append("0x851a040fc0dcbb13a272ebc272f2bc2ce1e11c4d")
    # contracts.append("0x1f9b4756b008106c806c7e64322d7ed3b72cb284")
    # contracts.append("0x812c0b2a2a0a74f6f6ed620fbd2b67fec7db2190")
    # contracts.append("0x797aab1ce7c01eb727ab980762ba88e7133d2157")
    # contracts.append("0x10fdbd1e48ee2fd9336a482d746138ae19e649db")
    # contracts.append("0xe7db46742c51a7bd64b8d83b8201239d759786be")
    # contracts.append("0xbadac56c9aca307079e8b8fc699987aac89813ee")
    # contracts.append("0x8c3b7a4320ba70f8239f83770c4015b5bc4e6f91")
    # contracts.append("0x9a975fe93cff8b0387b958adb9082b0ed0659ad2")
    # contracts.append("0x523effc8bfefc2948211a05a905f761cba5e8e9e")
    # contracts.append("0x299e254a8a165bbeb76d9d69305013329eea3a3b")
    # contracts.append("0x338eee1f7b89ce6272f302bdc4b952c13b221f1d")
    # contracts.append("0x3d5bc3c8d13dcb8bf317092d84783c2697ae9258")
    # contracts.append("0x2a537fa9ffaea8c1a41d3c2b68a9cb791529366d")
    # contracts.append("0xfd609a03b393f1a1cfcacedabf068cad09a924e2")
    # contracts.append("0xeff039c3c1d668f408d09dd7b63008622a77532c")
    # contracts.append("0xcbc1065255cbc3ab41a6868c22d1f1c573ab89fd")
    # contracts.append("0xe89a6d0509faf730bd707bf868d9a2a744a363c7")
    # contracts.append("0x228619cca194fbe3ebeb2f835ec1ea5080dafbb2")
    # contracts.append("0x4112a717edd051f77d834a6703a1ef5e3d73387f")
    # contracts.append("0x4baa77013ccd6705ab0522853cb0e9d453579dd4")
    # # rerankTransactions(contracts, incident, hack)
    # getStatsMoveFilesCache(incident, contracts, hack)
    # # FetchTxs(incident)

# No source code for the border contracts. Give up:

    # category = 'FlashSyn'  # bZx1
    # contract = "0xb0200B0677dD825bb32B93d055eBb9dc3521db9D"
    # categoryContract2File(category, contract)

#  dropped

    # # Jan 19, 2022 Multichain Permit Attack  AnySwap  
    # category = 'DeFiHackLabs'
    # contract = "0x6b7a87899490EcE95443e979cA9485CBE7E71522"
    # categoryContract2File(category, contract)
    pass


def main2():
    # # # Study: Uniswap
    # incident = "Uniswap2"
    # # contracts = []
    # # contracts.append("0x1F98415757620B543A52E61c46B32eB19261F984")
    # # contracts.append("0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696")
    # # contracts.append("0xB753548F6E010e7e680BA186F9Ca1BdAB2E90cf2")
    # # contracts.append("0xbfd8137f7d1516D3ea5cA83523914859ec47F573")
    # # contracts.append("0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6")
    # # contracts.append("0xE592427A0AEce92De3Edee1F18E0157C05861564")
    # # contracts.append("0x42B24A95702b9986e82d421cC3568932790A48Ec")
    # # contracts.append("0x91ae842A5Ffd8d12023116943e72A606179294f3")
    # # contracts.append("0xEe6A57eC80ea46401049E92587E52f5Ec1c24785")
    # # contracts.append("0xC36442b4a4522E871399CD717aBDD847Ab11FE88")
    # # contracts.append("0xA5644E29708357803b5A882D272c41cC0dF92B34")
    # # contracts.append("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")
    # # contracts.append("0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45")
    # # contracts.append("0x000000000022D473030F116dDEE9F6B43aC78BA3")
    # # contracts.append("0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD")
    # # contracts.append("0xe34139463bA50bD61336E0c446Bd8C0867c6fE65")
    # # rerankTransactionsStudy(contracts, incident)
    # FetchTxs(incident)



    # # Study: AAVE
    # incident = "AAVE2"
    # # contracts = []
    # # contracts.append("0xc2aaCf6553D20d1e9d78E365AAba8032af9c85b0")
    # # contracts.append("0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2")
    # # contracts.append("0x64b761D848206f447Fe2dd461b0c635Ec39EbB27")
    # # contracts.append("0x8164Cc65827dcFe994AB23944CBC90e0aa80bFcb")
    # # contracts.append("0x2f39d218133AFaB8F2B819B1066c7E434Ad94E9e")
    # # contracts.append("0xbaA999AC55EAce41CcAE355c77809e68Bb345170")
    # # contracts.append("0x7B4EB56E7CD4b454BA8ff71E4518426369a138a3")
    # # contracts.append("0x162A7AC02f547ad796CA549f757e2b8d1D9b10a6")
    # # contracts.append("0x91c0eA31b49B69Ea18607702c5d9aC360bf3dE7d")
    # # contracts.append("0x893411580e590D62dDBca8a703d61Cc4A8c7b2b9")
    # # contracts.append("0xC7be5307ba715ce89b152f3Df0658295b3dbA8E2")
    # # contracts.append("0x54586bE62E3c3580375aE3723C145253060Ca0C2")
    # # contracts.append("0x464c71f6c2f760dda6093dcb91c24c39e5d6e18c")
    # # contracts.append("0x3d569673dAa0575c936c7c67c4E6AedA69CC630C")
    # # contracts.append("0xADC0A53095A0af87F3aa29FE0715B5c28016364e")
    # # contracts.append("0x02e7B8511831B1b02d9018215a0f8f500Ea5c6B3")
    # # contracts.append("0x8761e0370f94f68Db8EaA731f4fC581f6AD0Bd68")
    # # contracts.append("0x78F8Bd884C3D738B74B420540659c82f392820e0")
    # # contracts.append("0xb748952c7bc638f31775245964707bcc5ddfabfc")
    # # rerankTransactionsStudy(contracts, incident)
    # FetchTxs(incident)



    # # do it tomorrow
    # # Study: Lido
    # incident = "Lido2"
    # # contracts = []
    # # contracts.append("0xC1d0b3DE6792Bf6b4b37EccdcC24e45978Cfd2Eb")
    # # contracts.append("0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84")
    # # contracts.append("0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0")
    # # contracts.append("0x8F73e4C2A6D852bb4ab2A45E6a9CF5715b3228B7")
    # # contracts.append("0xFdDf38947aFB03C621C71b06C9C70bce73f12999")
    # # contracts.append("0x55032650b14df07b85bF18A3a3eC8E0Af2e028d5")
    # # contracts.append("0xaE7B191A31f627b4eB1d4DaC64eaB9976995b433")
    # # contracts.append("0xC77F8768774E1c9244BEed705C4354f2113CFc09")
    # # contracts.append("0x388C818CA8B9251b393131C08a736A67ccB19297")
    # # contracts.append("0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1")
    # # contracts.append("0xb9d7934878b5fb9610b3fe8a5e441e8fad7e293f")
    # # contracts.append("0xD15a672319Cf0352560eE76d9e89eAB0889046D3")
    # # contracts.append("0xF95f069F9AD107938F6ba802a3da87892298610E")
    # # rerankTransactionsStudy(contracts, incident)
    # FetchTxs(incident)



    incident = "SphereX"
    contracts = []
    contracts.append("0xf5d35b9e95f6842a2064a2dd24f8deede9d58f97")
    contracts.append("0x6231a192089fb636e704d2c7807d7a79c2457b07")
    contracts.append("0xc92b021ff09ae005cb3fccb66af8db01fc4cdf90")
    rerankTransactionsStudy_SphereX(contracts)
    FetchTxs(incident)






def main3():
    # incident = "Bedrock_DeFi"
    # hack = "0x725f0d65340c859e0f64e72ca8260220c526c3e0ccde530004160809f6177940"
    # contracts = []
    # contracts.append("0x004e9c3ef86bc1ca1f0bb5c7662861ee93350568")
    # contracts.append("0x51a7f889480c57cbeea81614f7d0be2b70db6c5e")
    # contracts.append("0x047d41f2544b7f63a8e991af2068a363d210d6da")
    # rerankTransactionsNew(contracts, incident, hack)
    # FetchTxs(incident)


    # incident = "DoughFina"
    # hack = "0x92cdcc732eebf47200ea56123716e337f6ef7d5ad714a2295794fdc6031ebb2e"
    # contracts = []
    # contracts.append("0x9f54e8eaa9658316bb8006e03fff1cb191aafbe6")
    # contracts.append("0x534a3bb1ecb886ce9e7632e33d97bf22f838d085")
    # rerankTransactionsNew(contracts, incident, hack)
    # FetchTxs(incident)


    # incident = "OnyxDAO"
    # hack = "0x46567c731c4f4f7e27c4ce591f0aebdeb2d9ae1038237a0134de7b13e63d8729"
    # contracts = []
    # contracts.append("0x2ccb7d00a9e10d0c3408b5eefb67011abfacb075")
    # contracts.append("0xcc53f8ff403824a350885a345ed4da649e060369")
    # contracts.append("0xbd20ae088dee315ace2c08add700775f461fea64")
    # contracts.append("0xa2cd3d43c775978a96bdbf12d733d5a1ed94fb18")
    # contracts.append("0xf3354d3e288ce599988e23f9ad814ec1b004d74a")
    # contracts.append("0x7a89e16cc48432917c948437ac1441b78d133a16")
    # contracts.append("0x2c6650126b6e0749f977d280c98415ed05894711")
    # contracts.append("0xee894c051c402301bc19be46c231d2a8e38b0451")
    # rerankTransactionsNew(contracts, incident, hack)
    # FetchTxs(incident)

    incident = "Audius"
    hack = "0xfefd829e246002a8fd061eede7501bccb6e244a9aacea0ebceaecef5d877a984"
    contracts = []
    contracts.append("0x4deca517d6817b6510798b7328f2314d3003abac")
    contracts.append("0xe6d97b2099f142513be7a2a068be040656ae4591")
    contracts.append("0x4d7968ebfd390d5e7926cb3587c39eff2f9fb225")
    # rerankTransactionsNew(contracts, incident, hack)
    FetchTxs(incident)

    # incident = "OmniNFT"
    # hack = "0x264e16f4862d182a6a0b74977df28a85747b6f237b5e229c9a5bbacdf499ccb4"
    # contracts = []
    # contracts.append("0x218615c78104e16b5f17764d35b905b638fe4a92")
    # contracts.append("0xebe72cdafebc1abf26517dd64b28762df77912a9")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)

    # incident = "MetaSwap"
    # hack = "0x2b023d65485c4bb68d781960c2196588d03b871dc9eb1c054f596b7ca6f7da56"
    # contracts = []
    # contracts.append("0x824dcd7b044d60df2e89b1bb888e66d8bcf41491")
    # contracts.append("0xacb83e0633d6605c5001e2ab59ef3c745547c8c7")
    # contracts.append("0x5f86558387293b6009d7896A61fcc86C17808D62")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)

    # incident = "Auctus"
    # hack = "0x2e7d7e7a6eb157b98974c8687fbd848d0158d37edc1302ea08ee5ddb376befea"
    # contracts = []
    # contracts.append("0xe7597f774fd0a15a617894dc39d45a28b97afa4f")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)

    # incident = "BaconProtocol"
    # hack = "0x7d2296bcb936aa5e2397ddf8ccba59f54a178c3901666b49291d880369dbcf31"
    # contracts = []
    # contracts.append("0xb8919522331c59f5c16bdfaa6a121a6e03a91f62")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)

    # incident = "MonoXFi"
    # hack = "0x9f14d093a2349de08f02fc0fb018dadb449351d0cdb7d0738ff69cc6fef5f299"
    # contracts = []
    # contracts.append("0x2920f7d6134f4669343e70122ca9b8f19ef8fa5d")
    # contracts.append("0xc36a7887786389405ea8da0b87602ae3902b88a1")
    # contracts.append("0x59653e37f8c491c3be36e5dd4d503ca32b5ab2f4")
    # contracts.append("0x532d7ebe4556216490c9d03460214b58e4933454")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)

    # incident = "NowSwap"
    # hack = "0xf3158a7ea59586c5570f5532c22e2582ee9adba2408eabe61622595197c50713"
    # contracts = []
    # contracts.append("0x9536a78440f72f5e9612949f1848fe5e9d4934cc")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)


    # incident = "PopsicleFi"
    # hack = "0xcd7dae143a4c0223349c16237ce4cd7696b1638d116a72755231ede872ab70fc"
    # contracts = []
    # contracts.append("0xc4ff55a4329f84f9bf0f5619998ab570481ebb48")
    # contracts.append("0xd63b340f6e9cccf0c997c83c8d036fa53b113546")
    # contracts.append("0xb53dc33bb39efe6e9db36d7ef290d6679facbec7")
    # contracts.append("0x6f3f35a268b3af45331471eabf3f9881b601f5aa")
    # contracts.append("0xdd90112eaf865e4e0030000803ebbb4d84f14617")
    # contracts.append("0xe22eacac57a1adfa38dca1100ef17654e91efd35")
    # rerankTransactionsNew(contracts, incident, hack)
    # # FetchTxs(incident)







if __name__ == "__main__":
    main2()

    # main2()
