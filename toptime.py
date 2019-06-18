import os
import numpy as np
import tempfile
from scipy import interpolate

class T1():
    def __init__(self, path):
        with open(os.path.abspath(path), 'r') as f:
            top = f.read()
        top = top.split()
        self.header = top[0:9]
        self.end = top[-33:]
        self.count = int(top[0])  # 40 - размерность сетки
        self.step = float(top[1])  # 9.800000 - шаг сетки
        self.curvR = float(top[2])  # 1389.600000 – радиус кривизны
        self.diam = float(top[3])  # 376.000000 – диаметр обработки
        self.buff = float(top[4])  # 376.000000
        self.devD = float(top[5])  # 58.000000 – диаметр инструмента
        self.devPress = float(top[6])  # 130.000000 – удельное давление
        self.devSpeed = float(top[7])  # 300.000000 – скорость шпинделя об.\мин.
        self.devEx = float(top[8])  # 6.000000 – эксцентриситет
        del top[0:9]
        del top[-33:]
        top = np.array(top, float)
        self.top = top.reshape(self.count, self.count)

    def rms(self):
        return np.std(self.top[self.top < 9000]) * self.factor

    def top_for_display(self):
        ans = self.top
        ans[self.top > 9000] = 0
        return ans

class Top():
    def __init__(self, path):
        with open(os.path.abspath(path), 'r') as f:
            top = f.read()
        top = top.split()
        self.header = top[0:8]
        self.end = top[:-2]
        self.count = int(top[0])
        self.factor = float(top[1])
        self.step = float(top[2])
        del top[0:8]
        del top[-2:]
        top = np.array(top, float)
        self.top = np.flipud(top.reshape(self.count, self.count))

    @staticmethod
    def write_file(header, top, end):
        top_write = []
        top_write.extend(header)
        top_write.extend(top.flatten().tolist())
        top_write.extend(end)

        text = ''
        i = 0
        for e in top_write:
            if i < 3:
                text += str(e) + ' '
                i += 1
            elif i == 3:
                text += str(e) + ' \n'
                i = 0

        path = os.path.join(tempfile.gettempdir(), 'top_data.top')

        with open(path, 'w') as f:
            f.write(text)

    def multiply (self, number):
        self.top = self.top*number

    def coordinates(self):
        coord_list = []
        for idx, item in np.ndenumerate(self.top):
            coord_list.append([item, self.convert(idx, coord=False)[0], self.convert(idx, coord=False)[1]])
        coord = np.array(coord_list, float)
        return coord

    def valid(self):
        v = self.top < 9000.
        return v

    def convert(self, xy, coord = True):
        """Converts from coordinates to top indices if coord == True, otherwise
        converts from top indices to coordinates"""

        if coord:
            x_top = int(xy[1] / self.step + self.count / 2)
            y_top = int(xy[0] / self.step + self.count / 2)
            return (x_top, y_top)

        else:
            x_coord = (xy[1] - self.count / 2) * self.step
            y_coord = (xy[0] - self.count / 2) * self.step
            return (x_coord, y_coord)

    def __add__(self, other):

        sum_factor = 2.0*self.factor*other.factor/(self.factor + other.factor)

        if self.count == other.count:
            sum_count = self.count
            sum_step = self.step
            sum_1 = self.top * self.factor + other.top * other.factor
            sum = sum_1 / sum_factor
            i = 0
            for a in sum:
                k = 0
                for b in a:
                    if b >= 5000:
                        sum[i, k] = 10000
                        k += 1
                    else:
                        k += 1
                i += 1

        elif self.count <= other.count:
            sum_count = other.count
            sum_step = other.step
            x = y = np.arange(1, self.count+1, 1)
            f = interpolate.interp2d(x, y, self.top, kind='cubic')
            xnew = ynew = np.arange(1, other.count+1, 1)
            z = f(xnew, ynew)
            sum_1 = z * self.factor + other.top * other.factor
            sum = sum_1 / sum_factor
            i = 0
            for a in sum:
                k = 0
                for b in a:
                    if b >= 5000:
                        sum[i, k] = 10000
                        k += 1
                    else:
                        k += 1
                i += 1

        else:
            sum_count = self.count
            sum_step = self.step
            x = y = np.arange(1, other.count + 1, 1)
            f = interpolate.interp2d(x, y, self.top, kind='cubic')
            xnew = ynew = np.arange(1, self.count + 1, 1)
            z = f(xnew, ynew)
            sum_1 = self.top * self.factor + z * other.factor
            sum = sum_1 / sum_factor
            i = 0
            for a in sum:
                k = 0
                for b in a:
                    if b >= 5000:
                        sum[i, k] = 10000
                        k += 1
                    else:
                        k += 1
                i += 1

        header = []
        header.append(sum_count)
        header.append(sum_factor)
        header.append(sum_step)
        header.extend(self.header[3:8])

        Top.write_file(header, sum, self.end)

    def start_point(self):
        a = self.count - np.where(self.valid())[0][0]
        b = np.where(self.valid())[1][0]
        return (a, b)

    def rms(self):
        return np.std(self.top[self.top < 9000]) * self.factor

    def top_for_display(self):
        ans = self.top
        ans[self.top > 9000] = 0
        return ans