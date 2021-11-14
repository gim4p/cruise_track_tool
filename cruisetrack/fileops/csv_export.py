import sys
from datetime import datetime

import numpy as np
import pandas as pd

from cruisetrack.fileops import fprintf_copy


def CSV_export(Lon, Lat, filename):  #### CSV file export
    if np.median(Lon) > 360:  # wants decimal degree
        print('not implemented yet')
        '''
        lay_er = QgsProject.instance().mapLayersByName("testestUTM")[0]
        zone = layers.crs() # returns a reference to the active QgsMapLayer
        print(zone)
        Lat, Lon=utmToLatLng(zone, Lon, Lat, northernHemisphere=True)
        '''

    # decimal degree into DD MM.MMMMM
    DD_lon = np.floor(Lon);
    DD_lat = np.floor(Lat)  # make DD MM.MMMMM
    DM_lon = np.array(Lon - DD_lon) * 60;
    DM_lat = np.array(Lat - DD_lat) * 60;
    WP = range(1, len(Lon) + 1)
    data_arra_y = np.array([WP, DD_lon, DM_lon, DD_lat, DM_lat])
    data_fram_e = pd.DataFrame(data_arra_y)
    #### make format and export file
    now = datetime.now()
    datestring = now.strftime("%d/%m/%Y %H:%M:%S")
    backslashpositions = [i for i in range(len(filename)) if filename.startswith("/", i)]
    backslashpositions = backslashpositions[len(backslashpositions) - 1]
    # fname=(filename[backslashpositions+1:]+'_'+datestring)
    fname = filename[backslashpositions + 1:]
    original_stdout = sys.stdout  # Save a reference to the original standard output
    with open(filename, "a") as f_out:
        f_out.seek(0)
        f_out.truncate()
        f_out.write(';Route ' + fname + '\n')
        f_out.close
    with open(filename, "a") as f_out:
        sys.stdout = f_out  # Change the standard output to the file we created.
        print(''.join(str(fprintf_copy(sys.stdout,
                                       ";\nWP %03.f NAME\nLAT  %.f°%.5f LON  %.f°%.5f\nRL (Rumb Line)\nXTE= 0.00nm\nTurnRadius= 0.00nm\n"
                                       , data_fram_e.iloc[0, waypoint], data_fram_e.iloc[3, waypoint]
                                       , data_fram_e.iloc[4, waypoint], data_fram_e.iloc[1, waypoint]
                                       , data_fram_e.iloc[2, waypoint])) for waypoint in list(range(0, len(Lon)))))
        sys.stdout = original_stdout  # Reset the standard output to its original value
    #### still unable making filling info during loop correct -> last line 'None'*nb of Positions -> for making it work quickly, just cut out last line (later finding error in loop)
    readFile = open(filename)
    lines = readFile.readlines()
    readFile.close()
    w = open(filename, 'w')
    w.writelines([item for item in lines[:-1]])
    w.close()