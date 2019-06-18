import numpy as np

def ext_traj(t, path):

    time = path[:, 2]
    time = time[1:]

    i = 0
    t1 = 0.0

    while True:
        t1 += time[i]
        if t1 >= t:
            t0 = t1 - time[i]
            break
        i += 1

    x0, y0 = path[i, 0], path[i, 1]
    k = (t - t0)/time[i]
    x1, y1 = path[i+1, 0], path[i+1, 1]

    x = x0 + k*(x1 - x0)
    y = y0 + k*(y1 - y0)

    xy = np.array([x, y], float)
    return xy