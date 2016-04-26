#coding: utf-8
from Tkinter import *
import tkFileDialog
import tkMessageBox
from Processor import Processor
from ChannelManager import ChannelManager
import threading
import ttk

trainDataFiles = []
trainLetters = []
testDataFiles = []
testLetters = []
subset = []
pr = Processor("",0)
trainedData = 0
setTrainLetterFiles = 0
setTrainDataFiles = 0
setTestLetterFiles = 0
setTestDataFiles = 0

def setButtsDisabled():
    #selectTrainDataButton.configure(state=DISABLED)
    #trainLettersButton.configure(state=DISABLED)
    trainButton.configure(state=DISABLED)
    #selectTestDataButton.configure(state=DISABLED)
    #testLettersButton.configure(state=DISABLED)
    testButton.configure(state=DISABLED)

def setButtsNormal():
    # selectTrainDataButton.configure(state=NORMAL)
    # trainLettersButton.configure(state=NORMAL)
    trainButton.configure(state=NORMAL)
    # selectTestDataButton.configure(state=NORMAL)
    # testLettersButton.configure(state=NORMAL)
    testButton.configure(state=NORMAL)

def getTrainDataFiles():
    #ziska nazvy suborov
    filez = list(tkFileDialog.askopenfilenames(parent=root,title='Choose a file'))
    global trainDataFiles,setTrainDataFiles


    trainDataFilesView.configure(state='normal')
    if (len(filez) != 0):
        trainDataFilesView.delete('1.0', END)
        trainDataFiles = [x.encode('ascii','ignore') for x in filez]
        setTrainDataFiles = 1
    for i in range (len(trainDataFiles)):
        trainDataFilesView.insert(INSERT, trainDataFiles[i]+"\n")

    trainDataFilesView.configure(state='disabled')

def getTrainLetterFiles():
    #ziska nazvy suborov
    file = tkFileDialog.askopenfilename(parent=root,title='Choose a file')
    global trainLetters,setTrainLetterFiles


    trainLettersView.configure(state='normal')
    if (len(file) != 0):
        trainLettersView.delete('1.0', END)
        trainLetters = file.encode('ascii','ignore')
        setTrainLetterFiles = 1
    trainLettersView.insert(INSERT, trainLetters+"\n")
    trainLettersView.configure(state='disabled')

def getTestDataFiles():
    #ziska nazvy suborov
    filez = list(tkFileDialog.askopenfilenames(parent=root,title='Choose a file'))
    global testDataFiles,setTestDataFiles

    testDataFilesView.configure(state='normal')
    if (len(filez) != 0):
        testDataFilesView.delete('1.0', END)
        testDataFiles = [x.encode('ascii','ignore') for x in filez]
        setTestDataFiles = 1
    for i in range (len(testDataFiles)):
        testDataFilesView.insert(INSERT, testDataFiles[i]+"\n")

    testDataFilesView.configure(state='disabled')

def getTestLetterFiles():
    #ziska nazvy suborov
    file = tkFileDialog.askopenfilename(parent=root,title='Choose a file')
    global testLetters,setTestLetterFiles
    testLettersView.configure(state='normal')
    if (len(file) != 0):
        testLettersView.delete('1.0', END)
        testLetters = file.encode('ascii','ignore')
        setTestLetterFiles = 1
    testLettersView.insert(INSERT, testLetters+"\n")
    testLettersView.configure(state='disabled')

def trainClassifier():
    if useEpoc.get() != 1:
        chanNum = 64
    else:
        chanNum = 14

    def train():
        repsCount.configure(state=DISABLED)
        setButtsDisabled()
        progTrainLabel["text"] = 'Filtrujem signál...'
        trainProgress["value"] = 0
        global pr,trainedData
        trainLetter = []

        trainWords = open(trainLetters).readlines()

        #nacitanie trenovacich a cielovych znakov do pola
        for i in range(len(trainWords)):
            tmp = map(int, trainWords[i].rstrip().split(','))
            trainLetter.append(tmp)


        trainProgress["maximum"] = len(sum(trainLetter[:len(trainDataFiles)],[])) - 1

        pr = Processor(trainDataFiles,chanNum)
        # postupne spracuj trenovaciu cast datasetu
        pr.trainClassifier(trainLetter,trainProgress,progTrainLabel,int(repsCount.get()))
        progTrainLabel["text"] = 'Trénovanie dokončené.'
        repsCount.configure(state=NORMAL)
        setButtsNormal()
        trainedData = 1
        print "Training completed"


    if setTrainDataFiles != 0:
        if setTrainLetterFiles != 0:
            if len(repsCount.get()) != 0:
                t = threading.Thread(target=train)
                t.start()
            else:
                tkMessageBox.showinfo("Chyba", "Nastav počet setov vysvietení!")
        else:
            tkMessageBox.showinfo("Chyba", "Chýba označenie tréningových znakov")
    else:
        tkMessageBox.showinfo("Chyba", "Chýbajú tréningové data subóry")

