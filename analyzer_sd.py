from typing import List
import csv

from analyzer import Analyzer

class SDAnalyzer(Analyzer):

    def __init__(self, filename):
        super().__init__(filename)

    @property
    def data_points(self) -> List[List[float]]:
        """
            Uses the following CSV format from SD card:
                time, lat, long, gps alt (ft), sens alt (ft), pressure (Pa), temprature, wind  (kn)
            :return:
            """
        with open(self.filename, 'r', newline="") as input_file:
            reader = csv.DictReader(input_file)
            split_rows = [{'time': x['Time'], 'lat': x['Latitude'], 'long': x['Longitude'],
                           'GPS Alt': x['GPS Alt'], 'Sens Alt': x['Sens Alt'], 'Pressure': x['Pressure'],
                           'Temp': x['Sens Temp'], 'Wind': x['Windspeed']} for x in reader]

        output = []
        for row in split_rows:
            output.append([float(row['lat']), float(row['long']), float(row['GPS Alt']), float(row['Wind'])])

        return output
