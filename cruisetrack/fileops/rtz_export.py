import sys
from datetime import datetime

import numpy as np

from cruisetrack.fileops import fprintf_copy


def rtz_export(Lon,
               Lat, filename):  #### RTZ file export, copied from Knut Krämer (working group member), translated to python

    if np.median(Lon) > 360:  # wants decimal degree, if UTM --> switch
        print('not implemented yet')
        '''
        laye_rs=QgsProject.instance()
        zone = laye_rs.crs().authid() # returns a reference to the active QgsMapLayer
        Lat, Lon=utmToLatLng(zone, Lon, Lat, northernHemisphere=True)
        '''

    original_stdout = sys.stdout  # Save a reference to the original standard output
    now = datetime.now()
    datestring = now.strftime("%d/%m/%Y %H:%M:%S")
    backslashpositions = [i for i in range(len(filename)) if filename.startswith("/", i)]
    backslashpositions = backslashpositions[len(backslashpositions) - 1]
    # fname=(filename[backslashpositions+1:]+'_'+datestring)
    fname = filename[backslashpositions + 1:-4]
    with open(filename, "a") as f_out:
        f_out.seek(0)
        f_out.truncate()
        f_out.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n<route xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.acme.com/RTZ/1/0" version="1.0" xsi:schemaLocation="http://www.acme.com/RTZ/1/0 rtz.xsd">\n<routeInfo routeName="' + fname + '"/>\n<waypoints>\n<defaultWaypoint>\n<leg portsideXTD="0.00" starboardXTD="0.00" safetyContour="5.00" safetyDepth="5.00" geometryType="Loxodrome"/>\n</defaultWaypoint>\n')
        f_out.close()

    with open(filename, "a") as f_out:
        sys.stdout = f_out  # change the standard output to the file we created.
        print(''.join(str(fprintf_copy(sys.stdout,
                                       '<waypoint id="%03d">\n<position lat="%.10f" lon="%.10f"/>\n</waypoint>\n'
                                       , waypoint + 1, Lat[waypoint], Lon[waypoint])) for waypoint in
                      list(range(0, len(Lon)))))
        sys.stdout = original_stdout  # Reset the standard output to its original value
    #### still unable making filling info during loop correctly -> last line 'None'*nb of Positions -> for making it work quickly, just cut out last line (later finding error in loop)
    readFile = open(filename)
    lines = readFile.readlines()
    readFile.close()
    w = open(filename, 'w')
    w.writelines([item for item in lines[:-1]])
    w.close()

    #### add 5 lines
    with open(filename, "a") as f_out:
        sys.stdout = f_out  # change the standard output to the file we created.
        print(''.join(str(fprintf_copy(sys.stdout,
                                       '</waypoints>\n<schedules>\n<schedule id="0" name="Base Calculation"/>\n</schedules>\n</route>\n'
                                       ))))

    #### still unable making filling info during loop correctly -> last line 'None'*nb of Positions -> for making it work quickly, just cut out last line (later finding error in loop)
    readFile = open(filename)
    lines = readFile.readlines()
    readFile.close()
    w = open(filename, 'w')
    w.writelines([item for item in lines[:-1]])
    w.close()