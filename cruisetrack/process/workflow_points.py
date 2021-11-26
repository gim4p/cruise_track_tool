import pandas as pd
from PyQt5.QtCore import QVariant
from matplotlib import pyplot as plt
from qgis.core import QgsField, QgsFeatureRequest

from cruisetrack.process.tsp_nn import tsp_nn


def point_workflow(layer_provider, laye_r):
    """run through stations most efficiently (traveling salesman problem approach)"""
    df = point_layer_to_df(layer_provider, laye_r)

    lon, lat = calc_lat_lon(df)

    plot_track()
    return lon, lat


def point_layer_to_df(layer_provider, laye_r) -> pd.DataFrame:
    layer_provider.addAttributes([QgsField("X", QVariant.Double),
                                  QgsField("Y", QVariant.Double)])
    laye_r.updateFields()
    laye_r.startEditing()

    for fea_t in laye_r.getFeatures():
        geom = fea_t.geometry().asPoint()  # MultiPoint [.geometry().asMultiPoint()] noch extra abdecken
        fea_t["X"] = geom[0]
        fea_t["Y"] = geom[1]
        laye_r.updateFeature(fea_t)
    laye_r.commitChanges()

    df = pd.DataFrame(fea_t.attributes() for fea_t in laye_r.getFeatures(QgsFeatureRequest()))
    return df


def calc_lat_lon(df: pd.DataFrame):
    station_order = tsp_nn(df)
    station_order = station_order.tolist()

    lon = df.iloc[station_order, 0]
    lon = lon.values.tolist()  # not necessary, but for fprintf easier for now, change later
    lat = df.iloc[station_order, 1]
    lat = lat.values.tolist()

    return lon, lat


def plot_track(lon, lat):
    # plot the track to check the track
    plt.figure(4)
    plt.plot(lon, lat, label="track")
    plt.plot(lon, lat, 'r*', label="stations")
    plt.ylabel('Lat')
    plt.xlabel('Lon')
    plt.legend()
    plt.show()

