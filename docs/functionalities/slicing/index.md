# 🔪 BVH slicing <!-- {docsify-ignore} -->
## Getting an individual slice
You can get a specific time slice of the bvh animation with the *getBvhSlice(bvhData, fromFrame, toFrame)* method. This method returns a copy of the original bvhData object, but with modified motion.

```python
from bvhTools.bvhSlicer import getBvhSlice

cutBvh = getBvhSlice(bvhData, 100, 234) # get a new BVHData object, containing just the frames from 100 to 234
```

## Getting many slices
You can also get many time slices of the bvh animation, using the *getBvhSlices(bvhData, fromFrames, toFrames)* method. This returns a list of bvhData objects, each one is a copy of the original bvhData, but modified motion.

```python
from bvhTools.bvhSlicer import getBvhSlices

fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # gets 3 BVHData objects: motion from 0 to 100, 200 to 300, 400 to 500
```

## Grouping multiple slices
You can group multiple BVH files with different motions together, using the *groupBvhSlices(bvhDataList)* to get one BVH with all the motion data. Take into account that all the headers should be the same as this method just appends the motion parts together.

```python
from bvhTools.bvhSlicer import getBvhSlices, groupBvhSlices

fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # first get the slices
finalBvh = groupBvhSlices(cutBvhs) # all the BVHs will be grouped into one BVHData object
```

## Appending motion slices to one bvhData object
You can append multiple BVH files with different motions to a base BVH file, using the *appendBvhSlices(baseBvh, bvhsToAppend)* method.

```python
from bvhTools.bvhSlicer import getBvhSlices, appendBvhSlices

fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # slices
finalBvh = appendBvhSlices(baseBvh, cutBvhs) # append the slices to a base BVH
```