import numpy as np
from OpenGL.GLU import gluLookAt
from OpenGL.GL import (
    glMatrixMode,
    glLoadIdentity,
    glPushMatrix,
    glLoadMatrixd,
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

        self.__update_pose()

    def apply_zoom(self, incr_value):
        pos = np.array(self.__pos)
        center = np.array(self.__center)
        dir = (pos - center) / np.linalg.norm(pos - center)  # normalized

        self.__pos += dir * incr_value * self.__dt

    def get_scale(self):
        return self.__scale

    def move(self, mouse_rel):
        trans_diff = self.__get_trans_diff(mouse_rel) * self.__speed

        self.__pos += trans_diff * self.__dt
        self.__center += trans_diff * self.__dt

    def rotate(self, mouse_rel):
        trans_diff = self.__get_trans_diff(mouse_rel) * self.__speed

        self.__pos += trans_diff * self.__dt * 2

    def set_up(self, up):
        self.__up = up

    def set_center(self, center):
        self.__center = center

    def set_pos(self, pos):
        self.__pos = pos

    def set_pose(self, pose):
        up = pose[:3, 1]  # y
        eye = pose[:3, 3]  # t
        negativeZ = pose[:3, 2]

        center = eye + negativeZ * -1 * np.linalg.norm(
            np.array(self.__center) - np.array(self.__pos)
        )

        self.set_up(up)
        self.set_pos(eye)
        self.set_center(center)

    def get_pose(self):
        return self.__pose

    # ==============================================================================
    # Private methods

    def __update_pose(self):
        self.__pose = np.eye(4)
        self.__pose[:3, :3] = np.array(glGetFloatv(GL_MODELVIEW_MATRIX))[:3, :3]
        self.__pose[:3, 3] = self.__pos

    def __get_trans_diff(self, mouse_rel):
        mouse_rel = np.array([*mouse_rel, 0])
        mouse_rel[0] = -mouse_rel[0]

        old_pose = self.__pose.copy()
        self.__pose = utils.translate_in_self(self.__pose, mouse_rel)
        trans_diff = self.__pose[:3, 3] - old_pose[:3, 3]

        return trans_diff
