# 💻 Data structures and useful functions <!-- {docsify-ignore} -->
In this section you will find how to access the data from a **bvhData** object (i.e. the structure of a bvhData object). This way it provides a map on how to access different parts of the **bvhData** object. For example, how can I get the frame-time or the number of frames of a **bvhData** object?

Moreover, there are many useful functions that help to easily get and print useful information about a **bvhData** object, such as the hierarchy or the top part or head of the motion array of the file and the dimensions of the array.

## Data structures
### The bvhData object
The bvhData object is a hierarchical object with the following components and their respective data types:
``` 
bvhData 
    ├── header (string)
    ├── skeleton (Skeleton)
    |   |
    |   ├── root (Joint)
    |   ├── joints (Joint[])
    |   ├── jointIndexes (int[])
    |   └── hierarchyIndexes (int[])
    ├── motion (MotionData)
    |   |
    |   ├── numFrames (int)
    |   ├── frameTime (float)
    |   └── frames (float[][])
    ├── skeletonDims (float[])
    └── motionDims (float[])
```
All these attributes can be directly accessed, and there are also some helper functions for ease of access to typical attributes.

##### getSkeletonDim(dimName)
Returns one specific dimension of the skeleton in frame 1 (as usually in motion capture scenarios, the actor stands on a t pose, frame 0 can be the most useful frame to calculate the skeleton dimensions).

The options for *dimName* are "height", "width" and "depth".

**Note**: If it would be necessary to calculate the skeleton dimensions based on a different frame, the [Forward Kinematics](../forwardKinematics/index.md) module permits to calculate the world positions of all joints in any given frame.

##### getFKAtFrame(frame)
This method is also better defined in the [Forward Kinematics](../forwardKinematics/index.md) section. It returns a dictionary containing the world positions of all joints.
##### getFKAtFrameNormalized(frame)
This method is, again, better defined in the [Forward Kinematics](../forwardKinematics/index.md) section. It returns a dictionary containing the world positions of all joints.

### The Skeleton object
The skeleton object contains both the root joint for easy access and all the joint hierarchy, but also the very useful jointIndexes and hierarchyIndexes lists.

#### The jointIndexes dictionary
This dictionary contains, for each joint in the skeleton, where the joint values start in each frame of the motion list. For example, if the root joint ('Hips', for instance) contains 6 channels, the second joint ('LeftLeg') contains 3 and the third joint ('RightLeg') another 3, jointIndexes would look like this:
```
{'Hips': 0, 'LeftUpLeg': 6, 'LeftLeg': 9}
```
This dictionary has been very useful in many situations in which I had to perform specific changes in the motion data. The end_site joints do not contain any channels, so this list will contain the sme index as their parent joint (the real joint that makes use of the rotation values).

This dictionary can also be returned in an abbreviated list form, using the *getJointyIndexesList()* method.
#### The hierarchyIndexes dictionary
The hierarchyIndexes dictionary contains, for each joint in the skeleton, the index of its parent bone. The root, as it will not have a parent, will have index -1. For the above example, supposing that both legs are connected to the hips, the hierarchyIndexes would look like this:
```
{'Hips': -1, 'LeftUpLeg': 0, 'LeftLeg': 0}
```
This dictionary can also be returned in an abbreviated list form, using the *getHierarchyIndexesList()* method.

Finally, there are many helper functions to easily retrieve information from the skeletons, such as getting a Joint object given its name, or the index of a specific joint.

