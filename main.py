"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""

import csv
from statistics import mean

from raw_input import process_raw_input_direwolf
from calculation import calculate_components_dd


def write_output(datapoints):
    """Writes wind datapoints to a csv file."""
    with open("output.csv", 'w', newline="") as file:
        writer = csv.writer(file)
        file.write("Altitude,WindY,WindX\n")
        writer.writerows(datapoints)



raw_data = process_raw_input_direwolf()

datapoints = []
for i in range(len(raw_data)-1):
    (y_wind, x_wind) = calculate_components_dd(raw_data[i+1][1], raw_data[i][1],
                                                            raw_data[i+1][0],raw_data[i][0],
                                                            raw_data[i+1][2],raw_data[i][2],
                                                            mean([raw_data[i+1][3], raw_data[i][3]]),
                                                            20)
    datapoints.append([raw_data[i][2], x_wind, y_wind])


write_output(datapoints)

