from typing import Tuple, List

import numpy as np
import pandas as pd
from qgis.core import QgsVectorLayer

from cruisetrack.process import plot_track
from cruisetrack.process.tsp_nn import tsp_nn


def point_workflow(laye_r: QgsVectorLayer, flip_ns, flip_we) -> Tuple[List, List]:
    """
    Point workflow utilizing Traveling Salesman Problem Solver for creating shortest track.

    :param laye_r: QgsVectorLayer (Point)
    :return: Tuple of Lat and Lon lists
    """
    df = point_layer_to_df(laye_r)
    lon, lat = calc_lat_lon(df)
    if flip_we or flip_ns:
        lon=np.flip(lon)
        lat=np.flip(lat)
    plot_track(lon, lat)
    return lon, lat


def point_layer_to_df(laye_r: QgsVectorLayer) -> pd.DataFrame:
    """
    Convert QgsVectorLayer to DataFrame

    :param laye_r: QgsVectorLayer (Point)
    :return: DataFrame containing X, Y coordinates
    """
    row_list = []
    for feat in laye_r.getFeatures():
        row_list.append({'X': feat.geometry().asPoint().x(),
                         'Y': feat.geometry().asPoint().y()})
    df = pd.DataFrame(row_list)
    return df


def calc_lat_lon(df: pd.DataFrame) -> Tuple[List[float], List[float]]:
    """
    Create stations based on input point, using Traveling Salesman Problem Solver.

    :param df: DataFrame containing X, Y coordinates
    :return: Tuple of Lat and Lon lists
    """
    station_order = tsp_nn(df)
    station_order = station_order.tolist()

    lon = df.iloc[station_order, 0]
    lon = lon.values.tolist()  # not necessary, but for fprintf easier for now, change later
    lat = df.iloc[station_order, 1]
    lat = lat.values.tolist()

    return lon, lat




