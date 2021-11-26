import pandas as pd
from unittest import TestCase

from cruisetrack.process.workflow_points import calc_lat_lon


class TestPointWorkflow(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/point_layer_as_df.csv')

    def test_calc_lat_lon(self):
        calc_lat_lon(self.df)


