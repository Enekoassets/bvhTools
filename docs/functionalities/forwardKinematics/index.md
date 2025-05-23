# 🏃 Forward Kinematics <!-- {docsify-ignore} -->
The forward kinematics module returns a **Dict** object containing the global positions and rotations of the skeleton in a specific frame.

We can directly compute the forward kinematics calling the *getFKAtFrame(frameNumber)* function over any bvhData object.

```python
# Supposing we loaded the bvh file into bvhData
fk = bvhData.getFKAtFrame(42)
print(fk)
# Output:
'''
{'Hips':
    (array([[-0.02719991, -0.02534224,  0.99930873], [ 0.99330309,  0.11161069,  0.02986686], [-0.11229043,  0.99342882,  0.02213672]]), 
    [-225.111603, 91.898651, -432.551514]), 
'LeftUpLeg':
    (array([[ 0.06344131,  0.01758197, -0.99783068], [-0.99795395,  0.00907691, -0.06328921], [ 0.00794447,  0.99980422,  0.01812185]]), 
    array([-214.62028169,   92.52381984, -430.48398993])),
'LeftLeg':
    (array([[ 0.03644904,  0.17293715, -0.9842582 ], [-0.98920051, -0.13367165, -0.06011858], [-0.14196415,  0.97581998,  0.16619731]]), 
    array([-211.86059535,   49.11282203, -430.13844715])),
    ...))}
'''
```
The output is a dictionary, which has the names of the joints and end sites as keys, and contains both global positions and global rotations as values.

For example, we can just get the position of the "RightLeg" as so:
```python 
print(fk["RightLeg"][1])
# Output:
# [-239.19694216   48.56157723 -432.49042668]
```

We can also get all the positions/rotations as a list:
```python
print([value[0] for value in fk.values()]) # returns a list of all rotations
print([value[1] for value in fk.values()]) # returns a list of all positions
```
## Getting normalized positions

If you need normalized positions (the rotations remain the same) you should use *getFkAtFrameNormalized(frameNumber, dimension = "height")*. The normalization dimension options are ["height", "width", "depth"].

```python
fk = bvhData.getFKAtFrameNormalized(42)
# Now, the normalized position for RightLeg is different than before.
print(fk["RightLeg"][1])
# Output:
# [-1.63358778  0.33164972 -2.95367937]
```
**Note:** Getting normalized position does **not** mean that all values will be between 0 and 1. As the normalization is done by dividing all the values with the height, width or depth, global positions can still have any value. However, this can be useful to get many skeletons in different bvh files to have the same height, for example.

This allows, for instance, to compare different sized skeletons' joint velocities.