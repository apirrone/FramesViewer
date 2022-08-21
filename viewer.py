from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R
from reachy_sdk import ReachySDK
import backtrace
import json
import time
import pickle
import utils

backtrace.hook(
    reverse=False,
    align=True,
    strip_path=True,
    enable_on_envvar_only=False,
    on_tty=False,
    conservative=False,
    styles={})

# reachy = ReachySDK('localhost')

def init():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 1000)
    glutCreateWindow(b"Visu")

    glClearColor(1.,1.,1.,1.)
    glShadeModel(GL_SMOOTH)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
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

def mouseClick(button, mode, x, y):
    global mouse_l_pressed, mouse_m_pressed, prev_mouse_pos, zoom
    if mode == 0:
        prev_mouse_pos = np.array([x, y])
    else:
        prev_mouse_pos = np.array([0, 0])

    if button == 0:
        if mode == 0:
            mouse_l_pressed = True
        elif mode == 1:
            mouse_l_pressed = False

    if button == 3 : 
        zoom += 0.05
    elif button == 4:
        zoom = max(0, zoom - 0.05)

    if button == 2:
        if mode == 0:
            mouse_m_pressed = True
        elif mode == 1:
            mouse_m_pressed = False


    

def mouseMotion(x, y):
    global mouse_rel, mouse_l_pressed, mouse_m_pressed, prev_mouse_pos
    # if mouse_l_pressed:
    mouse_pos = np.array([x, y])
    mouse_rel = mouse_pos - prev_mouse_pos

    prev_mouse_pos = mouse_pos.copy()
    # else:
    #     mouse_rel = np.array([0, 0])




    
prev_mouse_pos = np.array([0, 0])
mouse_l_pressed = False
mouse_m_pressed = False
mouse_rel = np.array([0, 0])
zoom = 5
camera_position = [3, -3, 3, 0, 0, 0, 0, 0, 1]
t = 0
start = time.time()
def display():
    global mouse_rel, t, zoom
    t = round(time.time() - start)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    
    # T_world_torso = utils.make_pose([0, 0, 0], [0, 0, 0])
    # utils.displayFrame(T_world_torso, zoom) 

    utils.displayWorld(zoom)

    T_hand_tag = utils.make_pose([0, 0, 0.05], [-np.pi/2, 0, -np.pi/2], degrees = False) # approximate, translation missing but is not much

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
                             
    T_torso_cylinder = np.array([[ 0.22,  0.02, -0.97,  0.43],
                                 [-0.67, -0.73, -0.17, -0.04],
                                 [-0.71,  0.69, -0.15,  0.03],
                                 [ 0.  ,  0.  ,  0.  ,  1.  ]])

    utils.displayFrame(T_torso_cylinder, zoom)



    T_camera_torso = pickle.load(open("../../Pollen/INCIA_cylinder_grasping/camera_calibration/T_camera_torso.pckl", 'rb'))
    T_torso_camera = np.linalg.inv(T_camera_torso)

    utils.displayFrame(T_torso_camera, zoom, blink=False, t=t)

    # T_torso_hand = reachy.r_arm.forward_kinematics()
    # utils.displayFrame(T_torso_hand)

    if mouse_l_pressed:
        utils.rotate_camera(camera_position,-mouse_rel[0]*0.001, [0, 0, 1*abs(mouse_rel[0])])

    # if mouse_m_pressed:
    #     utils.move_camera(camera_position, mouse_rel)

    glutSwapBuffers()
    glutPostRedisplay()    




init()

