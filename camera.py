import numpy as np
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from scipy.spatial.transform import Rotation as R
from FramesViewer import utils
import time 

class Camera():
    def __init__(self, pos, center, up=[0, 0, 1], zoom=5):
        self.pos    = pos
        self.center = center
        self.up     = up
        self.zoom   = zoom

        self.pose   = None

        self.dt     = 0

        self.update(0)

    def updatePose(self):
        self.pose         = np.eye(4)
        self.pose[:3, :3] = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))[:3, :3]
        self.pose[:3, 3]  = self.pos

    def update(self, dt):
        self.dt = dt

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.pos[0], self.pos[1], self.pos[2], self.center[0], self.center[1], self.center[2], self.up[0], self.up[1], self.up[2])

        self.updatePose()

    def applyZoom(self, incr_value):
        self.zoom = max(0, self.zoom - incr_value*self.dt)

    def getTransDiff(self, mouse_rel):
        mouse_rel = np.array([*mouse_rel, 0])
        mouse_rel[0] = -mouse_rel[0]

        old_pose = self.pose.copy()
        self.pose = utils.translateInSelf(self.pose, mouse_rel)
        trans_diff = self.pose[:3, 3] - old_pose[:3, 3]

        return trans_diff


    def move(self, mouse_rel):
        trans_diff = self.getTransDiff(mouse_rel)

        self.pos    += trans_diff*self.dt
        self.center += trans_diff*self.dt

    def rotate(self, mouse_rel):
        trans_diff = self.getTransDiff(mouse_rel)
        
        self.pos   += trans_diff*self.dt*2

