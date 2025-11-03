# 📊 BVH metrics<!-- {docsify-ignore} -->
The **bvhMetrics** class contains functions to automatically analyze and many metrics from the BVH file, such as foot contacts, speeds, accelerations, jerks... 

## 👣 Foot contacts
You can automatically foot contact masks for a specific bvh file. **bvhTools** has two methods to compute foot contacts: a method **based on joint speeds**, and another method based on the **joint heights**.

**Note**: If you are not sure which method is the best for you animation or you don't know which threshold parameters are the best in your case, you can use the **bvhVisualizer** class to visualize the foot contacts given a specific method and specific parameters.

### Foot contacts based on joint speeds
The *getFootContactsSpeedMethod(bvh, footNames = ["LeftFoot", "RightFoot"], threshold = 0.1, timeDiff = -1)* method computes the foot contacts of an animation, by using the foot speed magnitude in each frame to create a boolean mask for each foot.

The method needs a list of foot names (it can be an arbitrary number of feet, useful for quadruped animation, among others). For these feet, the method will return a numpy array of dimension ([number of feet] x [number of frames]). **Note**: the first frame is duplicated so the mask will have the same dimension as the number of frames.

The **threshold** value controls what speed value (in m/s) is considered as being moving, and therefore, not on the floor. The **timeDiff** is the delta time used to calculate the speed in each frame. By default (timeDiff = -1), this method will use the *frame time* information from the BVH file as the delta time.

```python
from bvhTools.bvhMetrics import getFootContactsSpeedMethod

footCtc = getFootContactsSpeedMethod(bvh, ["footL", "footR"], 2)
# footCtc will have a 2x1000 boolean np array (number of frames = 1000)
# any foot faster than 2 m/s will be marked as 1, else 0 
```

### Foot contacts based on joint height
The *getFootContactsHeightMethod(bvh, footNames = ["LeftFoot", "RightFoot"], threshold = 0.1, referenceFrame = 0)* method computes the foot contacts of an animation, by using the foot height in each frame to create a boolean mask for each foot.

The method needs a list of foot names (it can be an arbitrary number of feet, useful for quadruped animation, among others). For these feet, the method will return a numpy array of dimension ([number of feet] x [number of frames]).

This method first computes the height of the floor by averaging the Y values of all feet in a specific frame. Then, it will create a binary mask for each foot if any foot is higher than a threshold value in a frame. The **threshold** value controls what height value (in meters) is considered as being in the air. The **referenceFrame** value determines which frame will be used to compute the floor height.

```python
from bvhTools.bvhMetrics import getFootContactsHeightMethod

footCtc = getFootContactsHeightMethod(bvh, ["foot1", "foot2", "foot3", "foot4"], 0.2)
# footCtc will have a 4x1000 boolean np array (number of frames = 1000, example for a quadruped)
# any foot lower than 20cm from the floor will be marked as 1, else 0 
```

## 🚀 Speeds
The module can compute per frame speeds for all the joints. The speeds can be calculated in vector form or in scalar form (magnitudes of vectors).

### Calculate speed vectors per frame
The *getSpeedVectors(bvh, timeDiff = -1)* method computes the speed vectors of all joints per frame. It returns a numpy array of dimension ([number of joints] x [number of frames - 1] x [3]). 

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getSpeedVectors

speeds = getSpeedVectors(bvh) # speeds will have a 22x999x3 numpy array (number of frames = 1000)
```

### Calculate speed magnitudes per frame
If instead of the speed vectors, their magnitude is needed (for plotting the speeds per frame, for instance), the *getSpeeds(bvh, timeDiff = -1)* method returns a numpy array of dimension ([number of joints] x [number of frames - 1]).

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getSpeedVectors

speeds = getSpeedVectors(bvh) # speeds will have a 22x999 numpy array (number of frames = 1000)
```

### Calculate average speeds
The *getAvgSpeeds(bvh, timeDiff = -1)* method returns the average speed for each joint, taking into account all the frames. It averages all vectors of all frames, and returns one average vector per joint.

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getAvgSpeeds

