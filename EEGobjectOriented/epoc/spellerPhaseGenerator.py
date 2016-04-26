import numpy as np

from numpy import genfromtxt

for l in range (10):
    for m in range (7):
        my_data = genfromtxt('F:/participant'+str(l+1)+'/spellerCode'+str(m+1)+'.csv', delimiter=',')
        stimCode = my_data[1:]

        output = []
        state = 1
        isiDone = 0
        for i in range (len(stimCode)):
            if stimCode[i] != 0 and i != 0 and stimCode[i-1] == 0:
                isiDone+=1
                state = 2

            if state == 2 and isiDone == 180 and stimCode[i] == 0:
                isiDone = 0
                state = 3

            output.append(str(state))

        import csv
        b = open('F:/participant'+str(l+1)+'/spellerPhase'+str(m+1)+'.csv', 'wb')
        a = csv.writer(b)
        a.writerows(output)
        b.close()

print "done"