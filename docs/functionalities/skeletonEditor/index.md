# 💀 Skeleton editor <!-- {docsify-ignore} -->
The skeleton editor enables to modify the original skeleton in the BVH file. Currently, by using the *bvhSkeletonEditor* class, you can delete parts of the BVH skeleton recursively by choosing a bone.

## 🦴 Removing limbs (or any bone and all it's children)
With the *removeLimb(bvhData, limbName)* method you can choose a bone (it can't be the root bone), and remove it and all it's children **both** from the **hierarchy and** from the **motion data** automatically. All the other motion data is going to be left untouched.

```python
from bvhTools.bvhSkeletonEditor import removeLimb

bvhDataNoLeg = removeLimb(bvhData, "LeftLeg")
```
Imagine that for the example above, the old **bvhData** object had a hierarchy in which the **leftLeg** bone contained one child called **leftFoot** and this bone had another child called **leftToe** which was an **End Site** itself.

Then, for this example, the bvhData skeleton would contain 3 less bones after removing the **leftLeg** and the bvhData motion would contain 9 less rotation columns (3 rotations * 3 bones).

**Note:** After using this method, the internal hierarchy of the bones is going to be automatically updated. The **index** and **motionIndex** values of all **Joint** objects will be updated. The **jointIndexes** and **hierarchyIndexes** dictionaries of the **Skeleton** object will also be automatically updated.

## 📏 Scaling the skeleton

With the *scaleSkeleton(bvhData, scaleFactor)* function you can scale the entire skeleton by a factor (the factor has to be greater than 0). Internally, this method will scale the offset values of each bone, as well as the position coordinates of the root bone in all the motion frames.

The method will return a new **bvhData** object, with the changed offset and motion values, therefore containing a scaled version of the BVH.

```python
from bvhTools.bvhSkeletonEditor import scaleSkeleton

bvhDataScaled = scaleSkeleton(bvhData, 0.8)
```