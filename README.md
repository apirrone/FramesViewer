# FramesViewer 

A simple live 6D frames viewer

![FramesViewer](assets/FramesViewer.png)

## Installation
```python
pip3 install -e .
```

## Example : 
```python
from FramesViewer import FramesViewer
from FramesViewer import utils as fv_utils

import time

fv = FramesViewer([1000, 1000])
fv.start()

frame1 = fv_utils.make_pose([0.15, 0.15, 0], [45, 0, 0])
frame2 = fv_utils.make_pose([0.15, 0.15, 0.15], [0, 90, 45])

fv.pushFrame(frame1, "frame1", [1, 0, 0])
fv.pushFrame(frame2, "frame2", [0, 1, 0])

# An infinite loop is needed to keep the viewer thread alive.
while True:
    time.sleep(0.01)
```

Once `fv.start()` is called, the viewer runs in a separate thread. 

You can then dynamically call `fv.pushFrame(...)` to add, update or remove frames.


