
__all__ = ['get_composed_rotation']

import math
import numpy as np
#from numpy.linalg import inv

def get_rotation_Z(phi):    #phi is in degrees, returns matrix of the rotation
    phi_d = math.radians(phi)
    return np.array([[math.cos(phi_d),-math.sin(phi_d),0],
                     [math.sin(phi_d),math.cos(phi_d),0],
                     [0,0,1]])


def get_rotation_Y(phi):    #phi is in degrees, returns matrix of the rotation
    phi_d = math.radians(phi)
    return np.array([[math.cos(phi_d),0, math.sin(phi_d)],
                     [0,1,0],
                     [-math.sin(phi_d),0,math.cos(phi_d)]])


def get_rotation_X(phi):    #phi is in degrees, returns matrix of the rotation
    phi_d = math.radians(phi)
    return np.array([[1,0,0],
                     [0, math.cos(phi_d),-math.sin(phi_d)],
                     [0, math.sin(phi_d),math.cos(phi_d)]])

def get_composed_rotation(phi_X, phi_Y, phi_Z): 
    # angles in degrees, returns matrix of the composed rotation
    # order of matrix multiplication (rotations) must be verified!!!
    # at the moment Rot_X is applied first
    # later rotation must multiply earlier from the left

    phi_X_d = math.radians(phi_X)
    phi_Y_d = math.radians(phi_Y)
    phi_Z_d = math.radians(phi_Z)

    return get_rotation_Z(phi_Z) @ get_rotation_Y(phi_Y) @ get_rotation_X(phi_X)

def apply_rotation(phi_X, phi_Y, phi_Z, v): 
    return get_composed_rotation(30, 0, 30) @ v

    

