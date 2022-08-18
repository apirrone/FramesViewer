from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R

import backtrace
backtrace.hook(
    reverse=False,
    align=True,
    strip_path=True,
    enable_on_envvar_only=False,
    on_tty=False,
    conservative=False,
    styles={})

def init():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(700,700)
    glutCreateWindow(b"Visu")

    glClearColor(1.,1.,1.,1.)
    glShadeModel(GL_SMOOTH)
    
    # glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    lightZeroPosition = [10.,4.,10.,1.]
    lightZeroColor = [0.8,1.0,0.8,1.0] #green tinged
    
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    
    glEnable(GL_LIGHT0)
    
    glutDisplayFunc(display)
    
    glMatrixMode(GL_PROJECTION)
    
    gluPerspective(70., 1. ,1. ,40.)
    
    glMatrixMode(GL_MODELVIEW)
    
    gluLookAt(5, -5, 5,
              0, 0, 0,
              0, 0, 1)
    
    glPushMatrix()
    glutMainLoop()
    
    glutSwapBuffers()
    glutPostRedisplay()
    return

def displayFrame(pose):   
    glPushMatrix()

    tvec = pose[:3, 3]
    rot_mat = pose[:3, :3]

    x_end_vec = rot_mat @ [1, 0, 0] + tvec
    y_end_vec = rot_mat @ [0, 1, 0] + tvec
    z_end_vec = rot_mat @ [0, 0, 1] + tvec

    glDisable(GL_LIGHTING)    
    glLineWidth(6)

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

def make_pose(tvec, rvec, degrees=True):

    pose = np.eye(4)
    pose[:3, :3] = R.from_euler('xyz', rvec, degrees=degrees).as_matrix()
    pose[:3, 3] = tvec

    return pose

def display():

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    torso_frame = make_pose([0, 0, 0], [0, 0, 0]) # origin
    displayFrame(torso_frame)

    # T_torso_head = make_pose([0, 0, 3], [0, 0, 0])
    # displayFrame(T_torso_head)

    T_torso_camera = make_pose([0, 0, 3], [-90, 0, -90])
    displayFrame(T_torso_camera)

    
    # T_world_hand = make_pose([1.5, 0, 1], [0, 0, 0])
    # displayFrame(T_world_hand)

    glutSwapBuffers()
    glutPostRedisplay()    


init()

