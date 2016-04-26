#coding: utf-8
from Individual import Individual
from Visualizer import Visualizer
from random import randint
from sklearn import cross_validation
from sklearn.lda import LDA

"""
Trieda pomocou genetického algoritmu vyberá vhodnú podmnožinu elektród.
"""
class ChannelManager:
    # vyber elektrod pomocou GA, vypocet fitness pomocou LDA accuracy riesenia
    indivsInGen = 50
    threshold = 1
    geneLength = 8
    eliteCount = 3

    def __init__(self, processor, chanNum):
        self.processor = processor
        self.topFitness = 0
        self.topIndiv = Individual([])
        self.chanNum = chanNum
        self.topSolutionProgress = []
        self.visualizer = Visualizer()

    # vyber jedinca na krizenie pomocou rulety, uprava fitness jedincov -min+1
    def chooseIndiv (self,aktGen):

        tmpMin = 100
        tmpMax = 0
        sumGenerationFitness = 0
        for i in range(self.indivsInGen):
            sumGenerationFitness += aktGen[i].fitness
            if aktGen[i].fitness < tmpMin:
                tmpMin = aktGen[i].fitness
            if aktGen[i].fitness > tmpMax:
                tmpMax = aktGen[i].fitness

        sumGenerationFitness+=self.indivsInGen*(tmpMax-2*tmpMin + 1)

        randomNum = randint(0,int(sumGenerationFitness))

        tmpSum = 0
        index = 0
        while tmpSum < randomNum:
            tmpSum += aktGen[index].fitness + tmpMax - 2*tmpMin + 1
            if tmpSum < randomNum:
                index+=1

        return index

    def countFitnesses(self,aktGen):
        sumFit = 0
        for i in range(len(aktGen)):
            lda = LDA(n_components=2)
            targArray = self.processor.cl.reduce(self.processor.sf,self.processor,aktGen[i].genes)
            scores = cross_validation.cross_val_score(lda,targArray, self.processor.cl.targetVals, cv=5)
            aktGen[i].fitness = scores.mean()*100

            sumFit += aktGen[i].fitness

        print "Average fitness: ", sumFit/len(aktGen)
        return sumFit/len(aktGen)

    def getSubset (self,maxSets):
        print "Getting subset!"

        aktGen = []

        # 1. vytvor prvu skupinu jedincov (random)
		# 2. ohodnot skupinu fitnesom ()
		# 3. ruleta - vyber vhodnych
		# 4. skriz -> vygeneruj generaciu
		# 5. ak neni dosiahnute optimalne riesenie ani max pocet generacii preskoc na krok 2

        # tvorba prvej generacie
        for i in range (self.indivsInGen):
            tmp = []
            for i in range (self.geneLength):
                tmp.append(randint(0,self.chanNum-1))
            ind = Individual(tmp)
            aktGen.append(ind)

        l = 0
        oldAverage = 0
        while 1:
            newGen = []
            l+=1
            print "Generation number:",l
            breaker = 0
            # vyrataj fitness aktualnej gen
            average = self.countFitnesses(aktGen)
            if l == 1:
                oldAverage = average

            for i in range (self.indivsInGen):
                # aktGen[i].countFitness(self.processor,self.targetLetter)
                if aktGen[i].fitness == 100:
                    breaker = 1
                if (aktGen[i].fitness > self.topFitness):
                    self.topIndiv = aktGen[i]
                    self.topFitness = aktGen[i].fitness
                    print "New top subset! ",self.topIndiv.genes, self.topFitness

            ## zaznamenaj aktualne top riesenie pre vysledny graf
            self.topSolutionProgress.append(self.topFitness)

            # plotnutie rozdelenia jedincov
            # if l % 25 == 0 or l == 1:
            #     self.visualizer.plotFitnessesInGeneration(aktGen)

            # test ci sa naslo top riesenie alebo ci riesenie nestagnuje
            if breaker == 1:
                break

            if l % 25 == 0:
                if average - oldAverage < self.threshold:
                    break
                else:
                    oldAverage = average


            # prida eliteCount top jedincov automaticky do novej generacie
            eliteList = sorted(aktGen, key=lambda x: x.fitness, reverse=True)[:self.eliteCount]
            newGen.extend(eliteList)


            # vygeneruj generaciu
            for m in range (self.indivsInGen - self.eliteCount):
                #ruleta - vyber jedincov na krizenie
                rNum1 = self.chooseIndiv(aktGen)
                rNum2 = self.chooseIndiv(aktGen)

                # osetrenie, aby sa krizili rozne jedince
                while rNum2 == rNum1:
                    rNum2 = self.chooseIndiv(aktGen)

                # skrizenie - sanca 90%, 10% sa prenesu rovno do dalsej generacie
                useCrossover = randint(1,10)
                if useCrossover == 1 and m != self.indivsInGen-1:
                    newGen.append(aktGen[rNum1])
                    newGen.append(aktGen[rNum2])
                    m+=1
                else:
                    newIndiv = aktGen[rNum1].crossover(aktGen[rNum2],self.chanNum)
                    newGen.append(newIndiv)

            aktGen = newGen


        # plot progress of top solution
        #self.visualizer.plotSolutionProgress(self.topSolutionProgress)

        return self.topIndiv.genes


