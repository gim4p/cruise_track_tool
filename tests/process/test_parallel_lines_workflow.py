import pandas as pd
from unittest import TestCase
import pickle

from cruisetrack.process import plot_track
from cruisetrack.process.workflow_lines import process_lines


class TestLineWorkflowParallelLines(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/parallel_lines_as_df.csv')
        self.params2 = pickle.load(open('/home/markus/scripting/cruise_track/tests/data'
                                        '/parallel_lines_as_df.pickle', "rb"))
        print('')

    def test_process_lines(self):
        lon, lat = process_lines(self.df, **self.params2)
        # plot_track(lon, lat, label='start')
