from fitparse import FitFile, FitParseError
import numpy as np
import matplotlib.pylab as plt
from scipy.ndimage.filters import gaussian_filter1d
import numbers
import cv2
import codecs, json 


# todo speichern in Datei mit tagen damit ATL,CTL,TSB berechnet werden können!
# todo speichern des datums etc--> serialisierung des objekts und hinzufügen einer liste! --> möglichst so, dass ein fehler nicht alles kaputt macht
class fitAnalyzer:
    total_calories=total_ascent=total_distance=max_cadence = 0
    avg_power=avg_cadence=start_time=sport=max_power=max_speed = 0
    
    def __init__(self, fitFilePath, ftp):
        try:
            self.fitfile = FitFile(fitFilePath)
            self.fitfile.parse()
        except FitParseError as e:
            raise NameError("Error parsing/loading .FIT file")

        self.numberRecords = self.__getRecordNumber()
        self.ftp = ftp
        self.powerVec = self.__getFieldVector("power")
        self.speedVec = self.__getFieldVector("enhanced_speed") * 3.6
        self.cadenceVec = self.__getFieldVector("cadence")
        self.__getGeneralStats()

    def __str__(self):
        return "Hier sollte ein sinnvoller string ausgegebn werden!"

    # todo is there an efficient way to do this?
    def __getRecordNumber(self):
        count = 0
        for record in self.fitfile.get_messages('record'):
            count += 1
        return count

    def __getFieldVector(self, fieldString):
        vec = np.zeros(self.numberRecords)
        i = 0
        for record in self.fitfile.get_messages('record'):
            vec[i] = record.get_value(fieldString)
            i += 1
        return vec

    def __getAverage(self, vec):
        return np.average(vec)

    # todo better way to do this?
    def __getGeneralStats(self):
        lock = False
        for idx, record in enumerate(self.fitfile.get_messages()):
            if lock:
                self.total_ascent = record.get_value("total_ascent")
                self.total_calories = record.get_value("total_calories")
                break;
            if (isinstance(record.get_value("avg_power"), numbers.Number)):
                self.avg_power = record.get_value("avg_power")
                self.avg_cadence = record.get_value("avg_cadence")
                self.start_time = record.get_value("start_time")
                self.sport = record.get_value("sport")
                self.max_cadence = record.get_value("max_cadence")
                self.max_power = record.get_value("max_power")
                self.max_speed = record.get_value("max_speed")
                self.total_distance = record.get_value("total_distance")
                lock = True


    def __getNormalized(self):
        # assuming there is a timestep every second --> 30 sec moving avg
        mvAvgLen = 30
        mvAvg = np.cumsum(self.powerVec, dtype=float)
        mvAvg[mvAvgLen:] = mvAvg[mvAvgLen:] - mvAvg[:-mvAvgLen]
        mvAvg = mvAvg[mvAvgLen - 1:] / mvAvgLen
        return np.power(np.average(np.power(mvAvg, 4)), .25)

    def getIntensityFactor(self):
        return self.__getNormalized() / self.ftp

    def getTrainingStressScore(self):
        # assuming one record per second!
        return (self.numberRecords * self.__getNormalized() * self.getIntensityFactor()) / (36 * self.ftp)

    def plotPower(self):
        avg = self.__getAverage(self.powerVec)
        normPower = self.__getNormalized()
        print("Avg. Power: " + str(avg) + " Norm. Power: " + str(normPower))
        #sigma kann als parameter noch eingestellt werden, wie sehr gesmoothed werden soll (sieht mit 3 aber nicht schlecht aus)
        smoothedPower = gaussian_filter1d(self.powerVec, sigma=3)
        self.__plot(smoothedPower,"Power","Time in min","Power in Watts")


    def plotSpeed(self):
        smoothedSpeed = gaussian_filter1d(self.speedVec,sigma=3)
        self.__plot(smoothedSpeed,"Speed","Time in min","Speed in km/h")

    def plotCadence(self):
        smoothedCadence = gaussian_filter1d(self.cadenceVec,sigma=3)
        self.__plot(smoothedCadence,"Cadence","Time in min","Cadence in 1/min")

    def __plot(self,plotVec,title,xlabel,ylabel):
        t = np.arange(0, self.numberRecords / 60, 1 / 60)
        plt.plot(t, plotVec, linewidth=1)
        plt.title(title)
        plt.xlabel(xlabel);
        plt.ylabel(ylabel)
        plt.show()
    
    def calcKmeans(self):
        data = np.transpose(np.vstack((self.cadenceVec,self.powerVec)))
        data = np.float32(data)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)
        compactness,labels,centers = cv2.kmeans(data,5,None,criteria,10,flags=cv2.KMEANS_RANDOM_CENTERS)
        print()
        print("Compactness: " + str(compactness))
        print("Centers: " + str(centers))

    def plotPowerCadence(self):
        colors = np.random.rand(self.numberRecords)
        smoothedCadence = gaussian_filter1d(self.cadenceVec,sigma=3)
        smoothedPower = gaussian_filter1d(self.powerVec,sigma=3)
        plt.scatter(smoothedCadence,smoothedPower,c=colors,alpha=.5,s=2)
        plt.title("Power-Cadence")
        plt.show()
    
    def serialize(self):
        powerList = self.powerVec.tolist() # nested lists with same data, indices
        file_path = "ser.json" ## your path variable
        json.dump({"powerList" : powerList}, codecs.open(file_path, 'w', encoding='utf-8'), separators=(',', ':'), sort_keys=True, indent=4)
    
    def deserialize(self,path):
        obj_text = codecs.open(path, 'r', encoding='utf-8').read()
        b_new = json.loads(obj_text)
        a_new = np.array(b_new)
        #print(a_new)

print("Opencv successfully installed: Version: " + str(cv2.__version__))
ana = fitAnalyzer("file.fit", 275)
print("Anzahl an Records: " + str(ana.numberRecords))
print("Intensity Factor: " + str(ana.getIntensityFactor()))
print("TSS: " + str(ana.getTrainingStressScore()))
#ana.plotPowerCadence()
#ana.plotPower()
#ana.plotSpeed()
#ana.plotCadence()
ana.calcKmeans()
print("ToString: " + str(ana))
ana.serialize()
ana.deserialize("ser.json")
