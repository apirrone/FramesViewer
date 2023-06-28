import numpy as np
from OpenGL.GLU import gluSphere, gluNewQuadric
from OpenGL.GL import (
    glEnable,
    glPushMatrix,
    glDisable,
    glColor3f,
    glBegin,
    glEnd,
    glPopMatrix,
    glVertex3f,
    glLineWidth,
    glTranslatef,
    GL_LIGHTING,
    GL_LINES,
)


class Frame:
    def __init__(
        self,
        pose: np.ndarray,
        name: str,
        color: tuple = None,
        thickness: int = 4,
    ):
        self.pose = pose
        self.absolute_pose = pose.copy()
        self.name = name
        self.color = color
        self.thickness = thickness

    def display(self, size, camera):
        pose = self.absolute_pose.copy()

        glPushMatrix()

        size = size * camera.getScale()

        trans = pose[:3, 3] * camera.getScale()
        rot_mat = pose[:3, :3]

        x_end_vec = rot_mat @ [size, 0, 0] + trans
        y_end_vec = rot_mat @ [0, size, 0] + trans
        z_end_vec = rot_mat @ [0, 0, size] + trans

        glDisable(GL_LIGHTING)
        glLineWidth(self.thickness)
        glBegin(GL_LINES)

        # X
        glColor3f(1, 0, 0)
        glVertex3f(trans[0], trans[1], trans[2])
        glVertex3f(x_end_vec[0], x_end_vec[1], x_end_vec[2])

        # Y
        glColor3f(0, 1, 0)
        glVertex3f(trans[0], trans[1], trans[2])
        glVertex3f(y_end_vec[0], y_end_vec[1], y_end_vec[2])

        # Z
        glColor3f(0, 0, 1)
        glVertex3f(trans[0], trans[1], trans[2])
        glVertex3f(z_end_vec[0], z_end_vec[1], z_end_vec[2])

        glEnd()

        if self.color is not None:
            glColor3f(self.color[0], self.color[1], self.color[2])
            glTranslatef(trans[0], trans[1], trans[2])
            gluSphere(gluNewQuadric(), size / 10, 10, 10)

        glLineWidth(1)
        glEnable(GL_LIGHTING)
        glPopMatrix()
