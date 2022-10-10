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
# TODO make proper package (avoid defining utils here, should be in a separate file)
# TODO history size for points lists (need to be managed differently)
class FramesViewer():
    
    def __init__(self, window_size:list = [1000, 1000], name:str = b"FramesViewer", size:int = 0.1):
        """
        The constructor for the class FramesViewer.
        Arguments:
            window_size : A list of size 2 defining the size of the viewer window in pixels. 
            name        : The name of the viewer window
            size        : Sort of a scaling factor. Adjust this depending on the scale of your coordinates
        """

        self.__window_size     = window_size
        self.__name            = name

        self.__prev_mouse_pos  = np.array([0, 0])
        self.__mouse_l_pressed = False
        self.__mouse_m_pressed = False
        self.__ctrl_pressed    = False
        self.__mouse_rel       = np.array([0, 0])

        self.__t               = None

        self.__startTime       = time.time()

        self.__frames          = {}
        self.__points          = {}

        self.__size            = size

        self.__camera          = Camera((3, -3, 3), (0, 0, 0))

        self.__prev_t          = time.time()
        self.__dt              = 0

        self.__dts             = []
        self.__fps             = 0

    # ==============================================================================
    # Public methods
    
    def start(self):
        """
        Starts the viewer thread.
        """
        self.__t        = threading.Thread(target=self.__initGL, name=self.__name)
        self.__t.daemon = True
        
        self.__t.start()

    def pushFrame(self, frame:np.ndarray, name:str, color:tuple=None, thickness:int=4):
        """
        Adds or updates a frame.
        If the frame name does not exist yet, it is added.
        If the frame name exists, its values is updated.
        Arguments:
            frame     : a 6D pose matrix of size [4, 4]
            name      : the name of the frame
            color     : a list of size 3 (RGB between 0 and 1)
            thickness : the thickness of the lines drawn to show the frame
        """
        self.__frames[name] = (frame.copy(), color, thickness)

    def deleteFrame(self, name:str):
        """
        Deletes the frame of name \"name\".
        Arguments:
            name : The name of the frame to be deleted
        """
        if name in self.__frames:
            del self.__frames[name]

    # Point is a (x, y, z) position in space
    def pushPoint(self, point:list, name:str, color:tuple=(0, 0, 0), size:int=1):
        """
        Adds or updates a points list.
        If the points list name does not exist yet, it is created.
        If the points list name exists, the point is added to the list.
        Arguments:
            point     : a point's coordinates [x, y, z]
            name      : the name of the points list
            color     : a list of size 3 (RGB between 0 and 1)
            size      : the size of the point
        """
        if name not in self.__points:
            self.__points[name] = []

        self.__points[name].append((point.copy(), color, size))


    def deletePointsList(self, name:str):
        """
        Deletes the points list of name \"name\".
        Arguments:
            name : The name of the points list to be deleted
        """
        if name in self.__points:
            del self.__points[name]

    # ==============================================================================
    # Private methods

    def __initGL(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.__window_size[0], self.__window_size[1])
        glutCreateWindow(self.__name)

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
        
        glutDisplayFunc(self.__display)
        
        glMatrixMode(GL_PROJECTION)

        gluPerspective(70., 1. ,1. ,40.)

        glMatrixMode(GL_MODELVIEW)
        
        glPushMatrix()
        
        glutMouseFunc(self.__mouseClick)
        glutMotionFunc(self.__mouseMotion)
        glutKeyboardFunc(self.__keyboard)

        glutMainLoop()

        glutSwapBuffers()
        glutPostRedisplay()

    # TODO not working yet
    def __handleResize(self):
        tmp = glGetIntegerv(GL_VIEWPORT)
        current_window_size = (tmp[2], tmp[3])
        if current_window_size != self.window_size:
            self.window_size = current_window_size

            # glutReshapeWindow(self.window_size[0], self.window_size[1])
            
            # glViewport(tmp[0], tmp[1], tmp[2], tmp[3])
            # glutPostRedisplay()
            # print("coucou")

    def __display(self):

        self.__dt = time.time() - self.__prev_t
        self.__prev_t = time.time()

        self.__dts.append(self.__dt)

        elapsed = np.sum(self.__dts)
        if elapsed >= 1.: # one second worth of dts
            self.__dts = self.__dts[1:]

        if elapsed != 0:
            self.__fps = len(self.__dts) / elapsed

        # print(self.__fps)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # self.handleResize()

        self.__displayWorld()
        
        try:
            for name, (frame, color, thickness) in self.__frames.items():
                self.__displayFrame(frame, color, thickness)
        except RuntimeError as e:
            # print("RuntimeError :", e)
            pass
        
        for name in self.__points.keys():
            self.__displayPoints(name)
    
        self.__camera.update(self.__dt)

        if self.__mouse_l_pressed:
            if self.__ctrl_pressed:
                self.__camera.move(self.__mouse_rel)
            else:
                self.__camera.rotate(self.__mouse_rel)

        self.__mouse_rel = np.array([0, 0])

        glutSwapBuffers()
        glutPostRedisplay()    


    def __displayPoints(self, name):
        
        _, color, size = self.__points[name][0]

        glPushMatrix()
        glDisable(GL_LIGHTING)    

        glColor3f(color[0], color[1], color[2])
        glPointSize(size)
        glBegin(GL_POINTS)

        try:
            for point, _, _ in self.__points[name]:
                glVertex3f(point[0]*self.__camera.getZoom(), point[1]*self.__camera.getZoom(), point[2]*self.__camera.getZoom())
        except RuntimeError as e:
            print("RuntimeError :", e)
            pass

        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __displayPoint(self, _pos, color=(0, 0, 0), size=1):
        pos = _pos.copy()

        glPushMatrix()
        glDisable(GL_LIGHTING)    

        glColor3f(color[0], color[1], color[2])
        glPointSize(size)
        glBegin(GL_POINTS)

        glVertex3f(pos[0]*self.__camera.getZoom(), pos[1]*self.__camera.getZoom(), pos[2]*self.__camera.getZoom())
        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __displayFrame(self, _pose, color=None, thickness=4):   
        pose = _pose.copy()

        glPushMatrix()

        size = self.__size*self.__camera.getZoom()

        trans = pose[:3, 3]*self.__camera.getZoom()
        rot_mat = pose[:3, :3]

        x_end_vec = rot_mat @ [size, 0, 0] + trans
        y_end_vec = rot_mat @ [0, size, 0] + trans
        z_end_vec = rot_mat @ [0, 0, size] + trans

        glDisable(GL_LIGHTING)    
        glLineWidth(thickness)

        # X
        glColor3f(1, 0, 0)
        glBegin(GL_LINES)
        glVertex3f(trans[0], trans[1], trans[2])
        glVertex3f(x_end_vec[0], x_end_vec[1], x_end_vec[2])
        glEnd()

        # Y
        glColor3f(0, 1, 0)
        glBegin(GL_LINES)
        glVertex3f(trans[0], trans[1], trans[2])
        glVertex3f(y_end_vec[0], y_end_vec[1], y_end_vec[2])
        glEnd()

        # Z
        glColor3f(0, 0, 1)
        glBegin(GL_LINES)
        glVertex3f(trans[0], trans[1], trans[2])
        glVertex3f(z_end_vec[0], z_end_vec[1], z_end_vec[2])
        glEnd()

        if color is not None:
            glColor3f(color[0], color[1], color[2])
            glTranslatef(trans[0], trans[1], trans[2])
            gluSphere(gluNewQuadric(), size/10, 10, 10)

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __mouseClick(self, button, mode, x, y):
        if mode == 0:
            self.__prev_mouse_pos = np.array([x, y])
        else:
            self.__prev_mouse_pos = np.array([0, 0])

        if button == 0:
            if mode == 0:
                self.__mouse_l_pressed = True
            elif mode == 1:
                self.__mouse_l_pressed = False

        if button == 3 : 
            self.__camera.applyZoom(10)
        elif button == 4:
            self.__camera.applyZoom(-10)

        if button == 2:
            if mode == 0:
                self.__mouse_m_pressed = True
            elif mode == 1:
                self.__mouse_m_pressed = False

        if glutGetModifiers() == 2:
            self.__ctrl_pressed = True
        else:    
            self.__ctrl_pressed = False

    def __mouseMotion(self, x, y):
        mouse_pos = np.array([x, y])
        self.__mouse_rel = mouse_pos - self.__prev_mouse_pos

        self.__prev_mouse_pos = mouse_pos.copy()

    def __keyboard(self, key, x, y):
        pass

    def __displayWorld(self):

        self.__displayFrame(utils.make_pose([0, 0, 0], [0, 0, 0])) 

        glPushMatrix()

        size = self.__size*self.__camera.getZoom()
        length = 15
        alpha = 0.04

        pose = utils.make_pose([0, 0, 0], [0, 0, 0])

        trans = pose[:3, 3]*self.__camera.getZoom()
        rot_mat = pose[:3, :3]


        x_end_vec = rot_mat @ [length*size, 0, 0] + trans
        y_end_vec = rot_mat @ [0, length*size, 0] + trans
        z_end_vec = rot_mat @ [0, 0, length*size] + trans

        glDisable(GL_LIGHTING)    
        glLineWidth(3)

        # X
        glColor4f(0, 0, 0, alpha)
        for i in range(length+1):
            glBegin(GL_LINES)
            glVertex3f(trans[0], trans[1]+i*size, trans[2])
            glVertex3f(x_end_vec[0], x_end_vec[1]+i*size, x_end_vec[2])

            glVertex3f(trans[0]+i*size, trans[1], trans[2])
            glVertex3f(y_end_vec[0]+i*size, y_end_vec[1], y_end_vec[2])
            glEnd()


        # Y
        glColor4f(0, 0, 0, alpha)
        for i in range(length+1):
            glBegin(GL_LINES)
            glVertex3f(trans[0], trans[1], trans[2]+i*size)
            glVertex3f(y_end_vec[0], y_end_vec[1], y_end_vec[2]+i*size)

            glVertex3f(trans[0], trans[1]+i*size, trans[2])
            glVertex3f(z_end_vec[0], z_end_vec[1]+i*size, z_end_vec[2])
            glEnd()

        # Z
        glColor4f(0, 0, 0, alpha)
        for i in range(length+1):
            glBegin(GL_LINES)
            glVertex3f(trans[0]+i*size, trans[1], trans[2])
            glVertex3f(z_end_vec[0]+i*size, z_end_vec[1], z_end_vec[2])
            glVertex3f(trans[0], trans[1], trans[2]+i*size)
            glVertex3f(x_end_vec[0], x_end_vec[1], x_end_vec[2]+i*size)
            glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()


class utils():
    """
    A static class containing useful functions to manipulate 6D pose matrices
    """

    @staticmethod
    def make_pose(translation:np.ndarray, xyz:np.ndarray, degrees:bool=True):
        """
        Creates a 6D pose matrix from a position vector (translation) and \"roll pitch yaw\" angles (xyz).
        Arguments :
            translation : a list of size 3. This is the translation component of the pose matrix
            xyz         : a list of size 3. x, y and z are the roll, pitch, yaw angles that are used to build the rotation component of the pose matrix
            degrees     : True or False. are the angles you provided for \"xyz\" in degrees or in radians ?
        Returns : 
            pose : the constructed pose matrix. This is a 4x4 numpy array
        """
        pose = np.eye(4)
        pose[:3, :3] = R.from_euler('xyz', xyz, degrees=degrees).as_matrix()
        pose[:3, 3] = translation
        return pose

    @staticmethod
    def rotateInSelf(_frame, rotation):
        """
        TODO
        """
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
        """
        TODO
        """
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
        """
        TODO
        """
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
        """
        TODO
        """
        frame = _frame.copy()

        translate = utils.make_pose(translation, [0, 0, 0])

        return translate @ frame


from camera import Camera