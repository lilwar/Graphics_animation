import os


class Ina:
    def __init__(self, path):
        with open(os.path.abspath(path), 'r') as f:
            ina = f.readlines()
            shield_count = int(ina[0])
            self.shield_count = shield_count
            self.diameter = float(ina[self.shield_count + 1])
            self.pressure = float(ina[self.shield_count + 2])
            self.w_speed = float(ina[self.shield_count + 3])
            self.ecc = float(ina[self.shield_count + 4])
            self.removal = float(ina[self.shield_count + 5])
            profile = []
            for element in ina[self.shield_count + 7].split():
                profile.append(float(element))
            profile.append(0.)
            self.profile = profile
            self.profile_x = list(self.profile_x_coord())

    def profile_x_coord(self):
        to_return = len(self.profile)
        returned = 0
        for i in range(0, to_return + 1):
            for j in range(0, i + 1):
                if returned <= to_return:
                    yield (i ** 2 + j ** 2) ** 0.5
                    returned += 1

    def get_prof_point(self, r):
        x = r * (2 * self.profile_x[-1] + 1) / (self.diameter + self.ecc)
        L = len(self.profile)
        for i in range(0, L):
            if i == L - 1:
                return 0.0
                break
            if self.profile_x[i] <= x <= self.profile_x[i + 1]:
                dd = x - self.profile_x[i]
                EE = self.profile_x[i + 1] - self.profile_x[i]
                if EE <= 0.0:
                    EE = 1.0
                pp = self.profile[i + 1] - self.profile[i]
                return self.profile[i] + pp * dd / EE
                break
