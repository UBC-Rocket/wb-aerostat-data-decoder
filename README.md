# wb-aerostat-data-decoder
Decodes and reformats APRS packets into a form usable by the wb_wind_analysis repo

**Project summary** 

As the weather balloon collects rises through the atmosphere, it will collect data at regular intervals. At the end of each interval, the flight computer will save the longitude, latitude, altitude, and sensor wind speed at its current location. This set of data, (lat_i, long_i, alt_i, wind_i), is referred to as a "datapoint" in the code. The purpose of this program is to take all of the datapoints collected by the weather balloon and determine the horizontal wind velocity experienced by the balloon at each location. The velocity is reported as two vectors, one parallel to the longitude lines (N/S) and one parallel to latitude lines (E/W), as a function of the altitude at the start of the interval. 

Transmitting every single datapoint over APRS networks is very expensive, so in order to reduce the number of times that we need to transmit, some data needs to be left out. In both the firmware and this program, it is assumed that the GPS latitude and longitude will not be recorded at every interval; instead, it will be recorded every n times that data is collected. Most likely, we will transmit every 60 seconds but collect data every 15 seconds. Every fourth datapoint will include GPS data, while the other 3 will not; instead, the 3 "incomplete" datapoints will be of the form (alt_i, wind_i). 

To make up for this loss of data, this program implements a rough interpolation algorithm to estimate where the balloon was for those 3 incomplete data points. The following diagram hopefully shows what is happening clearly:

![Data interpolation](https://github.com/UBC-Rocket/wb-aerostat-data-decoder/blob/main/resources/interpolation.png?raw=true)

- In essence, we draw a vector between two complete datapoints, then chop this vector up into 4 pieces and pretend that the balloon was at the tip of each small vector when one of the incomplete datapoints was collected. 
- In the diagram, the vector between the two complete datapoints starts at (lat(t), long(t) and goes to (lat(t+60), long(t+60)). This vector is chopped up into 4 pieces. One of the incomplete datapoints might be (alt(t+30), wind(t+30)). After interpolating the position, our approximate complete datapoint is (lat_est(t+30), long_est(t+30), alt(t+30), wind(t+30)). 
- I expect this approach to be fairly accurate since the wind generally blows in the same direction over the course of a minute.
- Why do we need to do this? This program's algorithm for calculating wind velocity vectors relies on the GPS position. Note that this interpolation algorithm is only needed for data received over APRS. As of writing this, I have been primarily testing the vector calculation code on SD-card files, which are not limited by the 60-second transmission interval of APRS and so can record complete data points every 15 seconds.

Once we have a list of complete data points, including those that were calculated using interpolation, we can calculate the wind velocity vectors at each altitude. The process for doing so is similar to the following description. The following process is repeated for each set of two consecutive data points. 

1) Calculate the displacement, in meters, travelled by the balloon in the N/S and E/W directions (delta y and delta x respectively). Since the latitude and longitude values are technically angles, we need to convert the changes in lat and long to distances.
  - Latitude lines are evenly spaced, so in order to calculate the distance in meters, we simply convert the change in latitude to radians and multiply by the radius of the Earth: <img src="https://render.githubusercontent.com/render/math?math=\Delta y = \frac{\pi}{180}*R_{Earth} * \Delta Lat">. Essentially, we're finding the arclength between two positions on the globe. 
  - Longitude lines are not evenly spaced. The length of 1 degree of longitude depends on the latitude (varying from 0 meters at the poles to a maximum at the equator). The equation is similar to the one for latitude, except that we multiply the result by a "correction" factor, cos(lat_i): <img src="https://render.githubusercontent.com/render/math?math=\Delta x = \frac{\pi}{180}*R_{Earth} * \Delta Long * \cos{(Lat_1)}">.
  - Note that this model assumes a perfectly spherical Earth. There are formulas for calculating the correction factor for the real Earth but they are more complicated.  
2) Calculate the balloon's change in altitude
3) Calculate the balloon's bearing (arctan((Delta y)/(Delta x)) and then convert from an angle in arctangent's domain to bearing).
4) We calculate the vertical velocity of the balloon (delta Latitude / change in time between two datapoints)
5) We deal with the wind sensor velocity. The wind sensor is a great tool to have, but it measures the wind speed relative to the balloon, not the actual wind speed. This presents a problem - the balloon will be rising at a high speed, and the wind sensor will capture that. Therefore, we must remove the vertical wind velocity component from the sensor value using Pythagoras. Finally, we split the horizontal wind sensor speed to x and y components using the bearing we calculated in the step 3.
  - We rely on the assumption that the wind is purely horizontal, and so the wind sensor's "vertical" component is purely due to the balloon rising. Not sure how accurate this is.
  - Also assume that the balloon always travels in the same direction as the wind, and that the payload doesn't shake or spin (something that actually happens on balloon flights).
  - The "wind speed" used in this calculation is the average of the wind speeds measured by the sensor at each end of the 15-second interval (i.e. wind_i and wind_{i+1}).
5) We add the wind sensor velocity to the balloon's velocity for the x and y components. Return these values as a function of alt_i (the altitude at the beginning of the datapoint).

We repeat this process for every set of 2 consecutive data points. Then output all of the vectors to a csv file.

![Vector calculation](https://github.com/UBC-Rocket/wb-aerostat-data-decoder/blob/main/resources/readme_image.png?raw=true)


