import numpy as np
from scipy.spatial.transform import Rotation as R

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
    frame = make_pose([0, 0, 0], rotation) @ frame        
    frame = np.linalg.inv(toOrigin) @ frame

    return frame
    
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
    frame = make_pose([0, 0, 0], rotation) @ frame        
    frame = np.linalg.inv(toOrigin) @ frame

    return frame
    
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
    frame = make_pose(translation, [0, 0, 0]) @ frame
    frame = np.linalg.inv(toOrigin) @ frame

    return frame

def translateAbsolute(_frame, translation):
    """
    TODO
    """
    frame = _frame.copy()

    translate = make_pose(translation, [0, 0, 0])

    return translate @ frame


# TODO check that
def swapAxes(_frame:np.ndarray, ax1_str:str, ax2_str:str):
    assert ax1_str in ["x", "y", "z"]
    assert ax2_str in ["x", "y", "z"]
    assert ax1_str != ax2_str
    axesIndices = {"x" : 0, "y" : 1, "z" : 2}

    frame = _frame.copy()
    
    tmp = frame[:3, axesIndices[ax2_str]].copy()
    frame[:3, axesIndices[ax2_str]] = frame[:3, axesIndices[ax1_str]]
    frame[:3, axesIndices[ax1_str]] = tmp

    trans = frame[:3, 3].copy()

    frame[:3, 3][axesIndices[ax2_str]] = trans[axesIndices[ax1_str]]
    frame[:3, 3][axesIndices[ax1_str]] = trans[axesIndices[ax2_str]]
    
    return frame