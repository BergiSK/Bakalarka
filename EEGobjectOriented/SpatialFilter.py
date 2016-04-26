#coding: utf-8

from IsiBin import IsiBin
import numpy as np
from sklearn.decomposition import FastICA
from Visualizer import Visualizer

"""
Trieda sa stará o priestorové filtrovanie signálu pomocou metódy ICA, taktiež vykonáva Grand Averaging vybratých elektród.
"""

numComponents = 8

# priestorové rozloženie elektród pre 64 elektródové EEG
channelPositionsDataset = np.array([np.array([0,0,0,0,22,23,24,0,0,0,0]),
np.array([0,0,0,25,26,27,28,29,0,0,0]),
np.array([0,30,31,32,33,34,35,36,37,38,0]),
np.array([0,39,1,2,3,4,5,6,7,40,0]),
np.array([43,41,8,9,10,11,12,13,14,42,44]),
np.array([0,45,15,16,17,18,19,20,21,46,0]),
np.array([0,47,48,49,50,51,52,53,54,55,0]),
np.array([0,0,0,56,57,58,59,60,0,0,0]),
np.array([0,0,0,0,61,62,63,0,0,0,0]),
np.array([0,0,0,0,0,64,0,0,0,0,0])])

# priestorové rozloženie elektród pre 14 elektródové EEG - Epoc
channelPositionsEpoc = np.array([np.array([0,0,1,0,0,14,0,0]),
np.array([0,2,0,3,12,0,13,0]),
np.array([0,0,4,0,0,11,0,0]),
np.array([5,0,0,0,0,0,0,10]),
np.array([0,0,0,0,0,0,0,0]),
np.array([0,6,0,0,0,0,9,0]),
np.array([0,0,7,0,0,8,0,0])])

