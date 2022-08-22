# FramesViewer 

A simple live 6D frames viewer

![FramesViewer](assets/FramesViewer.png)



## Example : 
```python
from FramesViewer import FramesViewer

fv = FramesViewer([1000, 1000])
fv.start()

fv.pushFrame(frame1, "frame1")
fv.pushFrame(frame2, "frame2")

...
...
...

fv.popFrame("frame1")
...

```

Once `fv.start()` is called, the viewer runs in a separate thread. 

You can then dynamically call `fv.pushFrame(...)` to add, update or remove frames.


