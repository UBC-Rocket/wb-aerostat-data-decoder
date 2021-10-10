from typing import List
import csv

import analyzer_compressed


class DirewolfAnalyzer(analyzer_compressed.CompressedAnalyzer):

    def __init__(self, filename):
        super().__init__(filename)

    @property
    def data_points(self) -> List[List[float]]:
        with open(self.filename, 'r', newline="") as input_file:
            reader = csv.DictReader(input_file)
            split_rows = [{'lat': x['latitude'], 'long': x['longitude'], 'alt': x['altitude'], 'comment': x['comment']}
                          for x in reader]

        return DirewolfAnalyzer.process_input(split_rows)


class AprsFiAnalyzer(analyzer_compressed.CompressedAnalyzer):

    def __init__(self, filename):
        super().__init__(filename)

    @property
    def data_points(self) -> List[List[float]]:
        with open(self.filename, 'r', newline="") as input_file:
            reader = csv.DictReader(input_file)
            split_rows = [{'lat': x['latitude'], 'long': x['longitude'], 'alt': x['altitude'], 'comment': x['comment']}
                          for x in reader]
        return DirewolfAnalyzer.process_input(split_rows)