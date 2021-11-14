from typing import List, Dict, Union
import csv

import analyzer
import config

class CompressedAnalyzer(analyzer.Analyzer):
    """
    Parent class for analyzers that deal with base-91 compressed data.
    """

    def __init__(self, filename, timestep):
        super().__init__(filename, timestep)

    @property
    def data_points(self) -> List[List[float]]:

        return []


    """
    Supporting functions for data_points
    """

    @staticmethod
    def process_input(raw: List[Dict[str, Union[List, str]]]) -> List[List[float]]:

        ds = []
        for element in raw:
            # last char in comment is for latest windspeed
            # then come the additional GPS positions (end index 8*GPS_QUANTITY acknowledges that we start at index 1, not 0)
            # finally come all of the altitude/velocity data, to the very end
            latest_wind_speed = CompressedAnalyzer.unpack_wind_speed(element['comment'][-1])
            gps_data_stringchain = element['comment'][0:(8 * (config.GPS_POINTS_DESIRED - 1))]
            sens_data_stringchain = element['comment'][
                                    (8 * (config.GPS_POINTS_DESIRED - 1)):-1]  # from end of GPS sentence!

            latitudes = []
            longitudes = []
            altitudes = []
            wind_speeds = []

            # Split each string contianing multiple GPS/sensor datapoints into individual pieces of data
            # example: Lat1Long1Lat2Long2Lat3Long3 --> (Lat1, Lat2, Lat3...) and (Long1, Long2, Long3...
            for i in range(config.GPS_POINTS_DESIRED - 1):
                latitudes.append(CompressedAnalyzer.unpack_latitude(gps_data_stringchain[(8 * i):(8 * (i + 1) - 4)]))
                longitudes.append(
                    CompressedAnalyzer.unpack_longitude(gps_data_stringchain[((8 * i) + 4):(8 * (i + 1))]))

            for i in range(config.SENS_POINTS_DESIRED - 1):
                altitudes.append(CompressedAnalyzer.unpack_altitude(sens_data_stringchain[(3 * i):(3 * (i + 1) - 1)]))
                wind_speeds.append(CompressedAnalyzer.unpack_wind_speed(sens_data_stringchain[(3 * i) + 2]))

            # Append the latest data, which doesn't come from the comment (except for windspeed which does)
            latitudes.append(float(element['lat']))
            longitudes.append(float(element['long']))
            altitudes.append(float(element['alt']))
            wind_speeds.append(float(latest_wind_speed))

            ds.append(
                {'lats': latitudes, 'longs': longitudes, 'altitudes': altitudes, 'wind_speeds': wind_speeds})

        data_points_builder = []
        for i in range(len(ds) - 1):
            interpolated_pos = CompressedAnalyzer.interpolate_gps_positions(ds[i],
                                                                    ds[i + 1])  # We lose the first minute of data
            for j in range(config.SENS_POINTS_DESIRED):
                data_points_builder.append(
                    [interpolated_pos[j][0], interpolated_pos[j][1], ds[i + 1]['altitudes'][j],
                     ds[i + 1]['wind_speeds'][j]])

        return data_points_builder

    @staticmethod
    def base91_to_int(compressed_char):
        """
        :param compressed_char: a base91 compressed character
        :return: the number in base 91 corresponding to that character
        """
        return ord(compressed_char) - 33

    @staticmethod
    def unpack_latitude(compressed_string):
        """
        :param compressed_string: A 4-character string containing a gps latitude in base91 format
        :return: Signed gps latitude in decimal degrees format
        """
        st = [CompressedAnalyzer.base91_to_int(x) for x in compressed_string]
        return 90.0 - (st[0] * 91.0 ** 3 + st[1] * 91.0 ** 2 + st[2] * 91.0 + st[3]) / 380926.0

    @staticmethod
    def unpack_longitude(compressed_string):
        """
        :param compressed_string: A 4-character string containing a gps longitude in base91 format
        :return: Signed gps longitude in decimal degrees format
        """
        st = [CompressedAnalyzer.base91_to_int(x) for x in compressed_string]
        return -180.0 + (st[0] * 91.0 ** 3 + st[1] * 91.0 ** 2 + st[2] * 91.0 + st[3]) / 190463.0

    @staticmethod
    def unpack_altitude(compressed_string):
        """
        :param compressed_string: A 2-character string containing a gps altitude in base91 format
        :return: Altitude, in meters, to 0.4% accuracy
        """
        alt = [CompressedAnalyzer.base91_to_int(x) for x in compressed_string]
        if (alt[0] > 124) or (alt[1] > 124):
            return 0.12345
            # In case of glitch, where an ASCII value ends up being too high, set the altitude to zero. At least we'll know a glitch occured.
        else:
            return CompressedAnalyzer.feet_to_meters(1.002 ** (alt[0] * 91.0 + alt[1]))

    @staticmethod
    def unpack_wind_speed(compressed_string):
        """
        :param compressed_string: A 1-character string containing a wind speed measurement in base91 format
        :return: Wind speed, in km/h.
        """
        return CompressedAnalyzer.knots_to_meters_per_sec(1.08 ** CompressedAnalyzer.base91_to_int(compressed_string) - 1.0)

    @staticmethod
    def fix_ascii_slashes(s: Str):

        s_new = s

        for i in range(len(s_new) - 1):
            if s_new[i : i+1] == "\\\'":
                s_new.replace("\\\'", "\'")
            elif s[i : i+1] == '\\\"':
                s_new.replace('\\\"', '\"')
            elif s[i : i+1] == '\\\\':
                s_new.replace('\\\\', "\\")
        return s_new

    """
    Relating to GPS interpolation
    """

    @staticmethod
    def interpolate_linear(lat1, long1, lat2, long2, ratio):
        """Given two GPS points, you can draw a straight line between them. Then estimate the position
        of the balloon between two GPS data measurements using that straight line.
        :param lat1: latitude of first point
        :param lat2: latitude of second point
        :param long1: longitude of first point
        :param long2: longitude of second point
        :param ratio: the ratio signifying the fractional distance between the two points (ex. 0.5 = half way)
        :return: a list containing tuples of intermediate (lat, long) points.
        """
        lat_intrmd = lat1 + ratio * (lat2 - lat1)
        long_intrmd = long1 + ratio * (long2 - long1)
        return [lat_intrmd, long_intrmd]

    @staticmethod
    def interpolate_gps_positions(unpacked_prev, unpacked_curr):
        """
        IMPORTANT: the number of GPS positions must be the same for both unpacked1 and unpacked2. Same thing with the number
        of sensor measurements. The function assumes that the number of sensor measurements determines the number of final
        gps positions.

        :param unpacked_prev: A dictionary containing the latitudes, longitudes, altitudes, and wind velocities observed
                            during the previous minute's transmission.
        :param unpacked_curr: A dictionary containing the " during the current minute's transmission
        :return: A list of datapoints containing " where some of the GPS data has been interpolated.
        """
        output_positions = []
        q_known = len(unpacked_curr['lats'])
        q_want = len(unpacked_curr['altitudes'])

        for i in range(q_want):
            # Checks if we'll find a measurement in the known set that is at the same relative time as in the want set.
            if q_known / q_want * i % 1 == 0:
                # No interpolation
                output_positions.append([unpacked_curr['lats'][int(q_known / q_want * i)],
                                         unpacked_curr['longs'][int(q_known / q_want * i)]])
            else:
                # Interpolate
                next_latest = 1 / q_known
                while next_latest < i / q_want:
                    next_latest += 1 / q_known

                ratio = q_known * (i / q_want - next_latest)
                if i == 1:
                    output_positions.append(CompressedAnalyzer.interpolate_linear(unpacked_prev['lats'][-1], unpacked_prev['longs'][-1],
                                                                                  unpacked_curr['lats'][i], unpacked_curr['longs'][i],
                                                                                  ratio))
                else:
                    output_positions.append(
                        CompressedAnalyzer.interpolate_linear(unpacked_curr['lats'][i - 1], unpacked_curr['longs'][i - 1],
                                                              unpacked_curr['lats'][i], unpacked_curr['longs'][i], ratio))

        return output_positions