def test():
    if useEpoc.get() != 1:
        chanNum = 64
    else:
        chanNum = 14

    global trainedData
    def testFunc():
        setButtsDisabled()
        guessView.delete('1.0', END)
        progTestLabel["text"] = 'Získavam množinu elektród...'
        succesLab["text"] = 'Presnosť:'
        testProgress["value"] = 0
        global pr,subset
        targetLetter = []
        targWords = open(testLetters).readlines()

        #nacitanie trenovacich a cielovych znakov do pola
        for i in range(len(targWords)):
            tmp = targWords[i].rstrip().split(',')
            targetLetter.append(tmp)

        testProgress["maximum"] = len(sum(targetLetter[:len(testDataFiles)],[])) - 1

        if radioVar.get() == 2:
            subset = []
            for i in range(chanNum):
                subset.append(i)
        else:
            channelManager = ChannelManager(pr,chanNum)
            subset = channelManager.getSubset(int(repsCount.get()))

            # subset = [15,16,17,18,19,49,50,51]
            #subset =[15,17,19,56,58,31,35,10]


        pr.guessChars(subset,testDataFiles,targetLetter,testProgress,progTestLabel,guessView,succesLab,int(repsCount.get()))
        progTestLabel["text"] = 'Testovanie dokončené.'
        setButtsNormal()

    if setTestDataFiles != 0:
        if trainedData == 1:
            t = threading.Thread(target=testFunc)
            t.start()
        else:
            tkMessageBox.showinfo("Chyba", "Najprv treba natrénovať klasifikátor")
    else:
        tkMessageBox.showinfo("Chyba", "Chýbajú testavacie data subóry")



########### GUI #######################

# create the window
root = Tk()

#modify the root window
root.wm_state('zoomed')
root.title("P300 Detector")
root.geometry("1300x700")

mainFrame = Frame(root, padx=10, pady=10)
mainFrame.grid(row=0,column=0)

## rozlozenie na 3 sekcie
leftFrame = Frame(mainFrame, padx=10,relief=GROOVE,borderwidth=2)
leftFrame.grid(row=0,column=0)
rightFrame = Frame(mainFrame, padx=10,relief=GROOVE,borderwidth=2)
rightFrame.grid(row=0,column=1,sticky=N)
botFrame = Frame(mainFrame, pady=25,padx=10,relief=RIDGE,borderwidth=2)
botFrame.grid(row=1,columnspan=2)

### TRAIN PART ###
#row0
labelTrainFiles = Label(leftFrame, text='Vyber trénovacie súbory').grid(row=0, column=0,sticky=W)
selectTrainDataButton = Button(leftFrame, text = "Vyber", command = getTrainDataFiles)
selectTrainDataButton.grid(row=0, column=1,sticky=E)

#row1
trainDataFilesView = Text(leftFrame,state='disabled', padx = "8px", height = 5, width = 65)
scrollb = Scrollbar(leftFrame, command=trainDataFilesView.yview)
trainDataFilesView['yscrollcommand'] = scrollb.set
trainDataFilesView.grid(row=1, columnspan = 2)
scrollb.grid(row=1, column=3, sticky='nswe')

#row2
trainLettersLabel = Label(leftFrame, text='Vyber súbory s trénovacími znakmi').grid(row=2,column=0,sticky=W)
trainLettersButton = Button(leftFrame, text = "Vyber", command = getTrainLetterFiles)
trainLettersButton.grid(row=2,column=1,sticky=E)

