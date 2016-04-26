#coding: utf-8
import numpy as np
from scipy.signal import butter, lfilter
import math
import scipy as sc

"""
Trieda sa stara o predspracovanie, filtrovanie a downsample signalu.
"""

class Preprocessor:

    def __init__(self, channelCount,subset):
        self.channelCount = channelCount
        self.processedSignal = []
        self.subset = subset

    #channelindex dataset <0;63>
    def removeBaseline(self, ChannelIndex):
        # zober uvodny interval kludoveho stavu - code 0 - nic nie je vysvietene
        i = 0
        if self.channelCount == 64:
            while self.phaseInSequence[i] != 2:
                i+=1
        else:
            while self.stimulusCode[i] == 0:
                i+=1

        ChannelSignal = self.signal[:,ChannelIndex]
        # z najdeneho intervalu vyrataj priemer
        baseLine = np.mean(ChannelSignal[:i])

        # vytvor nove pole s odstranenim baseline
        bLineRemoved = [((float)(x) - baseLine) for x in ChannelSignal]
        return bLineRemoved

    #butterworth Bandpass filter
    def filterBpass(self, fs, cutOffLow, cutOffHigh, bLineRemoved):
        #fs / 2 je nyq frekvencia
        B, A = butter(2, cutOffHigh / (fs / 2), btype='low') # 1st order Butterworth low-pass
        C, D = butter(2, cutOffLow / (fs / 2), btype='high') # 1st order Butterworth high-pass

        bLineRemoved_low = lfilter(B, A, bLineRemoved)
        bLineRemoved_low_high = lfilter(C, D, bLineRemoved_low)
        return bLineRemoved_low_high

    # downsampluje signal
    def downSampleChannel (self, R, channelSignal):
        dsSignal = []
        # z 140 samplov spravime 140/R
        # padding 0 na koniec aby sa dal spravit downsamp., koniec pola aj tak nie je dolezity
        pad_size = math.ceil(float(len(channelSignal))/R)*R - len(channelSignal)
        b_padded = np.append(channelSignal, np.zeros(pad_size)*np.NaN)

        dsTmp = sc.nanmean(b_padded.reshape(-1,R), axis=1)
        dsSignal.append(dsTmp)

        return dsSignal

    # upravi opisne pole stimCode podla downsample faktoru
    def repairStimCode (self,R):
        num1 = -1
        num2 = -1
        num1count = 0
        num2count = 0
        output = []
        for i in range(len(self.stimulusCode)):
            if num1 == -1:
                num1 = self.stimulusCode[i]
            elif num2 == -1:
                num2 = self.stimulusCode[i]

            if num1 == self.stimulusCode[i]:
                num1count+=1

            if num2 == self.stimulusCode[i]:
                num2count+=1

            if (i + 1)%R == 0:

                if num1count > num2count:
                    output.append(num1)
                else:
                    output.append(num2)
                num1count = 0
                num2count = 0
                num1 = -1
                num2 = -1

        self.stimulusCode = output

    # vrati predspracovane data vsetkych elektrod(channelov)
    # mode = 0, hladaj na vsetkych elektrodach
    def preprocess (self, fs, cutOffLow, cutOffHigh, sf, signal, stimulusCode, phaseInSequence, mode = 0):

        bLineRemoved_low_highSignal = []
        self.processedSignal = []
        downSampFactor = 12

        self.signal = signal
        self.stimulusCode = stimulusCode
        self.phaseInSequence = phaseInSequence

        if mode == 1:
            for i in range(self.channelCount):
                bLineRemoved = self.removeBaseline(i)
                bLineRemoved_low_high = self.filterBpass(fs,cutOffLow,cutOffHigh, bLineRemoved)
                bLineRemoved_low_highSignal.append(bLineRemoved_low_high)

            ## transferne na IC a s5 cez mixing matrix s vynulovanymi noisy komponentami
            icaFiltered = sf.ica.inverse_transform(sf.ica.transform(np.array(bLineRemoved_low_highSignal).T)).T

            if len(self.subset) != 0:
                for i in self.subset:
                    dsChan = self.downSampleChannel(downSampFactor,icaFiltered[i])
                    self.processedSignal.append(dsChan[0])
            else:
                for i in range(self.channelCount):
                    dsChan = self.downSampleChannel(downSampFactor,icaFiltered[i])
                    self.processedSignal.append(dsChan[0])

        else:
            for i in range (self.channelCount):
                bLineRemoved = self.removeBaseline(i)
                bLineRemoved_low_high = self.filterBpass(fs,cutOffLow,cutOffHigh, bLineRemoved)
                bLineRemoved_low_highSignal.append(bLineRemoved_low_high)

            icaFiltered = sf.icaFilter(np.array(bLineRemoved_low_highSignal).T)
            print "Signal reconstructed by ICA!"

            for i in range(self.channelCount):
                dsChan = self.downSampleChannel(downSampFactor,icaFiltered[i])
                self.processedSignal.append(dsChan[0])


        self.repairStimCode(downSampFactor)

        print "Preprocessing completed"

        return self.processedSignal