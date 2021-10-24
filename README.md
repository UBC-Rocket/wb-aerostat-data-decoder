# wb-aerostat-data-decoder
Decodes and reformats APRS packets into a form usable by the wb_wind_analysis repo

![Diagram of two points on Earth](https://github.com/UBC-Rocket/wb-aerostat-data-decoder/blob/main/resources/readme_image.png?raw=true)

**Explanation of model:** 

The weather balloon collects data at regular intervals in order to help us calculate wind velocity vectors. The data includes the longitude, latitude, altitude, and sensor wind speed. One "measurement" of this data is referred to as a "datapoint" within the code. As the balloon moves through the atmosphere, it will collect hundreds of such data points. We can draw vectors between each set of 2 points using the GPS data (lat1, long1) and (lat2, long2) in order to approximate the flight path of the balloon. 

In order to collect more data, we want to measure several datapoints in between each data transmission (most likely will transmit every 60 seconds but collect data every 15 seconds). The trouble is that we cannot fit four datapoints into a single transmission, and so instead in a single 60-second time period, we collect one full datapoint (containing longitude and latitude as well as altitude and wind speed) and 3 "incomplete" datapoints that only contain altitude and wind speed. Then, this program interpolates the location at which each "incomplete" data point was taken, by chopping up the aforementioned vector into 4 smaller vectors, all tip to tail. 

Once we have a list of _complete_ data points (including those that were calculated using interpolation), we can calculate the balloon's average velocity as it travels from (lat1, long1) to (lat2, long2). We can then add the wind velocity measured by the wind sensor* to the balloon's velocity to calculate the average wind speed between the two points. The process followed by this program is in essence the same, but the balloon's translation and sensor speed are separated into horizontal and vertical components and calculations are done on the components.

Here is a breakdown of the specific process undertaken by the program to calculate the wind components:
- Calculate the displacement, in meters, travelled by the balloon in the N/S and E/W directions. Remember that latitude and longitude values are technically angles, measured with respect to the equator (in the case of latitude) and Greenwich (in the case of longitude). 
  - Latitude lines are evenly spaced, so in order to calculate the distance in meters, we simply convert the change in latitude to radians and multiply by the radius of the Earth: <img src="https://render.githubusercontent.com/render/math?math=\Delta y = \frac{\pi}{180}*R_{Earth} * \Delta Lat">. 
  - Longitude lines are not evenly spaced. The length of 1 degree of longitude depends on the latitude (varying from 0 meters at the poles to a maximum at the equator). The equation for the distance travelled along a longitude line is similar, except that we multiply the result by cos(lat1): <img src="https://render.githubusercontent.com/render/math?math=\Delta x = \frac{\pi}{180}*R_{Earth} * \Delta Long * \cos{(Lat_1)}">.
  - Note that this model assumes a perfectly spherical Earth.
- Calculate the balloon's change in altitude, and bearing (using the x and y components)
- Process the wind sensor velocity. We calculate the vertical velocity of the balloon (delta Latitude / change in time between two datapoints), then use Pythagoras to remove the vertical component from the wind sensor velocity. Finally, we split the horizontal part of the wind sensor speed to x and y components using the bearing we calculated in the previous step.
  - Assume that the wind sensor is picking up vertical wind speed in this way.
  - Also assume that the balloon always travels in the same direction as the wind, and ignore the payload's shaking or rotation.
- For x and y components, add wind sensor velocity to the balloon's velocity. Return these values as a function of alt1 (the altitude at the earlier datapoint).

