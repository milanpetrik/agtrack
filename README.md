
Tracker of Accelerometer and Gyroscope Sensors 
===============================================

The program loads and parses a file with the measurements from accelerometer
    and gyroscope.


Input Data File
---------------

The input file is expected to contain measured data from accelerometer and
    gyroscope.
The accelerometer data is represented by acceleration vectors (a_x, a_y, a_z)
    in [m/s^2].
The gyroscope data is represented by vectors (g_x, g_y, g_z) where the
    coordinates represent angular velocities in [deg/s] with respect to x-axis,
    y-axis, and z-axis.
All these values respect a Cartesian system of axes that is fixed to the body
    of the device.

The input file is a text file with the extension ".ag" (which stands for
    "accelerometer and gyroscope") and containing time-synchronized data from
    the accelerometer and gyroscope as lines in the format:

    <float>;<float>;<float>;<float>;<float>;<float>

    where <float> is a float number either in the format `1.234` or in the
    format `1,234`.
All the floats are in the range from `-2.0` to `2.0`.
No higher or lower values are possible and the values `-2.0` and `2.0` are
    considered as saturation.

The first three floats represents x, y, z coordiantes of an acceleration vector;
    these values are actually multiples of the gravitational acceleration (9.80665
    m/s^2) and the half of `acc_range` (the acceleration range in [m/s^2]).
Hence, if `a_x` is the first value of the line read from the file,
    the x-coordiante of the acceleration in [m/s^2] is given by
    `a_x*9.80665*acc_range/2`.

The second triplet of floats represents the angular velocities with respect to
    x-axis, y-axis, and z-axis.
These values are actually multiples of the half of `gyr_range` (the gyroscope
    range in [deg/s]).
Hence, if `g_x` is the fourth value of the line read from the file,
    the angular velocity arounf the x-axis in [deg/s] is given by
    `g_x*gyr_range/2`.

The file may also contain the lines of the format:

    frequency = <natural number>
    acc_range = <natural number>
    gyr_range = <natural number>

    to specify the sampling frequency in [Hz], the acceleration range in
    [m/s^2], and the gyroscope range in [deg/s].
These three values can be, however, also specified by program parameters as
    described in the sequel.

All the lines of the input file that begin with "#" are ignored.
All the lines that do not match the criteria described above (hence are not
    understood by the parser) are ignored, as well.


Example of Input Data File
--------------------------

    frequency = 10
    acc_range = 4
    gyr_range = 90
    AccelX;AccelY;AccelZ;GyroX;GyroY;GyroZ
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    # rozjezd
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    1,000; 0,000;0,500;0,000;0,000;0,000
    # jizda
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    0,000; 0,000;0,500;0,000;0,000;0,000
    # brzdeni
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000
    -1,000; 0,000;0,500;0,000;0,000;0,000

The sampling frequency is set to 10 [Hz], hence 10 lines represent 1 second of
    measurements.

The acceleration range is set to 4, hence e.g. the value `0,5` will stand for
    `0.5*9.80665*4/2 = 9.80665` [m/s^2].

The gyroscope range is set to 90, hence e.g. the value `1,0` will stand for
    `1.0*90/2 = 45` [deg/s].

The line `AccelX;AccelY;AccelZ;GyroX;GyroY;GyroZ` is ignored.

The device stands still for the first 1 second. The value `0,500` in the third
    coordiante simulates the gravitational acceleration.
Then, for another 1 second, the device accelerates in the direction of the
    x-axis with tha value of the acceleration equal to
    `1.0*9.80665*4/2 = 19.6133` [m/s^2].
Then, for another 1 second, there is no acceleration; hence the device performs
    a uniform linear motion in the direction of the x-axis.
Then, for the final 1 second, there is the negative acceleration `-1,000` in
    the direction of the x-axis; hence the device slows down until the zero
    velocity.


Running the Program
-------------------

    python agtrack.py [-h] [-f F] [-a A] [-g G] [--grav GRAV] [-q] [--draw] [--drawxy] [--drawyz] [--drawxz] input
                  
* positional arguments:
    * input ... input data file
* options:
    * -h, --help  ... show this help message and exit
    * -f F        ... sampling frequency [Hz], e.g. 833, 1660
    * -a A        ... acceleration range (multiple of the gravitational acceleration), e.g. 2, 4, 8
    * -g G        ... gyroscope range [deg/s], e.g. 16, 125, 250, 500, 1000, 2000
    * --grav GRAV ... gravitational acceleration in m/s^2; 9.80665 by default
    * -q          ... suppress warnings
    * --draw      ... draw a 3D plot
    * --drawxy    ... draw a 2D plot (x and y axes)
    * --drawyz    ... draw a 2D plot (y and z axes)
    * --drawxz    ... draw a 2D plot (x and z axes)
