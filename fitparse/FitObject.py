import codecs
import json
import numbers

import numpy as np
from fitparse import FitFile, FitParseError
import importlib

importlib.import_module("FitObject")


class FitObject:
    total_calories = total_ascent = total_distance = max_cadence = 0
    avg_power = avg_cadence = start_time = sport = max_power = max_speed = 0
    fitfile = numerRecords = powerVec = speedVec = cadenceVec = 0

    def __init__(self, path, readJson=False):
        if not readJson:
            self.__path = path
            try:
                self.fitfile = FitFile(self.__path)
                self.fitfile.parse()
            except FitParseError as e:
                raise NameError("Error parsing/loading .FIT file")

            self.numberRecords = self.__getRecordNumber()
            self.powerVec = self.__getFieldVector("power")
            self.speedVec = self.__getFieldVector("enhanced_speed") * 3.6
            self.cadenceVec = self.__getFieldVector("cadence")
            self.__getGeneralStats()
        else:
            self.deserialize(path)

    def __str__(self):
        outstr = ""
        outstr += ("Fitobject: " + str(self.start_time) + "\n")
        outstr += ("Avg. Power: " + str(self.avg_power) + "Watts" + "\n")
        outstr += ("Distance: " + str(self.total_distance / 1000) + "km" + "\n")
        outstr += ("Ascent: " + str(self.total_ascent) + "m" + "\n")
        outstr += ("Calories burned: " + str(self.total_calories) + "kcal" + "\n")
        outstr += ("Avg. Cadence: " + str(self.avg_cadence) + "1/min" + "\n")
        outstr += ("Max. speed: " + str(self.max_speed * 3.6) + "km/h" + "\n")
        outstr += ("Max. Power: " + str(self.max_power) + "Watts" + "\n")
        outstr += ("Max. Cadence: " + str(self.max_cadence) + "1/min" + "\n")
        return outstr

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

    def __getNormalized(self):
        # assuming there is a timestep every second --> 30 sec moving avg
        mvAvgLen = 30
        mvAvg = np.cumsum(self.powerVec, dtype=float)
        mvAvg[mvAvgLen:] = mvAvg[mvAvgLen:] - mvAvg[:-mvAvgLen]
        mvAvg = mvAvg[mvAvgLen - 1:] / mvAvgLen
        return np.power(np.average(np.power(mvAvg, 4)), .25)

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

    def serialize(self, outPath):
        data = {}
        data["ascent"] = self.total_ascent
        data["calories"] = self.total_calories
        data["totalDistance"] = self.total_distance
        data["max_speed"] = self.max_speed
        data["max_power"] = self.max_power
        data["max_candence"] = self.max_cadence
        data["sport"] = self.sport
        data["avg_cadence"] = self.avg_cadence
        data["avg_power"] = self.avg_power
        data["speedVec"] = self.speedVec.tolist()
        data["powerVec"] = self.powerVec.tolist()
        data["cadenceVec"] = self.cadenceVec.tolist()
        data["start_time"] = str(self.start_time)

        json.dump(data, codecs.open(outPath, 'w', encoding='utf-8'), separators=(',', ':'),
                  sort_keys=True, indent=4)

    def deserialize(self, path):
        data = json.loads(codecs.open(path, 'r', encoding='utf-8').read())
        self.total_ascent = data["ascent"]
        self.total_calories = data["calories"]
        self.total_distance = data["totalDistance"]
        self.max_speed = data["max_speed"]
        self.max_power = data["max_power"]
        self.max_cadence = data["max_candence"]
        self.sport = data["sport"]
        self.avg_cadence = data["avg_cadence"]
        self.avg_power = data["avg_power"]
        self.speedVec = np.array(data["speedVec"])
        self.powerVec = np.array(data["powerVec"])
        self.cadenceVec = np.array(data["cadenceVec"])
        self.start_time = data["start_time"]
