import sys
from datetime import datetime

import numpy as np
import pandas as pd

from cruisetrack.fileops import fprintf_copy


def csv_export(longitude, latitude, filename: str):
    """CSV file export"""
    if np.median(longitude) > 360:  # wants decimal degree
        print('not implemented yet')

    # decimal degree into DD MM.MMMMM
    dd_lon = np.floor(longitude)
    dd_lat = np.floor(latitude)  # make DD MM.MMMMM
    dm_lon = np.array(longitude - dd_lon) * 60
    dm_lat = np.array(latitude - dd_lat) * 60
    wp = range(1, len(longitude) + 1)
    data_arra_y = np.array([wp, dd_lon, dm_lon, dd_lat, dm_lat])
    data_fram_e = pd.DataFrame(data_arra_y)

    # make format and export file
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
    with open(filename, "a") as f_out:
        sys.stdout = f_out  # Change the standard output to the file we created.
        print(''.join(str(fprintf_copy(sys.stdout,
                                       ";\nWP %03.f NAME\nLAT  %.f°%.5f LON  %.f°%.5f\nRL (Rumb Line)\nXTE= 0.00nm\nTurnRadius= 0.00nm\n"
                                       , data_fram_e.iloc[0, waypoint], data_fram_e.iloc[3, waypoint]
                                       , data_fram_e.iloc[4, waypoint], data_fram_e.iloc[1, waypoint]
                                       , data_fram_e.iloc[2, waypoint])) for waypoint in list(range(0, len(longitude)))))
        sys.stdout = original_stdout  # Reset the standard output to its original value
    #### still unable making filling info during loop correct -> last line 'None'*nb of Positions -> for making it work quickly, just cut out last line (later finding error in loop)
    read_file = open(filename)
    lines = read_file.readlines()
    read_file.close()
    w = open(filename, 'w')
    w.writelines([item for item in lines[:-1]])
    w.close()
