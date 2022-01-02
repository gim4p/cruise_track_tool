from typing import List

from matplotlib import pyplot as plt


def plot_track(lon: List[float], lat: List[float], label: str = 'stations'):
    """
    Quick Matplotlib plot.

    :param label: Label for points.
    :param lon: List of Floats
    :param lat: List of Floats
    :return:
    """
    # plot the track to check the track
    plt.figure(4)
    plt.plot(lon, lat, label="track")
    plt.plot(lon[0], lat[0], 'r*', label=label)
    plt.ylabel('Lat')
    plt.xlabel('Lon')
    plt.legend(loc="upper left")
    plt.show()