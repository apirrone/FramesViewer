from FramesViewer import FramesViewer
from FramesViewer import utils as fv_utils
import time

fv = FramesViewer()
fv.start()

# Frames
frame1 = fv_utils.make_pose([0.15, 0.15, 0], [45, 0, 0])
frame2 = fv_utils.make_pose([0.15, 0.15, 0.15], [0, 90, 45])
frame3 = frame2.copy()

fv.pushFrame(frame1, "frame1", [1, 0, 0])
fv.pushFrame(frame2, "frame2", [0, 1, 0])

fv.pushFrame(frame3, "frame3")
fv.deleteFrame("frame3")

fv.createPointsList("a", size=10, color=(1, 0, 0))

# Points
for i in range(10):
    for j in range(10):
        for z in range(10):
            fv.pushPoint("a", [i*0.1, j*0.1, z*0.1])

# An infinite loop is needed to keep the viewer thread alive.
while True:
    frame2 = fv_utils.translateAbsolute(frame2, [0, 0.0005, 0])
    frame2 = fv_utils.rotateInSelf(frame2, [0.5, 0.5, 0.5])
    fv.pushFrame(frame2, "frame2", [0, 1, 0])
    time.sleep(0.01)
