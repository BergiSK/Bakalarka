#coding: utf-8

from random import randint

"""
Trieda je reprezentáciou jedinca pre genetický algoritmus, každý gén predstavuje použitú elektródu.
"""

class Individual:

    numGenes = 8

    def __init__(self,subset):
        self.genes = subset
        self.fitness = 0

    # jednoduche krizenie v jednom bode
    def crossover (self,indiv2,chanNum):
        minimumGenesTransimitted = 2
        new = []
        crossPoint = randint(minimumGenesTransimitted,self.numGenes-minimumGenesTransimitted)


        for i in range(self.numGenes):
            # 1<= a <= 1000 -- 1000 cisiel; sanca 0,1x8 genov = 0,8%
            useMutation = randint(1,1000)

            if i < crossPoint:
                if useMutation == 1:
                    mutatedGene = randint(0,chanNum-1)
                    new.append(mutatedGene)
                else:
                    new.append(self.genes[i])
            else:
                if useMutation == 1:
                    mutatedGene = randint(0,chanNum-1)
                    new.append(mutatedGene)
                else:
                    new.append(indiv2.genes[i])

        child = Individual(new)
        return child
