import copy
import argparse
import numpy as np
from numpy.linalg import inv 
from rotations import *
from agfile import read_ag_file

class AGTracker:

    def __init__(self,
                 filename,
                 frequency = None,
                 acc_range = None,
                 gyr_range = None,
                 grav = 9.80665):
        self.ag_data = read_ag_file(filename,
                                    frequency = frequency,
                                    acc_range = acc_range,
                                    gyr_range = gyr_range,
                                    grav = grav)

    def parse(self):
        #print(self.ag_data['measurements'])
        for (acc, gyr) in self.ag_data['measurements']:
            print(acc, gyr)

    def load_file(self, filename, frequency, acc_range, gyr_range):
        self.history = []
        self.filename = filename
        self.frequency = frequency
        self.acc_range = acc_range
        self.gyr_range = gyr_range
        self.acc_coef = self.acc_range / 2
        self.gyr_coef = self.gyr_range / 2
        self.period = 1 / self.frequency
        self.initial_acceleration = None
        self.rotation = np.identity(3) # matrix of a rotation from the beginning of the movement
        time = 0.0
        velocity = [0.0, 0.0, 0.0]
        position = [0.0, 0.0, 0.0]
        #angle = [0.0, 0.0, 0.0]
        with open(self.filename, "r") as input_file:
            first = True
            for line in input_file:
                if first: # ignore the first line of the file
                    first = False
                else:
                    words = line.strip().replace(',', '.').split(';') # using strip() to remove "\n" at the end of the line
                    numbers = list(map(float, words))
                    acceleration_in_current_coordinates = numbers[:3]
                    for i in range(len(acceleration_in_current_coordinates)):
                        acceleration_in_current_coordinates[i] *= self.acc_coef * grav_accel
                    angle_velocity = numbers[3:]
                    for i in range(len(angle_velocity)):
                        angle_velocity[i] *= self.gyr_coef
                    angle_velocity = np.asarray(angle_velocity)
                    angle_change_in_current_coordinates = angle_velocity * self.period
                    if self.initial_acceleration == None:
                        self.initial_acceleration = copy.copy(acceleration_in_current_coordinates)
                    rotation_in_current_coordinates = get_composed_rotation(*angle_change_in_current_coordinates)
                    rotation_in_starting_coordinates = self.rotation @ rotation_in_current_coordinates @ inv(self.rotation)
                    self.rotation = rotation_in_starting_coordinates @ self.rotation
                    acceleration = self.rotation @ acceleration_in_current_coordinates
                    for i in range(3):
                        acceleration[i] -= self.initial_acceleration[i]
                        velocity[i] += acceleration[i] * self.period
                        position[i] += velocity[i] * self.period
                        #angle[i] += angle_velocity[i] * self.period
                    history_item = {}
                    history_item['time'] = time
                    history_item['acceleration'] = copy.copy(acceleration)
                    history_item['velocity'] = copy.copy(velocity)
                    history_item['position'] = copy.copy(position)
                    history_item['angle velocity'] = copy.copy(angle_velocity)
                    #history_item['angle'] = copy.copy(angle)
                    self.history.append(history_item)
                    time += self.period

    def draw(self):
        import matplotlib.pyplot as plt
        pos_x = []
        pos_y = []
        pos_z = []
        for item in self.history:
            pos_x.append(item['position'][0])
            pos_y.append(item['position'][1])
            pos_z.append(item['position'][2])

        fig = plt.figure().add_subplot(projection='3d')

        fig.plot(pos_x, pos_y, pos_z, "b.", label='parametric curve')
        fig.legend()

        plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help = "input data file")
    parser.add_argument("-f", help = "sampling frequency [Hz], e.g. 833, 1660")
    parser.add_argument("-a", help = "acceleration range (multiple of the gravitational acceleration), e.g. 2, 4, 8")
    parser.add_argument("-g", help = "gyroscope range [deg/s], e.g. 16, 125, 250, 500, 1000, 2000")
    parser.add_argument("--grav", help = "gravitational acceleration in m/s^2; 9.80665 by default")
    parser.add_argument("--draw", action = "store_true", help = "draw a plot")

    args = parser.parse_args()
    if args.f:
        frequency = int(args.f)
    else:
        frequency = None
    if args.a:
        acc_range = int(args.a)
    else:
        acc_range = None
    if args.g:
        gyr_range = int(args.g)
    else:
        gyr_range = None
    if args.grav:
        grav = float(args.grav)
    else:
        grav = 9.80665

    agtracker = AGTracker(args.input,
                          frequency = frequency,
                          acc_range = acc_range,
                          gyr_range = gyr_range,
                          grav = grav)
    #agtracker.parse()

    if args.draw:
        agtracker.draw()

