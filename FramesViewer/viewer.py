from OpenGL.GLUT import (
    glutInit,
    glutCreateWindow,
    glutInitDisplayMode,
    glutInitWindowSize,
    glutDisplayFunc,
    glutMouseFunc,
    glutMotionFunc,
    glutKeyboardFunc,
    glutMainLoop,
    glutSwapBuffers,
    glutPostRedisplay,
    GLUT_DEPTH,
    GLUT_DOUBLE,
    GLUT_RGB,
)
from OpenGL.GLU import gluPerspective, gluSphere, gluNewQuadric
from OpenGL.GL import (
    glClearColor,
    glShadeModel,
    glEnable,
    glBlendFunc,
    glMatrixMode,
    glPushMatrix,
    glClear,
    glLightf,
    glDisable,
    glColor3f,
    glPointSize,
    glBegin,
    glEnd,
    glPopMatrix,
    glVertex3f,
    glLineWidth,
    glTranslatef,
    glColor4f,
    glLightfv,
    GL_SMOOTH,
    GL_BLEND,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_DEPTH_TEST,
    GL_LIGHTING,
    GL_LIGHT0,
    GL_POSITION,
    GL_DIFFUSE,
    GL_CONSTANT_ATTENUATION,
    GL_LINEAR_ATTENUATION,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_POINTS,
    GL_LINES,
)

import sys
import numpy as np
from scipy.spatial.transform import Rotation as R
import time
import threading
import FramesViewer.utils as utils
from FramesViewer.camera import Camera
from FramesViewer.inputs import Inputs
from FramesViewer.mesh import Mesh

# TODO display the frames names in the viewer
# TODO display fps in viewer


