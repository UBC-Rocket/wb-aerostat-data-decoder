class datapoint:

    def __init__(self, date, time, gps_lat, gps_long, gps_deg, wind_data_points):
        self.date = date
        self.time = time
        self.gps_lat = gps_lat
        self.gps_long = gps_long
        self.gps_deg = gps_deg
        self.wind_data_points = wind_data_points
        #not sure if these will be cleaned up (altitude,x,y) or raw (altitude,windspeed_magnitude)


class datapoints:

    def __init__(self):
        self.datapoints = []

    @property
    def wind_data_points(self):
        """Takes only wind data points from all the data collected and returns them in a single list"""
        data = []
        for datapoint in self.datapoints:
            data.append(datapoint.wind_data_points)

        return data