if __name__ == "__main__":
    main()




#class AGTracker:
#
#    def __init__(self, file_name, frequency, acc_range, gyr_range):
#        self.load_file(file_name, frequency, acc_range, gyr_range)
#
#    def load_file(self, file_name, frequency, acc_range, gyr_range):
#        self.history = []
#        self.file_name = file_name
#        self.frequency = frequency
#        self.acc_range = acc_range
#        self.gyr_range = gyr_range
#        self.acc_coef = self.acc_range / 2
#        self.gyr_coef = self.gyr_range / 2
#        self.period = 1 / self.frequency
#        self.initial_acceleration = None
#        self.rotation = np.identity(3) # matrix of a rotation from the beginning of the movement
#        time = 0.0
#        velocity = [0.0, 0.0, 0.0]
#        position = [0.0, 0.0, 0.0]
#        #angle = [0.0, 0.0, 0.0]
#        with open(self.file_name, "r") as input_file:
#            first = True
#            for line in input_file:
#                if first: # ignore the first line of the file
#                    first = False
#                else:
#                    words = line.strip().replace(',', '.').split(';') # using strip() to remove "\n" at the end of the line
#                    numbers = list(map(float, words))
#                    acceleration_in_current_coordinates = numbers[:3]
#                    for i in range(len(acceleration_in_current_coordinates)):
#                        acceleration_in_current_coordinates[i] *= self.acc_coef * grav_accel
#                    angle_velocity = numbers[3:]
#                    for i in range(len(angle_velocity)):
#                        angle_velocity[i] *= self.gyr_coef
#                    angle_velocity = np.asarray(angle_velocity)
#                    angle_change_in_current_coordinates = angle_velocity * self.period
#                    if self.initial_acceleration == None:
#                        self.initial_acceleration = copy.copy(acceleration_in_current_coordinates)
#                    rotation_in_current_coordinates = get_composed_rotation(*angle_change_in_current_coordinates)
#                    rotation_in_starting_coordinates = self.rotation @ rotation_in_current_coordinates @ inv(self.rotation)
#                    self.rotation = rotation_in_starting_coordinates @ self.rotation
#                    acceleration = self.rotation @ acceleration_in_current_coordinates
#                    for i in range(3):
#                        acceleration[i] -= self.initial_acceleration[i]
#                        velocity[i] += acceleration[i] * self.period
#                        position[i] += velocity[i] * self.period
#                        #angle[i] += angle_velocity[i] * self.period
#                    history_item = {}
#                    history_item['time'] = time
#                    history_item['acceleration'] = copy.copy(acceleration)
#                    history_item['velocity'] = copy.copy(velocity)
#                    history_item['position'] = copy.copy(position)
#                    history_item['angle velocity'] = copy.copy(angle_velocity)
#                    #history_item['angle'] = copy.copy(angle)
#                    self.history.append(history_item)
#                    time += self.period
#
#    def draw(self):
#        import matplotlib.pyplot as plt
#        pos_x = []
#        pos_y = []
#        pos_z = []
#        for item in self.history:
#            pos_x.append(item['position'][0])
#            pos_y.append(item['position'][1])
#            pos_z.append(item['position'][2])
#
#        fig = plt.figure().add_subplot(projection='3d')
#
#        fig.plot(pos_x, pos_y, pos_z, "b.", label='parametric curve')
#        fig.legend()
#
#        plt.show()
#
#def main():
#    parser = argparse.ArgumentParser()
#    parser.add_argument("input", help = "input data file")
#    parser.add_argument("-a", help = "acceleration range (multiple of 9.80665 m/s^2), e.g. 2, 4, 8")
#    parser.add_argument("-g", help = "gyroscope range [deg/s], e.g. 16, 125, 250, 500, 1000, 2000")
#    parser.add_argument("-f", help = "sampling frequency [Hz], e.g. 833, 1660")
#    parser.add_argument("--draw", action = "store_true", help = "draw a plot")
#
#    args = parser.parse_args()
#
#    agtracker = AGTracker(args.input, int(args.f), int(args.a), int(args.g))
#
#    if args.draw:
#        agtracker.draw()
#
#if __name__ == "__main__":
#    main()
