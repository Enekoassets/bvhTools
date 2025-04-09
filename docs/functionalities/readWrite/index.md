# 📖 Reading and ✏️ writing BVH files <!-- {docsify-ignore} -->
## 📖 Reading BVH files 

To load a BVH file to later use it inside Python, just provide the file path, and the method will return a **BVHData** object.
```python
from bvhIO import readBvhFile

bvhData = readBvhFile("test.bvh")
```

## ✏️ Writing BVH files

To write the content of a **BVHData** object, use the provide the **BVHData** object, the output path and optionally, the number of decimals for the motion (default = 6).
```python
from bvhIO import writeBvhFile

writeBvhFile(bvhData, "test_new.bvh")
```
This has many uses. For example, you can load a BVH file, make modifications to the **BVHData** object and then write it to a new BVH file, without the need of doing anything else. For example, the following code snippet does this: it loads a BVH, it centers it on its feet starting on frame 100, it takes a motion slice from frame 100 to 200 and then writes the new centered and cut BVH to a new file.

```python
from bvhIO import readBvhFile, writeBvhFile
from bvhManipulation import centerSkeletonFeet
from bvhSlicing import getBvhSlice

bvhData = readBvhFile("test.bvh") # read the data
centeredBvh = centerSkeletonFeet(bvhData, 100) # put it standing on the center on frame 100
centeredBvhSlice = getBvhSlice(centeredBvh, 100, 200) # get the motion slice from frame 100 to 200
writeBvhFile(centeredBvhSlice, "test_centered_cut.bvh") # write the new file
```