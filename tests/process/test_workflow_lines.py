import pandas as pd
from unittest import TestCase
import pickle

from cruisetrack.process.workflow_lines import process_lines


class TestLineWorkflow(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/line_layer_as_df.csv')
        self.params1 = pickle.load(open('../tests/data/line_layer_as_df.pickle', "rb"))

    def test_process_lines(self):
        process_lines(self.df, **self.params1)


class TestLineWorkflowIndividualLines(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/line_layer_as_df_individual_line.csv')
        self.params2 = pickle.load(open('../data'
                                       '/line_layer_as_df_individual_line.pickle', "rb"))

    def test_process_lines(self):
        process_lines(self.df, **self.params2)



class TestLineWorkflowParallelLines(TestCase):

    def setUp(self) -> None:
        self.df = pd.read_csv('../data/line_layer_as_df_parallel_tracks.csv')
        self.params2 = pickle.load(open('../tests/data'
                                       '/line_layer_as_df_parallel_tracks.pickle', "rb"))

    def test_process_lines(self):
        process_lines(self.df, **self.params2)


