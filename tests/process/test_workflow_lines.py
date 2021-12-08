import pandas as pd
from unittest import TestCase
import pickle

from cruisetrack.process.workflow_lines import process_lines


class TestLineWorkflow(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/line_layer_as_df.csv')
        self.params = pickle.load(open('/home/markus/scripting/cruise_track/tests/data/line_layer_as_df.pickle', "rb"))

    def test_process_lines(self):
        process_lines(self.df, **self.params)


class TestLineWorkflowIndividualLines(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/line_layer_as_df_individual_line.csv')
        self.params = pickle.load(open('/home/markus/scripting/cruise_track/tests/data'
                                       '/line_layer_as_df_individual_line.pickle', "rb"))

    def test_process_lines(self):
        process_lines(self.df, **self.params)


