# 📋 Writing data to CSV files <!-- {docsify-ignore} -->
The library permits directly writing CSV files from a loaded BVH. There are currently 2 different types of CSV that can be written.

## Writing positions and rotations to the CSV
This function essentially dumps all the data in the BVH to CSV format, without any modification. The header will contain all the channels of the BVH file as header (of course, without the offset values). i.e. it will contain all position and rotation channels with their respective joint names. Then, in each line, the content of the MOTION part of the BVH will be written.

```python
from bvhTools.bvhIO import writeBvhToCsv

writeBvhToCsv(bvhData, "testBvhFiles/test.csv")
```

This line would write a "test.csv" file, containing something like the following:

```
Hips_Xposition,Hips_Yposition,Hips_Zposition,Hips_Zrotation,Hips_Yrotation,Hips_Xrotation,LeftUpLeg_Zrotation,LeftUpLeg_Yrotation,LeftUpLeg_Xrotation,...,RightHand_Zrotation,RightHand_Yrotation,RightHand_Xrotation,
193.614899,90.217430,358.243408,90.722131,-0.039963,80.816198,169.431517,-5.014797,164.945489,...,-1.370320,2.343926,11.519194,-11.883262
193.622101,90.232063,358.219391,90.691668,-0.086480,80.761994,169.396642,-5.052796,164.886463,...,-1.367081,2.358585,11.511749,-11.787184
193.640396,90.268059,358.167297,90.608811,-0.200569,80.649241,169.317903,-5.147205,164.802260,...,-1.358694,2.374591,11.400060,-11.883140
193.657303,90.314194,358.120087,90.546677,-0.308917,80.559479,169.287127,-5.203993,164.821494,...,-1.356723,2.381432,11.372279,-11.892400
...
```

## Writing position data to the CSV (FK)
This function calculates the positions of all the joints and end effectors using Forward Kinematics, and writes all the data to a CSV file. As a header, it will write all the joint names, followed by the subscript "_x", "_y" or "_z". Then, for the motion part, it will calculate and then write the absolute position values of the joints in the respective columns.

```python
from bvhTools.bvhIO import writePositionsToCsv

writePositionsToCsv(bvhData, "testBvhFiles/testPosition.csv")
``` 
This line would write a "testPosition.csv" file, containing something like the following:

```
Hips_x,Hips_y,Hips_z,LeftUpLeg_x,LeftUpLeg_y,LeftUpLeg_z,LeftLeg_x,LeftLeg_y,LeftLeg_z,...,RightHand_EndSite_x,RightHand_EndSite_y,RightHand_EndSite_z
193.614899, 90.217430, 358.243408,203.729600, 90.445930, 361.761049,206.751585, 47.876350, 370.184141,...,121.788415, 146.195613, 366.969226
193.622101, 90.232063, 358.219391,203.733624, 90.452274, 361.746682,206.749249, 47.881751, 370.167285,...,121.791191, 146.187852, 366.942054
193.640396, 90.268059, 358.167297,203.745342, 90.466481, 361.714671,206.743821, 47.892433, 370.123571,...,121.810296, 146.191131, 366.886719
193.657303, 90.314194, 358.120087,203.756954, 90.494811, 361.683456,206.734650, 47.909917, 370.044685,...,121.838642, 146.193285, 366.839774
...
```