class Viewer:
    def __init__(
        self,
        window_size: list = [1000, 1000],
        name: str = b"FramesViewer",
        size: int = 0.1,
    ):
        """
        The constructor for the class FramesViewer.
        Arguments:
            window_size : A list of size 2 defining the size of the viewer window in pixels.
            name        : The name of the viewer window
            size        : Sort of a scaling factor. Adjust this depending on the scale of your coordinates
        """

        self.__window_size = window_size
        self.__name = name

        self.__t = None

        self.__frames = {}
        self.__links = {}

        self.__points = {}
        self.__points_visible = {}

        self.__meshes = {}

        self.__size = size

        self.__camera = Camera((3, -3, 3), (0, 0, 0))
        self.__inputs = Inputs()
        self.__prev_t = time.time()
        self.__dt = 0

        self.__dts = []
        self.__fps = 0

    def __reset_camera(self):
        self.__camera = Camera((3, -3, 3), (0, 0, 0))

    # ==============================================================================
    # Public methods

    def start(self):
        """
        Starts the viewer thread.
        """
        self.__t = threading.Thread(target=self.__initGL, name=self.__name)
        self.__t.daemon = True

        self.__t.start()

    # Frames
    def pushFrame(
        self, frame: np.ndarray, name: str, color: tuple = None, thickness: int = 4
    ):
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

    def deleteFrame(self, name: str):
        """
        Deletes the frame of name \"name\".
        Arguments:
            name : the name of the frame to be deleted
        """
        if name in self.__frames:
            del self.__frames[name]

    def pushLink(self, frame1: str, frame2: str, color: tuple = (0, 0, 0)):
        """
        Adds a (visual) link between two frames. The order does not matter.
        Arguments:
            frame1 : the name of the first frame
            frame2 : the name of the second frame
            color  : the color of the link
        """

        if frame1 not in self.__frames.keys() and frame2 in self.__frames.keys():
            print("Error : frames ", frame1, "or", frame2, " don't exist")
            return

        link = tuple(sorted((frame1, frame2)))

        if tuple(sorted((frame1, frame2))) in self.__links.keys():
            print("Error : link (", frame1, ",", frame2, ") already exists")
            return

        self.__links[link] = color

    def deleteLink(self, frame1: str, frame2: str):
        """
        Deletes a link between two frames.
        Arguments :
            frame1 : the name of the first frame
            frame2 : the name of the second frame
        """
        link = tuple(sorted((frame1, frame2)))

        if link not in self.__links.keys():
            print("Error : link (", frame1, ",", frame2, ") does not exist")
            return

        del self.__links[link]

    # Points
    def pushPoint(self, name: str, point: list):
        """
        Adds or updates a points list.
        If the points list name does not exist yet, it is created.
        If the points list name exists, the point is added to the list.
        Arguments:
            name      : the name of the points list
            point     : a point's coordinates [x, y, z]
        """

        if name not in self.__points:
            print("Error : points list", name, "does not exist")
            return

        self.__points[name]["points"].append(point.copy())

    def createPointsList(
        self,
        name: str,
        points: list = [],
        color: tuple = (0, 0, 0),
        size: int = 1,
        rotation: list = [0, 0, 0],
        translation: list = [0, 0, 0],
        visible: bool = True,
    ):
        """
        Creates a list of points. It can be initialized with points, or set empty, then updated with updatePointsList().
        Arguments :
            name    : the name of the points list
            points  : a list of points with which the list is initialized
            color   : the color of the points in that list
            size    : the size of the points in that list
            visible : should the points be visible or not
        """

        if name in self.__points:
            raise RuntimeError(str("Error : points list " + name + " already exists"))
            # print("Error : points list", name, "already exists")
            # return

        self.__points[name] = {
            "points": points.copy(),
            "color": color,
            "size": size,
            "rotation": rotation,
            "translation": translation,
            "oldness": -1,
        }
        self.__points_visible[name] = visible

    def updatePointsList(
        self,
        name: str,
        points: list,
        color: tuple = None,
        size: int = None,
        rotation: list = None,
        translation: list = None,
        visible: bool = None,
    ):
        """
        Updates a list of points.
        Arguments :
            name        : the name of the points list to be updated
            points      : a new points list that replaces the previous one
            color       : a new color. If not set, the color is not updated
            size        : a new size. If not set, the size is not updated
            rotation    : apply a rotation to all the points of the list
            translation : apply a translation to all the points of the list
            visible     : update the visibility of the points. If not set, the visibility does not change
        """

        if name not in self.__points:
            print("Error : points list", name, "does not exist")
            return

        if rotation is not None:
            self.__points[name]["rotation"] = rotation
        points = self.__rotatePoints(points, self.__points[name]["rotation"])

        if translation is not None:
            self.__points[name]["translation"] = translation
        points = self.__translatePoints(points, self.__points[name]["translation"])

        self.__points[name]["points"] = points

        if color is not None:
            self.__points[name]["color"] = color
        if size is not None:
            self.__points[name]["size"] = size

        self.__points[name]["oldness"] = -1

        if visible is not None:
            self.changePointsListVisibility(name, visible)

    def translatePointsList(self, name: str, translation: list):
        """
        Applies a translation to all the points of the list.
        Arguments :
            name        : then name of the points list
            translation : the translation to be applied
        """

        if name not in self.__points:
            print("Error : points list", name, "does not exist")
            return

        for i, point in enumerate(self.__points[name]["points"]):
            self.__points[name]["points"][i] += translation

    def rotatePointsList(
        self, name: str, rotation: list, center: list = [0, 0, 0], degrees: bool = True
    ):
        """
        Applies a rotation to all the points of the list.
        Arguments :
            name     : the name of the points list
            rotation : the rotation to be applied [x, y, z]
            center   : the center of rotation
            degrees  : are the values of the rotation in degrees or radians ?
        """

        if name not in self.__points:
            print("Error : points list", name, "does not exist")
            return

        rot_mat = R.from_euler("xyz", rotation, degrees=degrees).as_matrix()
        for i, point in enumerate(self.__points[name]["points"]):
            self.__points[name]["points"][i] = rot_mat @ point

    def changePointsListVisibility(self, name: str, visible: bool):
        """
        Updates the visibility of a points list.
        Arguments:
            name    : the name of the points list
            visible : should the points of the list be visible or not
        """

        if name not in self.__points:
            print("Error : points list", name, "does not exist")
            return

        self.__points_visible[name] = visible

    def deletePointsList(self, name: str):
        """
        Deletes the points list of name \"name\".
        Arguments:
            name : The name of the points list to be deleted
        """
        if name in self.__points:
            del self.__points[name]

    def getPointsList(self, name: str):
        """
        Returns a points list.
        Arguments :
            name : the name of the points list
        """

        if name not in self.__points:
            print("Error : points list", name, "does not exist")
            return

        return self.__points[name]["points"].copy()

    def hideOldPointsLists(self, max_oldness=1):
        for name in self.__points.keys():
            if self.__points[name]["oldness"] > max_oldness:
                self.changePointsListVisibility(name, False)
            else:
                self.changePointsListVisibility(name, True)

    def createMesh(self, name: str, path: str, pose: np.ndarray, scale=1.):
        if name not in self.__meshes:
            self.__meshes[name] = Mesh(path, pose, self.__size, scale=scale)
        else:
            print("Error : mesh", name, "already exists. Use updateMesh() instead")

    def updateMesh(self, name: str, pose: np.ndarray):
        if name not in self.__meshes:
            print("Error : mesh", name, "does not exist")
            return

        self.__meshes[name].setPose(pose)

    def get_key_pressed(self):
        return self.__inputs.getKeyPressed()

    # ==============================================================================
    # Private methods

    def __initGL(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.__window_size[0], self.__window_size[1])
        glutCreateWindow(self.__name)

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glShadeModel(GL_SMOOTH)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        lightZeroPosition = [10.0, 4.0, 10.0, 1.0]
        lightZeroColor = [0.8, 1.0, 0.8, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)

        glEnable(GL_LIGHT0)

        glutDisplayFunc(self.__run)

        glMatrixMode(GL_PROJECTION)

        gluPerspective(70.0, 1.0, 1.0, 40.0)

        glMatrixMode(GL_MODELVIEW)

        glPushMatrix()

        glutMouseFunc(self.__inputs.mouseClick)
        glutMotionFunc(self.__inputs.mouseMotion)
        glutKeyboardFunc(self.__inputs.keyboard)

        glutMainLoop()

        glutSwapBuffers()
        glutPostRedisplay()

    def __run(self):
        self.__dt = time.time() - self.__prev_t
        self.__prev_t = time.time()

        self.__dts.append(self.__dt)

        elapsed = np.sum(self.__dts)
        if elapsed >= 1.0:  # one second worth of dts
            self.__dts = self.__dts[1:]

        if elapsed != 0:
            self.__fps = len(self.__dts) / elapsed

        self.__handleInputs()
        self.__camera.update(self.__dt)

        self.__display()

    def __handleInputs(self):
        if self.__inputs.mouseMPressed():
            self.__camera.move(self.__inputs.getMouseRel())

        if self.__inputs.mouseLPressed():
            if self.__inputs.ctrlPressed():
                self.__camera.move(self.__inputs.getMouseRel())
            else:
                self.__camera.rotate(self.__inputs.getMouseRel())

        if self.__inputs.wheelUp():
            self.__camera.applyZoom(-15)

        if self.__inputs.wheelDown():
            self.__camera.applyZoom(15)

        # TODO how to be able to check keys pressed inside FramesViewer AND outside ?
        # self.__inputs.getKeyPressed()
        # if self.__inputs.getKeyPressed() == b'c':
        # self.__reset_camera()

        self.__inputs.setMouseRel(np.array([0, 0]))

    def __display(self):
        # print(self.__fps)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.__displayWorld()

        try:
            for name, (frame, color, thickness) in self.__frames.items():
                self.__displayFrame(frame, color, thickness)
        except RuntimeError:
            pass

        self.__displayLinks()

        try:
            for name in self.__points.keys():
                if self.__points_visible[name]:
                    self.__displayPoints(name)
                    self.__tickPointsList(name)
        except RuntimeError:
            pass

        for name, mesh in self.__meshes.items():
            mesh.render(self.__camera.getScale(), showFrame=True)

        glutSwapBuffers()
        glutPostRedisplay()

    def __displayPoints(self, name):
        color = self.__points[name]["color"]
        size = self.__points[name]["size"]

        glPushMatrix()
        glDisable(GL_LIGHTING)

        glColor3f(color[0], color[1], color[2])
        glPointSize(size)
        glBegin(GL_POINTS)

        try:
            for point in self.__points[name]["points"]:
                glVertex3f(
                    point[0] * self.__camera.getScale(),
                    point[1] * self.__camera.getScale(),
                    point[2] * self.__camera.getScale(),
                )
        except RuntimeError as e:
            print("RuntimeError :", e)
            pass

        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __tickPointsList(self, name):
        self.__points[name]["oldness"] += 1

    def __displayPoint(self, _pos, color=(0, 0, 0), size=1):
        pos = _pos.copy()

        glPushMatrix()
        glDisable(GL_LIGHTING)

        glColor3f(color[0], color[1], color[2])
        glPointSize(size)
        glBegin(GL_POINTS)

        glVertex3f(
            pos[0] * self.__camera.getScale(),
            pos[1] * self.__camera.getScale(),
            pos[2] * self.__camera.getScale(),
        )
        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __displayFrame(self, _pose, color=None, thickness=4):
        pose = _pose.copy()

        glPushMatrix()

        size = self.__size * self.__camera.getScale()

        trans = pose[:3, 3] * self.__camera.getScale()
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

        if color is not None:
            glColor3f(color[0], color[1], color[2])
            glTranslatef(trans[0], trans[1], trans[2])
            gluSphere(gluNewQuadric(), size / 10, 10, 10)

        glLineWidth(1)
        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __displayLinks(self):
        thickness = 2

        glPushMatrix()
        glDisable(GL_LIGHTING)
        glLineWidth(thickness)
        glBegin(GL_LINES)

        for link, color in self.__links.items():
            frame1_pos = self.__frames[link[0]][0][:3, 3] * self.__camera.getScale()
            frame2_pos = self.__frames[link[1]][0][:3, 3] * self.__camera.getScale()

            glColor3f(color[0], color[1], color[2])
            glVertex3f(frame1_pos[0], frame1_pos[1], frame1_pos[2])
            glVertex3f(frame2_pos[0], frame2_pos[1], frame2_pos[2])

        glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __displayWorld(self):
        self.__displayFrame(utils.make_pose([0, 0, 0], [0, 0, 0]))

        glPushMatrix()

        size = self.__size * self.__camera.getScale()
        length = 15
        alpha = 0.04

        pose = utils.make_pose([0, 0, 0], [0, 0, 0])

        trans = pose[:3, 3] * self.__camera.getScale()
        rot_mat = pose[:3, :3]

        x_end_vec = rot_mat @ [length * size, 0, 0] + trans
        y_end_vec = rot_mat @ [0, length * size, 0] + trans
        z_end_vec = rot_mat @ [0, 0, length * size] + trans

        glDisable(GL_LIGHTING)
        glLineWidth(3)

        # X
        glColor4f(0, 0, 0, alpha)
        for i in range(length + 1):
            glBegin(GL_LINES)
            glVertex3f(trans[0], trans[1] + i * size, trans[2])
            glVertex3f(x_end_vec[0], x_end_vec[1] + i * size, x_end_vec[2])

            glVertex3f(trans[0] + i * size, trans[1], trans[2])
            glVertex3f(y_end_vec[0] + i * size, y_end_vec[1], y_end_vec[2])
            glEnd()

        # Y
        glColor4f(0, 0, 0, alpha)
        for i in range(length + 1):
            glBegin(GL_LINES)
            glVertex3f(trans[0], trans[1], trans[2] + i * size)
            glVertex3f(y_end_vec[0], y_end_vec[1], y_end_vec[2] + i * size)

            glVertex3f(trans[0], trans[1] + i * size, trans[2])
            glVertex3f(z_end_vec[0], z_end_vec[1] + i * size, z_end_vec[2])
            glEnd()

        # Z
        glColor4f(0, 0, 0, alpha)
        for i in range(length + 1):
            glBegin(GL_LINES)
            glVertex3f(trans[0] + i * size, trans[1], trans[2])
            glVertex3f(z_end_vec[0] + i * size, z_end_vec[1], z_end_vec[2])
            glVertex3f(trans[0], trans[1], trans[2] + i * size)
            glVertex3f(x_end_vec[0], x_end_vec[1], x_end_vec[2] + i * size)
            glEnd()

        glEnable(GL_LIGHTING)
        glPopMatrix()

    def __rotatePoints(
        self,
        points: list,
        rotation: list,
        center: list = [0, 0, 0],
        degrees: bool = True,
    ):
        pp = []
        rot_mat = R.from_euler("xyz", rotation, degrees=degrees).as_matrix()
        for point in points:
            pp.append(rot_mat @ point)

        return pp

    def __translatePoints(self, points: list, translation):
        pp = []
        for point in points:
            pp.append(point + translation)

        return pp