#row3
trainLettersView = Text(leftFrame,state='disabled', padx = "8px", height = 1, width = 65)
trainLettersView.grid(row=3,columnspan = 2)

#row4
optionsFrame = Frame(leftFrame)
optionsFrame.grid(row=4,columnspan = 2,sticky=W)

#row5
trainButton = Button(leftFrame, text = "Trénuj", command = trainClassifier, width = 15)
trainButton.grid(row=5, column = 1, sticky=E)
repsLabel = Label(leftFrame, text='Počet setov vysvietení:').grid(row=5,column=0,sticky=W)
repsCount = Entry(leftFrame, width = 5)
repsCount.grid(row=5, column = 1,sticky=W)

#row6
trainProgress = ttk.Progressbar(leftFrame,orient="horizontal",length=300, mode="determinate")
trainProgress.grid(row=6, column=1, sticky=E)
progTrainLabel = Label(leftFrame, text='Priebeh trénovania')
progTrainLabel.grid(row=6, column=0,sticky=W)

### sekcia volby elektrod a typu dat
radioVar = IntVar()
R1 = Radiobutton(optionsFrame, text="Nájdi optimálnu podmnožinu elektród", variable=radioVar, value=1)
R2 = Radiobutton(optionsFrame, text="Použi všetky elektródy", variable=radioVar, value=2)

R1.grid(row=0,column = 1, sticky=W)
R2.grid(row=0,column = 2, sticky=W)
R2.select()

# EPOC checkbox
useEpoc = IntVar()
useEpocBox = Checkbutton(optionsFrame, text = "Epoc dáta", variable = useEpoc, \
                 onvalue = 1, offvalue = 0, height=5, \
                 width = 20)
useEpocBox.grid(row=0,column = 0, sticky=W)

leftFrame.rowconfigure(6,pad=20)
leftFrame.rowconfigure(0,pad=20)
leftFrame.rowconfigure(2,pad=20)

### TEST PART ###
#row0
labelTestFiles = Label(rightFrame, text='Vyber testovacie súbory').grid(row=0, column=0,sticky=W)
selectTestDataButton = Button(rightFrame, text = "Vyber", command = getTestDataFiles)
selectTestDataButton.grid(row=0, column=1,sticky=E)

#row1
testDataFilesView = Text(rightFrame,state='disabled', padx = "18px", height = 5, width = 65)
scrollb = Scrollbar(rightFrame, command=testDataFilesView.yview)
testDataFilesView['yscrollcommand'] = scrollb.set
testDataFilesView.grid(row=1, columnspan=2)
scrollb.grid(row=1, column=3, sticky='nswe')

#row2
testLettersLabel = Label(rightFrame, text='Vyber súbory obsahujúce cieľové testovacie znaky').grid(row=2,column=0,sticky=W)
testLettersButton = Button(rightFrame, text = "Vyber", command = getTestLetterFiles)
testLettersButton.grid(row=2,column=1,sticky=E)

#row3
testLettersView = Text(rightFrame,state='disabled', padx = "18px", height = 1, width = 65)
testLettersView.grid(row=3,columnspan=2)

#row4
empty6 =  Label(rightFrame, text='').grid(row=4, columnspan=3)

#row5
testButton = Button(rightFrame, text = "Testuj", command = test, width = 15)
testButton.grid(row=5,columnspan=3, sticky = E)

#row6
testProgress = ttk.Progressbar(rightFrame,orient="horizontal",length=300, mode="determinate")
testProgress.grid(row=6, column=1, sticky = E)
progTestLabel = Label(rightFrame, text='Priebeh testovania')
progTestLabel.grid(row=6, column=0,sticky=W)

#row config
rightFrame.rowconfigure(0,pad=20)
rightFrame.rowconfigure(2,pad=20)
rightFrame.rowconfigure(6,pad=20)

#################### GUESSED FIELD #############################
succesLab =  Label(botFrame, text='Presnosť:')
succesLab.grid(row=0, column=0, sticky=W)

guessView = Text(botFrame,state='disabled', padx = "5px", height = 2)
guessView.grid(row=1,rowspan=2,column=0,columnspan = 2)

botFrame.rowconfigure(1,pad=20)

#zobrazenie okna
root.mainloop()

