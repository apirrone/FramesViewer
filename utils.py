from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import numpy as np
from scipy.spatial.transform import Rotation as R
def displayFrame(pose, zoom, size=0.05, blink=False, t=0):   

    if blink and t % 2 == 0:
        return

    glPushMatrix()

    size *= zoom

    tvec = pose[:3, 3]*zoom
    rot_mat = pose[:3, :3]

    x_end_vec = rot_mat @ [size, 0, 0] + tvec
    y_end_vec = rot_mat @ [0, size, 0] + tvec
    z_end_vec = rot_mat @ [0, 0, size] + tvec

    glDisable(GL_LIGHTING)    
    glLineWidth(2)

    # X
    glColor3f(1, 0, 0)
    glBegin(GL_LINES)
    glVertex3f(tvec[0], tvec[1], tvec[2])
    glVertex3f(x_end_vec[0], x_end_vec[1], x_end_vec[2])
    glEnd()

    # Y
    glColor3f(0, 1, 0)
    glBegin(GL_LINES)
    glVertex3f(tvec[0], tvec[1], tvec[2])
    glVertex3f(y_end_vec[0], y_end_vec[1], y_end_vec[2])
    glEnd()

    # Z
    glColor3f(0, 0, 1)
    glBegin(GL_LINES)
    glVertex3f(tvec[0], tvec[1], tvec[2])
    glVertex3f(z_end_vec[0], z_end_vec[1], z_end_vec[2])
    glEnd()

    glEnable(GL_LIGHTING)
    glPopMatrix()


def make_pose(translation, xyz, degrees=True):
    pose = np.eye(4)
    pose[:3, :3] = R.from_euler('xyz', xyz, degrees=degrees).as_matrix()
    pose[:3, 3] = translation
    return pose


def set_camera_position(pos, center, up=[0, 0, 1]):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(pos[0], pos[1], pos[2], center[0], center[1], center[2], up[0], up[1], up[2])

def rotate_camera(camera_position, angle, axis): # angle in rad

    pos = camera_position[:3]
    axis = np.array(axis)
    rot_mat = R.from_euler('xyz', axis*angle, degrees=False).as_matrix()
    new_pos = rot_mat @ pos

    camera_position[:3] = new_pos

    set_camera_position(new_pos, camera_position[3:6])

# def move_camera(camera_position, translation):
#     camera_position[:3] += [*translation*0.01, 0]
#     print([*translation, 0])
    
#     set_camera_position(camera_position[:3], camera_position[3:6])


def displayWorld(zoom, size=0.05):

    displayFrame(make_pose([0, 0, 0], [0, 0, 0]), zoom) 

    glPushMatrix()

    size *= zoom
    length = 10
    alpha = 0.04

    pose = make_pose([0, 0, 0], [0, 0, 0])

    tvec = pose[:3, 3]*zoom
    rot_mat = pose[:3, :3]


    x_end_vec = rot_mat @ [size*10, 0, 0] + tvec
    y_end_vec = rot_mat @ [0, size*10, 0] + tvec
    z_end_vec = rot_mat @ [0, 0, size*10] + tvec

    glDisable(GL_LIGHTING)    
    glLineWidth(2)

    # X
    glColor4f(0, 0, 0, alpha)
    for i in range(length+1):
        glBegin(GL_LINES)
        glVertex3f(tvec[0], tvec[1]+i*size, tvec[2])
        glVertex3f(x_end_vec[0], x_end_vec[1]+i*size, x_end_vec[2])

        glVertex3f(tvec[0]+i*size, tvec[1], tvec[2])
        glVertex3f(y_end_vec[0]+i*size, y_end_vec[1], y_end_vec[2])
        glEnd()


    # Y
    glColor4f(0, 0, 0, alpha)
    for i in range(length+1):
        glBegin(GL_LINES)
        glVertex3f(tvec[0], tvec[1], tvec[2]+i*size)
        glVertex3f(y_end_vec[0], y_end_vec[1], y_end_vec[2]+i*size)

        glVertex3f(tvec[0], tvec[1]+i*size, tvec[2])
        glVertex3f(z_end_vec[0], z_end_vec[1]+i*size, z_end_vec[2])
        glEnd()

    # Z
    glColor4f(0, 0, 0, alpha)
    for i in range(length+1):
        glBegin(GL_LINES)
        glVertex3f(tvec[0]+i*size, tvec[1], tvec[2])
        glVertex3f(z_end_vec[0]+i*size, z_end_vec[1], z_end_vec[2])
        glVertex3f(tvec[0], tvec[1], tvec[2]+i*size)
        glVertex3f(x_end_vec[0], x_end_vec[1], x_end_vec[2]+i*size)
        glEnd()

    glEnable(GL_LIGHTING)
    glPopMatrix()

