"""
Unit tests for analyzer classes.
"""
import analyzer_sd

import unittest
import csv


class TestSDMethods(unittest.TestCase):

    def test_1_simple(self):
        expected_dx = -9.33
        expected_dy = -24.22

        t = analyzer_sd.SDAnalyzer("resources/sdTestFile2Simple.csv", 30)
        t.output_vectors("test1_output.csv")

        with open("test1_output.csv", "r", newline="") as test_file:
            reader = csv.DictReader(test_file)
            split_rows = [{"A": float(x['Altitude']), "Y": float(x["WindY"]), "X": float(x["WindX"])} for x in reader]

        self.assertTrue(abs(split_rows[0]["X"] - expected_dx) < 0.5)
        self.assertTrue(abs(split_rows[0]["Y"] - expected_dy) < 0.5)

    def test_2_purely_longitudinal(self):
        expected_dx = 18.474
        expected_dy = 0

        t = analyzer_sd.SDAnalyzer("resources/sdTestFile3JustHorizontal.csv", 15)
        t.output_vectors("test2_output.csv")

        with open("test2_output.csv", "r", newline="") as test_file:
            reader = csv.DictReader(test_file)
            split_rows = [{"A": float(x['Altitude']), "Y": float(x["WindY"]), "X": float(x["WindX"])} for x in reader]

        self.assertTrue(abs(split_rows[0]["X"] - expected_dx) < 0.5)
        self.assertTrue(abs(split_rows[0]["Y"] - expected_dy) < 0.5)

    def test_3_purely_latitudinal(self):
        expected_dx = 0.0
        expected_dy = 13.45

        t = analyzer_sd.SDAnalyzer("resources/sdTestFile4JustLatitudal.csv", 15)
        t.output_vectors("test3_output.csv")

        with open("test3_output.csv", "r", newline="") as test_file:
            reader = csv.DictReader(test_file)
            split_rows = [{"A": float(x['Altitude']), "Y": float(x["WindY"]), "X": float(x["WindX"])} for x in reader]

        self.assertTrue(abs(split_rows[0]["X"] - expected_dx) < 0.5)
        self.assertTrue(abs(split_rows[0]["Y"] - expected_dy) < 0.5)


