## 🔪 BVH slicing
You can get a specific time slice of the bvh animation with the bvhSlicer class.

```python
cutBvh = getBvhSlice(bvhData, 100, 234) # get a new BVHData object, contianing just the frames from 100 to 234
```

You can also get many time slices of the bvh animation, each one in a new BVHData object.

```python
fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # gets 3 BVHData objects: motion from 0 to 100, 200 to 300, 400 to 500
```

You can group multiple BVH files with different motions together, to get one BVH with all the motion data. Take into account that all the headers should be the same as this method just appends the motion parts together.

```python
fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # first get the slices
finalBvh = groupBvhSlices(cutBvhs) # all the BVHs will be grouped into one BVHData object
```

You can append multiple BVH files with different motions to a base BVH file.

```python
fromFrames = [0, 200, 400]
toFrames = [100, 300, 500]
cutBvhs = getBvhSlices(bvhData, fromFrames, toFrames) # slices
finalBvh = appendBvhSlices(baseBvh, cutBvhs) # append the slices to a base BVH
```