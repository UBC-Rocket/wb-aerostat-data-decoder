"""


"""

import csv

mode = input("Enter 'r' to import raw packets,"
             "or 'o' to import packets from an organized DireWolf csv output"
             "(file should be called input.txt): ")

if mode == 'r':
    #open .txt file
    #create raw_input object
    #call a function to pass raw data to datapoints object
    pass

elif mode == 'o':
    # open .csv file
    # create organized_input object
    # call a function to pass raw data to datapoints object
    pass


def write_output(wind_datapoints):
    """Writes wind datapoints to a csv file."""
    with open("output.csv", 'r') as file:
        writer = csv.writer(file)
        file.write("Altitude,WindX,WindY\n")
        writer.writerows(wind_datapoints)