class SpatialFilter:

    def __init__(self, chanNum):
        global numComponents
        if chanNum == 14:
            numComponents = 4
        else:
            numComponents = 8
        self.ica = FastICA(n_components=numComponents,max_iter=800)
        self.chanNum = chanNum

    # funkcia vykonáva filtrovanie pomocou metódy ICA, pre 64 el. signál
    # obsahuje funkčné heuristiky na identifikáciu P300 komponentov
    def icaFilter (self,signal):
        global numComponents
        if self.chanNum == 64:
            numComponents = 8
            channelPositions = channelPositionsDataset
            frontBottomBorder = 2
            centerLeftBorder = 2
            centerRightBorder = 9
            centerBottomBorder = 7
            centerTopBorder = 2
            leftBorder = 2
            rightBorder = 9

        else:
            numComponents = 4
            channelPositions = channelPositionsEpoc
            frontBottomBorder = 1
            centerLeftBorder = 1
            centerRightBorder = 7
            centerBottomBorder = 6
            centerTopBorder = 1
            leftBorder = 1
            rightBorder = 7

        components = self.ica.fit_transform(signal)
        ############################ Výber P300 komponentov ############################
        toRejectFound = []
        for i in range(numComponents):
            component = self.ica.mixing_[:,i]

            ## výpočet priemerných potenciálov na jednotlivých miestach hlavy ##

            ## Front average potential ##
            frontChannels = channelPositions[:frontBottomBorder]
            frontChannels = [list(y for y in x if y) for x in frontChannels]
            sumFront = 0
            sumChanFront = 0
            for m in range(len(frontChannels)):
                for n in frontChannels[m]:
                    sumFront+=abs(component[n-1])
                    sumChanFront+=1

            averageFront = sumFront/sumChanFront

            ## Center average potential ##
            centerChannels = channelPositions[centerTopBorder:centerBottomBorder,centerLeftBorder:centerRightBorder]
            centerChannels = [list(y for y in x if y) for x in centerChannels]
            sumCenter = 0
            sumChanCenter = 0
            for m in range(len(centerChannels)):
                for n in centerChannels[m]:
                    sumCenter+=abs(component[n-1])
                    sumChanCenter+=1

            averageCenter = sumCenter/sumChanCenter

            ## Left average potential ##
            leftChannels = channelPositions[:,:leftBorder]
            leftChannels = [list(y for y in x if y) for x in leftChannels]
            sumLeft = 0
            sumChanLeft = 0
            for m in range(len(leftChannels)):
                for n in leftChannels[m]:
                    sumLeft+=abs(component[n-1])
                    sumChanLeft+=1

            averageLeft = sumLeft/sumChanLeft


            ## Right average potential ##
            rightChannels = channelPositions[:,rightBorder:]
            rightChannels = [list(y for y in x if y) for x in rightChannels]
            sumRight = 0
            sumChanRight = 0
            for m in range(len(rightChannels)):
                for n in rightChannels[m]:
                    sumRight+=abs(component[n-1])
                    sumChanRight+=1

            averageRight = sumRight/sumChanRight

            ratioSum = (averageFront+averageRight+averageLeft)/averageCenter
            ratioFrontalBack = (averageFront+averageCenter)/(averageLeft+averageRight)

            toUse = 0
            ### heuristiky na základe priestorového rozloženia
            if self.chanNum == 64:
                if int(ratioSum) == 1:
                    toUse = 1

                if ratioFrontalBack > 1 and ratioFrontalBack < 3  and not (averageFront/averageCenter > 2):
                    toUse = 1

                if ratioSum < 1:
                    toUse = 1
            else:
                totalAverage = abs(component.mean())
                maxChan = abs(max(component.min(), component.max(), key=abs))

                if totalAverage*3 > maxChan and ratioSum < 5:
                    toUse = 1
                if averageCenter > averageFront and averageCenter > averageRight and averageCenter > averageLeft and ratioSum < 5:
                    toUse = 1
                if ratioSum < 2:
                    toUse = 1

            if toUse == 0:
                toRejectFound.append(i+1)
                print "IC"+str(i+1)+"\t Front:"+str(int(averageFront))+"\t Center:"+str(int(averageCenter))\
                  +"\t Right:"+str(int(averageRight))+"\t Left:"+str(int(averageLeft))+"\t Ratio:"+str(ratioSum)
            else:
                print "USED: IC"+str(i+1)+"\t Front:"+str(int(averageFront))+"\t Center:"+str(int(averageCenter))\
                  +"\t Right:"+str(int(averageRight))+"\t Left:"+str(int(averageLeft))+"\t Ratio:"+str(ratioSum)


        #### Zobrazenie komponentov (Heatmapa, časový rad, ) ######
        # visualizer = Visualizer()
        # visualizer.plotComponents(self.ica,channelPositions,components)

        #################### Odstránenie nežiadúcich komponentov z mixovacej matice ##################
        compNums = toRejectFound
        compNums.sort(reverse=True)

        ### Výber komponentov ručne
        # rejected = raw_input("Enter numbers of rejected components")
        # compNums = rejected.split()
        # for m in range (len(compNums)):
        #     compNums[m] = int(compNums[m])
        # compNums.sort(reverse=True)

        for i in compNums:
            self.ica.mixing_[:,i-1] = 0


        reconstructed = self.ica.inverse_transform(components)

        ### Zobrazenie grafu filtrovaného signálu ###
        # visualizer.plotSignalRepairing(signal,reconstructed)

        return reconstructed.T


    # spriemerovany char list pre jeden cielovy typ vysvietenia, vystupom je single element z povodnych N elektrod
    # mode = 0 - reduce, z 64 elektrod zober len tie z najdeneho subsetu
    # mode = 1 - guess, zober vsetky elektrody, signal co si dostal uz je len zo subsetu
    def grandAveragingFilter (self,isiBinList,subset,mode, isiCount = 12):
        chl = [IsiBin() for i in range(isiCount)]
        chl = isiBinList

        output = []
        for i in range(len(chl)):
            #print "Grand averaging letter:",i,"\n"
            charChannList = chl[i]
            epoch = []
            for m in range(len(charChannList.channelsSignalsAveraged[0])):
                tmp = []
                if mode == 0:
                    for l in subset:
                        tmp.append(charChannList.channelsSignalsAveraged[l][m])
                else:
                    for l in range (len(charChannList.channelsSignalsAveraged)):
                        tmp.append(charChannList.channelsSignalsAveraged[l][m])

                epoch.append(np.mean(tmp))
            output.append(epoch)

        return output