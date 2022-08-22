from FramesViewer import FramesViewer
import pickle
import numpy as np
import time
from reachy_sdk import ReachySDK

reachy = ReachySDK('localhost')

fv = FramesViewer([1000, 1000])
fv.start()

T_camera_torso = pickle.load(open("../../Pollen/INCIA_cylinder_grasping/camera_calibration/T_camera_torso.pckl", 'rb'))
T_torso_camera = np.linalg.inv(T_camera_torso)
fv.pushFrame(T_torso_camera, "T_torso_camera")

i = 0
while True:
    # time.sleep(0.01)

    fv.pushFrame(reachy.r_arm.forward_kinematics(), "T_torso_hand")
