import sys
import re
from scipy import stats
import numpy as np


def fileReader(markerFile, concValueFile):
    markerdict = {}
    concValueList = []
    headerline = []
    values = []

    with open(markerFile) as file:
        for _ in range(7):
            next(file)
        for line in file:
            if line[0].isalpha() or line == 'individual names:\n':
                if headerline and values:
                    markerdict[tuple(headerline)] = values
                    values = []
                headerline = re.sub("; ", "", line).replace("\n", "")
                headerline = headerline.split(" ")
            else:
                temp = line.strip().split()
                for i in temp:
                    values.append(i)

    with open(concValueFile) as file:
        for _ in range(8):
            next(file)
        for line in file:
            temp = line.replace("\n", "").split("\t")
            if temp[1] != '-':
                concValueList.append(temp[1])

    return markerdict, concValueList


def dataSorter(markerDict, valueDict):
    sortedDict = {}

    for header in markerDict:
        aValues = []
        bValues = []
        nestedDict = {}
        # for indexValue in range(len(markerDict[header])):
        #     if markerDict[header][indexValue] == 'a':
        #         try:
        #             if valueDict[indexValue+1] != '-':
        #                 aValues.append(valueDict[indexValue + 1])
        #         except KeyError:
        #             continue
        #     elif markerDict[header][indexValue] == 'b':
        #         try:
        #             if valueDict[indexValue] != '-':
        #                 bValues.append(valueDict[indexValue + 1])
        #         except KeyError:
        #             continue
        for indexValue in range(len(markerDict[header]) - 1):
            if markerDict[header][indexValue] == 'a':
                aValues.append(valueDict[indexValue])
            elif markerDict[header][indexValue] == 'b':
                bValues.append(valueDict[indexValue])
        nestedDict['a'] = aValues
        nestedDict['b'] = bValues
        sortedDict[header] = nestedDict

    return sortedDict


def tTest(sortedDict):
    pValues = {}

    for key in sortedDict:
        # print(key)
        aValues = np.array(sortedDict[key]['a']).astype(np.float)
        bValues = np.array(sortedDict[key]['b']).astype(np.float)
        tStat, pValue = stats.ttest_ind(aValues, bValues)
        # print("P-Value:{0} T-Statistic:{1}".format(pValue, tStat))
        pValues[key] = {"pValue": pValue, "tStat": tStat}

    return pValues


def main():
    markerFile = sys.argv[1]
    concValueFile = sys.argv[2]

    markerDict, concValueList = fileReader(markerFile, concValueFile)
    sortedDict = dataSorter(markerDict, concValueList)

    pValues = tTest(sortedDict)
    for i in pValues:
        print(pValues[i]['pValue'])


main()
