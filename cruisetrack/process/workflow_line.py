import pandas as pd
from PyQt5.QtCore import QVariant
from matplotlib import pyplot as plt
from qgis.core import QgsField, QgsFeatureRequest

from cruisetrack.process.tsp_nn import tsp_nn


def line_workflow(layer_provider, laye_r):
    """run through stations most efficiently (traveling salesman problem approach)"""
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

    station_order = tsp_nn(df)
    station_order = station_order.tolist()

    Lon = df.iloc[station_order, 0]
    Lon = Lon.values.tolist()  # not necessary, but for fprintf easier for now, change later
    Lat = df.iloc[station_order, 1]
    Lat = Lat.values.tolist()

    #### plot the track to check the track
    plt.figure(4)
    plt.plot(Lon, Lat, label="track")
    plt.plot(Lon, Lat, 'r*', label="stations")
    plt.ylabel('Lat')
    plt.xlabel('Lon')
    plt.legend()
    plt.show()
