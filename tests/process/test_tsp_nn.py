import pandas as pd
from unittest import TestCase

from cruisetrack.process.tsp_nn import tsp_nn


class TestTravellingSalesMan(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/point_layer_as_df.csv')

    def test_tsp_nn(self):
        tsp_nn(self.df)



