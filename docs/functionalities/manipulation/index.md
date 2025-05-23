# 🤚 BVH manipulation <!-- {docsify-ignore} -->
The **bvhManipulation** class contains many functions to make typical operations on BVH files (**moving and rotating** the skeleton in many ways). These functions take a **bvhData** object as input, and they return a modified copy of the object, so the old object is not directly modified and both objects remain intact.

## Centering the skeleton root
The *centerSkeletonRoot(bvhData, frame = 0)* function can be used to center the skeleton root and set its position to (0,0,0) on a specific frame, provide the number of the frame you want the root to be centered in. This means that in the frame that you provide, the root will be in (0,0,0) and all the animation will be shifted accordingly. Useful to center any animation in frame 0 (Default frame = 0).

```python
from bvhTools.bvhManipulation import centerSkeletonRoot

centeredBvhRoot = centerSkeletonRoot(bvhData)
centeredBvhRoot = centerSkeletonRoot(bvhData, 42) # center at frame 42
```

## Centering the skeleton feet
The *centerSkeletonFeet(bvhData, leftFootName = "LeftFoot", rightFootName = "RightFoot", frame = 0)* function centers the whole skeleton in the X and Z axes for a specific frame, and it also centers it on the Y axis, to put the feet on Y = 0. In other words, the skeleton will be standing on (0,0,0) on the provided frame. It uses the two feet to calculate the average Y height, so the names of both feet joints are needed. (Default leftFootName = "LeftFoot", rightFootName = "RightFoot"). Useful to center the feet of any animation in frame 0 (Default frame = 0).

```python
from bvhTools.bvhManipulation import centerSkeletonFeet

centeredBvhRoot = centerSkeletonFeet(bvhData)
centeredBvhRoot = centerSkeletonFeet(bvhData, leftFootName = "lFoot", rightFootName = "rFoot", frame = 42) # center at frame 42 using custom left and right foot names
```

## Centering the skeleton on the X and Z axes
The *centerSkeletonXZ(bvhData, frame = 0)* function centers the whole skeleton without changing the height of the animation. By default, it centers on the (0,0) on frame 0, but any frame can be specified.

```python
from bvhTools.bvhManipulation import centerSkeletonXZ

centeredBvh = centerSkeletonXZ(bvhData)
```

## Centering the skeleton around a specific joint
The *centerSkeletonAroundJoint(bvhData, jointName, frame = 0)* function centers the skeleton around a specific joint at a specific frame. In short, the selected joint will be on (0,0,0) at the specified frame (Default frame = 0).

```python
from bvhTools.bvhManipulation import centerSkeletonAroundJoint

centeredBvh = centerSkeletonAroundJoint(bvhData, "RightArm", 30) # The RightArm joint will be at (0,0,0) at frame 30
```

## Moving the skeleton around (adding an offset to the animation)
The *moveSkeleton(bvhData, offsets)* function shifts the enitre animation by adding a position offset to the root in every frame. The method uses the [X, Y, Z] convention where Y is the vertical axis.

```python
from bvhTools.bvhManipulation import moveSkeleton

movedData = moveSkeleton(bvhData, [5, 5, 0]) # Move the whole animation 5 units in the X axis and 5 units in the y axis
```

## Rotating the BVH in world coordinates
With *rotateSkeletonWorld(bvhData, rotations)*, you can rotate the BVH around the world center. The method uses the [X, Y, Z] convention where Y is the vertical axis.

```python
from bvhTools.bvhManipulation import rotateSkeletonWorld

rotatedBvh = rotateSkeletonWorld(bvhData, [0, 90, 0]) # The new motion will be rotated 90 degrees around the vertical Y axis. 
```

## Rotating the BVH in local coordinates
With *rotateSkeletonLocal(bvhData, rotations)*, you can rotate the BVH around the center of the root at whatever frame you choose (default = 0). The method uses the [X, Y, Z] convention, where Y is the vertical axis.

```python
from bvhTools.bvhManipulation import rotateSkeletonLocal

rotatedBvh = rotateSkeletonLocal(bvhData, [0, 90, 0]) # The new motion will be rotated 90 degrees around the vertical Y axis around the root joint position.
```