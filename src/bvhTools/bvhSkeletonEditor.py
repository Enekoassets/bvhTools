import copy
import numpy as np
from bvhTools.bvhDataTypes import BVHData

def _addChildrenToList(joint, jointsToDelete):
    jointsToDelete.append(joint.name)
    for child in joint.children: 
        _addChildrenToList(child, jointsToDelete)

def removeLimb(bvhData: BVHData, jointName: str) -> BVHData:
    """Removes a specific limb from a BVH file. It removes the selected
    bone and all its children, and modifies the motion section by
    removing the angle values of the newly removed bones. It returns a
    new BVHData object without the limb.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be modified.
        jointName: str
            The selected bone to remove. All its children will also be removed.
    Returns
    -------
        BVHData
            The new animation with the modified skeleton, without the selected limb.
    """
    bvhDataCopy = copy.deepcopy(bvhData)
    if(jointName == bvhDataCopy.skeleton.root.name):
        print(f"\033[1;33mWARNING\033[0m: you are trying to remove the root joint. You can't do this as this would return an empty BVH. Returning bvh unchanged.")
        return bvhDataCopy

    topJoint = bvhDataCopy.skeleton.getJoint(jointName)
    # create the list with names of joints to delete
    jointsToDelete = []
    jointsToDelete.append(jointName)
    for child in topJoint.children:
        _addChildrenToList(child, jointsToDelete)

    motionColumnsToDelete = []
    # create the list with motion column numbers to delete
    for jointToDeleteName in jointsToDelete:
        joint = bvhDataCopy.skeleton.getJoint(jointToDeleteName)
        offset = 0
        for channel in joint.channels:
            motionColumnsToDelete.append(joint.motionIndex + offset)
            offset += 1

    # iterate over the names in reverse order
    for jointToDeleteName in reversed(jointsToDelete):
        joint = bvhDataCopy.skeleton.getJoint(jointToDeleteName)
        # REMOVE the JOINT FROM it's PARENTS list
        joint.parent.children = [child for child in joint.parent.children if child.name != jointToDeleteName]
        # REMOVE the JOINT itself
        del bvhDataCopy.skeleton.joints[jointToDeleteName]
    
    # REMOVE the necessary part of the MOTION columns
    bvhDataCopy.motion.frames = [[num for i, num in enumerate(frame) if i not in motionColumnsToDelete] for frame in bvhDataCopy.motion.frames]

    # REFRESH the indexes and motionIndexes for all joints and their respective dictionaries
    newSkeleton = bvhDataCopy.skeleton
    newSkeleton.jointIndexes = newSkeleton._buildJointIndexDict(newSkeleton.root, [0])
    newSkeleton.hierarchyIndexes = newSkeleton._buildHierarchyIndexDict(newSkeleton.root, [0])
    return bvhDataCopy
    
def scaleSkeleton(bvhData: BVHData, scaleFactor: float) -> BVHData:
    """Scales the skeleton of a BVH file, by scaling all the bones in
    the skeleton. It updates the OFFSET values of the BVH by scaling
    all the offsets in the skeleton by the selected factor. It does
    not modify the motion section.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be scaled.
        scaleFactor: float
            The scaling factor, multiplied to all bones. Can be any number, but it should not be 0 or less.
    Returns
    -------
        BVHData
            The new animation with the scaled skeleton.
    """
    bvhDataCopy = copy.deepcopy(bvhData)
    if(scaleFactor<=0.0):
        print(f"\033[1;33mWARNING\033[0m: The scale factor has to be greater than 0. Returning bvh unchanged.")
        return bvhDataCopy
    for bone in bvhDataCopy.skeleton.joints.values():
        bone.offset = np.multiply(bone.offset, scaleFactor)
    rootJoint = bvhDataCopy.skeleton.root
    if any(rootJoint.getChannelIndex(axis) == 0 for axis in ["Xposition", "Yposition", "Zposition"]):
        positionSlice = slice(0,3)
    else:
        positionSlice = slice(3,6)
    for frame in bvhDataCopy.motion.frames:
        frame[positionSlice] = np.multiply(frame[positionSlice], scaleFactor)
    return bvhDataCopy