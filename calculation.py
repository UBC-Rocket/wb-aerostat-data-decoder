"""
Functions related to calculation of wind velocity components for each datapoint (from GPS data)

"""

import math


def calculate_components(long_2, long_1, lat_2, lat_1, alt_2, alt_1, sensor_speed, time_step):
    """
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
    delta_lat_mins = (lat_2 % (math.floor(lat_2/100))) - (lat_1 % (math.floor(lat_1/100)))
    delta_long_mins = (long_2 % (math.floor(long_2/100))) - (long_1 % (math.floor(long_1/100)))
    disp_lat = (math.pi/180 * 6378137/60) * delta_lat_mins
    # Yes, we use the LATitude value in the argument for cosine when calculating LONGitude.
    disp_long = (math.pi/180 * 6378137/60 * math.cos(math.radians(round(lat_1/100)))) * delta_long_mins

    # 1) Use GPS bearing data or GPS displacements to get the bearing angle in degrees
    bearing = calculate_bearing(disp_lat, disp_long)

    # 2) Calculate the change in altitude.
    disp_altitude = alt_2 - alt_1

    # 3) The balloon is going to be rising at ~5 m/s, and we want to remove the vertical component of this velocity so that we are left
    # just with the horizontal component. We use the fact that v^2 = v_h^2 + v_z^2. Taking v from the wind sensor,
    # and v_z from altitude differences, we calculate v_h
    sensor_speed_horizontal = math.sqrt((sensor_speed/3.6)**2 - (disp_altitude/time_step)**2)
    # divide by 3.6 to convert from km/h to m/s

    # 4) Split the resulting v_horizontal into components parallel to N/S and E/W axes, using the bearing calculated in step 1
    (sensor_speed_long, sensor_speed_lat) = split_vector_to_components(sensor_speed_horizontal, bearing)

    # 5) Add the GPS displacments (step 0) to relative wind velocity (step 4)*
    # I use math.copysign as a temporary fix, while I figure out why step 4 didn't fix the sign.
    return (disp_lat/time_step + math.copysign(sensor_speed_lat, disp_lat), disp_long/time_step + math.copysign(sensor_speed_long, disp_long))


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
    disp_lat = (math.pi/180 * 6378137) * delta_lat
    # Yes, we use the LATitude value in the argument for cosine when calculating LONGitude.
    disp_long = (math.pi/180 * 6378137 * math.cos(math.radians(lat_1))) * delta_long

    # 1) Use GPS bearing data or GPS displacements to get the bearing angle in degrees
    bearing = calculate_bearing(disp_lat, disp_long)

    # 2) Calculate the change in altitude.
    disp_altitude = alt_2 - alt_1

    # 3) The balloon is going to be rising at ~5 m/s, and we want to remove the vertical component of this velocity so that we are left
    # just with the horizontal component. We use the fact that v^2 = v_h^2 + v_z^2. Taking v from the wind sensor,
    # and v_z from altitude differences, we calculate v_h
    if sensor_speed/3.6 < abs(disp_altitude/time_step):
        sensor_speed_horizontal = math.sqrt((disp_altitude / time_step) ** 2 - (sensor_speed / 3.6) ** 2)
    else:
        sensor_speed_horizontal = math.sqrt((sensor_speed/3.6)**2 - (disp_altitude/time_step)**2)
    # divide by 3.6 to convert from km/h to m/s

    # 4) Split the resulting v_horizontal into components parallel to N/S and E/W axes, using the bearing calculated in step 1
    (sensor_speed_long, sensor_speed_lat) = split_vector_to_components(sensor_speed_horizontal, bearing)

    # 5) Add the GPS displacments (step 0) to relative wind velocity (step 4)*
    # I use math.copysign as a temporary fix, while I figure out why step 4 didn't fix the sign.
    return (disp_lat/time_step + math.copysign(sensor_speed_lat, disp_lat), disp_long/time_step + math.copysign(sensor_speed_long, disp_long))


def calculate_bearing(delta_lat, delta_long):
    """
    :param delta_lat: change in latitude
    :param delta_long: change in longitude
    :return: bearing, in degrees
    """
    if delta_long == 0:
        return 0.123456
    raw_angle = math.atan(delta_lat/delta_long)
    if delta_lat > 0 and delta_long > 0: #1st quadrant
        return math.degrees(abs(raw_angle))
    elif delta_lat < 0 and delta_long > 0: #2nd quadrant
        return 90 + math.degrees(abs(raw_angle))
    elif delta_lat < 0 and delta_long < 0: #3rd quadrant
        return 180 + math.degrees(abs(raw_angle))
    elif delta_lat > 0 and delta_long < 0: #4th quadrant
        return 270 + math.degrees(abs(raw_angle))
    else:
        return ValueError("Incorrect angle input")


def split_vector_to_components(vec, bearing):
    """
    :param vec: magnitude of the vector
    :param bearing: bearing in DEGREES (can be either with respect to north, or an angle between 0 or 90
    :return: the (horizontal, vertical) components of the vector magnitude
    """
    return (vec*math.cos(math.radians(bearing)), vec*math.sin(math.radians(bearing)))


def estimate_gps_position(lat1, long1, lat2, long2, quantity_intrmd_pts):
    """Given two GPS points, you can draw a straight line between them. Then estimate the position
    of the balloon between two GPS data measurements using that straight line.
    :param lat1: latitude of first point
    :param lat2: latitude of second point
    :param long1: longitude of first point
    :param long2: longitude of second point
    :param quantity_intrmd_pts: number of points to make in between the two known ones
    :return: a list containing tuples of intermediate (lat, long) points.
    """
    output = []
    for i in range(len(quantity_intrmd_pts)):
        lat_intrmd = lat1 + (i/(1+len(quantity_intrmd_pts)))*(lat2-lat1)
        long_intrmd = long1 + (i/(1+len(quantity_intrmd_pts)))*(long2-long1)
        output.append((lat_intrmd,long_intrmd))
    return output
