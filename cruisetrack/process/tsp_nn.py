import numpy as np


def tsp_nn(stations_xy):  #### quickly transferred from matlab function by Joseph Kirk % Email: jdkirk630@gmail.com
    stations = list(range(0, np.size(stations_xy,
                                     0)))  #### simple implementation of traveling salesman problem by nearest neighbour
    xv, yv = np.meshgrid(stations, stations)
    dist_mat = np.square(stations_xy.iloc[xv.flatten()].to_numpy() - stations_xy.iloc[
        yv.flatten()].to_numpy())  # attention: tsp nearest neighbour using lat lon (for relative idx in our lat ok)
    dist_mat = np.sqrt(dist_mat.sum(1))
    dist_mat = np.reshape(dist_mat, (len(stations), len(stations)))

    pop = np.zeros((len(stations), len(stations)))
    optimal_distances_vec = np.zeros(len(stations))

    for nn in list(range(0, len(optimal_distances_vec))):
        d = 0
        thisRte = np.zeros(len(stations))
        visited = np.zeros(len(stations))
        I = nn
        visited[I] = 1
        thisRte[1] = I

        for mm in list(range(0, len(stations) - 1)):
            dists = dist_mat[I, :]
            dists[
                visited == 1] = np.nan  # manipulating the vector derived from an array changes here the array wtf, no idea why, yet -> dump but for now define dist_mat new
            J = np.nanargmin(dists)
            visited[J] = 1
            thisRte[mm + 1] = J
            d = d + dist_mat[I, J]
            I = J
            dist_mat = np.square(stations_xy.iloc[xv.flatten()].to_numpy() - stations_xy.iloc[yv.flatten()].to_numpy())
            dist_mat = np.sqrt(dist_mat.sum(1))
            dist_mat = np.reshape(dist_mat, (len(stations), len(stations)))

        d = d + dist_mat[I, nn]
        pop[nn, :] = thisRte
        optimal_distances_vec[nn] = d

    optRoute = pop[optimal_distances_vec.argmin()]
    return optRoute