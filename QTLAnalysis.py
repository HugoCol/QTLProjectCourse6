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
        aValues = np.array(sortedDict[key]['a']).astype(np.float)
        bValues = np.array(sortedDict[key]['b']).astype(np.float)
        tStat, pValue = stats.ttest_ind(aValues, bValues)
        pValues[key] = {"pValue": pValue, "tStat": tStat}

    return pValues


def main():
    markerFile = sys.argv[1]
    concValueFile = sys.argv[2]

    markerDict, concValueList = fileReader(markerFile, concValueFile)
    sortedDict = dataSorter(markerDict, concValueList)

    pValues = tTest(sortedDict)


main()
