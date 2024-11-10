import argparse

def read_ag_file(filename,
                 frequency = None,
                 acc_range = None,
                 gyr_range = None,
                 grav = 9.80665,
                 quiet = False):
    """
        Read a text file with the measurements from accelerometer and
            gyroscope.

        Args:
            filename (str): name of the file
            frequency (int): frequency in Hz
            acc_range (int): accelerometer range as a multiple of g
                (gravitational acceleration)
            gyr_range (int): gyroscope range in degrees per second
            grav (float): gravitational acceleration in m*s^(-2); `9.80665` by default
            quiet (bool): suppress warnings; `False` by default

        Returns (dict): a dictionary with the keys:

            * 'frequency' (int): frequency in Hz
            * 'acc_range' (int): accelerometer range as a multiple of g
                (gravitational acceleration)
            * 'gyr_range' (int): gyroscope range in degrees per second
            * 'grav' (float): gravitational acceleration in m*s^(-2)
            * 'measurements' (list of ((float, float, float), (float, float, float))):
                list of `((ax, ay, az), (gx, gy, gz))` where `(ax, ay, az)` is
                the acceleration and `(gx, gy, gz)` is the angular velocity
                given by the gyroscope
    """
    coord_names = ['x', 'y', 'z']
    if acc_range != None:
        acc_coef = acc_range / 2
    else:
        acc_coef = None
    if gyr_range != None:
        gyr_coef = gyr_range / 2
    else:
        gyr_coef = None
    measurements = []
    with open(filename) as f:
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
                if left_value == 'frequency':
                    frequency = int(right_value)
                elif left_value == 'acc_range' and acc_range == None:
                    acc_range = int(right_value)
                    acc_coef = acc_range / 2
                elif left_value == 'gyr_range' and gyr_range == None:
                    gyr_range = int(right_value)
                    gyr_coef = gyr_range / 2
            elif line[0].isdigit() or line[0] == '-':
                if acc_range == None:
                    raise Exception('acc_range not defined')
                if gyr_range == None:
                    raise Exception('gyr_range not defined')
                words = line.strip().replace(',', '.').split(';') # strip() removes "\n" at the end of the line
                numbers = list(map(float, words))
                # warnings
                if not quiet:
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
                acceleration = [v*acc_coef*grav for v in numbers[:3]]
                angular_velocity = [v*gyr_coef for v in numbers[3:]]
                measurements.append((tuple(acceleration), tuple(angular_velocity)))
    return {'frequency': frequency,
            'acc_range': acc_range,
            'gyr_range': gyr_range,
            'grav': grav,
            'measurements': measurements}

def main():
    """
        Runs read_ag_file() from console with a filename as an argument and
            displays the values of frequency, acc_range, gyr_range, and the number
            of measurements.
    """
    parser = argparse.ArgumentParser(
        prog = 'python3 agfile.py',
        description = 'Reads a text file with the measurements from accelerometer and gyroscope and displays the values of frequency, acc_range, gyr_range, and the number of measurements.',
        epilog = 'Text at the bottom of help')
    parser.add_argument("input", help = "input AG file")
    parser.add_argument("-q", action = "store_true", help = "suppress warnings")
    args = parser.parse_args()
    if args.q:
        quiet = True
    else:
        quiet = False
    ag_data = read_ag_file(args.input, quiet = quiet)
    print('frequency:', ag_data['frequency'])
    print('acc_range:', ag_data['acc_range'])
    print('gyr_range:', ag_data['gyr_range'])
    print('measurements:', len(ag_data['measurements']))

if __name__ == "__main__":
    main()
