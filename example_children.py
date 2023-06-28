from FramesViewer.viewer import Viewer
from FramesViewer import utils
import time

fv = Viewer()
fv.start()

trunk = fv.pushFrame(utils.make_pose([0.1, 0.1, 0.1], [0, 0, 0]), "trunk", [0, 0, 1])
fv.addChild("trunk", "left_shoulder_roll", utils.make_pose([0.1, 0, 0], [0, 0, 0]))

while True:
    time.sleep(0.01)