speeds = getAvgSpeeds(bvh) # speeds will have a 22x3 numpy array (number of frames = 1000)
```

### Calculate average speeds per frame
Instead of averaging all the frames, the *getAvgSpeedsPerFrame(bvh, timeDiff = -1)* averages the speed vectors of all the joints together, and returns a numpy array containing the average vector of each frame. This can be useful to plot these vectors' magnitudes in a plot, for example.

```python
from bvhTools.bvhMetrics import getAvgSpeedsPerFrame

speeds = getAvgSpeedsPerFrame(bvh) # speeds will have a 3x999 numpy array (number of frames = 1000)
```

## 🏎️ Accelerations
The module can compute per frame accelerations for all the joints. The accelerations can be calculated in vector form or in scalar form (magnitudes of vectors).

### Calculate acceleration vectors per frame
The *getAccelerationVectors(bvh, timeDiff = -1)* method computes the acceleration vectors of all joints per frame. It returns a numpy array of dimension ([number of joints] x [number of frames - 2] x [3]). 

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getAccelerationVectors

accelerations = getAccelerationVectors(bvh) # accelerations will have a 22x998x3 numpy array (number of frames = 1000)
```

### Calculate acceleration magnitudes per frame
If instead of the acceleration vectors, their magnitude is needed (for plotting the accelerations per frame, for instance), the *getAccelerations(bvh, timeDiff = -1)* method returns a numpy array of dimension ([number of joints] x [number of frames - 2]).

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getAccelerationVectors

accelerations = getAccelerationVectors(bvh) # accelerations will have a 22x998 numpy array (number of frames = 1000)
```

### Calculate average accelerations
The *getAvgAccelerations(bvh, timeDiff = -1)* method returns the average acceleration for each joint, taking into account all the frames. It averages all vectors of all frames, and returns one average vector per joint.

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getAvgAccelerations

accelerations = getAvgAccelerations(bvh) # accelerations will have a 22x3 numpy array (number of frames = 1000)
```

### Calculate average accelerations per frame
Instead of averaging all the frames, the *getAvgAccelerationsPerFrame(bvh, timeDiff = -1)* averages the acceleration vectors of all the joints together, and returns a numpy array containing the average vector of each frame. This can be useful to plot these vectors' magnitudes in a plot, for example.

```python
from bvhTools.bvhMetrics import getAvgAccelerationsPerFrame

accelerations = getAvgAccelerationsPerFrame(bvh) # accelerations will have a 3x998 numpy array (number of frames = 1000)
```

## 🚗 Jerks
The module can compute per frame jerks for all the joints. The jerks can be calculated in vector form or in scalar form (magnitudes of vectors).

### Calculate jerk vectors per frame
The *getJerkVectors(bvh, timeDiff = -1)* method computes the jerk vectors of all joints per frame. It returns a numpy array of dimension ([number of joints] x [number of frames - 3] x [3]). 

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getJerkVectors

jerks = getJerkVectors(bvh) # jerks will have a 22x997x3 numpy array (number of frames = 1000)
```

### Calculate jerk magnitudes per frame
If instead of the jerk vectors, their magnitude is needed (for plotting the jerks per frame, for instance), the *getJerks(bvh, timeDiff = -1)* method returns a numpy array of dimension ([number of joints] x [number of frames - 3]).

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getJerkVectors

jerks = getJerkVectors(bvh) # jerks will have a 22x997 numpy array (number of frames = 1000)
```

### Calculate average jerks
The *getAvgJerks(bvh, timeDiff = -1)* method returns the average jerk for each joint, taking into account all the frames. It averages all vectors of all frames, and returns one average vector per joint.

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getAvgJerks

jerks = getAvgJerks(bvh) # jerks will have a 22x3 numpy array (number of frames = 1000)
```

### Calculate average jerks per frame
Instead of averaging all the frames, the *getAvgJerksPerFrame(bvh, timeDiff = -1)* averages the acceleration vectors of all the joints together, and returns a numpy array containing the average vector of each frame. This can be useful to plot these vectors' magnitudes in a plot, for example.

```python
from bvhTools.bvhMetrics import getAvgJerksPerFrame

speeds = getAvgJerksPerFrame(bvh) # speeds will have a 3x997 numpy array (number of frames = 1000)
```