# 🤚 BVH manipulation <!-- {docsify-ignore} -->
The **bvhManipulation** class contains many functions to make typical operations on BVH files (**moving and rotating** the skeleton in many ways). These functions take a **BVHData** object as input, and they return a modified copy of the object, so the old object is not directly modified and both objects remain intact.

## Centering the skeleton root
##### `centerSkeletonRoot(bvhData: BVHData, frame: int = 0) -> BVHData`

This function can be used to center the skeleton root and set its position to (0,0,0) on a specific frame, provide the number of the frame you want the root to be centered in. This means that in the frame that you provide, the root will be in (0,0,0) and all the animation will be shifted accordingly. Useful to center any animation in frame 0 (Default frame = 0).

```python
from bvhTools.bvhManipulation import centerSkeletonRoot

centeredBvhRoot = centerSkeletonRoot(bvhData)
centeredBvhRoot = centerSkeletonRoot(bvhData, 42) # center at frame 42
```

## Centering the skeleton feet
##### `centerSkeletonFeet(bvhData: BVHData, leftFootName: str = "LeftFoot", rightFootName: str = "RightFoot", frame: int = 0) -> BVHData`

This function centers the whole skeleton in the X and Z axes for a specific frame, and it also centers it on the Y axis, to put the feet on Y = 0. In other words, the skeleton will be standing on (0,0,0) on the provided frame. It uses the two feet to calculate the average Y height, so the names of both feet joints are needed. (Default leftFootName = "LeftFoot", rightFootName = "RightFoot"). Useful to center the feet of any animation in frame 0 (Default frame = 0).

```python
from bvhTools.bvhManipulation import centerSkeletonFeet

centeredBvhFeet = centerSkeletonFeet(bvhData)
centeredBvhFeet = centerSkeletonFeet(bvhData, leftFootName = "lFoot", rightFootName = "rFoot", frame = 42) # center at frame 42 using custom left and right foot names
```

## Standing the skeleton on the floor
##### `standSkeletonOnFloor(bvhData: BVHData, leftFootName: str = "LeftFoot", rightFootName: str = "RightFoot", fkFrame: int = 0) -> BVHData`

This function puts the feet on Y = 0, but it does not change the X and Z coordinates. In other words, the skeleton will be raised or lowered to (X,0,Z) on the provided frame. It uses the two feet to calculate the average Y height, so the names of both feet joints are needed. (Default leftFootName = "LeftFoot", rightFootName = "RightFoot").

```python
from bvhTools.bvhManipulation import standSkeletonOnFloor

standingBvh = standSkeletonOnFloor(bvhData)
standingBvh = standSkeletonOnFloor(bvhData, leftFootName = "lFoot", rightFootName = "rFoot", frame = 42) # center at frame 42 using custom left and right foot names
```

## Centering the skeleton on the X and Z axes
##### `centerSkeletonXZ(bvhData: BVHData, frame: int = 0) -> BVHData`

This function centers the whole skeleton without changing the height of the animation. By default, it centers on the (0,0) on frame 0, but any frame can be specified.

```python
from bvhTools.bvhManipulation import centerSkeletonXZ

centeredBvh = centerSkeletonXZ(bvhData)
```

## Centering the skeleton around a specific joint
##### `centerSkeletonAroundJoint(bvhData: BVHData, jointName: str, frame: int = 0) -> BVHData`

This function centers the skeleton around a specific joint at a specific frame. In short, the selected joint will be on (0,0,0) at the specified frame (Default frame = 0).

```python
from bvhTools.bvhManipulation import centerSkeletonAroundJoint

centeredBvh = centerSkeletonAroundJoint(bvhData, "RightArm", 30) # The RightArm joint will be at (0,0,0) at frame 30
```

## Moving the skeleton around (adding an offset to the animation)
##### `moveSkeleton(bvhData: BVHData, offset: list[float]) -> BVHData`
This function shifts the enitre animation by adding a position offset to the root in every frame. The method uses the [X, Y, Z] convention where Y is the vertical axis.

