from math import sqrt
import numpy as np


def cutting(point : np.array, top, ins, t):

    def distance(x1, x2, y1, y2):
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def delta(top_factor, remov_factor, pressure, ecc, f, w):
        c = (100.0 * top_factor) / (remov_factor * pressure * (np.pi * ecc * w / 30.0))
        return f * t / c

    def profile_interp(r, d, profile):
        p = 0
        for i in range(len(profile)):
            if d[i]>=r:
                p = i
                break
        f1 = profile[p]

        try:
            f0 = profile[p-1]
            k = (d[p] - r) / (d[p] - d[p - 1])
        except IndexError:
            f0 = 0
            k = 0

        f = (1.-k)*f1 + k*f0

        return f

    cut = np.zeros(top.count**2, float)
    d0 = [0, 1, sqrt(2), 2, sqrt(5), sqrt(8), 3, sqrt(10)]
    step = (ins.diameter/2 + ins.ecc) / sqrt(10)
    d = [i*step for i in d0]
    grid = top.coordinates()

    for idx, item in enumerate(grid):
        if distance(point[0], item[1], point[1], item[2]) < (ins.diameter/2 + ins.ecc) and item[0] != 10000:
            r = distance(point[0], item[1], point[1], item[2])
            f = profile_interp(r, d, ins.profile)
            k = ins.removal
            cut[idx] = delta(top.factor, k, ins.pressure, ins.ecc, f, ins.w_speed)

    cut = cut.reshape(top.count, top.count)
    return cut