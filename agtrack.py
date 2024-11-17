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
        measurements (list of (numpy.array, numpy.array)):
            list of `([ax, ay, az], [gx, gy, gz])` where `[ax, ay, az]` is
            the acceleration and `[gx, gy, gz]` is the angular velocity
            given by the gyroscope
        trajectory (list of numpy.array): the resulting trajectory as a list of
            positions (i.e. three coordinates)
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
        self.trajectory = None
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
                    #self.measurements.append((tuple(acceleration), tuple(angular_velocity)))
                    self.measurements.append((np.array(acceleration), np.array(angular_velocity)))

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
    def parse(self):
        # The initial acceleration
        #   It will be computed as the average of the first n measurements,
        #   where n is the values of `init_acc_range`.
        #   It is supposed to be a vector of the gravitational acceleration.
        #   Subsequently, this vector will be subtracted from all the
        #   acceleration measurements.
        init_acc = np.array([0.0, 0.0, 0.0])
        init_acc_range = 10
        for i in range(init_acc_range):
            acc, __ = self.measurements[i]
            init_acc += acc
        init_acc /= init_acc_range
        #print('init_acc:', init_acc)

        # The initial rotation as a matrix
        rotation = np.identity(3)

        # Construction of the trajectory
        #   as a list of (time, pos, vel, acc, gyr) where:
        #       time ... absolute time in seconds
        #       pos = (sx, sy, sz) ... position
        #       vel = (vx, vy, vz) ... velocity
        #       acc = (ax, ay, az) ... acceleration
        self.trajectory = [(0.0, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))]
        dt = 1 / self.frequency # time period between two data samples
        time = 0.0 # starting time
        vel = np.array([0.0, 0.0, 0.0]) # initial velocity
        pos = np.array([0.0, 0.0, 0.0]) # initial position
        for i in range(len(self.measurements)):
            time += dt
            acc_meas, gyr_meas = self.measurements[i] # measured acceleration and gyroscope angular velocity
            acc_meas = np.array(acc_meas)
            gyr_meas = np.array(gyr_meas)
            acc_meas -= init_acc
            # gyroscope
            rotation_in_current_coords = get_composed_rotation(gyr_meas[0]*dt, gyr_meas[1]*dt, gyr_meas[2]*dt)
            rotation_in_starting_coords = rotation @ rotation_in_current_coords @ inv(rotation)
            rotation = rotation_in_starting_coords @ rotation
            acc = rotation @ acc_meas
            # Euler's Method
            vel += acc * dt
            pos += vel * dt
            # the result
            self.trajectory.append((time, tuple(pos), tuple(vel), tuple(acc)))

    def draw_3D(self):
        """
            Draw `self.trajectory` as a 3D plot.
        """
        import matplotlib.pyplot as plt
        fig = plt.figure().add_subplot(projection='3d')
        plot_x = []
        plot_y = []
        plot_z = []
        for time, (x, y, z), __, __ in self.trajectory:
            plot_x.append(x)
            plot_y.append(y)
            plot_z.append(z)
        fig.plot(plot_x, plot_y, plot_z, "b.", label='Trajectory')
        fig.set_xlabel('x')
        fig.set_ylabel('y')
        fig.set_zlabel('z')
        fig.legend()
        plt.show()

    def draw_2D(self):
        """
            Draw `self.trajectory` as a 2D plot involving only x and y
                coordinates.
        """
        import matplotlib.pyplot as plt
        plot_x = []
        plot_y = []
        print(self.trajectory[0])
        for time, (x, y, z), __, __ in self.trajectory:
            plot_x.append(x)
            plot_y.append(y)
        plt.plot(plot_x, plot_y, "b.", label="Trajectory")
        plt.legend()
        plt.axis('equal')
        plt.show()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help = "input data file")
    parser.add_argument("-f", help = "sampling frequency [Hz], e.g. 833, 1660")
    parser.add_argument("-a", help = "acceleration range (multiple of the gravitational acceleration), e.g. 2, 4, 8")
    parser.add_argument("-g", help = "gyroscope range [deg/s], e.g. 16, 125, 250, 500, 1000, 2000")
    parser.add_argument("--grav", help = "gravitational acceleration in m/s^2; 9.80665 by default")
    parser.add_argument("-q", action = "store_true", help = "suppress warnings")
    parser.add_argument("--draw", action = "store_true", help = "draw a 3D plot")
    parser.add_argument("--draw2d", action = "store_true", help = "draw a 2D plot")

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
    if args.q:
        quiet = True
    else:
        quiet = False

    agtracker = AGTracker(args.input,
                          frequency = frequency,
                          acc_range = acc_range,
                          gyr_range = gyr_range,
                          grav = grav,
                          quiet = quiet)
    agtracker.parse()

    if args.draw:
        agtracker.draw_3D()

    if args.draw2d:
        agtracker.draw_2D()

if __name__ == "__main__":
    main()
