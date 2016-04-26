#coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as col

"""
Trieda slúžiaca na zobrazovanie grafov.
"""
class Visualizer:

    def plotFitnessesInGeneration(self,generation):

        individuals = []
        for i in range (len(generation)):
            individuals.append(generation[i].fitness)

        plt.hist(individuals, facecolor='g', alpha=0.75)

        plt.title('Fitness distribution in generation')
        plt.xlabel('Fitness')
        plt.ylabel('Number of individuals')
        plt.grid(True)
        plt.show()


    def plotSolutionProgress (self,topSolutions):
        plt.plot(topSolutions, 'ro')
        plt.title('Top solution progress')
        plt.xlabel('Generation')
        plt.ylabel('Fitness of top solution')
        plt.show()

    ################################## Zobrazí rozdiely medzi originálnym a prefiltrovaným signálom ######################
    def plotSignalRepairing(self,signal,reconstructed):
        numSamples = 3400
        numRows = 8

        n = 8000

        if signal.shape[1] == 64:
            # elektródy 21 - 29 zodpovedajú predným elektródam pri 64 elektródovom EEG so štandardným rozložením
            reconstructedToPlot = reconstructed[n:numSamples+n,21:29]
            originalToPlot = signal[n:numSamples+n,21:29]
        else:
            reconstructedToPlot = reconstructed[n:numSamples+n,[0,1,2,3,10,11,12,13]]
            originalToPlot = signal[n:numSamples+n,[0,1,2,3,10,11,12,13]]

        t = 10.0 * np.arange(numSamples, dtype=float)/numSamples
        ticklocs = []
        f1 = plt.figure("Original and reconstructed signal")
        ax = f1.add_subplot(111)
        plt.xlim(0, 10)
        plt.xticks(np.arange(10))
        dmin = originalToPlot.min()
        dmax = originalToPlot.max()
        dr = (dmax - dmin)*0.7  # Crowd them a bit.
        y0 = dmin
        y1 = (numRows - 1) * dr + dmax
        plt.ylim(y0, y1)

        #######################################################
        # nakreslí pôvodný signál - modrou #
        segs = []
        for i in range(numRows):
            segs.append(np.hstack((t[:, np.newaxis], originalToPlot[:, i, np.newaxis])))
            ticklocs.append(i*dr)

        offsets = np.zeros((numRows, 2), dtype=float)
        offsets[:, 1] = ticklocs

        linesOriginal = col.LineCollection(segs, offsets=offsets,transOffset=None,)
        ax.add_collection(linesOriginal)

        # nakreslí opravený signál - červenou#
        segs = []
        for i in range(numRows):
            segs.append(np.hstack((t[:, np.newaxis], reconstructedToPlot[:, i, np.newaxis])))

        linesReconstructed = col.LineCollection(segs, offsets=offsets,transOffset=None,color=[1, 0, 0])
        ax.add_collection(linesReconstructed)
        #####################################################################

        # nastavenie y-osi
        ax.set_yticks(ticklocs)
        ylabels = []
        for i in range(numRows):
            ylabels.append("CH"+str(i+1))
        ax.set_yticklabels(ylabels)

        plt.xlabel('time (s)')

        plt.show()

    # zobrazí jednotlivé nezávislé komponenty
    def plotComponents (self,ica,channelPositions,icaSignal):
        numComponents = ica.mixing_.shape[1]
        print "drawing..."
        for i in range (numComponents):
            f1 = plt.figure("IC"+str(i+1))
            ax = f1.add_subplot(311)
            heatData = np.array([])
            for m in range (len(channelPositions)):
                rowData = np.array([])
                for l in range (len(channelPositions[m])):
                    chanIndex = channelPositions[m][l]
                    if chanIndex != 0:
                        rowData = np.hstack((rowData,abs(ica.mixing_[chanIndex-1,i])))
                    else:
                        rowData = np.hstack((rowData, np.min(ica.mixing_)))
                if m == 0:
                    heatData = rowData
                else:
                    heatData = np.vstack((heatData,rowData))

            heatmap = ax.pcolor(heatData, cmap=plt.cm.jet,vmin=np.min(abs(ica.mixing_[:,i])), vmax=np.max(abs(ica.mixing_[:,i])))
            f1.colorbar(heatmap)

            ax.plot()

            ## frekvenčné spektrum komponentu
            ax2 = f1.add_subplot(312)

            n = len(icaSignal[8000:11400,i]) # dĺžka signálu
            k = np.arange(n)
            T = n/240
            frq = k/T
            frq = frq[range(n/2)]

            Y = np.fft.fft(icaSignal[8000:11400,i])/n # fft a normalizacia
            Y = Y[range(n/2)]
            ax2.plot(frq,abs(Y),'r')
            ax2.set_xlabel('Freq (Hz)')
            ax2.set_ylabel('|Y(freq)|')
            ax2.set_title("frequency")

            ax3 = f1.add_subplot(313)
            ax3.set_title("time course")
            ax3.plot(icaSignal[8000:11400,i])
            f1.savefig("F:/plots/IC"+str(i)+".png")

        plt.show()