from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
from scipy.spatial.transform import Rotation as R

def make_pose(translation, xyz, degrees=True):
    pose = np.eye(4)
    pose[:3, :3] = R.from_euler('xyz', xyz, degrees=degrees).as_matrix()
    pose[:3, 3] = translation
    return pose
