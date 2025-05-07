## 👩‍🔬 Use Cases <!-- {docsify-ignore} -->
Here you can find real use cases of the library, with some explanations of the situation or use case, and how I used **bvhTools** to solve the problem.
### Use Case 1 (Centering an entire dataset)
I recorded an animation dataset using [Freemocap](https://freemocap.org/), which is a great open-source tool to record motion capture data without any mocap suits. Then, I retargeted the motion to the [LAFAN1](https://github.com/ubisoft/ubisoft-laforge-animation-dataset/tree/master) skeleton structure, as I had to use the same skeleton for some neural network training. For that I used a [open-source blender addon](https://github.com/Mwni/blender-animation-retargeting).

This process generated skeletons which were not centered in the world space, and were not rotated properly either. Because of that, I used **bvhTools** to center and rotate all the bvh files in my dataset, in just 4 lines of operating code:

```python
import os
from bvhTools import bvhIO
from bvhTools import bvhManipulation

folder_path = 'path/to/my/folder'

for filename in os.listdir(folder_path):
    if filename.endswith('.bvh'):
        bvhFile = bvhIO.readBvh(filename)
        bvhFile = bvhManipulation.centerSkeletonFeet(bvhFile)
        bvhFile = bvhManipulation.rotateSkeletonLocal([0, 90, 0])
        bvhIO.writeBvh(filename)
```