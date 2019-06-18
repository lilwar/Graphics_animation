import numpy as np
from scipy import optimize
from cut import cutting

def solution(trajectory, top, ina):
    n = len(trajectory)
    m = top.count**2

    M = np.zeros((n, m), float)
    b = np.where(top.valid(), top.top, np.zeros_like(top.top))
    b = b.flatten()

    for i in range(len(trajectory)):
        M[i] = cutting(trajectory[i], top, ina, 1).flatten()

    A = M.transpose()
    x = optimize.nnls(A, b)

    return x[0]


