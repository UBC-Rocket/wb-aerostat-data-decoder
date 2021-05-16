"""
Data decoder for WB Aerostat subteam. Converts raw APRS packets into a form usable by the wb_wind_analysis repo.

"""

import csv

from raw_input import process_raw_input_direwolf


raw_data = process_raw_input_direwolf()
print(raw_data)




def write_output(wind_datapoints):
    """Writes wind datapoints to a csv file."""
    with open("output.csv", 'r') as file:
        writer = csv.writer(file)
        file.write("Altitude,WindX,WindY\n")
        writer.writerows(wind_datapoints)