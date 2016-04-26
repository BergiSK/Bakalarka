#coding: utf-8
import numpy as np
from IsiBin import IsiBin

"""
Trieda slúži na zoskupenie a spriemerovanie časových okien prislúchajúcich jednotlivým stimulom.
"""

class EpochManager:

    def __init__(self, signal, stimulusCode, phaseInSequence):
        self.signal = signal
        self.stimulusCode = stimulusCode
        self.phaseInSequence = phaseInSequence

    # najde casti signalu prisluchajuce jednotlivym stimulom (vysvietenia riadku/stlpca)
    def createEpochs(self, isiCount = 12):
        isi = []
        for i in range(isiCount):
            sublist = []
            isi.append(sublist)

        prev = self.stimulusCode[0]
        for i in range (len(self.stimulusCode)):
            cur = self.stimulusCode[i]
            # ak sa prave nieco vysvietilo
            if cur != prev and cur != 0:
                isi[cur-1].append(i)
            prev = cur
        return isi

    # spriemeruje najdene okna
    def averageEpochs(self, signal, isiList, maxIndex, minIndex, maxSets, isiNum = 12, epochLeng=14):
        isiBinList = [IsiBin() for i in range(isiNum)]

        for l in range(len(isiList)):
            for j in range(len(signal)):
                chanSignal = signal[j]
                epoch = []

                for i in range(1,epochLeng+1):
                    tmp = []
                    # USE LESS STIMULI SETS.. max is 15.. - Handicap
                    setsUsed = 0
                    for m in range (len(isiList[l])):
                        if setsUsed == maxSets:
                            break
                        if isiList[l][m] > maxIndex:
                            break
                        if isiList[l][m] + epochLeng >= len(chanSignal):
                            break
                        if isiList[l][m] > minIndex and isiList[l][m]+i < len(self.phaseInSequence):
                                setsUsed+=1
                                tmp.append(chanSignal[isiList[l][m]+i])

                    epoch.append(np.mean(tmp))
                isiBinList[l].channelsSignalsAveraged.append(epoch)

        return isiBinList

    # posunie signal nad os "x" a umocni hodnoty pre lepsiu rozlisnost
    def scaleEpochs (self,epochs):
        #12 isi
        for i in range (len(epochs)):
            # 64 channels
            for l in range(len(epochs[i].channelsSignalsAveraged)):
                #najde global min a posunie onho cely signal nahor, vzniknu <0;n> hodnoty, hodnoty umocni pre vyssiu rozlisnost
                min = abs(np.amin(epochs[i].channelsSignalsAveraged[l]))
                tmpMoved = [pow(((float)(x) + min),2) for x in epochs[i].channelsSignalsAveraged[l]]

                epochs[i].channelsSignalsAveraged[l] = tmpMoved

        return epochs

    # ziska spriemerovane epochy
    def getAveragedEpochs (self, maxIndex, minIndex,isiList,maxSets):
        #ziska spriemerovane odozvy (64*28) priemerne data na kazdej elektrode napriec setmi vysvieteni daneho riadka / stlpca
        avEpochs = self.averageEpochs(self.signal,isiList,maxIndex,minIndex,maxSets)
        # zvyrazni hodnoty
        scEpochs = self.scaleEpochs(avEpochs)
        return scEpochs