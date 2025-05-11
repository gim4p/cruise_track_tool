from typing import List

from matplotlib import pyplot as plt


def plot_track(lon: List[float], lat: List[float]):
    """
    Quick Matplotlib plot.

    :param label: Label for points.
    :param lon: List of Floats
    :param lat: List of Floats
    :return:
    """
    # plot the track to check the track

    fig=plt.figure()
    plt.plot(lon, lat, label="track")
    plt.plot(lon, lat, 'k.', label="waypoint")
    plt.plot(lon[0], lat[0], 'r*', label="start")
    plt.plot(lon[len(lon)-1], lat[len(lon)-1], 'ko', label="stop")
    plt.ylabel('Lat')
    plt.xlabel('Lon')
    plt.legend(loc="upper left")
    plt.show()