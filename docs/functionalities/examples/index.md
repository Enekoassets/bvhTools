## 🧑‍🔬 Simple Examples <!-- {docsify-ignore} -->

### Example 1 (read -> rotate skeleton -> write)
Load a BVH file, rotate it 90 degrees on the vertical axis, center it in the world and write the new animation

```python
from bvhTools import bvhIO
from bvhTools import bvhManipulation

# Read the file
bvh = bvhIO.readBvh("test1.bvh")

# Rotate it 90 degrees on the vertical axis
bvh = bvhManipulation.rotateSkeletonLocal(bvh, [0, 90, 0])

# Center it in the world
bvh = bvhManipulation.centerSkeletonRoot(bvh)

# write the result
bvhIO.writeBvh(mergedBvh, "merged.bvh")
```

### Example 2 (read -> move skeletons -> merge -> write)
Read two BVH files, put both standing in the center, merge them into a single animation and write the new animation

```python
from bvhTools import bvhIO
from bvhTools import bvhManipulation
from bvhTools import bvhSlicer

# Read the files
bvh1 = bvhIO.readBvh("test1.bvh")
bvh2 = bvhIO.readBvh("test2.bvh")

# Put each one standing in the center
bvh1 = bvhManipulation.centerSkeletonFeet(bvh1)
bvh2 = bvhManipulation.centerSkeletonFeet(bvh2)

# Merge the together
mergedBvh = bvhSlicer.groupBvhSlices([bvh1, bvh2])

# write the result
bvhIO.writeBvh(mergedBvh, "merged.bvh")
```

### Example 3 (read -> print)
Read a BVH file and print its header and the first 20 frames of motion

```python
from bvhTools import bvhIO

# Read the file
bvh = bvhIO.readBvh("test1.bvh")

# print the header
print(bvh.header)

# print the first 20 frames
for frameIndex in range(20):
    print(bvh.motion.getFrame(frameIndex)) # This also works: print(bvh.motion[frameIndex])
```