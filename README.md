# bvhTools
This repository contains a Python library to work with BVH (Biovision Hierarchy) files. It is in development and it currently contains I/O methods to read and write BVH files and methods to edit animations.

**Index**
- [bvhTools](#bvhtools)
  - [Loading BVH files](#loading-bvh-files)
  - [Writing BVH files](#writing-bvh-files)
  - [The BVHData object](#the-bvhdata-object)
    - [The Motion Data object](#the-motion-data-object)
    - [The Skeleton Object](#the-skeleton-object)
  - [Forward Kinematics](#forward-kinematics)
  - [BVH manipulation](#bvh-manipulation)
    - [Centering the skeleton root](#centering-the-skeleton-root)
    - [Centering the skeleton feet](#centering-the-skeleton-feet)
    - [Centering the skeleton around a specific joint](#centering-the-skeleton-around-a-specific-joint)
  - [BVH slicing](#bvh-slicing)
  - [BVH viewer](#bvh-viewer)
  - [Writing data to CSV files](#writing-data-to-csv-files)
    - [Writing positions and rotations to the CSV](#writing-positions-and-rotations-to-the-csv)
    - [Writing position data to the CSV (FK)](#writing-position-data-to-the-csv-fk)

<a id="loadBVH"></a>
## Loading BVH files
To load a BVH file to later use it inside Python, just provide the file path, and the method will return a **BVHData** object.
```python
from bvhIO import readBvhFile

bvhData = readBvhFile("test.bvh")
```

<a id="writeBVH"></a>
## Writing BVH files
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

<a id="methodsBVH"></a>
## The BVHData object
The **BVHData** object contains the information of the entire BVH file in an accessible way. It has the following structure, and you can get all the necessary attributes:

```
BVHData
└─── header
└─── skeleton
└─── motion
└─── skeleton_dims (used for normalization purposes)
```
### The Motion Data object
```
MotionData
└─── num_frames
└─── frame_time
└─── frames
```
### The Skeleton Object
```
Skeleton
└─── root
└─── joints
└─── joint_indexes
```

<a id="forwardKinematics"></a>
## Forward Kinematics
The forward kinematics module returns a **Dict** object containing the global positions and rotations of the skeleton in a specific frame.
```python
fk = bvhData.getFKAtFrame(42)
```
It can also return the normalized FK positions (the rotations remain the same). The normalization dimension is the height of the skeleton by default, but the options are ["height", "width", "depth"].
 ```python
fk = bvhData.getFKAtFrameNormalized(42)
```
<a id="BVH Manipulation"></a>
## BVH manipulation
### Centering the skeleton root
To center the skeleton root and set its position to (0,0,0) on a specific frame, provide the number of the frame you want the root to be centered in. This means that in the frame that you provide, the root will be in (0,0,0) and all the animation will be shifted accordingly. Useful to center any animation in frame 0 (Default frame = 0).
```python
centeredBvhRoot = centerSkeletonRoot(bvhData)
centeredBvhRoot = centerSkeletonRoot(bvhData, 42) # center at frame 42
```
### Centering the skeleton feet
This centers the whole skeleton in the X and Z axes for a specific frame, and it also centers it on the Y axis, to put the feet on Y = 0. In other words, the skeleton will be standing on (0,0,0) on the provided frame. It uses the two feet to calculate the average Y height, so the names of both feet joints are needed. (Default leftFootName = "LeftFoot", rightFootName = "RightFoot"). Useful to center the feet of any animation in frame 0 (Default frame = 0).
```python
centeredBvhRoot = centerSkeletonFeet(bvhData)
centeredBvhRoot = centerSkeletonFeet(bvhData, leftFootName = "lFoot", rightFootName = "rFoot", frame = 42) # center at frame 42 using custom left and right foot names
```
### Centering the skeleton around a specific joint
This centers the skeleton around a specific joint at a specific frame. In short, the selected joint will be on (0,0,0) at the specified frame.
```python
centeredBvh = centerSkeletonAroundJoint(bvhData, "RightArm", 0) # The RightArm joint will be at (0,0,0) at frame 0
```

<a id="BVH Slicing"></a>
## BVH slicing
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

<a id="BVH viewer"></a>
## BVH viewer
A simple BVH viewer is implemented using matplotlib for fast viewing. It contains a basic play/pause button and forward/back buttons to pass frames one by one. It also permits to jump to specific frames and to change the speed of time for faster/slower playback.
```python
from bvhVisualizerSimple import showBvhAnimation

showBvhAnimation(bvhData)
```

<a id="CSV writing"></a>
## Writing data to CSV files
The library permits directly writing CSV files from a loaded BVH. There are 2 different types of CSV that can be written.

### Writing positions and rotations to the CSV
This function essentially dumps all the data in the BVH to CSV format, without any modification. The header will contain all the channels of the BVH file as header (of course, without the offset values). i.e. it will contain all position and rotation channels with their respective joint names. Then, in each line, the content of the MOTION part of the BVH will be written.

```python
from bvhIO import writeBvhToCsv

writeBvhToCsv(bvhData, "testBvhFiles/test.csv")
```

### Writing position data to the CSV (FK)
This function calculates the positions of all the joints and end effectors using Forward Kinematics, and writes all the data to a CSV file. As a header, it will write all the joint names, followed by the subscript "_x", "_y" or "_z". Then, for the motion part, it will calculate and then write the absolute position values of the joints in the respective columns.

```python
from bvhIO import writePositionsToCsv

writePositionsToCsv(bvhData, "testBvhFiles/testPosition.csv")
```
