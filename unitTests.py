"""
Unit tests for analyzer classes.
"""

import unittest
import csv


class TestSDMethods(unittest.TestCase):

    def test_1_simple(self):
        expected_dx = -9.33
        expected_dy = -24.22

        with open("output.csv", "r", newline="") as test_file:
            reader = csv.DictReader(test_file)
            split_rows = [{"A": float(x['Altitude']), "Y": float(x["WindY"]), "X": float(x["WindX"])} for x in reader]

        self.assertTrue(abs(split_rows[0]["X"] - expected_dx) < 0.5)
        self.assertTrue(abs(split_rows[0]["Y"] - expected_dy) < 0.5)
