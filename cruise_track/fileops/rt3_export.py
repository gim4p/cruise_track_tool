import sys
from datetime import datetime

from cruise_track.fileops import fprintf_copy


def rt3_export(Lon, Lat, filename):  #### RT3 file export, copied from Marius Becker (working group member), translated to python

    original_stdout = sys.stdout  # save a reference to the original standard output
    now = datetime.now()
    datestring = now.strftime("%d/%m/%Y %H:%M:%S")
    backslashpositions = [i for i in range(len(filename)) if filename.startswith("/", i)]
    backslashpositions = backslashpositions[len(backslashpositions) - 1]
    fname = filename[backslashpositions + 1:]
    with open(filename, "a") as f_out:
        f_out.seek(0)
        f_out.truncate()
        f_out.write(
            '<TSH_Route RtName="' + fname + '" RtVersion="3" Checked="1" CheckTime="43951.515255">\nTSH RtServer route data file. Info: amo.\n<WayPoints WPCount="' + str(
                len(Lat)) + '" IdCounter="' + str(len(Lat)) + '">\n')
        f_out.close()
    with open(filename, "a") as f_out:
        sys.stdout = f_out  # Change the standard output to the file we created.
        print(''.join(str(fprintf_copy(sys.stdout,
                                       '<WayPoint Id="%.0f" WPName="%03.f" LegType="0" Lat="%.6f" Lon="%.6f" PortXTE="0.000000" StbXTE="0.000000" TurnRate="0.000000" TurnRadius="0.000000" SafetyContour="30.000000" SafetyDepth="30.000000" RudderAngle="0.000000" ArrivalC="0.000000" FlowPoint="off"/>\n'
                                       , waypoint + 1, waypoint + 1
                                       , Lat[waypoint] * 60, Lon[waypoint] * 60)) for waypoint in
                      list(range(0, len(Lon)))))
        sys.stdout = original_stdout  # Reset the standard output to its original value
    #### still unable making filling info during loop correct -> last line 'None'*nb of Positions -> for making it work quickly, just cut out last line (later finding error in loop)
    readFile = open(filename)
    lines = readFile.readlines()
    readFile.close()
    w = open(filename, 'w')
    w.writelines([item for item in lines[:-1]])
    w.close()
