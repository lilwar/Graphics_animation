import os
import numpy as np
import re
from math import sqrt

class Cnc():

    def __init__(self, path):
        with open(os.path.abspath(path), 'r') as f:
            cnc = f.readlines()
            cnc = cnc[4:]
            cnc_list=[]
            for row in cnc:
                raw = re.split('[XYZF]', row)
                raw = raw[1:]
                result = [float(e) for e in raw]
                cnc_list.append(result)
            self.cnc = np.array(cnc_list, float)

    def trajectory_with_time(self, beginner_point = np.array([0, 0, 0], float)):
        trajectory = np.zeros((len(self.cnc) + 1, 3), float)
        trajectory[0] = beginner_point

        for idx, e in enumerate(self.cnc):
            trajectory[idx+1, 0] = trajectory[idx, 0] + e[0]
            trajectory[idx+1, 1] = trajectory[idx, 1] + e[1]
            trajectory[idx+1, 2] = sqrt(e[0] ** 2 + e[1] ** 2) / e[3]

        return trajectory

    def trajectory(self, beginner_point = np.array([0, 0], float)):
        trajectory = np.zeros((len(self.cnc) + 1, 2), float)
        trajectory[0] = beginner_point

        for idx, e in enumerate(self.cnc):
            trajectory[idx+1, 0] = trajectory[idx, 0] + e[0]
            trajectory[idx+1, 1] = trajectory[idx, 1] + e[1]

        return trajectory