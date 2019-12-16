from fitparse import FitFile,FitParseError
import sys
import numpy as np
import matplotlib.pylab as plt

#todo is there an efficient way to do this?
def getRecordNumber(fitFile):
    count = 0
    for record in fitFile.get_messages('record'):
        count+=1
    return count

def getFieldVector(fitFile,fieldString,len):
    vec = np.zeros(len)
    i = 0
    for record in fitFile.get_messages('record'):
        vec[i] = record.get_value(fieldString)
        i+=1
    return vec

def getAverage(vec):
    return np.average(vec)


try:
    fitfile = FitFile("file.fit")
    fitfile.parse()
except FitParseError as e:
    print("Error parsing .FIT file")
    sys.exit(1)

anzahl = getRecordNumber(fitfile)
vec=getFieldVector(fitfile,"power",anzahl)
print("Vec: Länge: " + str(vec.size) + " Vec: " + str(vec))
print("Nach 2600sec: " + str(vec[2600]) + "Watts")
#stimmt mit strava überein!
print("Durchscnitt: " + str(getAverage(vec)))


#visualizing
t = np.arange(0,anzahl)
plt.plot(t,vec)
plt.show()


