import copy
import argparse
import numpy as np
from numpy.linalg import inv 
from rotations import *

class AGTracker:
    """
    Attributes:
        filename (str): name of the file with the measurements from
            accelerometer and gyroscope
        frequency (int): frequency in Hz
        acc_range (int): accelerometer range as a multiple of g
            (gravitational acceleration)
        gyr_range (int): gyroscope range in degrees per second
        grav (float): gravitational acceleration in m*s^(-2); `9.80665` by default
        measurements (list of ((float, float, float), (float, float, float))):
            list of `((ax, ay, az), (gx, gy, gz))` where `(ax, ay, az)` is
            the acceleration and `(gx, gy, gz)` is the angular velocity
            given by the gyroscope
        quiet (bool): suppress warnings; `False` by default
    """

    def __init__(self,
                 filename,
                 frequency = None,
                 acc_range = None,
                 gyr_range = None,
                 grav = 9.80665,
                 quiet = False):
        """
        Args:
            filename (str): name of the file with the measurements from
                accelerometer and gyroscope
            frequency (int): frequency in Hz
            acc_range (int): accelerometer range as a multiple of g
                (gravitational acceleration)
            gyr_range (int): gyroscope range in degrees per second
            grav (float): gravitational acceleration in m*s^(-2); `9.80665` by default
            quiet (bool): suppress warnings; `False` by default
        """
        self.filename = filename
        self.frequency = frequency
        self.acc_range = acc_range
        self.gyr_range = gyr_range
        self.grav = grav
        self.quiet = quiet
        self.measurements = None
        self.load()

    def load(self):
        """
            Read a text file with the measurements from accelerometer and
                gyroscope.

            The data are parsed and saved to the `measurements` attribute:

                * The acceleration data are multiplied by `self.acc_range/2`
                    and by `self.grav`.
                * The gyroscope data are multiplied by `self.gyr_range/2`.
        """
        coord_names = ['x', 'y', 'z'] # this is for reporting an error
        if self.acc_range != None:
            acc_coef = self.acc_range / 2
        else:
            acc_coef = None
        if self.gyr_range != None:
            gyr_coef = self.gyr_range / 2
        else:
            gyr_coef = None
        self.measurements = []
        with open(self.filename) as f:
            line_counter = 0
            # saturation counters count occurrences of `2.0` in the input data file
            # for each coordinate of the acceleration and the angular speed given
            # by the gyroscope
            sat_counter = 6 * [0]
            sat_begin = 6 * [None]
            for line in f:
                line_counter += 1
                if line[0] == '#': # ignore lines starting with '#'
                    continue
                elif line[0].isalpha() and '=' in line:
                    words = line.split('=')
                    left_value = words[0].strip()
                    right_value = words[1].strip()
                    if left_value == 'frequency' and self.frequency == None:
                        self.frequency = int(right_value)
                    elif left_value == 'acc_range' and self.acc_range == None:
                        self.acc_range = int(right_value)
                        acc_coef = self.acc_range / 2
                    elif left_value == 'gyr_range' and self.gyr_range == None:
                        self.gyr_range = int(right_value)
                        gyr_coef = self.gyr_range / 2
                elif line[0].isdigit() or line[0] == '-':
                    if self.acc_range == None:
                        raise Exception('acc_range not defined')
                    if self.gyr_range == None:
                        raise Exception('gyr_range not defined')
                    words = line.strip().replace(',', '.').split(';') # strip() removes "\n" at the end of the line
                    numbers = list(map(float, words))
                    # warnings
                    if not self.quiet:
                        for i in range(len(numbers)):
                            if abs(numbers[i] - 2.0) < 0.0001:
                                if sat_counter[i] == 0:
                                    sat_counter[i] = 1
                                    sat_begin[i] = line_counter
                                else:
                                    sat_counter[i] += 1
                            else:
                                if sat_counter[i] > 3:
                                    if i < 3:
                                        who = 'accelerometer'
                                        crd_name = coord_names[i]
                                    else:
                                        who = 'gyroscope'
                                        crd_name = coord_names[i - 3]
                                    print('WARNING: {} saturated in {} on {} lines starting from line {}'.format(
                                        who, crd_name, sat_counter[i], sat_begin[i]))
                                sat_counter[i] = 0
                                sat_begin[i] = None
                    # save data
                    acceleration = [v*acc_coef*self.grav for v in numbers[:3]]
                    angular_velocity = [v*gyr_coef for v in numbers[3:]]
                    self.measurements.append((tuple(acceleration), tuple(angular_velocity)))

    def parse(self):
        #print(self.ag_data['measurements'])
        for (acc, gyr) in self.measurements:
            print(acc, gyr)

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
    agtracker.parse()

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
