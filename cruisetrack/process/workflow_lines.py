from statistics import median
import math
import numpy as np
import numpy.matlib #gia20211128, for now (to let it work quickly), still not recommended
import pandas as pd
from PyQt5.QtCore import QVariant
from matplotlib import pyplot as plt
from qgis.core import QgsField, QgsPointXY, QgsPoint, QgsVectorLayer

from cruisetrack.process import plot_track


def line_features_to_df(laye_r) -> pd.DataFrame:
    row_list = []
    for fea_t in laye_r.getFeatures():
        geom = fea_t.geometry()
        verts = []
        for part in geom.get():  # https://gis.stackexchange.com/a/304805
            first_vertex = part[0]
            last_vertex = part[-1]
            verts.append(first_vertex)
            verts.append(last_vertex)
        start_point = verts[0]
        end_point = verts[-1]
        azimuth = abs(start_point.azimuth(end_point))
        row_list.append({
            'X_start': start_point.x(),
            'X_stop': end_point.x(),
            'Y_start': start_point.y(),
            'Y_stop': end_point.y(),
            'length': geom.length(),
            'X_mean': geom.centroid().asPoint().x(),
            'Y_mean': geom.centroid().asPoint().y(),
            'sort_by':  'Y_mean' if 45 < azimuth < 135 else 'X_mean'
        })
    df = pd.DataFrame(row_list)
    return df


def layer_to_dataframe(laye_r: QgsVectorLayer, single_line: bool, is_individual_trackline: bool):

    '''
    if single_line:
        if is_individual_trackline: #?
            df = line_features_to_df(laye_r)
        else: # parallel lines
            fea_t = [f for f in laye_r.getFeatures()][0]
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
        df = line_features_to_df(laye_r)
    '''
    df = line_features_to_df(laye_r)

    if is_individual_trackline: # if individual cruise track line should be followed
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
    df = df.rename(columns={0: 'x', 1: 'y'})

    return df


def lines_workflow(layer_provider, laye_r, is_individual_trackline, is_parallel_lines, is_mult_para_lines, is_nonebt,
                   is_normal_profile, flip_we, only_process_2nds, is_littorina, flip_ns):

    ''' if one wants to write sth into attribute table/ generate columns
    if laye_r.fields().indexFromName("X_start") == -1: # if there are the right fields still missing, make them
        layer_provider.addAttributes([QgsField("X_start", QVariant.Double),
                                      QgsField("X_stop", QVariant.Double), QgsField("Y_start", QVariant.Double),
                                      QgsField("Y_stop", QVariant.Double), QgsField("length", QVariant.Double),
                                      QgsField("X_mean", QVariant.Double)])
        laye_r.updateFields()
    '''


    coun_t = laye_r.featureCount()

    #if just one line, with multiple points, but as normal regular profile lines wanted (additinoally accessory tasks)
    single_line = True if coun_t == 0 else False
    df = layer_to_dataframe(laye_r=laye_r,
                            single_line=single_line,
                            is_individual_trackline=is_individual_trackline)

    # df.to_csv('tests/data/normal_profile_as_df.csv', index=False)
    # from cruisetrack.helper import pickle_dict
    # pickle_dict({'is_individual_trackline': is_individual_trackline,
    #              'is_mult_para_lines': is_mult_para_lines, 'is_nonebt': is_nonebt,
    #              'is_normal_profile': is_normal_profile, 'flip_we' : flip_we,
    #              'only_process_2nds': only_process_2nds, 'is_littorina': is_littorina,
    #              'flip_ns': flip_ns},
    #             'tests/data/normal_profile_as_df.pickle')

    lon, lat = process_lines(df, is_individual_trackline, is_parallel_lines, is_mult_para_lines, is_nonebt,
                   is_normal_profile, flip_we, only_process_2nds, is_littorina, flip_ns)
    plot_track(lon, lat)
    return lon, lat


