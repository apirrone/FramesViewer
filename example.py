from FramesViewer import FramesViewer
import time

fv = FramesViewer([1000, 1000])
fv.start()

frame1 = FramesViewer.make_pose([0.15, 0.15, 0], [45, 0, 0])
frame2 = FramesViewer.make_pose([0.15, 0.15, 0.15], [0, 90, 45])

fv.pushFrame(frame1, "frame1")
fv.pushFrame(frame2, "frame2")

# In this case, an infinite loop is needed to keep the viewer thread alive.
while True:
    time.sleep(0.01)
