#coding: utf-8
from Processor import Processor
from ChannelManager import ChannelManager


"""
Trieda slúži na testovacie spustenie metódy bez grafického rozhrania. Aby fungovala treba v triede procesor vypnúť
(zakomentovať) update GUI elementov.
"""

# inicializacia
chanNum = 14
repsCount = 15
pr = Processor("",0)
trainLetters = "epoc/etc/trainWords.txt"
testLetters = "epoc/etc/targetWords.txt"
trainDataFiles = []
testDataFiles = []

for i in range (5):
        trainDataFiles.append("epoc/spellerCode"+str(i+1)+".csv")
for i in range (5):
        trainDataFiles.append("epoc/spellerEEG"+str(i+1)+".csv")
for i in range (5):
        trainDataFiles.append("epoc/spellerPhase"+str(i+1)+".csv")

for i in range (2):
        testDataFiles.append("epoc/spellerCode"+str(i+6)+".csv")
for i in range (2):
        testDataFiles.append("epoc/spellerEEG"+str(i+6)+".csv")
for i in range (2):
        testDataFiles.append("epoc/spellerPhase"+str(i+6)+".csv")

# trénovanie klasifikátora
def train():
        global pr
        trainLetter = []

        trainWords = open(trainLetters).readlines()

        #nacitanie trenovacich a cielovych znakov do pola
        for i in range(len(trainWords)):
            tmp = map(int, trainWords[i].rstrip().split(','))
            trainLetter.append(tmp)

        pr = Processor(trainDataFiles,chanNum)
        # postupne spracuj trenovaciu cast datasetu
        pr.trainClassifier(trainLetter,repsCount)
        trainedData = 1
        print "Training completed"

# hádanie cieľových znakov
def testFunc():
        global pr,subset
        targetLetter = []
        targWords = open(testLetters).readlines()

        #nacitanie trenovacich a cielovych znakov do pola
        for i in range(len(targWords)):
            tmp = targWords[i].rstrip().split(',')
            targetLetter.append(tmp)

        channelManager = ChannelManager(pr,chanNum)
        #subset = channelManager.getSubset(repsCount)
        subset =[1,2,3,4,5,6,7,8,9,10,11,12,13,0]

        pr.guessChars(subset,testDataFiles,targetLetter,repsCount)

# beh programu
train()
testFunc()

