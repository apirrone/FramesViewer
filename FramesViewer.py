from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R
import time
import threading

# TODO better camera
# TODO display the frames names in the viewer

class FramesViewer():
    
    def __init__(self, window_size, name = b"FramesViewer", size = 0.1):
        self.window_size = window_size
        self.name = name
        self.camera_position = [3, -3, 3, 0, 0, 0, 0, 0, 1]
        self.zoom = 5
        self.prev_mouse_pos = np.array([0, 0])
        self.mouse_l_pressed = False
        self.mouse_m_pressed = False
        self.mouse_rel = np.array([0, 0])
        self.t = 0
        self.startTime = time.time()
        self.frames = {}
        self.size = size # sort of scaling factor. Adjust this depending on the scale of your coordinates

    def start(self):
        t = threading.Thread(target=self.initGL, name="FramesViewer_thread")
        t.daemon = True
        t.start()

    # Frames must be a pose matrix, a numpy array of shape (4, 4)
    # If the frame already exists, it is updated
    def pushFrame(self, frame, name):
        self.frames[name] = frame

    def popFrame(self, name):
        if name in self.frames:
            del self.frames[name]

    def initGL(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.window_size[0], self.window_size[1])
        glutCreateWindow(self.name)

        glClearColor(1.,1.,1.,1.)
        glShadeModel(GL_SMOOTH)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        lightZeroPosition = [10.,4.,10.,1.]
        lightZeroColor = [0.8,1.0,0.8,1.0]
        
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

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        t = round(time.time() - self.startTime)

        self.displayWorld()

        for name, frame in self.frames.items():
            self.displayFrame(frame)

        if self.mouse_l_pressed:
            self.rotate_camera(-self.mouse_rel[0]*0.001, [0, 0, 1*abs(self.mouse_rel[0])])

        glutSwapBuffers()
        glutPostRedisplay()    


    def displayFrame(self, pose):   

        glPushMatrix()

        size = self.size*self.zoom

        tvec = pose[:3, 3]*self.zoom
        rot_mat = pose[:3, :3]

        x_end_vec = rot_mat @ [size, 0, 0] + tvec
        y_end_vec = rot_mat @ [0, size, 0] + tvec
        z_end_vec = rot_mat @ [0, 0, size] + tvec

        glDisable(GL_LIGHTING)    
        glLineWidth(4)

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


    def displayWorld(self):

        self.displayFrame(self.make_pose([0, 0, 0], [0, 0, 0])) 

        glPushMatrix()

        size = self.size*self.zoom
        length = 15
        alpha = 0.04

        pose = self.make_pose([0, 0, 0], [0, 0, 0])

        tvec = pose[:3, 3]*self.zoom
        rot_mat = pose[:3, :3]


        x_end_vec = rot_mat @ [length*size, 0, 0] + tvec
        y_end_vec = rot_mat @ [0, length*size, 0] + tvec
        z_end_vec = rot_mat @ [0, 0, length*size] + tvec

        glDisable(GL_LIGHTING)    
        glLineWidth(3)

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

    
    @staticmethod
    def make_pose(translation, xyz, degrees=True):

        pose = np.eye(4)
        pose[:3, :3] = R.from_euler('xyz', xyz, degrees=degrees).as_matrix()
        pose[:3, 3] = translation
        return pose



