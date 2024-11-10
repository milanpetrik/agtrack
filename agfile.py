import argparse

def read_ag_file(filename,
                 frequency = None,
                 acc_range = None,
                 gyr_range = None,
                 grav = 9.80665):
    """
        Read a text file with the measurements from accelerometer and
            gyroscope.

        Args:
            filename (str): name of the file
            frequency (int): frequency in Hz
            acc_range (int): accelerometer range as a multiple of g
                (gravitational acceleration)
            gyr_range (int): gyroscope range in degrees per second
            grav (float): gravitational acceleration in m*s^(-2)

        Returns (dict): a dictionary with the keys:

            * 'frequency' (int): frequency in Hz
            * 'acc_range' (int): accelerometer range as a multiple of g
                (gravitational acceleration)
            * 'gyr_range' (int): gyroscope range in degrees per second
            * 'grav' (float): gravitational acceleration in m*s^(-2)
            * 'measurements' (list of ((float, float, float), (float, float, float))):
    """
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
        for line in f:
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
                acceleration = [v*acc_coef*grav for v in numbers[:3]]
                angle_velocity = [v*gyr_coef for v in numbers[3:]]
                measurements.append((tuple(acceleration), tuple(angle_velocity)))
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
    args = parser.parse_args()
    ag_data = read_ag_file(args.input)
    print('frequency:', ag_data['frequency'])
    print('acc_range:', ag_data['acc_range'])
    print('gyr_range:', ag_data['gyr_range'])
    print('measurements:', len(ag_data['measurements']))

if __name__ == "__main__":
    main()
