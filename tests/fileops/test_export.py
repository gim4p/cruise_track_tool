import pickle

from unittest import TestCase

from cruisetrack.fileops.csv_export import csv_export
from cruisetrack.fileops.rt3_export import rt3_export
from cruisetrack.fileops.rtz_export import rtz_export


class TestExportFunctions(TestCase):

    def setUp(self) -> None:
        dbfile = open('../data/lat_lon_sixpoints', 'rb')
        db = pickle.load(dbfile)

        self.lat = db["lat"]
        self.lon = db["lon"]

    def test_rt3_export(self):
        rt3_export(self.lon, self.lat, filename='../data/rt3_test.rt3')

    def test_rtz_export(self):
        rtz_export(self.lon, self.lat, filename='../data/rtz_test.rtz')

    def test_cvt_export(self):
        csv_export(self.lon, self.lat, filename='../data/cvt_test.cvt')


