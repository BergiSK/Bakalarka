#coding: utf-8
from sklearn.lda import LDA
import numpy as np
from sklearn import svm

"""
Trieda slúžiaca na klasifikáciu pomocou LDA.
"""

class Classifier:

    def __init__(self):
        self.signalArray = np.array([])
        self.targetVals = np.array([])

    # plni treningove pole
    def learn (self, signalArray, targetVals, tmp = 1):
        if tmp == 1:
            self.signalArray = np.vstack((self.signalArray,signalArray))
            self.targetVals = np.append(self.targetVals,targetVals)
        else:
            self.signalArray = signalArray
            self.targetVals = targetVals

    # sluzi na spriemerovanie natrenovaneho pola napriec elektrodami vybranymi subsetom
    def reduce (self, spatialFilter, processor, subset):
        reducedArray = np.array([])
        for i in range(len(self.signalArray)):
            tmp = spatialFilter.grandAveragingFilter(self.signalArray[i],subset,0)
            if i == 0:
                reducedArray = processor.prepairSignalArray(tmp)
            else:
                reducedArray = np.vstack((reducedArray,processor.prepairSignalArray(tmp)))

        return reducedArray

    # ziskava index znaku v matici
    def getMatrixIndex (self,predictedRowIndex,predictedColIndex):
        return predictedRowIndex*6 + predictedColIndex

    # hada znak
    def predictTarget (self,input,reducedArray = []):
        # reduced array predstavuje alternativu k naucenemu 64*28 polu
        if len(reducedArray) > 0:
            self.lda(reducedArray)
        else:
            self.lda()

        #0-5
        inpCols = input[:6]
        #6-11
        inpRows = input[6:]

        ## predpovedaj riadok
        inputProb = self.ldaMat.predict_proba(np.resize(inpRows,(len(inpRows),len(inpRows[1]))))
        predictedRowIndex = inputProb[:,1].argmax(axis=0)

        # predpovedaj stlpec
        inputProb = self.ldaMat.predict_proba(np.resize(inpCols,(len(inpCols),len(inpCols[1]))))
        predictedColIndex = inputProb[:,1].argmax(axis=0)

        # ziskaj index vysledneho znaku
        predictedIndex = self.getMatrixIndex(predictedRowIndex,predictedColIndex)

        # konvertuj index na znak
        return self.matrixCharConvert(predictedIndex)

    # vytvori model pre lda z natrenovaneho pola
    def lda(self, reducedArray = []):
        # components vyjadruju pocet stavov / classov medzi ktorymi rozlisujeme.. staci 0/1 pre target a non-target
        lda = LDA(n_components=2)
        if len(reducedArray) > 0:
            self.ldaMat = lda.fit(np.resize(reducedArray,(len(reducedArray),len(reducedArray[0]))), self.targetVals)
        else:
            self.ldaMat = lda.fit(np.resize(self.signalArray,(len(self.signalArray),len(self.signalArray[0]))), self.targetVals)

    # konvertuje index na znak
    def matrixCharConvert(self,num):
        if num <= 25:
            return chr(num+65)
        elif num != 35:
            return chr(num+23)
        else:
            return '_'
