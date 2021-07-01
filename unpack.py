"""
Functions related to decompressing our base91 APRS packets
"""

def base91_to_int(compressed_char):
    """
    :param compressed_char: a base91 compressed character
    :return: the number in base 91 corresponding to that character
    """
    return ord(compressed_char) - 33


def feet_to_meters(num):
    return num/3.2808399


def knots_to_kilom(num):
    return num/0.539956803


def unpack_latitude(compressed_string):
    """
    :param compressed_string: A 4-character string containing a gps latitude in base91 format
    :return: Signed gps latitude in decimal degrees format
    """
    st = [base91_to_int(x) for x in compressed_string]
    return 90.0 - (st[0]*91.0**3 + st[1]*91.0**2 + st[2]*91.0 + st[3])/380926.0


def unpack_longitude(compressed_string):
    """
    :param compressed_string: A 4-character string containing a gps longitude in base91 format
    :return: Signed gps longitude in decimal degrees format
    """
    st = [base91_to_int(x) for x in compressed_string]
    return -180.0 + (st[0] * 91.0** 3 + st[1] * 91.0**2 + st[2] * 91.0 + st[3]) / 190463.0


def unpack_altitude(compressed_string):
    """
    :param compressed_string: A 2-character string containing a gps altitude in base91 format
    :return: Altitude, in meters, to 0.4% accuracy
    """
    alt = [base91_to_int(x) for x in compressed_string]
    return feet_to_meters(1.002**(alt[0]*91.0 + alt[1]))


def unpack_wind_speed(compressed_string):
    """
    :param compressed_string: A 1-character string containing a wind speed measurement in base91 format
    :return: Wind speed, in km/h.
    """
    return knots_to_kilom(1.08**base91_to_int(compressed_string) - 1.0)

