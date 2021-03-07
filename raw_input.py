"""
Inputting APRS data from a .txt file containing raw APRS packets, one on each line.

"""

FILE_NAME = "input.txt"


def process_raw_input():

    split_contents = []
    with open(FILE_NAME, 'r') as input_file:
        contents = input_file.readlines()
        split_contents = [x.split for x in contents]


    return split_contents