#### *getJoint(jointName)*
Returns a [Joint](#the-joint-object) object given its name.

#### *getJointIndex(jointName)*
Given a joints name, it returns the value in the joint indexes list corresponding to that joint.

#### *getJointIndexesList()*
Returns the jointIndexes dictionary in an abbreviated list format. Example:
```
[0, 6, 9, 12, 15, 18, 18, 21, 24, 27, 30, 30, 33, 36, 39, 42, 45, 45, 48, 51, 54, 57, 57, 60, 63, 66, 69]
```

#### *getHierarchyIndexesList()*
Returns the hierarchyIndexes dictionary in an abbreviated list format. Example:

```
[-1, 0, 1, 2, 3, 4, 0, 6, 7, 8, 9, 0, 11, 12, 13, 14, 15, 13, 17, 18, 19, 20, 13, 22, 23, 24, 25]
```

#### *printSkeleton()*
This method is discussed in more detail [here](#print-skeleton-hierarchy). It basically prints the skeleton hierarchy in the console in a preformatted manner.

### The MotionData object
The MotionData attributes showed in the first hierarchy can be directly accessed. Moreover, there are some helper functions to easily retrieve and modify the frames array. This can also be performed with regular python list slicing.

#### *addFrame(frameData)*
Appends a frame to the end of the frames. The frameData has to have the same dimension as the other frames in order to work properly.

#### *getFrame(frameIndex)*
Returns the frame specified by *frameIndex*. It returns a list of float values.

#### *getFrameSlice(startFrame, endFrame)*
Returns a list of frames, from *startFrame* to *endFrame*. It returns a 2-dimensional list of floats.

#### *getValues(valueIndex)*
Returns a list of values specified by *valueIndex* (i.e. a vertical slice of the motion frames). 

#### *getValuesSlice(startValue, endValue)*
Returns a list of values specified from *startValue* to *endValue* (i.e. a vertical slice of the motion frames). 

#### *getValueAtFrame(valueIndex, frame)*
Returns the float value in column *valueIndex* and row *frame*.

#### *getValueByJointName(jointName)*
Returns all the rotation and position values of a joint for all frames. For example, if a bvh has 1000 frames and the root has 6 channels (Xpos, Ypos, Zpos, Xrot, Yrot, Zrot), *getValueByJointName("root")* will return a 6x1000 array of float values.

#### printHead(headSize = 10, verbose = False)
Useful function that prints a summary of the motion frames information. Explained in more detail [here](#print-head-of-the-motion-data).

### The Joint object
The joint object contains the following attributes with their respective data types, which can be directly accessed.
```
joint 
    ├── name (string)
    ├── index (int)
    ├── offset (float[])
    ├── channels (string[])
    ├── children (Joint[])
    └── parent (Joint)
```
There are also some helpful functions to perform many operations.

#### *getChannelCount()*
Returns the channel count of a specific joint (usually 6 for the root and 3 for any other joint).
#### *getPositionChannelsOrder()*
Returns a string containing the order of the joints position channels. Possible return outcomes: [XYZ, XZY, YXZ, YZX, ZXY, ZYX]. If the joint has no position channels, it will print a warning and return an empty string.

#### *getRotationChannelsOrder()*
Returns a string containing the order of the joints rotation channels. Possible return outcomes: [XYZ, XZY, YXZ, YZX, ZXY, ZYX]. If the joint has no position channels, it will print a warning and return an empty string.

#### *getChannelIndex(channelName)*
Given a channel name, (e.g. "positionY"), it returns the position of the channel in the channel list. If the channel does not exists, it prints a warning and returns -1.
#### *getRotationFromOffset(canonicalRotation)*
Given a canonical rotation (typically (0, 1, 0)), returns the relative rotation that needs to be performed to arrive to the normalized offset of the joint. In other words, it returns the offset in "rotation form".

## Examples of printing bvhData information
Given a bvh file that is loaded in a **bvhData** object called 'bvh', these are some examples on how to access some attributes:
```python
# Printing the name of the root joint
print(bvh.skeleton.root.name)

# Printing the channels of the joint called "Foot.R"
print(bvh.skeleton.getJoint("Foot.R").channels)

# Printing name of the parent of the joint called "Foot.R"
print(bvh.skeleton.getJoint("Foot.R").parent.name)

# Printing the hierarchy index dictionary (indexes of each joint's parent)
print(bvh.skeleton.hierarchyIndexes)

# Printing the jointIndexes (indexes where each joint values start in the motion section)
print(bvh.skeleton.jointIndexes)

# Printing the number of frames and frame time
print(f"Number of frames: {bvh.motion.numFrames} Frame time: {bvh.motion.frameTime}")

# Printing the values of the joint called "Foot.R"
print(bvh.skeleton.getValuesByJointName("Foot.R"))
```

## Useful functions
Apart from directly accessing, modifying and retrieving the data from a *bvhData* object, there are some really useful functions to very rapidly get or print information about a bvh file.
### Print head of the motion data
This prints the top 10 frames of the motion data in a summarized manner, as well as the dimensions of the motion data and frame time.
```python
bvhData.motion.printHead()
```
It also has a *verbose = True* mode to print the entire frames instead of summarizing them. The number of the frames that will be printed can also be changed with the *headSize* option.
This is an example of what the method can print with *headSize = 3*.
```
MOTION DATA
Number of frames: 7184
Number of channels: 69
Frame time: 0.033333
Motion dataframe size: 7184 x 69
HEAD
[-224.689499, 91.882057, -431.625488, 91.911438, 5.797277, 88.877003] ... [-22.244692, 15.926982, -1.200329, 7.052535, 3.369541, -14.328745]
[-224.692001, 91.882378, -431.627106, 91.911438, 5.800984, 88.87701] ... [-22.263239, 15.927381, -1.20032, 7.045754, 3.391573, -14.37221]
[-224.714798, 91.882637, -431.638702, 91.906342, 5.833432, 88.884257] ... [-22.289834, 15.967946, -1.200341, 7.010451, 3.451661, -14.264404]
```
### Print skeleton hierarchy
This prints the skeleton hierarchy to the console in a formatted manner, with colors and a hierarchical structure.
```python
bvhData.skeleton.printSkeleton()
```
It also has a *verbose = True* option, that prints the channels and offset of every joint. The following is an example of what the method prints without the verbose flag:
```
Hips 0:
├── LeftUpLeg 1
│   └── LeftLeg 2
│       └── LeftFoot 3
│           └── LeftToe 4
│               └── LeftToe_EndSite 5:
├── RightUpLeg 6
│   └── RightLeg 7
│       └── RightFoot 8
│           └── RightToe 9
│               └── RightToe_EndSite 10
└── Spine 11
    └── Spine1 12
        └── Spine2 13
            ├── Neck 14
            │   └── Head 15
            │       └── Head_EndSite 16
            ├── LeftShoulder 17
            │   └── LeftArm 18
            │       └── LeftForeArm 19
            │           └── LeftHand 20
            │               └── LeftHand_EndSite 21
            └── RightShoulder 22
                └── RightArm 23
                    └── RightForeArm 24
                        └── RightHand 25
                            └── RightHand_EndSite 26
```
### Get skeleton hierarchy as dict
This has been already discussed in the [skeleton](#the-skeleton-object) section. However, as it has been proven useful, it is repeated here.

You can retrieve a dictionary object that contains all the joint names as keys and their parents indexes as values. This is one example of the data that it returns:
```
{'Hips': -1, 'LeftUpLeg': 0, 'LeftLeg': 1, 'LeftFoot': 2, 'LeftToe': 3, 'LeftToe_EndSite': 4, 'RightUpLeg': 0, 'RightLeg': 6, 'RightFoot': 7, 'RightToe': 8, 'RightToe_EndSite': 9, 'Spine': 0, 'Spine1': 11, 'Spine2': 12, 'Neck': 13, 'Head': 14, 'Head_EndSite': 15, 'LeftShoulder': 13, 'LeftArm': 17, 'LeftForeArm': 18, 'LeftHand': 19, 'LeftHand_EndSite': 20, 'RightShoulder': 13, 'RightArm': 22, 'RightForeArm': 23, 'RightHand': 24, 'RightHand_EndSite': 25}
```
### Get simplified skeleton hierarchy as list
This has also been discussed in the [skeleton](#the-skeleton-object) section. You can retrieve a simplified version of the skeleton hierarchy as a list. It has proven to be very useful for many situations. This is the same example as above:
```
[-1, 0, 1, 2, 3, 4, 0, 6, 7, 8, 9, 0, 11, 12, 13, 14, 15, 13, 17, 18, 19, 20, 13, 22, 23, 24, 25]
```