"""
Inputting APRS data from a .txt file containing raw APRS packets, one on each line.

"""

import config
import re
import csv
from unpack import unpack_latitude, unpack_altitude, unpack_longitude, unpack_wind_speed


def process_input_legacy():

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


def process_input_dw_standard():
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


def process_input_dw_compressed():

    # For now, assume that DireWolf decompresses the GPS latitude, longitude, and altitude properly, but not comment.

    with open(config.INPUT_FILE_NAME, 'r', newline="") as input_file:
        reader = csv.DictReader(input_file)
        split_rows_A = [{'lat': x['latitude'], 'long': x['longitude'], 'alt': x['altitude'], 'comment': x['comment']} for x in reader]

    for element in split_rows_A:
        # first char in comment is for latest windspeed
        # then come the additional GPS positions (end index 8*GPS_QUANTITY acknowledges that we start at index 1, not 0)
        # finally come all of the altitude/velocity data, to the very end
        latest_wind_speed = unpack_wind_speed(element['comment'][0])
        gps_data_stringchain = element['comment'][1:(8*config.COMPR_GPS_QUANTITY)]
        sens_data_stringchain = element['comment'][(1+8*config.COMPR_GPS_QUANTITY):-1]

        latitudes = []
        longitudes = []
        altitudes = []
        wind_speeds = []

        # Split each string contianing multiple GPS/sensor datapoints into individual pieces of data
        # example: Lat1Long1Lat2Long2Lat3Long3 --> (Lat1, Lat2, Lat3...) and (Long1, Long2, Long3...
        for i in range(len(config.COMPR_GPS_QUANTITY - 1)):
            latitudes[i] = unpack_latitude(gps_data_stringchain[(8*i):(8*(i+1)-5)])
            longitudes[i] = unpack_longitude(gps_data_stringchain[((8*i)+4):(8*(i+1)-1)])

        for i in range(len(config.COMPR_SENS_QUANTITY - 1)):
            altitudes[i] = unpack_altitude(sens_data_stringchain[(3*i):(3*(i+1)-2)])
            wind_speeds[i] = unpack_wind_speed(sens_data_stringchain[(3*i)+2])

        # Append the latest data, which doesn't come from the comment (except for windspeed which does)
        latitudes.append(float(element['lat']))
        longitudes.append(float(element['long']))
        altitudes.append(float(element['alt']))
        wind_speeds.append(float(latest_wind_speed))

        return {'lats': latitudes, 'longs': longitudes, 'altitudes': altitudes, 'wind_speeds': wind_speeds}