```python
from bvhTools.bvhManipulation import moveSkeleton

movedData = moveSkeleton(bvhData, [5, 5, 0]) # Move the whole animation 5 units in the X axis and 5 units in the y axis
```

## Rotating the BVH in world coordinates
##### `rotateSkeletonWorld(bvhData: BVHData, rotations: list[float]) -> BVHData`
With this function, you can rotate the BVH around the world center. The method uses the [X, Y, Z] convention where Y is the vertical axis.

```python
from bvhTools.bvhManipulation import rotateSkeletonWorld

rotatedBvh = rotateSkeletonWorld(bvhData, [0, 90, 0]) # The new motion will be rotated 90 degrees around the vertical Y axis. 
```

## Rotating the BVH in local coordinates
##### `rotateSkeletonLocal(bvhData: BVHData, rotations: list[float]) -> BVHData`
With this function, you can rotate the BVH around the center of the root at whatever frame you choose (default = 0). The method uses the [X, Y, Z] convention, where Y is the vertical axis.

```python
from bvhTools.bvhManipulation import rotateSkeletonLocal

rotatedBvh = rotateSkeletonLocal(bvhData, [0, 90, 0]) # The new motion will be rotated 90 degrees around the vertical Y axis around the root joint position.
```

## Mirroring the skeleton
##### `mirrorSkeleton(bvhData: BVHData, flipAxis: str, jointPairs: list[list[str]]) -> BVHData:`

This function permits to flip the animation in any axis. However, it **does not** change the structure of the original bvh hierarchy. This means, that the skeleton being mirrored has to be symmetric. For example, if your animation file has just one right arm and no left arm, this function **will not** create a left arm and attach the right arm motion to it. It will just flip the right arm, which will stay in the same right side, but flipped. 

However, this does not mean that all the bones in the skeleton need to have a right-left counterpart: the back bones of an animation will just be flipped and a person bending to the left will bend to the right, for instance. If a bone **does have** a left-right counterpart, this function **will exchange** the motion between the two bones: for example, if a person scratches their head with their right hand, the flipped version will scratch the head with the left hand. For this to work, all the left-right pairs need to be provided in the *jointPairs* parameter, as a list containing pairs (lists of 2 strings).

```python
from bvhTools.bvhManipulation import mirrorSkeleton

# first, prepare the joints that need to be swapped
jointPairs = [["LeftUpLeg", "RightUpLeg"], ["LeftLeg", "RightLeg"], ["LeftFoot", "RightFoot"], ["LeftToe", "RightToe"], ["LeftShoulder", "RightShoulder"], ["LeftArm", "RightArm"], ["LeftForeArm", "RightForeArm"], ["LeftHand", "RightHand"]]

mirroredBvh = mirrorSkeleton(bvhData, "x", jointPairs) # The new motion will be flipped in the x axis
```

**Important note: Mirroring BVH animations is not trivial, and it depends on the forward direction of the animation. For this reason, a BVH file might need to be flipped in the X axis, while other might need to be flipped in the Z axis. Moreover, even after flipping, you might need to rotate the flipped skeleton so the forward directions match.You can do so with the [rotateSkeletonLocal](#rotating-the-bvh-in-local-coordinates) or the [rotateSkeletonWorld](#rotating-the-bvh-in-world-coordinates) functions. The following example shows how to do it:**

```python
from bvhTools.bvhManipulation import mirrorSkeleton, rotateSkeletonLocal

# first, prepare the joints that need to be swapped
jointPairs = [["LeftUpLeg", "RightUpLeg"], ["LeftLeg", "RightLeg"], ["LeftFoot", "RightFoot"], ["LeftToe", "RightToe"], ["LeftShoulder", "RightShoulder"], ["LeftArm", "RightArm"], ["LeftForeArm", "RightForeArm"], ["LeftHand", "RightHand"]]

mirroredBvh = mirrorSkeleton(bvhData, "z", jointPairs) # The new motion will be flipped in the z axis
mirroredBvh = rotateSkeletonLocal(mirroredBvh, [0, 180, 0]) # In this example, the new motion needed to be rotated in order to have the same forward direction as the original file
```