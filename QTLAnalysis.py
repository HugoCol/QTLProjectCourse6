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
                if valueDict[indexValue] != '-':
                    aValues.append(valueDict[indexValue])
            elif markerDict[header][indexValue] == 'b':
                if valueDict[indexValue] != '-':
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


def pValueFilter(pValues):
    filteredPValues = {}

    for key in pValues:
        if pValues[key]['pValue'] < 0.05:
            filteredPValues[key] = pValues[key]

    return filteredPValues


def fileWriter(pValues, filteredPValues):
    with open('results.csv', 'w') as file:
        file.write("Filtered results,\n")
        header_line = "Marker,pValue,tStat\n"
        file.write(header_line)
        for key in filteredPValues:
            markerName = key[0]
            pValue = str(filteredPValues[key]['pValue'])
            tStat = str(filteredPValues[key]['tStat'])
            line = markerName + ',' + pValue + ',' + tStat + '\n'
            file.write(line)

        file.write("\n\n\n")
        file.write("Unfiltered results\n")
        header_line = "Marker,pValue,tStat\n"
        file.write(header_line)
        for key in pValues:
            markerName = key[0]
            pValue = str(pValues[key]['pValue'])
            tStat = str(pValues[key]['tStat'])
            line = markerName + ',' + pValue + ',' + tStat + '\n'
            file.write(line)

    file.close()


def main():
    markerFile = sys.argv[1]
    concValueFile = sys.argv[2]

    markerDict, concValueList = fileReader(markerFile, concValueFile)
    sortedDict = dataSorter(markerDict, concValueList)

    pValues = tTest(sortedDict)

    filteredPValues = pValueFilter(pValues)

    fileWriter(pValues, filteredPValues)

    for key in pValues:
        print(key)
        print(pValues[key])


main()
