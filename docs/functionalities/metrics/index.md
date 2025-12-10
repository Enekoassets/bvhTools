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

### Calculate speeds (vector/magnitude)
The *getSpeeds(bvh, timeDiff = -1, type = "vector")* method computes the speed of all joints per frame. It calculates forward kinematics for each frame in the animation, and uses the difference between 2 frames to compute the speeds of each joint in each frame. The return type is controlled by the *type* parameter:
- **type = "vector":** returns a numpy array of speed vectors, of dimension ([num_joints] x [num_frames - 1] x [3]) 
- **type = "magnitude":** returns a numpy array of magnitudes of the speed vectors, of dimension ([num_joints] x [num_frames - 1]).

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

```python
from bvhTools.bvhMetrics import getSpeeds

speeds = getSpeeds(bvh) # speeds will have a 22x999x3 numpy array (number of frames = 1000)

speedMagnitudes = getSpeeds(bvh, type = "magnitude") # speedMagnitudes will be a 22x999 numpy array
```

### Calculate angular speeds (vector/magnitude)
The *getAngularSpeeds(bvh, timeDiff = -1, type = "vector")* calculates the angular speeds of each joint in each frame. It calculates the rotational difference in each frame for each joint, to then calculate the speed. The return type is controlled by the *type* parameter:
- **type = "vector":** returns a numpy array of angular speed vectors, of dimension ([num_joints] x [num_frames - 1] x [3]).
  
    The returned vectors are **rotation vectors**: the direction of the vector is the axis of rotation, and the magnitude of the vector is its angular speed value. This means that the output is not calculated using the difference between Euler angles, but the rotation's relative motion respect to the previous frame (composition of rotations), divided by the delta-time.
- **type = "magnitude":** returns a numpy array with the magnitude of the angular speed vectors, of size ([num_joints] x [num_frames - 1]).

The **timeDiff** variable enables setting a different delta time value if needed. By default (timeDiff = -1), the method uses the *Frame time* value from the bvh file.

### Calculate average speeds (vector/magnitude)
The *getAvgSpeeds(bvh, timeDiff = -1, type = "vector", mode = "perJoint") method returns the average speeds. The *type* parameter controls the [return type](#calculate-speeds-vectormagnitude) (vector/magnitude). The *mode* parameter controls the axis which will be used for doing the average:
- **perJoint:** the average is calculated per joint, meaning that the result will contain the average speed (vector/magnitude) of each joint during the entire animation. It returns a numpy array of dimension ([num_joints] x [3]) or ([num_joints]).
- **perFrame:** the average is calculated per frame, meaning that the result will contain the average speed of all joints in each frame. It returns a numpy array of dimension ([num_frames - 1] x[3]) or ([num_frames -1]).

### Calculate average angular speeds (vector/magnitude)
The *getAvgAngularSpeeds(bvh, timeDiff = -1, type = "vector", mode = "perJoint") method returns the average angular speeds. The *type* parameter controls the [return type](#calculate-angular-speeds-vectormagnitude) (vector/magnitude). The *mode* parameter controls te axis which will be used for doing the average:
- **perJoint:** the average is calculated per joint, meaning that the result will contain the average angular speed (vector/magnitude) of each joint during the entire animation. It returns a numpy array of dimension ([num_joints] x [3]) or ([num_joints]).
- **perFrame:** the average is calculated per frame, meaning that the result will contain the average angular speed of all joints in each frame. It returns a numpy array of dimension ([num_frames - 1] x[3]) or ([num_frames -1]).

## 🏎️ Accelerations
The module can compute per frame accelerations for all the joints. The method calls are used in exactly the same way as with the speed calculation, and the output format is also the same, but with accelerations, since the acceleration is the second order derivative and the speed is the first order derivative.

The following functions are available for acceleration calculations. Please refer to the corresponding speed counterpart by clicking on the method:

### Calculate accelerations (vector/magnitude)
*[getAccelerations(bvh, timeDiff = -1, type = "vector")](#calculate-speeds-vectormagnitude)*
### Calculate angular accelerations (vector/magnitude)
*[getAngularAccelerations(bvh, timeDiff = -1, type = "vector")](#calculate-angular-speeds-vectormagnitude)*
### Calculate average accelerations (vector/magnitude)
*[getAvgAccelerations(bvh, timeDiff = -1, type = "vector", mode = "perJoint")](#calculate-average-speeds-vectormagnitude)*
### Calculate average angular accelerations (vector/magnitude)
*[getAvgAngularAccelerations(bvh, timeDiff = -1, type = "vector", mode = "perJoint")](#calculate-average-angular-speeds-vectormagnitude)*

## 🚗 Jerks
The module can compute per frame jerks for all the joints. The method calls are used in exactly the same way as with the speed calculation, and the output format is also the same, but with jerks, since the jerk is the third order derivative and the speed is the first order derivative.

The following functions are available for jerk calculations. Please refer to the corresponding speed counterpart by clicking on the method:

### Calculate jerks (vector/magnitude)
*[getJerks(bvh, timeDiff = -1, type = "vector")](#calculate-speeds-vectormagnitude)*
### Calculate angular jerks (vector/magnitude)
*[getAngularJerks(bvh, timeDiff = -1, type = "vector")](#calculate-angular-speeds-vectormagnitude)*
### Calculate average jerks (vector/magnitude)
*[getAvgJerks(bvh, timeDiff = -1, type = "vector", mode = "perJoint")](#calculate-average-speeds-vectormagnitude)*
### Calculate average angular jerks (vector/magnitude)
*[getAvgAngularJerks(bvh, timeDiff = -1, type = "vector", mode = "perJoint")](#calculate-average-angular-speeds-vectormagnitude)*

## 🕺 Average pose
You can get the average pose of a BVH sequence with the *getAvgPose(bvh)* function. This will average the position channels of the root (and other joints if they have position channels) and also the rotation channels of all joints. To calculate the average rotations, **bvhTools** converts all rotations to quaternions, then checks the sign of each quaternion and flips them if needed (relative to the previous quaternion). Finally, it calculates the average quaternion, and converts it to Euler angles.

```python
from bvhTools.bvhMetrics import getAvgPose

avgBvh = getAvgPose(bvh)
```

This method does **not** return a numpy array containing the average pose. Instead, it returns a new [bvhData](../dataStructures/index.md) object, with the average pose already inserted in the motion attribute (it also sets numFrames = 1 for the new object). This enables to use the same data structures all the time. For example, we can calculate and then visualize the mean pose using the same visualization pipeline:

```python
from bvhTools.bvhMetrics import getAvgPose
from bvhTools.bvhVisualizerMpl import showBvhAnimation

avgBvh = getAvgPose(bvh)
showBvhAnimation(avgPose)
```

If the average pose is needed as a numpy array, just take it from the **motionData** field of the **bvhData** object:

```python
from bvhTools.bvhMetrics import getAvgPose

avgBvh = getAvgPose(bvh)
avgPoseList = avgBvh.motion.frames # avgPoseList will contain the numpy array object
```