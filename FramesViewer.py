from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import numpy as np
from scipy.spatial.transform import Rotation as R
import time
import threading

# Warning : Had to import Camera class at the end of the file (after defining utils)

# TODO display the frames names in the viewer
# TODO proper package (avoid defining utils here, should be in a separate file)

class FramesViewer():
    
    def __init__(self, window_size, name = b"FramesViewer", size = 0.1):
        self.window_size = window_size
        self.name = name

        self.prev_mouse_pos = np.array([0, 0])
        self.mouse_l_pressed = False
        self.mouse_m_pressed = False
        self.ctrl_pressed = False
        self.mouse_rel = np.array([0, 0])

        self.t = None

        self.startTime = time.time()

        self.frames = {}
        self.points = {}

        self.size = size # sort of scaling factor. Adjust this depending on the scale of your coordinates

        self.camera = Camera((3, -3, 3), (0, 0, 0))

        self.prev_t = time.time()
        self.dt = 0

    def start(self):
        self.t = threading.Thread(target=self.initGL, name="FramesViewer_thread")
        self.t.daemon = True
        self.t.start()

    # Frames must be a pose matrix, a numpy array of shape (4, 4)
    # If the frame already exists, it is updated
    def pushFrame(self, frame, name, color=None, thickness=4):
        self.frames[name] = (frame.copy(), color, thickness)

    # Point is a (x, y, z) position in space
    def pushPoint(self, point, name, color=(0, 0, 0), size=1):
        if name not in self.points:
            self.points[name] = []

        self.points[name].append((point.copy(), color, size))

    def cleanPoints(self, name):
        if name in self.points:
            del self.points[name]

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
        
        glPushMatrix()
        
        glutMouseFunc(self.mouseClick)
        glutMotionFunc(self.mouseMotion)
        glutKeyboardFunc(self.keyboard)

        glutMainLoop()

        glutSwapBuffers()
        glutPostRedisplay()

    # TODO not working yet
    def handleResize(self):
        tmp = glGetIntegerv(GL_VIEWPORT)
        current_window_size = (tmp[2], tmp[3])
        if current_window_size != self.window_size:
            self.window_size = current_window_size

            # glutReshapeWindow(self.window_size[0], self.window_size[1])
            
            # glViewport(tmp[0], tmp[1], tmp[2], tmp[3])
            # glutPostRedisplay()
            # print("coucou")




    def display(self):

        self.dt = time.time() - self.prev_t

        self.prev_t = time.time()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # self.handleResize()

        self.displayWorld()
        
        try:
            for name, (frame, color, thickness) in self.frames.items():
                self.displayFrame(frame, color, thickness)
        except RuntimeError as e:
            # print("RuntimeError :", e)
            pass

        try:
            for name, points in self.points.items():
                for point, color, size in points:
                    self.displayPoint(point, color, size)
        except RuntimeError as e:
            print("RuntimeError :", e)
            pass
    
        self.camera.update(self.dt)

        if self.mouse_l_pressed:
            if self.ctrl_pressed:
                self.camera.move(self.mouse_rel)
            else:
                self.camera.rotate(self.mouse_rel)

        self.mouse_rel = np.array([0, 0])



        glutSwapBuffers()
        glutPostRedisplay()    


    def displayPoint(self, _pos, color=(0, 0, 0), size=1):
        pos = _pos.copy()

        glPushMatrix()
        glDisable(GL_LIGHTING)    

        glColor3f(color[0], color[1], color[2])
        glPointSize(size)
        glBegin(GL_POINTS)

        glVertex3f(pos[0]*self.camera.zoom, pos[1]*self.camera.zoom, pos[2]*self.camera.zoom)
        glEnd()


        glEnable(GL_LIGHTING)
        glPopMatrix()

    def displayFrame(self, _pose, color=None, thickness=4):   

        pose = _pose.copy()

        glPushMatrix()

        size = self.size*self.camera.zoom

        tvec = pose[:3, 3]*self.camera.zoom
        rot_mat = pose[:3, :3]

        x_end_vec = rot_mat @ [size, 0, 0] + tvec
        y_end_vec = rot_mat @ [0, size, 0] + tvec
        z_end_vec = rot_mat @ [0, 0, size] + tvec

        glDisable(GL_LIGHTING)    
        glLineWidth(thickness)

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

        if color is not None:
            glColor3f(color[0], color[1], color[2])
            glTranslatef(tvec[0], tvec[1], tvec[2])
            gluSphere(gluNewQuadric(), size/10, 10, 10)

        glEnable(GL_LIGHTING)
        glPopMatrix()

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
            self.camera.applyZoom(10)
        elif button == 4:
            self.camera.applyZoom(-10)

        if button == 2:
            if mode == 0:
                self.mouse_m_pressed = True
            elif mode == 1:
                self.mouse_m_pressed = False

        if glutGetModifiers() == 2:
            self.ctrl_pressed = True
        else:    
            self.ctrl_pressed = False

    def mouseMotion(self, x, y):
        self.mouse_pos = np.array([x, y])
        self.mouse_rel = self.mouse_pos - self.prev_mouse_pos

        self.prev_mouse_pos = self.mouse_pos.copy()

    def keyboard(self, key, x, y):
        pass


    def displayWorld(self):

        self.displayFrame(utils.make_pose([0, 0, 0], [0, 0, 0])) 

        glPushMatrix()

        size = self.size*self.camera.zoom
        length = 15
        alpha = 0.04

        pose = utils.make_pose([0, 0, 0], [0, 0, 0])

        tvec = pose[:3, 3]*self.camera.zoom
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


class utils():
    def __init__(self):
        pass

    @staticmethod
    def make_pose(translation, xyz, degrees=True):

        pose = np.eye(4)
        pose[:3, :3] = R.from_euler('xyz', xyz, degrees=degrees).as_matrix()
        pose[:3, 3] = translation
        return pose

    @staticmethod
    def rotateInSelf(_frame, rotation):
        frame            = _frame.copy()

        toOrigin         = np.eye(4)
        toOrigin[:3, :3] = frame[:3, :3]
        toOrigin[:3, 3]  = frame[:3, 3]
        toOrigin         = np.linalg.inv(toOrigin)

        frame = toOrigin @ frame
        frame = utils.make_pose([0, 0, 0], rotation) @ frame        
        frame = np.linalg.inv(toOrigin) @ frame

        return frame
        
    @staticmethod
    def rotateAbout(_frame, rotation, center):
        frame            = _frame.copy()

        toOrigin         = np.eye(4)
        toOrigin[:3, :3] = frame[:3, :3]
        toOrigin[:3, 3]  = center
        toOrigin         = np.linalg.inv(toOrigin)

        frame = toOrigin @ frame
        frame = utils.make_pose([0, 0, 0], rotation) @ frame        
        frame = np.linalg.inv(toOrigin) @ frame

        return frame
        
    @staticmethod
    def translateInSelf(_frame, translation):
        frame = _frame.copy()

        toOrigin         = np.eye(4)
        toOrigin[:3, :3] = frame[:3, :3]
        toOrigin[:3, 3]  = frame[:3, 3]
        toOrigin         = np.linalg.inv(toOrigin)

        frame = toOrigin @ frame
        frame = utils.make_pose(translation, [0, 0, 0]) @ frame
        frame = np.linalg.inv(toOrigin) @ frame

        return frame

    @staticmethod
    def translateAbsolute(_frame, translation):
        frame = _frame.copy()

        translate = utils.make_pose(translation, [0, 0, 0])

        return translate @ frame


from camera import Camera