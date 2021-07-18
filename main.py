"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""

import csv
from statistics import mean

from input import process_input_dw_compressed
from calculation import calculate_components_dd, interpolate_gps_positions
import config
from unpack import feet_to_meters, knots_to_kilom


def write_output(datapoints):
    """Writes wind datapoints to a csv file."""
    with open("output.csv", 'w', newline="") as file:
        writer = csv.writer(file)
        file.write("Altitude,WindY,WindX\n")
        writer.writerows(datapoints)


def write_map_output(raw_data):
    with open("map_output.csv", 'w', newline="") as mapfile:
        mapfile.write("Datapoint_ID,Latitude,Longitude,Altitude\n")
        for i in range(len(raw_data)):
            mapfile.write(f"{i+1},{raw_data[i][0]},{raw_data[i][1]},{raw_data[i][2]}\n")



raw_data = process_input_dw_compressed()
cleaned_data = []
for i in range(len(raw_data) - 1):
    new_data = interpolate_gps_positions(raw_data[i], raw_data[i+1]) # We lose the first minute of data
    for j in range(config.COMPR_SENS_QUANTITY):
        cleaned_data.append([new_data[j][0], new_data[j][1], feet_to_meters(raw_data[i+1]['altitudes'][j]), knots_to_kilom(raw_data[i+1]['wind_speeds'][j])])

datapoints = []
for i in range(len(cleaned_data) - 1):
    (y_wind, x_wind) = calculate_components_dd(cleaned_data[i + 1][1], cleaned_data[i][1],
                                               cleaned_data[i + 1][0], cleaned_data[i][0],
                                               cleaned_data[i + 1][2], cleaned_data[i][2],
                                               mean([cleaned_data[i + 1][3], cleaned_data[i][3]]),
                                               60/config.COMPR_SENS_QUANTITY)
    datapoints.append([cleaned_data[i][2], y_wind, x_wind])


write_output(datapoints)
write_map_output(cleaned_data)
