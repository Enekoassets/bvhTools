# 🧑‍🔬 Simple Examples <!-- {docsify-ignore} -->
**Note: You can find a jupyter notebook with simple examples in the tutorials folder of the master branch.**

Here you can find some simple examples of typical BVH edition pipelines.

## 1) Read -> rotate and move skeleton -> write

In this example, we read a BVH file, we rotate the skeleton 90 degrees in the vertical axis, we center it so the root is in (0, 0, 0) in the first frame and we write it to a new file.


```python
from bvhTools import bvhIO, bvhManipulation

bvh = bvhIO.readBvh("test1.bvh")

bvhMod = bvhManipulation.rotateSkeletonLocal(bvh, [0, 90, 0])
bvhMod = bvhManipulation.centerSkeletonRoot(bvhMod)

bvhIO.writeBvh(bvhMod, "modifiedtest1.bvh")
```

## 2) Read -> move skeletons -> merge -> write

In this example, we read two separate BVH files with the same skeleton structure, we center each one so they stand in (0, 0, 0) in the first frame each, we put them together and write the result to a new file.


```python
from bvhTools import bvhIO, bvhManipulation, bvhSlicer

bvh1 = bvhIO.readBvh("test1.bvh")
bvh2 = bvhIO.readBvh("test2.bvh")

bvh1 = bvhManipulation.centerSkeletonFeet(bvh1)
bvh2 = bvhManipulation.centerSkeletonFeet(bvh2)

mergedBvh = bvhSlicer.groupBvhSlices([bvh1, bvh2])

bvhIO.writeBvh(mergedBvh, "merged.bvh")
```

## 3) Read -> print information -> visualize

In this example, we read a BVH file, and print many aspects regarding the animation and skeleton, such as the header, the skeleton hierarchy and some information of the animation. Finally, we open the visualizer to inspect it.


```python
from bvhTools import bvhIO, bvhVisualizer

bvh = bvhIO.readBvh("test1.bvh")

print(bvh.getHeader())
bvh.skeleton.printSkeleton(verbose = True)
print(f"fps: {bvh.motion.getFPS()}")
print(f"frame time: {bvh.motion.frameTime}")
print(f"number of frames: {bvh.motion.numFrames}")
bvh.motion.printHead(headSize = 20)

bvhVisualizer.showBvhAnimation(bvh)
```

## 4) Read -> calculate and plot speeds -> visualize mean pose
In this example, we will use bvhTools to easily read and calculate the speed magnitudes of an animation, and then plot the root speed during time using matplotlib. Finally, we are going to calculate the mean pose of the animation, and inspect it using the visualizer.


```python
from bvhTools import bvhIO, bvhMetrics, bvhVisualizer
import matplotlib.pyplot as plt
import numpy as np

bvh = bvhIO.readBvh("test1.bvh")

speeds = bvhMetrics.getSpeeds(bvh, type = "magnitude")
frameRange = np.arange(bvh.motion.numFrames - 1)
plt.plot(frameRange, speeds[:, 0], linewidth = 0.5)
plt.show()

avgPose = bvhMetrics.getAvgPose(bvh)
bvhVisualizer.showBvhAnimation(avgPose)
```

# 5) Read -> augment data using mirroring -> write
In this example, we are going to read a BVH file and augment it by creating a mirrored version of itself. This specific example does not need to be rotated after the mirroring, but take into account that your case might be different. Finally, we are going to write the mirrored file, and we will also visualize it to see the results.


```python
from bvhTools import bvhIO, bvhManipulation

bvh = bvhIO.readBvh("test1.bvh")

mirroredBvh = bvhManipulation.mirrorSkeleton(bvh, "z", [["LeftUpLeg", "RightUpLeg"], ["LeftLeg", "RightLeg"], ["LeftFoot", "RightFoot"], ["LeftToe", "RightToe"], 
                                                        ["LeftShoulder", "RightShoulder"], ["LeftArm", "RightArm"], ["LeftForeArm", "RightForeArm"], ["LeftHand", "RightHand"]])

bvhIO.writeBvh(mirroredBvh, "mirroredtest1")
```