def process_lines(df, is_individual_trackline, is_parallel_lines, is_mult_para_lines, is_nonebt,
                   is_normal_profile, flip_we, only_process_2nds, is_littorina, flip_ns):

    if is_mult_para_lines:

        if not is_nonebt:
            # if chaotic series of coordinates -> organise by X_mean/Y-mean (just sensefull if lines are relatively organised)
            sort_by_col = df['sort_by'].mode()[0]
            df = df.sort_values(by=sort_by_col)

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
            df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])

            if flip_ns:
                df = df.iloc[::-1]  # NS

        # series for normal profile
        if is_normal_profile:

            if flip_we: # flip along (WE)
                idx_reihe = -1 + np.sort(
                    np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) + \
                            np.matlib.repmat((2, 1, 3, 4), 1, len(np.arange(0, len(df) * 2, 4).tolist()))
            else:
                idx_reihe = -1 + np.sort(
                    np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) + \
                            np.matlib.repmat((1, 2, 4, 3), 1, len(np.arange(0, len(df) * 2, 4).tolist()))
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
            df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])

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
            df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])

    #############
    #############
    if is_individual_trackline:
        lon = df['x']
        lat = df['y']

        if not is_parallel_lines or is_nonebt:
            if flip_ns or flip_we:
                lon = df['x'].values[::-1]
                lat = df['y'].values[::-1]

        if is_parallel_lines and not is_nonebt: ## if parallel lines

            lis_t_individual = list(range(0, len(lon) ))
            odds_idx = lis_t_individual[1::2]
            evens_idx = lis_t_individual[::2]

            x_str = lon[evens_idx]
            x_stp = lon[odds_idx]
            y_str = lat[evens_idx]
            y_stp = lat[odds_idx]


            new_array = np.array([[x_str], [x_stp]])
            diff_x = np.diff(new_array, axis=0)
            new_array = np.array([[y_str], [y_stp]])
            diff_y = abs(np.diff(new_array, axis=0))

            azimuth = np.degrees(np.arctan(diff_y/diff_x))+90
            azimuth = azimuth.tolist()
            azimuth = azimuth[0] # maaaan, just no pthon guy...
            azimuth = azimuth[0]

            if azimuth[0] < 135 and azimuth[0] > 45:
                sort_by = np.tile('Y_mean', (len(x_str)))
            else:
                sort_by = np.tile('X_mean', (len(x_str)))

            arrays = np.transpose([x_str, x_stp, y_str, y_stp])
            df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])
            df['X_mean'] = (df['X_start'] + df['X_stop']) / 2
            df['Y_mean'] = (df['Y_start'] + df['Y_stop']) / 2
            df['sort_by'] = sort_by

            # if chaotic series of coordinates -> organise by X_mean/Y-mean (just sensefull if lines are relatively organised)
            sort_by_col = df['sort_by'].mode()[0]
            df = df.sort_values(by=sort_by_col)

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
            df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])

            ##
            if flip_ns:
                df = df.iloc[::-1]  # NS


            lis_t2 = list(range(0, len(df.index) * 2))
            odds_idx2 = lis_t2[1::2]
            evens_idx2 = lis_t2[::2]
            lon = np.zeros(len(df.index) * 2)
            lon[odds_idx2] = df['X_start']
            lon[evens_idx2] = df['X_stop']
            lat = np.zeros(len(df.index) * 2)
            lat[odds_idx2] = df['Y_start']
            lat[evens_idx2] = df['Y_stop']


            # series for normal profile
            if is_normal_profile:

                if flip_we:  # flip along (WE)
                    idx_reihe = -1 + np.sort(
                        np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) + \
                                np.matlib.repmat((2, 1, 3, 4), 1, len(np.arange(0, len(df) * 2, 4).tolist()))
                else:
                    idx_reihe = -1 + np.sort(
                        np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) + \
                                np.matlib.repmat((1, 2, 4, 3), 1, len(np.arange(0, len(df) * 2, 4).tolist()))

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
                df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])

            # just turn over one side (e.g. Littorina towing)
            elif is_littorina:
                lis_t = list(range(0, len(df)))
                odds_idx = lis_t[1::2]
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
                df = pd.DataFrame(arrays, columns=['X_start', 'X_stop', 'Y_start', 'Y_stop'])

        #############
        #############

    try:
        lon
    except NameError:
        ## convert df to series of lat and lon
        lis_t2 = list(range(0, len(df.index) * 2))
        odds_idx2 = lis_t2[1::2]
        evens_idx2 = lis_t2[::2]
        lon = np.zeros(len(df.index) * 2)
        lon[odds_idx2] = df['X_start']
        lon[evens_idx2] = df['X_stop']
        lat = np.zeros(len(df.index) * 2)
        lat[odds_idx2] = df['Y_start']
        lat[evens_idx2] = df['Y_stop']


    if is_normal_profile:

        lon_organised = np.zeros(len(df) * 2)
        lat_organised = np.zeros(len(df) * 2)
        for mm in list(range(0, len(df) * 2)):
            lon_organised[mm] = lon[int(idx_reihe[mm])]
            lat_organised[mm] = lat[int(idx_reihe[mm])]
        lon = lon_organised
        lat = lat_organised





    if not is_mult_para_lines or is_nonebt:
        if not is_individual_trackline:
            # flip along (ex-WE) for in general no further track manupulation
            if flip_we:
                idx_reihe = -1 + np.sort(
                    np.matlib.repmat(np.arange(0, len(df) * 2, 4).tolist(), 1, 4)) + \
                            np.matlib.repmat((2, 1, 4, 3), 1, len(np.arange(0, len(df) * 2, 4).tolist()))
                idx_reihe = idx_reihe[0][:]  # len(idx_reihe) # idx_reihe.tolist()
                idx_reihe = idx_reihe[0:len(df) * 2]
                lon_organised = np.zeros(len(df) * 2)
                lat_organised = np.zeros(len(df) * 2)
                for mm in range(0, len(df) * 2):
                    lon_organised[mm] = lon[int(idx_reihe[mm])]
                    lat_organised[mm] = lat[int(idx_reihe[mm])]
                lon = lon_organised
                lat = lat_organised
    return lon, lat
