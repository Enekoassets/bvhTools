## 👀 BVH viewer<!-- {docsify-ignore} -->
**Note: Currently, the viewer may give some importing errors.**

A simple BVH viewer is implemented using matplotlib for fast viewing. It contains a basic play/pause button and forward/back buttons to pass frames one by one. It also permits to jump to specific frames and to change the speed of time for faster/slower playback.

```python
from bvhTools.bvhVisualizerSimple import showBvhAnimation

showBvhAnimation(bvhData)
```