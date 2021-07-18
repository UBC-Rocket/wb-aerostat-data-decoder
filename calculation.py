"""
Functions related to calculation of wind velocity components for each datapoint (from GPS data)

"""

import math
import config


"""
Relating to GPS interpolation
"""


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
        if q_known/q_want*i % 1 == 0:
            # No interpolation
            output_positions.append([unpacked_curr['lats'][int(q_known/q_want*i)], unpacked_curr['longs'][int(q_known/q_want*i)]])
        else:
            # Interpolate
            next_latest = 1/q_known
            while next_latest < i/q_want:
                next_latest += 1/q_known

            ratio = q_known*(i/q_want - next_latest)
            if i == 1:
                output_positions.append(interpolate_linear(unpacked_prev['lats'][-1], unpacked_prev['longs'][-1], unpacked_curr['lats'][i], unpacked_curr['longs'][i], ratio))
            else:
                output_positions.append(interpolate_linear(unpacked_curr['lats'][i-1], unpacked_curr['longs'][i-1], unpacked_curr['lats'][i], unpacked_curr['longs'][i], ratio))

    return output_positions


"""
Relating to calculating wind components
"""


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
    if delta_lat == 0.0 and delta_long == 0.0:
        return 0.123456
    try:
        raw_angle = math.pi/2 - abs(math.atan(delta_lat/delta_long))
    except ZeroDivisionError:
        raw_angle = math.pi/2

    # Subtract from 90 so that 0 degrees is on +y axis rather than +x axis
    # Also, bearing goes CW while math angles go CCW

    if delta_lat >= 0.0 and delta_long >= 0.0: #NE
        return math.degrees(raw_angle)
    elif delta_lat <= 0.0 and delta_long >= 0.0: #SE
        return 90.0 + math.degrees(raw_angle)
    elif delta_lat <= 0.0 and delta_long <= 0.0: #SW
        return 180.0 + math.degrees(raw_angle)
    elif delta_lat >= 0.0 and delta_long <= 0.0: #NW
        return 270.0 + math.degrees(raw_angle)
    else:
        return ValueError("Incorrect angle input")


def split_vector_to_components(vec, bearing):
    """
    :param vec: magnitude of the vector
    :param bearing: bearing in DEGREES (can be either with respect to north, or an angle between 0 or 90
    :return: the (horizontal, vertical) components of the vector magnitude
    """
    return (vec*math.cos(math.radians(bearing)), vec*math.sin(math.radians(bearing)))


