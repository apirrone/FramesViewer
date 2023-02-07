import pywavefront
from OpenGL.GL import (
    glPolygonMode,
    glPushMatrix,
    glTranslatef,
    glRotatef,
    glBegin,
    glEnd,
    glVertex3f,
    glPopMatrix,
    glDisable,
    glLineWidth,
    glColor3f,
    glEnable,
    glScalef,
    GL_FRONT_AND_BACK,
    GL_LINE,
    GL_TRIANGLES,
    GL_FILL,
    GL_LIGHTING,
    GL_LINES,
)

from scipy.spatial.transform import Rotation as R
import numpy as np


class Mesh:
    def __init__(self, path_obj, pose, viewer_scale, scale=1.0, wireframe=False):
        self.__mesh = pywavefront.Wavefront(
            path_obj,
            collect_faces=True,
            encoding="ISO-8859-1",
        )
        self.__wireframe = wireframe
        self.__pose = pose
        self.__viewer_scale = viewer_scale
        self.__scale = [scale, scale, scale]

    def setPose(self, pose):
        self.__pose = pose

    def render(self, camera_scale, showFrame=False, visual_rot=[0, 0, 0]):
        if showFrame:
            self.displayFrame(self.__pose, self.__viewer_scale, camera_scale)

        if self.__wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        size = self.__viewer_scale * camera_scale

        glPushMatrix()
        glTranslatef(*np.array(self.__pose[:3, 3] * camera_scale))
        glScalef(*(np.array(self.__scale) * size))

        rot = R.from_matrix(self.__pose[:3, :3]).as_euler("xyz", degrees=False)

        for i, r in enumerate(rot):
            xyz = [0, 0, 0]
            xyz[i] = 1
            r += visual_rot[i]
            glRotatef(np.rad2deg(r), *xyz)

        for mesh in self.__mesh.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*self.__mesh.vertices[vertex_i])
            glEnd()

        glScalef(*(1 / np.array(self.__scale)))
        glPopMatrix()

        if self.__wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    @staticmethod
    def displayFrame(_pose, viewer_scale, camera_scale, thickness=10):
        pose = _pose.copy()

        glPushMatrix()

        size = viewer_scale * camera_scale

        trans = pose[:3, 3] * camera_scale
        rot_mat = pose[:3, :3]

        x_end_vec = rot_mat @ [size, 0, 0] + trans
        y_end_vec = rot_mat @ [0, size, 0] + trans
        z_end_vec = rot_mat @ [0, 0, size] + trans

        glDisable(GL_LIGHTING)
        glLineWidth(thickness)
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
        glLineWidth(1)
        glEnable(GL_LIGHTING)
        glPopMatrix()
