# 📋 Writing data to CSV files <!-- {docsify-ignore} -->
The library permits directly writing CSV files from a loaded BVH. There are 2 different types of CSV that can be written.

## Writing positions and rotations to the CSV
This function essentially dumps all the data in the BVH to CSV format, without any modification. The header will contain all the channels of the BVH file as header (of course, without the offset values). i.e. it will contain all position and rotation channels with their respective joint names. Then, in each line, the content of the MOTION part of the BVH will be written.

```python
from bvhTools.bvhIO import writeBvhToCsv

writeBvhToCsv(bvhData, "testBvhFiles/test.csv")
```

## Writing position data to the CSV (FK)
This function calculates the positions of all the joints and end effectors using Forward Kinematics, and writes all the data to a CSV file. As a header, it will write all the joint names, followed by the subscript "_x", "_y" or "_z". Then, for the motion part, it will calculate and then write the absolute position values of the joints in the respective columns.

```python
from bvhTools.bvhIO import writePositionsToCsv

writePositionsToCsv(bvhData, "testBvhFiles/testPosition.csv")
``` 