import argparse
import numpy as np

from fitparse import FitFile, FitParseError


class Timestamp:
    _valid_fields = ["cadence", "power", "distance", "altitude", "speed", "lat", "long", "temperature", "time"]
    _map_fields = {
        "cadence": "cadence",
        "power": "power",
        "distance": "distance",
        "altitude": "enhanced_altitude",
        "speed": "enhanced_speed",
        "lat": "position_lat",
        "long": "position_long",
        "temperature": "temperature",
        "time": "timestamp"
    }

    def __init__(self, record):
        self.record_dict = {}

        for record_data in record:
            self.record_dict[record_data.name] = record_data.value

    def get(self, record_name):
        assert record_name in self._valid_fields
        return self.record_dict.get(self._map_fields.get(record_name))


class SessionInfo:
    # todo noch viel mehr info! siehe jeweils dict dafür
    _valid_fiels = ["start_time", "start_position_lat", "start_position_long", "total_elapsed_time", "total_timer_time",
                    "total_distance", "total_cycles", "total_work", "time_standing", "total_calories",
                    "enhanced_avg_speed",
                    "enhanced_max_speed", "avg_power", "total_ascent", "total_descent", "normalized_power",
                    "training_stress_score", "intensity_factor", "threshold_power", "avg_heart_rate", "max_heart_rate",
                    "sport", "sub_sport", "avg_cadence", "max_cadence"]

    def __init__(self, session):
        self.session_dict = {}

        for session_msg in session:
            for data in session_msg:
                self.session_dict[data.name] = data.value

    def get(self, param_name):
        assert param_name in self._valid_fiels
        return self.session_dict.get(param_name)


def main():
    parser = argparse.ArgumentParser(description="Script for analysis of .fit files")
    parser.add_argument("-p", "--path", required=True, type=str, help="Path to .fit file")

    args = parser.parse_args()

    fit_file = None
    try:
        fit_file = FitFile(args.path)
        fit_file.parse()
    except FitParseError:
        raise FitParseError("Unable to parse fit file")

    timestamps = []

    for record in fit_file.get_messages("record"):
        timestamps.append(Timestamp(record))

    """
    events = fit_file.get_messages("event")
    for data in events:
        print(data.get_values())

    activity = fit_file.get_messages("activity")
    for data in activity:
        print(data.get_values())
    """

    session = fit_file.get_messages("session")
    session_info = SessionInfo(session)

    print(f"Sport: {session_info.get('sport')} - {session_info.get('sub_sport')}")
    print(f"Date: {session_info.get('start_time')}")
    print()
    print(f"Active time: {session_info.get('total_elapsed_time') / 60 : .1f}min " \
          f"Total time: {session_info.get('total_timer_time') / 60:.1f}min")
    print(f"Total distance: {session_info.get('total_distance') / 1000:.2f}km " \
          f"Avg. speed: {session_info.get('enhanced_avg_speed') * 3.6 : .2f}km/h")
    print(f"Total calories: {session_info.get('total_calories')}")
    print()
    print(f"Avg. power: {session_info.get('avg_power')}W Norm. power: {session_info.get('normalized_power')}W")
    print(f"TSS: {session_info.get('training_stress_score')} " \
          f"IF: {session_info.get('intensity_factor')} @ {session_info.get('threshold_power')}W FTP")
    print()
    print(f"Avg. heart rate: {session_info.get('avg_heart_rate')}bpm " \
          f"Max. heart rate: {session_info.get('max_heart_rate')}bpm")
    print(f"Avg. cadence: {session_info.get('avg_cadence')}rpm Max. cadence: {session_info.get('max_cadence')}rpm")


if __name__ == "__main__":
    main()
