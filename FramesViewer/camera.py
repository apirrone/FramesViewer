import numpy as np
from OpenGL.GLU import gluLookAt
from OpenGL.GL import (
    glMatrixMode,
    glLoadIdentity,
    glGetFloatv,
    GL_MODELVIEW,
    GL_MODELVIEW_MATRIX,
)
from FramesViewer import utils


class Camera:
    def __init__(self, pos, center, up=[0, 0, 1], scale=5, speed=3):
        self.__pos = pos
        self.__center = center
        self.__up = up

        self.__pose = None

        self.__dt = 0

        self.__scale = scale
        self.__speed = speed

        self.update(0)

    # ==============================================================================
    # Public methods

    def update(self, dt):
        self.__dt = dt

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            self.__pos[0],
            self.__pos[1],
            self.__pos[2],
            self.__center[0],
            self.__center[1],
            self.__center[2],
            self.__up[0],
            self.__up[1],
            self.__up[2],
        )

        self.__updatePose()

    def applyZoom(self, incr_value):
        pos = np.array(self.__pos)
        center = np.array(self.__center)
        dir = (pos - center) / np.linalg.norm(pos - center)  # normalized

        self.__pos += dir * incr_value * self.__dt

    def getScale(self):
        return self.__scale

    def move(self, mouse_rel):
        trans_diff = self.__getTransDiff(mouse_rel) * self.__speed

        self.__pos += trans_diff * self.__dt
        self.__center += trans_diff * self.__dt

    def rotate(self, mouse_rel):
        trans_diff = self.__getTransDiff(mouse_rel) * self.__speed

        self.__pos += trans_diff * self.__dt * 2

    # ==============================================================================
    # Private methods

    def __updatePose(self):
        self.__pose = np.eye(4)
        self.__pose[:3, :3] = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))[:3, :3]
        self.__pose[:3, 3] = self.__pos

    def __getTransDiff(self, mouse_rel):
        mouse_rel = np.array([*mouse_rel, 0])
        mouse_rel[0] = -mouse_rel[0]

        old_pose = self.__pose.copy()
        self.__pose = utils.translateInSelf(self.__pose, mouse_rel)
        trans_diff = self.__pose[:3, 3] - old_pose[:3, 3]

        return trans_diff
