import os, sys
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton,
QApplication, QFileDialog, QVBoxLayout, QHBoxLayout, QProgressBar)
from PyQt5.QtGui import QIcon
import numpy as np
import matplotlib.animation as animation
from matplotlib import pyplot as plt
from ina import Ina
from toptime import Top
from cnc import Cnc
from cut import cutting
from linear_system import solution
from matplotlib.patches import Circle
from math import sin, cos


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

        hbox4 = QHBoxLayout()
        self.runbtn = QPushButton("Run", self)
        self.runbtn.setToolTip('Run program')
        hbox4.addStretch(1)
        hbox4.addWidget(self.runbtn)
        hbox4.addStretch(1)
        self.runbtn.clicked.connect(self.show_animation)
        vbox.addLayout(hbox4)

        hbox3 = QHBoxLayout()
        self.lbl = QLabel("Animation completed: ", self)
        hbox3.addWidget(self.lbl)
        self.pbar = QProgressBar(self)
        hbox3.addWidget(self.pbar)
        vbox.addLayout(hbox3)

        self.setGeometry(300, 150, 500, 300)
        self.setWindowTitle('Graphics trajectory animation')

        self.setWindowIcon(QIcon('spirale.png'))

        self.show()

    def show_animation(self):

        if not os.path.isfile(self.top_name):
            print('No topography selected')
            return

        top = Top(self.top_name)

        if not os.path.isfile(self.traj_name):
            print('No trajectory selected')
            return

        cnc = Cnc(self.traj_name)
        a, b = top.start_point()
        x, y = top.convert((a, b), coord=False)

        traj = cnc.trajectory(np.array([x, y], float))

        if not os.path.isfile(self.ina_name):
            print('No instrument selected')
            return

        ina = Ina(self.ina_name)

        x = solution(traj, top, ina)  # находим решение системы линейных уравнений методом МНК

        top_list = []
        top_list.append(np.where(top.valid(), top.top, np.zeros_like(top.top)))
        i = 0

        for point in traj:
            current_cut = np.where(top.valid(), cutting(point, top, ina, x[i]), np.zeros_like(top.top))  # составляем список топографий, учитывая съем в каждой точке траектоории
            current_top = top_list[i] - current_cut
            top_list.append(current_top)
            i += 1

        fig, ax = plt.subplots()

        ax.axis([0, top.count-1, 0, top.count-1])

        circle = Circle((top.start_point()[1], top.start_point()[0]), radius=(ina.diameter / 2 + ina.ecc) / top.step, color='red', fill=True)  # вводим круг, изображающий инструмент
        ax.add_patch(circle)

        def init():
            ax.imshow(top_list[0], cmap='plasma')
            return top_list, circle

        def update(num, top_list, traj, circle, self):
            ax.cla()
            ax.axis([0, top.count - 1, 0, top.count - 1])
            ax.imshow(top_list[num], cmap='plasma')
            ax.add_patch(circle)
            x0, y0 = traj[num]
            x = x0 + ina.ecc * sin(0.2*num)
            y = y0 - ina.ecc * (1 - cos(0.2*num))
            circle.center = (top.convert((x, y))[1], top.convert((x, y))[0])
            self.pbar.setValue(num / len(top_list) * 100)
            return top_list, circle

        ani = animation.FuncAnimation(fig, update, len(top_list), init_func=init, fargs=[top_list, traj, circle, self], interval=100, repeat=False)
        plt.show()

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