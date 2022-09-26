from FramesViewer import FramesViewer
from FramesViewer import utils as fv_utils

import time

fv = FramesViewer([1000, 1000])
fv.start()

frame1 = fv_utils.make_pose([0.15, 0.15, 0], [45, 0, 0])
frame2 = fv_utils.make_pose([0.15, 0.15, 0.15], [0, 90, 45])

fv.pushFrame(frame1, "frame1", [1, 0, 0])
fv.pushFrame(frame2, "frame2", [0, 1, 0])

for i in range(10):
    for j in range(10):
        for z in range(10):
            fv.pushPoint([i*0.1, j*0.1, z*0.1], "a", (1, 0, 0), 10)

# An infinite loop is needed to keep the viewer thread alive.
while True:

    frame2 = fv_utils.translateAbsolute(frame2, [0, 0.001, 0])
    fv.pushFrame(frame2, "frame2", [0, 1, 0])
    time.sleep(0.01)
