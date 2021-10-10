"""
Parent class for Analyzers
"""
from typing import List
import math
from statistics import mean
import csv

import config


class Analyzer:
    """"""
    """
    High level functions
    """

    def __init__(self, filename):
        """Should create data_points from file input"""
        self.filename = filename

    @property
    def data_points(self) -> List[List[float]]:
        """
        List of data points where each data point is [Lat, Long, Altitude, sensor wind speed]
        """
        return []

    @property
    def vectors(self) -> [List[List[float]]]:
        """
        List of velocity vectors for a given altitude; Format for each point [Altitude, Y_component, X_component]
        """
        temp = []
        for i in range(len(self.data_points) - 1):
            (y_wind, x_wind) = Analyzer.calculate_components_dd(self.data_points[i + 1][1], self.data_points[i][1],
                                                                self.data_points[i + 1][0], self.data_points[i][0],
                                                                self.data_points[i + 1][2], self.data_points[i][2],
                                                                mean([self.data_points[i + 1][3],
                                                                      self.data_points[i][3]]),
                                                                config.TIME_STEP)
            temp.append([self.data_points[i][2], y_wind, x_wind])

        return temp

    def output_vectors(self):

        with open("output.csv", 'w', newline="") as file:
            writer = csv.writer(file)
            file.write("Altitude,WindY,WindX\n")
            writer.writerows(self.vectors)

    def output_map_line(self):
        with open("map_output.csv", 'w', newline="") as mapfile:
            mapfile.write("Datapoint_ID,Latitude,Longitude,Altitude\n")
            for i in range(len(self.data_points)):
                mapfile.write(f"{i + 1},{self.data_points[i][0]},{self.data_points[i][1]},{self.data_points[i][2]}\n")

    """
    Supporting methods for vectors(self)
    """

    @staticmethod
    def calculate_bearing(delta_lat, delta_long):
        """
        :param delta_lat: change in latitude
        :param delta_long: change in longitude
        :return: bearing, in degrees
        """
        if delta_lat == 0.0 and delta_long == 0.0:
            return 0.123456
        try:
            raw_angle = math.pi / 2 - abs(math.atan(delta_lat / delta_long))
        except ZeroDivisionError:
            raw_angle = math.pi / 2

        # Subtract from 90 so that 0 degrees is on +y axis rather than +x axis
        # Also, bearing goes CW while math angles go CCW

        if delta_lat >= 0.0 and delta_long >= 0.0:  # NE
            return math.degrees(raw_angle)
        elif delta_lat <= 0.0 and delta_long >= 0.0:  # SE
            return 90.0 + math.degrees(raw_angle)
        elif delta_lat <= 0.0 and delta_long <= 0.0:  # SW
            return 180.0 + math.degrees(raw_angle)
        elif delta_lat >= 0.0 and delta_long <= 0.0:  # NW
            return 270.0 + math.degrees(raw_angle)
        else:
            raise ValueError("Incorrect angle input")

    @staticmethod
    def split_vector_to_components(vec, bearing):
        """
        :param vec: magnitude of the vector
        :param bearing: bearing in DEGREES (can be either with respect to north, or an angle between 0 or 90
        :return: the (horizontal, vertical) components of the vector magnitude
        """
        return (vec * math.cos(math.radians(bearing)), vec * math.sin(math.radians(bearing)))

    @staticmethod
    def calculate_components_dd(long_2, long_1, lat_2, lat_1, alt_2, alt_1, sensor_speed, time_step):
        """
        THIS FUNCTION USES DECIMAL DEGREES (DD.ddddd) FOR LATITUDE AND LONGITUDE, INSTEAD OF DDMM.mmm format.

        :param long_2: longitude at end of time step
        :param long_1: longitude at start of time step
        :param lat_2: latitude at end of time step
        :param lat_1: latitude at start of time step
        :param alt_2: altitude at end of time step
        :param alt_1: altitude at start of time step
        :param sensor_speed: velocity measured by sensor in km/h
        :param time_step: time between two measurements, in seconds
        :return: (y_wind, x_wind) i.e. (latitude, longitude) velocities
        """
        # 0) Calculate the GPS displacements: i.e. displacement components of the balloon in meters (along N/S and E/W axes)
        delta_lat = lat_2 - lat_1
        delta_long = long_2 - long_1
        disp_lat = (math.pi / 180 * 6378137) * delta_lat
        # Yes, we use the LATitude value in the argument for cosine when calculating LONGitude.
        disp_long = (math.pi / 180 * 6378137 * math.cos(math.radians(lat_1))) * delta_long

        # 1) Use GPS bearing data or GPS displacements to get the bearing angle in degrees
        bearing = Analyzer.calculate_bearing(disp_lat, disp_long)

        # 2) Calculate the change in altitude.
        disp_altitude = alt_2 - alt_1

        # 3) The balloon is going to be rising at ~5 m/s, and we want to remove the vertical component of this velocity so that we are left
        # just with the horizontal component. We use the fact that v^2 = v_h^2 + v_z^2. Taking v from the wind sensor,
        # and v_z from altitude differences, we calculate v_h
        if sensor_speed < abs(disp_altitude / time_step):
            sensor_speed_horizontal = math.sqrt((disp_altitude / time_step) ** 2 - sensor_speed ** 2)
        else:
            sensor_speed_horizontal = math.sqrt(sensor_speed ** 2 - (disp_altitude / time_step) ** 2)

        # 4) Split the resulting v_horizontal into components parallel to N/S and E/W axes, using the bearing calculated in step 1
        (sensor_speed_lat, sensor_speed_long) = Analyzer.split_vector_to_components(sensor_speed_horizontal, bearing)

        # 5) Add the GPS displacments (step 0) to relative wind velocity (step 4)*
        # I use math.copysign as a temporary fix, while I figure out why step 4 didn't fix the sign.
        return (disp_lat / time_step + sensor_speed_lat,
                disp_long / time_step + sensor_speed_long)

    @staticmethod
    def feet_to_meters(num):
        return num / 3.2808399

    @staticmethod
    def knots_to_meters_per_sec(num):
        return num * 0.5144439999984337
