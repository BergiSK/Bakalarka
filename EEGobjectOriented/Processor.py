#coding: utf-8
from EpochManager import EpochManager
from Preprocessor import Preprocessor
from SpatialFilter import SpatialFilter
from Classifier import Classifier
from SignalLoader import SignalLoader
import numpy as np
import random
from Tkinter import *

"""
Hlavná riadiaca trieda, zodpovedná za koordináciu celého procesu.
"""

class Processor:

    def __init__(self,files,chanNum):
        self.signal = []
        self.stimulusCode = []
        self.phaseInSequence = []
        self.targetLetters = []
        self.firsttrain = 1
        self.cl = Classifier()
        self.sf = SpatialFilter(chanNum)
        self.rate = 0
        self.files = files
        self.chanNum = chanNum

    # Z cisla trenovacieho znaku urci jeho poziciu v speller matici
    def getCharIndexes (self,num):
        output = []
        #row index
        output.append((num/6)+6)
        #col index
        output.append(num % 6)
        return output


    # Pomocou opisneho pola phaseInSequence zisti na akych indexoch su prechody medzi cielovymi znakmi
    def findCharEnds (self):
        # najdi prechody medzi pismenami na ktore pouzivatel mysli (len pre dataset)
        charEnds = []
        for i in range (len(self.phaseInSequence)):
            if self.phaseInSequence[i] == 3 and self.phaseInSequence[i-1] == 2:
                tmp = (int)(i/12)
                #tmp = i
                charEnds.append(tmp)
        return charEnds

    # Transformuje list dat na numpy array
    def prepairSignalArray (self,finalData):
        converted = []
        for i in range(len(finalData)):
            converted.append(np.array(finalData[i]))

        return np.array(converted)

    # Vytvorenie znackovacieho pola pre IsiBinList - hovori ci dane vysvietenia zodpovedali cielovemu znaku
    def prepairTargetArray (self,targIndexes, isiCount = 12):
        output = []
        for i in range(isiCount):
            if i in targIndexes:
                output.append(1)
            else:
                output.append(0)

        return np.array(output)

    # Metoda trenuje klasifikator a updatuje pouzivatelske rozhranie
    def trainClassifier(self, trainLetter, progress, progLab, maxSets):

        # nacitanie a predspracovanie signalu
        signalLoader = SignalLoader(self.chanNum,self.files)
        prpr = Preprocessor(self.chanNum,[])
        signal,stimCode,phaseInSequence = signalLoader.loadSignal()
        self.signal = prpr.preprocess(240,1E-1,30E0,self.sf,signal,stimCode,phaseInSequence,0)
        self.stimulusCode = prpr.stimulusCode
        self.phaseInSequence = prpr.phaseInSequence
        self.targetLetters = sum(trainLetter,[])

        # najdenie prechodov medzi znakmi
        charEnds = self.findCharEnds()

        # rozdelenie dat do epoch
        em = EpochManager(self.signal,self.stimulusCode,self.phaseInSequence)
        isiList = em.createEpochs()

        # trening jednotlivych znakov
        for i in range(len(charEnds)):
            progress["value"] = i
            progLab["text"] = ("Trénujem znak: {}/{}").format(i+1, len(charEnds))
            print "Averaging character:",i,"\n"
            hi = charEnds[i]
            if i == 0:
                lo = 0
            else:
                lo = charEnds[i-1]

            rowColBinList = em.getAveragedEpochs(hi,lo,isiList,maxSets)
            finalDataArray = rowColBinList
            classMarks = self.prepairTargetArray(self.getCharIndexes(self.targetLetters[i]))

            if self.firsttrain == 1:
                self.cl.learn(finalDataArray,classMarks,0)
                self.firsttrain = 0
            else:
                self.cl.learn(finalDataArray,classMarks)

    # Metoda hada cielove znaky a updatuje pouzivatelske rozhranie
    def guessChars(self,subset,files,targetLetter,testProgress,progTestLabel,guessView,guessLab,maxSets):
        aktCharNum = 0
        totalChars = len(sum(targetLetter,[]))

        if self.chanNum != 64:
            files.sort()
            files = self.createTriplets(files)


        for m in range(len(files)):
            # nacitanie a predspracovanie signalu
            signalLoader = SignalLoader(self.chanNum,files[m])
            prpr = Preprocessor(self.chanNum,subset)
            signal, stimCode, phaseInSequence = signalLoader.loadSignal()
            self.signal = prpr.preprocess(240,1E-1,30E0,self.sf,signal,stimCode,phaseInSequence,1)
            self.stimulusCode = prpr.stimulusCode
            self.phaseInSequence = prpr.phaseInSequence
            if (len(targetLetter) > m):
                self.targetLetters = targetLetter[m]
            else:
                self.targetLetters = []
            print "Processing file:",m,"\n"

            # najdenie prechodov medzi znakmi
            charEnds = self.findCharEnds()

            # rozdelenie dat do epoch
            em = EpochManager(self.signal,self.stimulusCode,self.phaseInSequence)
            isiList = em.createEpochs()

            hit = 0
            # hadanie jednotlivych znakov
            for i in range(len(charEnds)):
                testProgress["value"] = aktCharNum
                progTestLabel["text"] = ("Hádam znak: {}/{}").format(aktCharNum+1, totalChars)
                aktCharNum +=1

                hi = charEnds[i]
                if i == 0:
                    lo = 0
                else:
                    lo = charEnds[i-1]

                rowColBinList = em.getAveragedEpochs(hi,lo,isiList,maxSets)
                finalDataArray = self.prepairSignalArray(self.sf.grandAveragingFilter(rowColBinList,subset,1))

                #pomocou klasifikatora
                char = self.cl.predictTarget(finalDataArray,self.cl.reduce(self.sf,self,subset))

                if len(self.targetLetters) > i:
                    if char == self.targetLetters[i]:
                        hit+=1
                        print "Succesfully guessed char:",char,"\n"
                    else:
                        print "Guessed char:",char,"\n"


                if i == 0:
                    text = "(" + char + ","
                elif i == len(charEnds) - 1:
                    text = char + ")"
                else:
                    text = char + ","

                guessView.configure(state='normal')
                guessView.insert(INSERT, text)
                guessView.configure(state='disabled')

            self.rate += (hit)*100/float(totalChars)
            print "\n Success rate= ",self.rate, "\n"
            guessLab["text"]=("Presnosť: {}").format(self.rate)

        return self.rate

    # Pomocna funkcia pre spracovanie csv suborov epoc dat
    def createTriplets(self, epocFiles):
        triplets = []
        for i in range(len(epocFiles)/3):
            triplet = []
            triplet.append(epocFiles[i])
            triplet.append(epocFiles[i+len(epocFiles)/3])
            triplet.append(epocFiles[i+2*len(epocFiles)/3])
            triplets.append(triplet)

        return triplets