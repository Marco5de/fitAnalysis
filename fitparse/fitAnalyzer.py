from fitparse import FitFile, FitParseError
import numpy as np
import matplotlib.pylab as plt
from scipy.ndimage.filters import gaussian_filter1d
import cv2
import FitObject


# todo speichern in Datei mit tagen damit ATL,CTL,TSB berechnet werden können!
# todo speichern des datums etc--> serialisierung des objekts und hinzufügen einer liste! --> möglichst so, dass ein fehler nicht alles kaputt macht
class fitAnalyzer:

    def __init__(self, ftp, fitobj):
        self.ftp = ftp
        self.fitobj = fitobj;

    def __getNormalized(self):
        # assuming there is a timestep every second --> 30 sec moving avg
        mvAvgLen = 30
        mvAvg = np.cumsum(self.fitobj.powerVec, dtype=float)
        mvAvg[mvAvgLen:] = mvAvg[mvAvgLen:] - mvAvg[:-mvAvgLen]
        mvAvg = mvAvg[mvAvgLen - 1:] / mvAvgLen
        return np.power(np.average(np.power(mvAvg, 4)), .25)

    def getIntensityFactor(self):
        return self.__getNormalized() / self.ftp

    def getTrainingStressScore(self):
        # assuming one record per second!
        return (self.fitobj.numberRecords * self.__getNormalized() * self.getIntensityFactor()) / (36 * self.ftp)

    def plotPower(self):
        avg = np.average(self.fitobj.powerVec)
        normPower = self.__getNormalized()
        print("Avg. Power: " + str(avg) + " Norm. Power: " + str(normPower))
        #sigma kann als parameter noch eingestellt werden, wie sehr gesmoothed werden soll (sieht mit 3 aber nicht schlecht aus)
        smoothedPower = gaussian_filter1d(self.fitobj.powerVec, sigma=3)
        self.__plot(smoothedPower,"Power","Time in min","Power in Watts")


    def plotSpeed(self):
        smoothedSpeed = gaussian_filter1d(self.fitobj.speedVec,sigma=3)
        self.__plot(smoothedSpeed,"Speed","Time in min","Speed in km/h")

    def plotCadence(self):
        smoothedCadence = gaussian_filter1d(self.fitobj.cadenceVec,sigma=3)
        self.__plot(smoothedCadence,"Cadence","Time in min","Cadence in 1/min")

    def __plot(self,plotVec,title,xlabel,ylabel,axis=0):
        axis = np.arange(0, self.fitobj.numberRecords / 60, 1 / 60)
        plt.plot(axis, plotVec, linewidth=1)
        plt.title(title)
        plt.xlabel(xlabel);
        plt.ylabel(ylabel)
        plt.show()
    
    def calcKmeans(self):
        data = np.transpose(np.vstack((self.fitobj.cadenceVec,self.fitobj.powerVec)))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
        compactness,labels,centers = cv2.kmeans(data,5,None,criteria,10,flags=cv2.KMEANS_RANDOM_CENTERS)
        print()
        print("Compactness: " + str(compactness))
        print("Centers: " + str(centers))

    def plotPowerCadence(self):
        colors = np.random.rand(self.fitobj.numberRecords)
        smoothedCadence = gaussian_filter1d(self.fitobj.cadenceVec,sigma=3)
        smoothedPower = gaussian_filter1d(self.fitobj.powerVec,sigma=3)
        plt.scatter(smoothedCadence,smoothedPower,c=colors,alpha=.5,s=2)
        plt.title("Power-Cadence")
        plt.show()
    


print("Opencv successfully installed: Version: " + str(cv2.__version__))
obj = FitObject.FitObject("file.fit")
ana = fitAnalyzer( 275,obj)

print("Intensity Factor: " + str(ana.getIntensityFactor()))
print("TSS: " + str(ana.getTrainingStressScore()))
ana.plotPowerCadence()
ana.plotPower()
ana.plotSpeed()
ana.plotCadence()
ana.calcKmeans()


