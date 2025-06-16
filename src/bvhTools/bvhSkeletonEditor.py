import copy
import numpy as np

def addChildrenToList(joint, jointsToDelete):
    jointsToDelete.append(joint.name)
    for child in joint.children: 
        addChildrenToList(child, jointsToDelete)

def removeLimb(bvhData, jointName):
    bvhDataCopy = copy.deepcopy(bvhData)
    if(jointName == bvhDataCopy.skeleton.root.name):
        print(f"\033[1;33mWARNING\033[0m: you are trying to remove the root joint. You can't do this as this would return an empty BVH. Returning bvh unchanged.")
        return bvhDataCopy

    topJoint = bvhDataCopy.skeleton.getJoint(jointName)
    # create the list with names of joints to delete
    jointsToDelete = []
    jointsToDelete.append(jointName)
    for child in topJoint.children:
        addChildrenToList(child, jointsToDelete)

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
    newSkeleton.jointIndexes = newSkeleton.buildJointIndexDict(newSkeleton.root, [0])
    newSkeleton.hierarchyIndexes = newSkeleton.buildHierarchyIndexDict(newSkeleton.root, [0])
    return bvhDataCopy
    
def scaleSkeleton(bvhData, scaleFactor):
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