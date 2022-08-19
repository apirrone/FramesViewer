from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R
from reachy_sdk import ReachySDK
import backtrace

backtrace.hook(
    reverse=False,
    align=True,
    strip_path=True,
    enable_on_envvar_only=False,
    on_tty=False,
    conservative=False,
    styles={})

# reachy = ReachySDK('localhost')

SCALING_FACTOR = 5
camera_position = [3, -3, 3, 0, 0, 0, 0, 0, 1]

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
    
    gluLookAt(camera_position[0], camera_position[1], camera_position[2], camera_position[3], camera_position[4], camera_position[5], camera_position[6], camera_position[7], camera_position[8])
    
    glPushMatrix()
    
    glutMouseFunc(mouseClick)
    glutMotionFunc(mouseMotion)

    glutMainLoop()


    glutSwapBuffers()
    glutPostRedisplay()
    return
    
prev_mouse_pos = np.array([0, 0])
mouse_l_pressed = False
mouse_rel = np.array([0, 0])


def mouseClick(button, mode, x, y):
    global mouse_l_pressed, prev_mouse_pos
    if mode == 0:
        mouse_l_pressed = True
        prev_mouse_pos = np.array([x, y])
    elif mode == 1:
        mouse_l_pressed = False
        prev_mouse_pos = np.array([0, 0])

def mouseMotion(x, y):
    global mouse_rel, mouse_l_pressed, prev_mouse_pos
    if mouse_l_pressed:
        mouse_pos = np.array([x, y])
        mouse_rel = mouse_pos - prev_mouse_pos

        prev_mouse_pos = mouse_pos.copy()
    else:
        mouse_rel = np.array([0, 0])


def displayFrame(pose, size=0.05):   
    glPushMatrix()

    size *= SCALING_FACTOR

    tvec = pose[:3, 3]*SCALING_FACTOR
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

def make_pose(tvec, rvec, degrees=True):
    pose = np.eye(4)
    pose[:3, :3] = R.from_euler('xyz', rvec, degrees=degrees).as_matrix()
    pose[:3, 3] = tvec
    return pose


def set_camera_position(pos, center, up=[0, 0, 1]):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(pos[0], pos[1], pos[2], center[0], center[1], center[2], up[0], up[1], up[2])

def rotate_camera(angle, axis): # angle in rad

    pos = camera_position[:3]
    axis = np.array(axis)
    rot_mat = R.from_euler('xyz', axis*angle, degrees=False).as_matrix()
    new_pos = rot_mat @ pos

    camera_position[:3] = new_pos

    set_camera_position(new_pos, camera_position[3:6])

def display():
    global mouse_rel
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    
    T_world_torso = make_pose([0, 0, 0], [0, 0, 0])
    displayFrame(T_world_torso)

    T_hand_tag = make_pose([0, 0, 0], [-np.pi/2, 0, -np.pi/2], degrees = False) # approximate, translation missing but is not much
    T_tag_hand = np.linalg.inv(T_hand_tag)

    # given by fk (rad, m)
    T_torso_hand = np.array([[-0.9138159 , -0.29510683, -0.27902053,  0.41941922],
                             [-0.13158546,  0.86510367, -0.48402573, -0.05093768],
                             [ 0.38422099, -0.40559536, -0.82937726,  0.075935  ],
                             [ 0.        ,  0.        ,  0.        ,  1.        ]])

    # given by aruco (rad, m)
    T_camera_tag = np.array([[ 0.88568147, -0.09010766,  0.45546563,  0.05219593],
                             [ 0.17211714, -0.84737062, -0.50233328,  0.14054844],
                             [ 0.43121227,  0.52330072, -0.73499138,  0.34714904],
                             [ 0.        ,  0.        ,  0.        ,  1.        ]])

    T_tag_camera = np.linalg.inv(T_camera_tag)

    T_torso_camera = T_torso_hand @ T_hand_tag @ T_tag_camera

    # print(T_torso_camera)
    displayFrame(T_torso_camera)

    # T_torso_hand = reachy.r_arm.forward_kinematics()

    # displayFrame(T_torso_hand)


    # T_torso_tag = T_torso_hand @ T_hand_tag

    # displayFrame(T_torso_tag)


    # rotate_camera(0.01, [1, 0, 0])
    rotate_camera(-mouse_rel[0]*0.001, [0, 0, 1*abs(mouse_rel[0])])

    glutSwapBuffers()
    glutPostRedisplay()    




init()

