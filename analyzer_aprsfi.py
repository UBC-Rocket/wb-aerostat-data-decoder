from typing import List
import csv
import codecs
import shutil


import analyzer_compressed

class AprsFiAnalyzer(analyzer_compressed.CompressedAnalyzer):

    def __init__(self, filename, timestep):
        super().__init__(filename, timestep)

    @property
    def data_points(self) -> List[List[float]]:
        no_quotes_filename = AprsFiAnalyzer.copy_file_without_comment_quotes(self.filename)
        with open(no_quotes_filename, 'r', newline="") as input_file:
            reader = csv.DictReader(input_file)
            split_rows = [{'lat': x['lat'],
                           'long': x['lng'],
                           'alt': x['altitude'],
                           'comment': AprsFiAnalyzer.decode_comment_utf8(x['comment'])}
                          for x in reader]
        return AprsFiAnalyzer.process_input(split_rows)

    def save_datapoints(self, filename):
        with open(filename, 'w', newline="") as file:
            writer = csv.writer(file)
            file.write("Lat, Long, Alt, Wind\n")
            writer.writerows(self.data_points)

    @staticmethod
    def decode_comment_utf8(original: str) -> str:
        """
        Fixes several formatting issues arising from download of data from aprs.fi. Specifically:
        - Removes unwanted " characters at beginning and end of string (which confuse the analyzer)
        - Fixes all ',' characters in string (which are removed when creating csv file)
        - Performs unicode escaope decoding
        :param original: original APRS base91 compressed comment
        :return: Compressed comment with aforementioned issues fixed.
        """
        new = original.strip('"')
        new.replace(" ", ",")
        return codecs.decode(new.encode('utf-8'), 'unicode_escape')

    @staticmethod
    def copy_file_without_comment_quotes(filename: str) -> str:
        no_quotes_filename = filename.split(".", 1)[0] + "_noQuotes.csv"
        with open(filename, 'r', newline="") as infile:
            lines = infile.readlines()

        with open(no_quotes_filename, 'w') as outfile:
            outfile.write(lines[0])
            for line in lines[1:]:
                no_quote_line = AprsFiAnalyzer.rreplace(line, '"', "", 1).replace('"', "", 1)
                outfile.write(no_quote_line)

        return no_quotes_filename

    @staticmethod
    def rreplace(s, old, new, occurrence):
        """
        Replaces rightmost occurence of old in s with new up to occurence times.
        CREDITS: User "mg." on Stackoverflow: https://stackoverflow.com/a/2556252
        """
        li = s.rsplit(old, occurrence)
        return new.join(li)

