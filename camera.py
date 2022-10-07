import numpy as np
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from scipy.spatial.transform import Rotation as R
from FramesViewer import utils

class Camera():
    def __init__(self):
        self.position = [3, -3, 3, 0, 0, 0, 0, 0, 1]
        self.zoom = 5
        self.T_camera_world = None
        self.T_world_camera = None

    def getCameraPosition(self):
        return self.position

    def setCameraPosition(self, pos, center, up=[0, 0, 1]):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(pos[0], pos[1], pos[2], center[0], center[1], center[2], up[0], up[1], up[2])

    def update(self):
        self.T_camera_world = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))
        self.T_world_camera = np.linalg.inv(self.T_camera_world)

    def applyZoom(self, incr_value):
        self.zoom = max(0, self.zoom - incr_value)

    def move(self, mouse_rel):

        mouse_rel = np.array([*mouse_rel, 0])
        mouse_rel[0] = -mouse_rel[0]

        T_camera_world = utils.translateInSelf(self.T_camera_world.copy(), mouse_rel)

        vec = T_camera_world[:3, 3]

        self.position[0] += vec[0]*0.01
        self.position[1] += vec[1]*0.01
        self.position[3] += vec[0]*0.01
        self.position[4] += vec[1]*0.01

        self.setCameraPosition(self.position[:3], self.position[3:6])

    def rotate(self, mouse_rel):
        # axis = [0, -0.005*self.mouse_rel[1], -0.005*self.mouse_rel[0]]
        # axis = [0, 0, -0.005*self.mouse_rel[0]]
        axis = [0, 0, -mouse_rel[0]*0.005]


        # TODO rotate about camera_position[3:6] (center)

        pos = self.position[:3]
        axis = np.array(axis)
        rot_mat = R.from_euler('xyz', axis, degrees=False).as_matrix()
        new_pos = rot_mat @ pos

        self.position[:3] = new_pos

        self.setCameraPosition(new_pos, self.position[3:6])

