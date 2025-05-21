## 👀 BVH viewer<!-- {docsify-ignore} -->
**Note: Currently, the viewer may give some importing errors.**

**Note: Currently, the only available viewer uses matplotlib. Other rendering techniques should be available in the future.**
### Matplotlib viewer
A simple BVH viewer is implemented using matplotlib for quick viewing, using the *showBvhAnimation()* function from the *bvhVisualizerMpl* class. It contains a basic play/pause button and forward/back buttons to pass frames one by one. It also permits to jump to specific frames and to change the speed of time for faster/slower playback.

```python
from bvhTools.bvhVisualizerMpl import showBvhAnimation

showBvhAnimation(bvhData)
```

The visualization can be **customized** using many options, even if not giving any parameters will show an animation with the default options. The complete function looks like this:

#### *showBvhAnimation(bvhData, showPoints = True, showLines = True, showQuivers = True, showLabels = False, pointColor = "#4287f5", pointMarker = "o", lineColor = "#666666", lineWidth = 2)*