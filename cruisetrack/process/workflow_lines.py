from statistics import median

import numpy as np
import pandas as pd
from PyQt5.QtCore import QVariant
from matplotlib import pyplot as plt
from qgis.core import QgsField, QgsPointXY, QgsFeatureRequest, QgsPoint


def process_lines(layer_provider, laye_r, is_individual_trackline, is_accessory, is_nonebt,
                  is_normal_profile, flip_we, only_process_2nds, is_littorina, flip_ns):
    field_name = "X_start"  # if there are the right fields still missing, make them
    field_index = laye_r.fields().indexFromName(field_name)
    if field_index == -1:
        layer_provider.addAttributes([QgsField("X_start", QVariant.Double),
                                      QgsField("X_stop", QVariant.Double), QgsField("Y_start", QVariant.Double),
                                      QgsField("Y_stop", QVariant.Double), QgsField("length", QVariant.Double),
                                      QgsField("X_mean", QVariant.Double)])
        laye_r.updateFields()

    # put data from shapefile into attribute table
    coun_t = -1
    for fea_t in laye_r.getFeatures():
        geom = fea_t.geometry()
        coun_t = coun_t + 1

    """ if just one line, with multiple points, 
    but as normal regular profile lines wanted (additinoally accessory tasks)"""
    if coun_t == 0:
        # print('just one line')
        # just for now double, whole script has still to be organized!
        if is_individual_trackline:
            laye_r.startEditing()
            for fea_t in laye_r.getFeatures():
                geom = fea_t.geometry().asMultiPolyline()
                for line in geom:
                    start_point = QgsPointXY(geom[0][0])
                    end_point = QgsPointXY(geom[-1][-1])
                    fea_t["X_start"] = start_point[0]
                    fea_t["X_stop"] = end_point[0]
                    fea_t["Y_start"] = start_point[1]
                    fea_t["Y_stop"] = end_point[1]
                    # ellipsoid; noch nicht herausgefunden, wie man das umstellt (trotz geänderter Projektion)
                    fea_t["length"] = fea_t.geometry().length()
                    if (abs(start_point.azimuth(end_point)) > 45) and (abs(start_point.azimuth(end_point)) < 125):
                        fea_t["X_mean"] = median([start_point[1], end_point[1]])
                    else:
                        fea_t["X_mean"] = median([start_point[0], end_point[0]])
                    laye_r.updateFeature(fea_t)
            laye_r.commitChanges()
            df = pd.DataFrame(fea_t.attributes() for fea_t in laye_r.getFeatures(QgsFeatureRequest()))
        else:

            geom = fea_t.geometry().asMultiPolyline()
            for line in geom:
                nb_points = len(line)
                pointseries_x = np.zeros(nb_points)
                pointseries_y = np.zeros(nb_points)
                for nn in list(range(0, nb_points)):
                    temp = line[nn]
                    pointseries_x[nn] = temp[0]
                    pointseries_y[nn] = temp[1]

            temp1 = QgsPoint(pointseries_x[0], pointseries_y[0])
            temp2 = QgsPoint(pointseries_x[1], pointseries_y[1])

            if (abs(temp1.azimuth(temp2)) > 45) and (abs(temp1.azimuth(temp2)) < 125):
                arrays = np.transpose([pointseries_x[::2], pointseries_x[1::2], pointseries_y[::2], pointseries_y[1::2],
                                       np.mean([pointseries_y[::2], pointseries_y[1::2]], 0),
                                       np.mean([pointseries_y[::2], pointseries_y[1::2]], 0)])
            else:
                arrays = np.transpose([pointseries_x[::2], pointseries_x[1::2], pointseries_y[::2], pointseries_y[1::2],
                                       np.mean([pointseries_y[::2], pointseries_y[1::2]], 0),
                                       np.mean([pointseries_x[::2], pointseries_x[1::2]], 0)])
            df = pd.DataFrame(arrays)

    else:
        laye_r.startEditing()
        for fea_t in laye_r.getFeatures():
            geom = fea_t.geometry().asMultiPolyline()
            for line in geom:
                start_point = QgsPointXY(geom[0][0])
                end_point = QgsPointXY(geom[-1][-1])
                fea_t["X_start"] = start_point[0]
                fea_t["X_stop"] = end_point[0]
                fea_t["Y_start"] = start_point[1]
                fea_t["Y_stop"] = end_point[1]
                # ellipsoid; noch nicht herausgefunden, wie man das umstellt (trotz geänderter Projektion)
                fea_t["length"] = fea_t.geometry().length()
                if (abs(start_point.azimuth(end_point)) > 45) and (abs(start_point.azimuth(end_point)) < 125):
                    fea_t["X_mean"] = median([start_point[1], end_point[1]])
                else:
                    fea_t["X_mean"] = median([start_point[0], end_point[0]])
                laye_r.updateFeature(fea_t)
        laye_r.commitChanges()
        df = pd.DataFrame(fea_t.attributes() for fea_t in laye_r.getFeatures(QgsFeatureRequest()))

    # if CheckBox 'accessory' active
    if is_accessory:
        if not is_nonebt:
            # if chaotic series of coordinates -> organise by X_mean/Y-mean (just sensefull if lines are relatively organised)
            df = df.sort_values(by=[5])
            # alle Linien gleich ausrichten
            new_lon_st = np.zeros(len(df))
            new_lon_sp = np.zeros(len(df))
            new_lat_st = np.zeros(len(df))
            new_lat_sp = np.zeros(len(df))
            for nn in list(range(0, len(df))):
                if df.iloc[nn, 0] < df.iloc[nn, 1]:
                    new_lon_st[nn] = df.iloc[nn, 0]
                    new_lon_sp[nn] = df.iloc[nn, 1]
                    new_lat_st[nn] = df.iloc[nn, 2]
                    new_lat_sp[nn] = df.iloc[nn, 3]
                else:
                    new_lon_st[nn] = df.iloc[nn, 1]
                    new_lon_sp[nn] = df.iloc[nn, 0]
                    new_lat_st[nn] = df.iloc[nn, 3]
                    new_lat_sp[nn] = df.iloc[nn, 2]
            arrays = np.transpose([new_lon_st, new_lon_sp, new_lat_st, new_lat_sp])
            df = pd.DataFrame(arrays)
        # series for normal profile
        if is_normal_profile:
            # flip along (WE)
            if flip_we:
                idx_reihe = -1 + np.sort(
                    np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) +\
                            np.matlib.repmat((2, 1, 3, 4), 1,len(np.arange(0,len(df) * 2,4).tolist()))
            else:
                idx_reihe = -1 + np.sort(
                    np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) +\
                            np.matlib.repmat((1, 2, 4, 3), 1,len(np.arange(0,len(df) * 2,4).tolist()))
            idx_reihe = idx_reihe[0][:]
            idx_reihe = idx_reihe[0:len(df) * 2]

        # series for every 2nd line
        elif only_process_2nds:
            reihe_hin = np.arange(0, len(df), 2).tolist()
            reihe_her = np.arange(1, len(df), 2).tolist()
            lon_st_hin = np.zeros(len(reihe_hin))
            lon_sp_hin = np.zeros(len(reihe_hin))
            lat_st_hin = np.zeros(len(reihe_hin))
            lat_sp_hin = np.zeros(len(reihe_hin))
            lon_st_her = np.zeros(len(reihe_her))
            lon_sp_her = np.zeros(len(reihe_her))
            lat_st_her = np.zeros(len(reihe_her))
            lat_sp_her = np.zeros(len(reihe_her))
            for nn in range(0, len(reihe_hin)):  # there
                if nn / 2 != np.round(nn / 2):
                    lon_st_hin[nn] = df.iloc[reihe_hin[nn], 0]
                    lon_sp_hin[nn] = df.iloc[reihe_hin[nn], 1]
                    lat_st_hin[nn] = df.iloc[reihe_hin[nn], 2]
                    lat_sp_hin[nn] = df.iloc[reihe_hin[nn], 3]
                else:
                    lon_st_hin[nn] = df.iloc[reihe_hin[nn], 1]
                    lon_sp_hin[nn] = df.iloc[reihe_hin[nn], 0]
                    lat_st_hin[nn] = df.iloc[reihe_hin[nn], 3]
                    lat_sp_hin[nn] = df.iloc[reihe_hin[nn], 2]
            testvec = np.zeros(len(df))  # back
            dito = 0
            for nn in range(1, len(df)):
                if nn / 2 == np.round(nn / 2):
                    dito = dito + 3
                else:
                    dito = dito + 1
                testvec[nn] = dito
            for nn in range(0, len(reihe_her)):
                if len(df) - 1 in testvec:
                    if nn / 2 != np.round(nn / 2):
                        lon_st_her[nn] = df.iloc[reihe_her[nn], 1]
                        lon_sp_her[nn] = df.iloc[reihe_her[nn], 0]
                        lat_st_her[nn] = df.iloc[reihe_her[nn], 3]
                        lat_sp_her[nn] = df.iloc[reihe_her[nn], 2]
                    else:
                        lon_st_her[nn] = df.iloc[reihe_her[nn], 0]
                        lon_sp_her[nn] = df.iloc[reihe_her[nn], 1]
                        lat_st_her[nn] = df.iloc[reihe_her[nn], 2]
                        lat_sp_her[nn] = df.iloc[reihe_her[nn], 3]
                else:
                    if nn / 2 != np.round(nn / 2):
                        lon_st_her[nn] = df.iloc[reihe_her[nn], 0]
                        lon_sp_her[nn] = df.iloc[reihe_her[nn], 1]
                        lat_st_her[nn] = df.iloc[reihe_her[nn], 2]
                        lat_sp_her[nn] = df.iloc[reihe_her[nn], 3]
                    else:
                        lon_st_her[nn] = df.iloc[reihe_her[nn], 1]
                        lon_sp_her[nn] = df.iloc[reihe_her[nn], 0]
                        lat_st_her[nn] = df.iloc[reihe_her[nn], 3]
                        lat_sp_her[nn] = df.iloc[reihe_her[nn], 2]

            # flip along (ex-WE)
            if flip_we:
                new_lat_st = np.concatenate((lat_sp_hin, lat_sp_her), axis=0)
                new_lat_sp = np.concatenate((lat_st_hin, lat_st_her), axis=0)
                new_lon_st = np.concatenate((lon_sp_hin, lon_sp_her), axis=0)
                new_lon_sp = np.concatenate((lon_st_hin, lon_st_her), axis=0)
            else:
                new_lat_st = np.concatenate((lat_st_hin, lat_st_her), axis=0)
                new_lat_sp = np.concatenate((lat_sp_hin, lat_sp_her), axis=0)
                new_lon_st = np.concatenate((lon_st_hin, lon_st_her), axis=0)
                new_lon_sp = np.concatenate((lon_sp_hin, lon_sp_her), axis=0)

            arrays = np.transpose([new_lon_st, new_lon_sp, new_lat_st, new_lat_sp])
            df = pd.DataFrame(arrays)

        # just turn over one side (e.g. Littorina towing)
        elif is_littorina:
            lis_t = list(range(0, len(df)));
            odds_idx = lis_t[1::2];
            evens_idx = lis_t[::2]
            vec = np.zeros(len(df))
            vec[odds_idx] = odds_idx
            vec[evens_idx] = np.add(evens_idx, 2).tolist()
            vec[1:] = np.add(vec[1:], -1).tolist()
            vec[0] = vec[0] - 1
            if len(df) / 2 != np.round(len(df) / 2):
                vec[len(vec) - 1] = vec[len(vec) - 1] - 1
            new_lon_st = np.zeros(len(df))
            new_lon_sp = np.zeros(len(df))
            new_lat_st = np.zeros(len(df))
            new_lat_sp = np.zeros(len(df))
            new_lon_st[odds_idx] = df.iloc[vec[odds_idx], 0]
            new_lon_sp[odds_idx] = df.iloc[vec[odds_idx], 1]
            new_lat_st[odds_idx] = df.iloc[vec[odds_idx], 2]
            new_lat_sp[odds_idx] = df.iloc[vec[odds_idx], 3]
            new_lon_st[evens_idx] = df.iloc[vec[evens_idx], 1]
            new_lon_sp[evens_idx] = df.iloc[vec[evens_idx], 0]
            new_lat_st[evens_idx] = df.iloc[vec[evens_idx], 3]
            new_lat_sp[evens_idx] = df.iloc[vec[evens_idx], 2]

            # flip along (ex-WE) cumbersome and double
            if flip_we:
                new_lat_st2 = new_lat_sp
                new_lat_sp2 = new_lat_st
                new_lon_st2 = new_lon_sp
                new_lon_sp2 = new_lon_st
                new_lat_st = new_lat_st2
                new_lat_sp = new_lat_sp2
                new_lon_st = new_lon_st2
                new_lon_sp = new_lon_sp2

            arrays = np.transpose([new_lon_st, new_lon_sp, new_lat_st, new_lat_sp])
            df = pd.DataFrame(arrays)

    # if individual cruise track line should be followed
    if is_individual_trackline:
        ind_track = 1
        lon_series = np.zeros([len(df), 200])
        lat_series = np.zeros([len(df), 200])
        coun_t = 0
        for fea_t in laye_r.getFeatures():
            geom = fea_t.geometry().constGet()
            for n in list(range(len(geom[0]))):
                vertices_on_line = QgsPointXY(geom[0][n])
                lon_series[coun_t, n] = vertices_on_line[0]
                lat_series[coun_t, n] = vertices_on_line[1]
            coun_t = coun_t + 1

        lon = []
        lat = []

        for n in list(range(coun_t)):
            lon = lon + list(filter(lambda num: num != 0, lon_series[n]))
            lat = lat + list(filter(lambda num: num != 0, lat_series[n]))

        arrays = [lon, lat]
        df = pd.DataFrame(arrays)
        df = df.T
    else:
        ind_track = 0

    # flip across (ex-NS)
    if flip_ns:
        df = df.iloc[::-1]

    # make just two culumns Lon and Lat
    if is_individual_trackline:
        lon = df[0]
        lat = df[1]

    else:
        lis_t2 = list(range(0, len(df.index) * 2))
        odds_idx2 = lis_t2[1::2]
        evens_idx2 = lis_t2[::2]
        lon = np.zeros(len(df.index) * 2)
        lon[odds_idx2] = df[0]
        lon[evens_idx2] = df[1]
        lat = np.zeros(len(df.index) * 2)
        lat[odds_idx2] = df[2]
        lat[evens_idx2] = df[3]

    if is_normal_profile:
        lon_organised = np.zeros(len(df) * 2)
        lat_organised = np.zeros(len(df) * 2)
        for mm in list(range(0, len(df) * 2)):
            lon_organised[mm] = lon[int(idx_reihe[mm])]
            lat_organised[mm] = lat[int(idx_reihe[mm])]
        lon = lon_organised
        lat = lat_organised

    if not is_accessory or is_nonebt:
        if ind_track != 1:
            # flip along (ex-WE) for in general no further track manupulation
            if flip_we:
                idx_reihe = -1 + np.sort(
                    np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) + \
                            np.matlib.repmat((2, 1, 4, 3), 1,len(np.arange(0,len(df) * 2,4).tolist()))
                idx_reihe = idx_reihe[0][:] # len(idx_reihe) # idx_reihe.tolist()
                idx_reihe = idx_reihe[0:len(df) * 2]
                lon_organised = np.zeros(len(df) * 2)
                lat_organised = np.zeros(len(df) * 2)
                for mm in range(0, len(df) * 2):
                    lon_organised[mm] = lon[int(idx_reihe[mm])]
                    lat_organised[mm] = lat[int(idx_reihe[mm])]
                lon = lon_organised
                lat = lat_organised

    # plot the track to check the track
    plt.figure(4)
    plt.plot(lon, lat, label="track")
    plt.plot(lon[0], lat[0], 'r*', label="start")
    plt.ylabel('Lat')
    plt.xlabel('Lon')
    plt.legend(loc="upper left")
    plt.show()
    return lon, lat
