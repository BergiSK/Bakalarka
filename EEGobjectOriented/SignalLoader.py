#coding: utf-8
from numpy import genfromtxt
import scipy.io as sio
import numpy as np


"""
Trieda slúži na načítanie dát signálu z Wadsworth datasetu, alebo z nášho experimentu s Epocom. Dáta musia byť označené dvomi
 opisnými poliami: PhaseInSequence a StimulusCode.
"""

class SignalLoader:

    def __init__(self, channelCount,files):
        self.channelCount = channelCount
        self.files = files

    def loadSignal(self):

        #self.files = open(self.filenameTxt).readlines()
        if isinstance(self.files, basestring):
            tmp = []
            tmp.append(self.files)
            self.files = tmp

        if self.channelCount != 64:
            self.files.sort()

        for i in range(len(self.files)):
            if self.channelCount == 64:
                #otvorenie matlab filu, nacitanie dat do poli, rstrip dava prec \n
                cont = sio.loadmat(self.files[i])

                if i == 0:
                    self.signal = cont['signal']
                    self.stimulusCode = cont['StimulusCode']
                    self.phaseInSequence = cont['PhaseInSequence']
                else:
                    self.signal = np.vstack((self.signal,cont['signal']))
                    self.stimulusCode = np.vstack((self.stimulusCode,cont['StimulusCode']))
                    self.phaseInSequence = np.vstack((self.phaseInSequence,cont['PhaseInSequence']))
            # epoc
            else:
                if i == len(self.files)/3:
                    break

                dataSignal = genfromtxt(self.files[i+len(self.files)/3], delimiter=',')
                dataStimCode = genfromtxt(self.files[i], delimiter=',')
                dataPhase = genfromtxt(self.files[i+2*len(self.files)/3], delimiter=',')


                if i == 0:
                    self.signal = dataSignal[1:,3:17]
                    self.stimulusCode = [int(m) for m in dataStimCode[1:]]
                    self.phaseInSequence = [int(m) for m in dataPhase]
                else:
                    self.signal = np.vstack((self.signal,dataSignal[1:,3:17]))
                    self.stimulusCode = np.hstack((self.stimulusCode,[int(m) for m in dataStimCode[1:]]))
                    self.phaseInSequence = np.hstack((self.phaseInSequence,[int(m) for m in dataPhase]))

        return self.signal,self.stimulusCode,self.phaseInSequence