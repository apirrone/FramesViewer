from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R
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


# TODO weird behaviour with displayWorld
class FramesViewer():
    def __init__(self, window_size, name = b"FramesViewer"):
        self.window_size = window_size
        self.name = name
        self.camera_position = [3, -3, 3, 0, 0, 0, 0, 0, 1]
        self.zoom = 5
        self.prev_mouse_pos = np.array([0, 0])
        self.mouse_l_pressed = False
        self.mouse_m_pressed = False
        self.mouse_rel = np.array([0, 0])
        self.t = 0
        self.start = time.time()

        self.frames = []

        self.initGL()

    # returns the frame id 
    def pushFrame(self, frame):
        self.frames.append(frame)
        return len(self.frames)

    def initGL(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_size[0], self.window_size[1])
        glutCreateWindow(self.name)

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
        
        glutDisplayFunc(self.display)
        
        
        glMatrixMode(GL_PROJECTION)

        gluPerspective(70., 1. ,1. ,40.)

        glMatrixMode(GL_MODELVIEW)
        
        gluLookAt(self.camera_position[0], self.camera_position[1], self.camera_position[2], self.camera_position[3], self.camera_position[4], self.camera_position[5], self.camera_position[6], self.camera_position[7], self.camera_position[8])
        
        glPushMatrix()
        
        glutMouseFunc(self.mouseClick)
        glutMotionFunc(self.mouseMotion)

        glutMainLoop()


        glutSwapBuffers()
        glutPostRedisplay()
        return

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        t = round(time.time() - self.start)


        self.displayWorld(self.zoom)

        for frame in self.frames:
            self.displayFrame(frame)

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

        self.displayFrame(T_torso_cylinder)



        T_camera_torso = pickle.load(open("../../Pollen/INCIA_cylinder_grasping/camera_calibration/T_camera_torso.pckl", 'rb'))
        T_torso_camera = np.linalg.inv(T_camera_torso)

        self.displayFrame(T_torso_camera, blink=False, t=t)

        # T_torso_hand = reachy.r_arm.forward_kinematics()
        # utils.displayFrame(T_torso_hand)

        if self.mouse_l_pressed:
            self.rotate_camera(-self.mouse_rel[0]*0.001, [0, 0, 1*abs(self.mouse_rel[0])])

        # if mouse_m_pressed:
        #     utils.move_camera(camera_position, mouse_rel)

        glutSwapBuffers()
        glutPostRedisplay()    


    def displayFrame(self, pose, size=0.05, blink=False, t=0):   

        if blink and t % 2 == 0:
            return

        glPushMatrix()

        size *= self.zoom

        tvec = pose[:3, 3]*self.zoom
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

    def set_camera_position(self, pos, center, up=[0, 0, 1]):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(pos[0], pos[1], pos[2], center[0], center[1], center[2], up[0], up[1], up[2])

    def rotate_camera(self, angle, axis): # angle in rad

        pos = self.camera_position[:3]
        axis = np.array(axis)
        rot_mat = R.from_euler('xyz', axis*angle, degrees=False).as_matrix()
        new_pos = rot_mat @ pos

        self.camera_position[:3] = new_pos

        self.set_camera_position(new_pos, self.camera_position[3:6])

    def mouseClick(self, button, mode, x, y):
        if mode == 0:
            self.prev_mouse_pos = np.array([x, y])
        else:
            self.prev_mouse_pos = np.array([0, 0])

        if button == 0:
            if mode == 0:
                self.mouse_l_pressed = True
            elif mode == 1:
                self.mouse_l_pressed = False

        if button == 3 : 
            self.zoom += 0.05
        elif button == 4:
            self.zoom = max(0, self.zoom - 0.05)

        if button == 2:
            if mode == 0:
                self.mouse_m_pressed = True
            elif mode == 1:
                self.mouse_m_pressed = False

    def mouseMotion(self, x, y):
        self.mouse_pos = np.array([x, y])
        self.mouse_rel = self.mouse_pos - self.prev_mouse_pos

        self.prev_mouse_pos = self.mouse_pos.copy()


    def displayWorld(self, size=0.05):

        self.displayFrame(utils.make_pose([0, 0, 0], [0, 0, 0])) 

        glPushMatrix()

        size *= self.zoom/20
        length = 10
        alpha = 0.04

        pose = utils.make_pose([0, 0, 0], [0, 0, 0])

        tvec = pose[:3, 3]*self.zoom
        rot_mat = pose[:3, :3]


        x_end_vec = rot_mat @ [size*length, 0, 0] + tvec
        y_end_vec = rot_mat @ [0, size*length, 0] + tvec
        z_end_vec = rot_mat @ [0, 0, size*length] + tvec

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


