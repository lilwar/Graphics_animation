import os
import sys
import numpy as np
import math
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton,
QApplication, QFileDialog, QVBoxLayout, QHBoxLayout)
from matplotlib import pyplot as plt
from scipy import optimize
from ina import Ina
from toptime import Top
from cnc import Cnc
from extend_trajectory import ext_traj

class MainWindow(QWidget):

    def __init__(self):

        super().__init__()

        self.initUI()


    def initUI(self):


        vbox = QVBoxLayout()
        self.setLayout(vbox)

        hbox = QHBoxLayout()
        self.lbl = QLabel("Choose topography file: ", self)
        hbox.addWidget(self.lbl)
        self.top_fopenbtn = QPushButton("Topography", self)
        self.top_fopenbtn.clicked.connect(self.open_top)
        hbox.addWidget(self.top_fopenbtn)
        vbox.addLayout(hbox)

        hbox1 = QHBoxLayout()
        self.lbl = QLabel("Choose cnc file: ", self)
        hbox1.addWidget(self.lbl)
        self.traj_fopenbtn = QPushButton("Trajectory", self)
        self.traj_fopenbtn.clicked.connect(self.open_cnc)
        hbox1.addWidget(self.traj_fopenbtn)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.lbl = QLabel("Choose instrument file: ", self)
        hbox2.addWidget(self.lbl)
        self.ina_fopenbtn = QPushButton("Instrument", self)
        self.ina_fopenbtn.clicked.connect(self.open_ina)
        hbox2.addWidget(self.ina_fopenbtn)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        self.runbtn = QPushButton("Run", self)
        self.runbtn.setToolTip('Run program')
        hbox3.addStretch(1)
        hbox3.addWidget(self.runbtn)
        hbox3.addStretch(1)
        self.runbtn.clicked.connect(self.profile_find_n_show)
        vbox.addLayout(hbox3)

        self.setGeometry(300, 150, 500, 300)
        self.setWindowTitle('Profile')

        self.show()

    def profile_find_n_show(self):

        if not os.path.isfile(self.traj_name):
            print('No trajectory selected')
            return

        if not os.path.isfile(self.top_name):
            print('No topography selected')
            return

        if not os.path.isfile(self.ina_name):
            print('No instrument selected')
            return

        self.top = Top(self.top_name)
        self.cnc = Cnc(self.traj_name)
        self.ina = Ina(self.ina_name)


        m = 40
        indices = self.top_valid_numbers()
        n = len(indices)

        matrix = np.zeros((n, m), float)

        k = 0

        while k < n:
            row = self.row_calculate(indices[k], m)
            matrix[k] = row
            k+=1

        vector_cut = np.zeros((n,), float)
        for i, item in enumerate(indices):
            vector_cut[i] = self.top.top.flatten()[item]


        z = optimize.nnls(matrix, vector_cut)[0]


        plt.plot(z)
        plt.show()


    def raw_cut(self, t=0.003):

        c = (100.0 * self.top.factor) / (self.ina.removal * self.ina.pressure * (np.pi * self.ina.ecc * self.ina.w_speed / 30.0))
        return t / c


    def new_traj(self, dt=0.003):

        a, b = self.top.start_point()
        mp = float(self.top.count / 2)
        x = self.top.step * (float(b) - mp)
        y = self.top.step * (-float(a) + mp - 1)

        traj_wt = self.cnc.trajectory_with_time(np.array([x, y, 0], float))

        time = traj_wt[:, 2]
        time = time[1:]

        t = 0.
        k = int(math.floor(time.sum() / dt))

        new_trajectory = np.zeros((k, 2), float)

        i = 0
        for element in range(k):
            new_trajectory[i] = ext_traj(t, traj_wt)
            t += dt
            i += 1

        return new_trajectory

    def top_valid_numbers(self):

        top_massive_valid = self.top.valid().flatten()
        top_valid_indices = []

        for i, element in enumerate(top_massive_valid):
            if element == True:
                top_valid_indices.append(i)

        return np.array(top_valid_indices, int)



    def row_calculate(self, k, m):

        trajectory = self.new_traj()
        x = self.top.coordinates()[k, 1]
        y = self.top.coordinates()[k, 2]
        rad = self.ina.diameter / 2 + self.ina.ecc
        step = rad / (m - 1)
        cut = self.raw_cut()

        row = np.zeros((m,), float)

        for p in trajectory:

            d = self.distance(x, p[0], y, p[1])
            if d < rad:
                r = 0
                f = 0
                while r < d:
                    r += step
                    f += 1
                dr = r - d
                k = dr/step
                row[f-1] = row[f-1] + k * cut
                row[f] = row[f] + (1-k) * cut


        return row



    def distance(self, x1, x2, y1, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


    def open_top(self):

        file_name = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.top_name = file_name

        self.top_fopenbtn.setText(os.path.basename(file_name))


    def open_cnc(self):

        file_name = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.traj_name = file_name

        self.traj_fopenbtn.setText(os.path.basename(file_name))


    def open_ina(self):

        file_name = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.ina_name = file_name

        self.ina_fopenbtn.setText(os.path.basename(file_name))


if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())