# 🔪 BVH slicing <!-- {docsify-ignore} -->
The **bvhSlicer** class contains functions to easily take parts of BVH animations or put together different animation data into one single **bvhData** object. All methods take a **bvhData** object as input and return another **bvhData** object or list, so no original objects are destroyed or changed.

## Getting an individual slice
With the *getBvhSlice(bvhData, fromFrame, toFrame)* method, you can get a specific time slice of the bvh animation. This method returns a copy of the original bvhData object, but with modified motion.

```python
from bvhTools.bvhSlicer import getBvhSlice

cutBvh = getBvhSlice(bvhData, 100, 234) # get a new BVHData object, containing just the frames from 100 to 234
```

## Getting many slices
With the *getBvhSlices(bvhData, fromFrames, toFrames)* method, you can get many time slices of the bvh animation. The method returns a list of bvhData objects, each one is a copy of the original bvhData, but with modified motion.

```python
from bvhTools.bvhSlicer import getBvhSlices

fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # gets 3 BVHData objects: motion from 0 to 100, 200 to 300, 400 to 500
```

## Grouping multiple slices
With the *groupBvhSlices(bvhDataList)* method, you can group multiple BVH files with different motions together, to get one BVH with all the motion data. Take into account that all the headers should be the same as this method just appends the motion parts together.

```python
from bvhTools.bvhSlicer import getBvhSlices, groupBvhSlices

fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # first get the slices
finalBvh = groupBvhSlices(cutBvhs) # all the BVHs will be grouped into one BVHData object
```

## Appending motion slices to one bvhData object
With the *appendBvhSlices(baseBvh, bvhsToAppend)* method, you can append multiple BVH files with different motions to a base BVH file.

```python
from bvhTools.bvhSlicer import getBvhSlices, appendBvhSlices

fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # slices
finalBvh = appendBvhSlices(baseBvh, cutBvhs) # append the slices to a base BVH
```