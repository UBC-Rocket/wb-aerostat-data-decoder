from typing import List
import csv

from analyzer import Analyzer


class SDAnalyzer(Analyzer):

    def __init__(self, filename, timestep):
        super().__init__(filename, timestep)

    @property
    def data_points(self) -> List[List[float]]:
        """
            Uses the following CSV format from SD card:
                time, lat, long, gps alt (ft), sens alt (ft), pressure (Pa), temperature, wind  (kn)
            :return:
            """
        with open(self.filename, 'r', newline="") as input_file:
            reader = csv.DictReader(input_file)
            split_rows = [{'time': x['Time'],
                           'lat': x['Latitude'],
                           'long': x['Longitude'],
                           'GPS Alt': x['GPS Alt'],
                           'Sens Alt': x['Sens Alt'],
                           'Pressure': x['Pressure'],
                           'Temp': x['Sens Temp'],
                           'Wind': x['Windspeed']
                           } for x in reader]

        output = []
        for row in split_rows:
            output.append(
                [float(row['lat']),
                 float(row['long']),
                 Analyzer.feet_to_meters(float(row['GPS Alt'])),
                 Analyzer.knots_to_meters_per_sec(float(row['Wind']))
                 ])

        return output
