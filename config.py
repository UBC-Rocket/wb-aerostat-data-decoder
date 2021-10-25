"""
Configuration for APRS message decoder.
"""

"""
Compressed format
"""

# Total number of measurements, including the one not in the comment.
COMPR_GPS_QUANTITY = 4
COMPR_SENS_QUANTITY = 4


"""
What will the APRS strings look like? [Deprecated]
"""

DATA_TYPE_IDENTIFIER = "/"
#For position WITH timestamp use '@' or '/'
#For position without timestamp, use '!' or '='

GPS_LAT_FORMAT = "[0-9]{4}\.[0-9]{2}(N|S|n|s)"
GPS_LONG_FORMAT = "[0-9]{5}\.[0-9]{2}(E|W|e|w)"
GPS_ALT_FORMAT = "(?:a)[0-9]+"
GPS_VEL_FORMAT = "(?:v)[0-9]+"