from fitparse import FitFile, FitParseError
import numpy as np
import matplotlib.pylab as plt
from scipy.ndimage.filters import gaussian_filter1d
import numbers


# todo refactoring, dass nicht alles 10x berechnet werden muss!
# todo speichern in Datei mit tagen damit ATL,CTL,TSB berechnet werden können!
class fitAnalyzer:
    fitfile = 0
    numberRecords = 0
    ftp = 0
    powerVec = 0

    def __init__(self, fitFilePath, ftp):
        try:
            self.fitfile = FitFile(fitFilePath)
            self.fitfile.parse()
        except FitParseError as e:
            raise NameError("Error parsing/loading .FIT file")

        self.numberRecords = self.__getRecordNumber()
        self.ftp = ftp
        self.powerVec = self.__getFieldVector("power")

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
        print()
        lock = False
        for idx, record in enumerate(self.fitfile.get_messages()):
            if lock:
                print("Total ascent: " + str(record.get_value("total_ascent")))
                print("Total calories: " + str(record.get_value("total_calories")))
                break;
            if (isinstance(record.get_value("avg_power"), numbers.Number)):
                print("Avg. Power: " + str(record.get_value("avg_power")))
                print("Avg. Cadence: " + str(record.get_value("avg_cadence")))
                print("Start time: " + str(record.get_value("start_time")))
                print("Sport: " + str(record.get_value("sport")))
                print("Max. Cadence: " + str(record.get_value("max_cadence")))
                print("Max. Power: " + str(record.get_value("max_power")))
                print("Max. Speed: " + str(record.get_value("max_speed")))
                print("Total distance: " + str(record.get_value("total_distance")))
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
        self.__getGeneralStats()
        avg = self.__getAverage(self.powerVec)
        normPower = self.__getNormalized()

        t = np.arange(0, self.numberRecords/60,1/60)
        #sigma kann als parameter noch eingestellt werden, wie sehr gesmoothed werden soll (sieht mit 3 aber nicht schlecht aus)
        smoothedPower = gaussian_filter1d(self.powerVec, sigma=3)

        plt.plot(t, smoothedPower,linewidth=1)
        plt.title("Power")
        plt.text(0, 640, str("Avg. Power: " + str(int(avg)) + "Watts"), fontsize=12, color="red")
        plt.text(0, 600, str("Norm. Power: " + str(int(normPower)) + "Watts"), fontsize=12, color="red")
        plt.xlabel("Time in min"); plt.ylabel("Power in W")
        plt.show()


ana = fitAnalyzer("file.fit", 275)
print("Anzahl an Records: " + str(ana.numberRecords))
print("Intensity Factor: " + str(ana.getIntensityFactor()))
print("TSS: " + str(ana.getTrainingStressScore()))
ana.plotPower()
