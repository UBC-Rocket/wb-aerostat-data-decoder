"""
Inputting APRS data from a .txt file containing raw APRS packets, one on each line.

"""

import config
import re
import csv


def process_raw_input_legacy():

    split_contents = []
    with open(config.INPUT_FILE_NAME, 'r') as input_file:
        contents = input_file.readlines()
        first_split = [x.split(config.DATA_TYPE_IDENTIFIER) for x in contents]
        # Each split will produce a header string and 'everything else' string.

        gps_lat = [re.findall(config.GPS_LAT_FORMAT,x[1]) for x in first_split]
        gps_long = [re.findall(config.GPS_LONG_FORMAT,x[1]) for x in first_split]
        altitude_values = [re.search(config.GPS_ALT_FORMAT, (x[1])).group(0) for x in first_split]
        velocity_values = [re.findall(config.GPS_VEL_FORMAT, (x[1])) for x in first_split]

        #Make a long list, each element being a list: (gps long, gps lat, [sublist of altitudes], [sublist of velocities])
        for i in range(len(gps_lat)):
            split_contents[i][0] = float(gps_lat[i][0]) #Since gps_lat is a list of lists
            split_contents[i][1] = float(gps_long[i][0])
            split_contents[i][2] = int(altitude_values[i])
            split_contents[i][3] = int(velocity_values[i])

    return split_contents


def process_raw_input_direwolf():
    with open(config.INPUT_FILE_NAME, 'r', newline="") as input_file:
        reader = csv.DictReader(input_file)
        split_contents = [{'lat': x['latitude'], 'long': x['longitude'], 'comment': x['comment']} for x in reader]

    # There are 3 or more altitude/value measurements for each GPS measurement.
    # We want each measurement, not each transmission, to be a data point.

    processed_input = []
    for element in split_contents:
        altitude_values = re.findall(config.GPS_ALT_FORMAT, element['comment'])
        velocity_values = re.findall(config.GPS_VEL_FORMAT, element['comment'])
        for i in range(len(altitude_values)):
            # The .replace function is used to remove the 'v' or 'a' character picked up using RegEx
            processed_input.append([float(element['lat']), float(element['long']), int(altitude_values[i].replace("a","")),
                                    int(velocity_values[i].replace("v",""))])

    return processed_input