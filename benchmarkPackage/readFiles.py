# read all json files under benchmarks/ folder
import os
import ujson as json
import sys
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# read all json files under benchmarks/ folder
path = SCRIPT_DIR + '/benchmarks/'


files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.json' in file:
            files.append(os.path.join(r, file))

def Hack2Contract():
    hack2contractMap = {}
    for f in files:
        benchmark = json.load(open(f))
        hackTx = benchmark['exploitTx']
        interface = benchmark['interface']
        implementation = benchmark['implementation']
        category = benchmark['category']
        if hackTx not in hack2contractMap:
            hack2contractMap[hackTx] = [(category, interface, implementation, benchmark)]
        else:
            hack2contractMap[hackTx].append((category, interface, implementation, benchmark))
    return hack2contractMap


def benchmark2ExploitTx(benchmark_name):
    for f in files:
        benchmark = json.load(open(f))
        benchmarkName = benchmark['benchmarkName']
        if benchmarkName == benchmark_name:
            return benchmark['exploitTx']
        


def main():
    exploit = benchmark2ExploitTx("RevestFi")
    print(exploit)
    # array = []
    # array2 = []
    # array3 = []

    # count = 0
    # count2 = 0
    # for f in files:
    #     benchmark = json.load(open(f))
    #     array.append( [benchmark['benchmarkName'], len(benchmark['trainingSet']), len(benchmark['testingSet']), len(benchmark['trainingSet']) + len(benchmark['testingSet'] )]  )
    #     if benchmark['interface'] != benchmark['implementation']:
    #         array2.append(benchmark['benchmarkName'])
    #         count += 1
    #     else:
    #         array3.append(benchmark['benchmarkName'])
    #         count2 += 1

    # # sort array by number of testingSet
    # array.sort(key=lambda x: x[1])

    # print("index (benchmark, trainingSet, testingSet size)")

    # for ii, a in enumerate(array):
    #     print(ii, a)

    # print("implementation == interface: ", count2)
    # print(array3)

    # for key in array3:
    #     for benchmarkname, trainingSet, testingSet, total in array:
    #         if benchmarkname == key:
    #             print(benchmarkname, trainingSet, testingSet, total)
        

    # print("implementation != interface: ", count)
    # print(array2)



if __name__ == "__main__":
    main()