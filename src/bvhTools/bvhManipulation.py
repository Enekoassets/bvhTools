import copy
from scipy.spatial.transform import Rotation as R
import numpy as np

def centerSkeletonRoot(bvhData, fkFrame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonFeet(bvhData, leftFootName = "LeftFoot", rightFootName = "RightFoot", fkFrame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    if(leftFootName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Left foot name ({leftFootName}) not found in skeleton")
    if(rightFootName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Right foot name ({rightFootName}) not found in skeleton")
    avgFootHeight = (bvhDataCopy.getFKAtFrame(fkFrame)[leftFootName][1][1] + bvhDataCopy.getFKAtFrame(fkFrame)[rightFootName][1][1]) / 2
    avgRootHeight = bvhDataCopy.getFKAtFrame(fkFrame)[bvhDataCopy.skeleton.root.name][1][1]
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]) + (avgRootHeight - avgFootHeight), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonXZ(bvhData, fkFrame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonAroundJoint(bvhData, jointName, fkFrame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    if(jointName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Selected joint ({jointName}) not found in skeleton")
    
    forwardFrame = bvhDataCopy.getFKAtFrame(fkFrame)
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    jointOffsets = forwardFrame[jointName][1] - forwardFrame[bvhDataCopy.skeleton.root.name][1]
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]) - jointOffsets[0], -float(frame[rootIndex + 1]) - jointOffsets[1], -float(frame[rootIndex + 2]) - jointOffsets[2]]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def standSkeletonOnFloor(bvhData, leftFootName = "LeftFoot", rightFootName = "RightFoot", fkFrame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    if(leftFootName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Left foot name ({leftFootName}) not found in skeleton")
    if(rightFootName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Right foot name ({rightFootName}) not found in skeleton")
    avgFootHeight = (bvhDataCopy.getFKAtFrame(fkFrame)[leftFootName][1][1] + bvhDataCopy.getFKAtFrame(fkFrame)[rightFootName][1][1]) / 2
    avgRootHeight = bvhDataCopy.getFKAtFrame(fkFrame)[bvhDataCopy.skeleton.root.name][1][1]
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offset = -float(frame[rootIndex + 1]) + (avgRootHeight - avgFootHeight)
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex+1] += offset

    return bvhDataCopy

def rotateSkeletonLocal(bvhData, angle, fkFrame=0):
    if(len(angle) != 3):
        raise Exception("angle must be a list of length 3")
    bvhDataCopy = copy.deepcopy(bvhData)
    rotation = R.from_euler('XYZ', [angle[0], angle[1], angle[2]], degrees=True)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    originPoint = bvhDataCopy.getFKAtFrame(fkFrame)[bvhDataCopy.skeleton.root.name][1]
    rootChannelOrder = bvhData.skeleton.root.getRotationChannelsOrder()
    for frameIndex, frame in enumerate(bvhDataCopy.motion.frames):
        fkFrameRootPos = bvhDataCopy.getFKAtFrame(frameIndex)[bvhDataCopy.skeleton.root.name][1]
        newPos = [x - y for x,y in zip(fkFrameRootPos, originPoint)]
        newPos = rotation.apply(newPos)
        newPos = [x + y for x,y in zip(newPos, originPoint)]
        baseRotation = R.from_euler(rootChannelOrder, frame[rootIndex+3:rootIndex+6], degrees=True)
        newRotation = rotation * baseRotation
        frame[rootIndex:rootIndex+3] = newPos
        frame[rootIndex+3:rootIndex+6] = newRotation.as_euler(rootChannelOrder, degrees=True)
    return bvhDataCopy

def rotateSkeletonWorld(bvhData, angle):
    if(len(angle) != 3):
        raise Exception("angle must be a list of length 3")
    bvhDataCopy = copy.deepcopy(bvhData)
    rotation = R.from_euler('XYZ', [angle[0], angle[1], angle[2]], degrees=True)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    rootChannelOrder = bvhData.skeleton.root.getRotationChannelsOrder()
    for frameIndex, frame in enumerate(bvhDataCopy.motion.frames):
        fkFrameRootPos = bvhDataCopy.getFKAtFrame(frameIndex)[bvhDataCopy.skeleton.root.name][1]
        newPos = rotation.apply(fkFrameRootPos)
        baseRotation = R.from_euler(rootChannelOrder, frame[rootIndex+3:rootIndex+6], degrees=True)
        newRotation = rotation * baseRotation
        frame[rootIndex:rootIndex+3] = newPos
        frame[rootIndex+3:rootIndex+6] = newRotation.as_euler(rootChannelOrder, degrees=True)
    return bvhDataCopy

def moveSkeleton(bvhData, offsets):
    if(len(offsets) != 3):
        raise Exception("offsets must be a list of length 3")
    bvhDataCopy = copy.deepcopy(bvhData)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def mirrorSkeleton(bvhData, flipAxis, jointPairs):
    if (flipAxis != "X" and flipAxis != "Y" and flipAxis != "Z" and flipAxis != "x" and flipAxis != "y" and flipAxis != "z"):
        print(f"\033[1;33mWARNING\033[0m: flipAxis needs to be X, Y or Z. Returning original BVH.")
        return bvhData

    bvhDataCopy = copy.deepcopy(bvhData)
    if(flipAxis == "X" or flipAxis == "x"):
        mirror_rot = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
    elif(flipAxis == "Y" or flipAxis == "y"):
        mirror_rot = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
    elif(flipAxis == "Z" or flipAxis == "z"):
        mirror_rot = np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]])

    for joint in bvhData.skeleton.joints.values():
        if("EndSite" in joint.name):
            continue
        jointIndex = bvhData.skeleton.getJointIndex(joint.name)
        rotChannelsOrder = joint.getRotationChannelsOrder()
        for frame in bvhDataCopy.motion.frames:
            if(joint.getChannelCount() == 3):
                rot = R.from_euler(rotChannelsOrder, frame[jointIndex:jointIndex+3], degrees=True)
                newRot = R.as_euler(R.from_matrix(mirror_rot @ rot.as_matrix() @ mirror_rot), rotChannelsOrder, degrees=True)
                frame[jointIndex:jointIndex+3] = [newRot[0], newRot[1], newRot[2]]
            else:
                if(flipAxis == "X" or flipAxis == "x"):
                    posFlip = joint.getChannelIndex("Xposition")
                if(flipAxis == "Y" or flipAxis == "y"):
                    posFlip = joint.getChannelIndex("Yposition")
                if(flipAxis == "Z" or flipAxis == "z"):
                    posFlip = joint.getChannelIndex("Zposition")

                if(posFlip == 0 or posFlip == 1 or posFlip == 2):
                    pos = np.asarray(frame[jointIndex:jointIndex+3]) * np.asarray([-1 if posFlip == 0 else 1, -1 if posFlip == 1 else 1, -1 if posFlip == 2 else 1])
                    rot = R.from_euler(rotChannelsOrder, frame[jointIndex+3:jointIndex+6], degrees=True)
                    newRot = R.as_euler(R.from_matrix(mirror_rot @ rot.as_matrix() @ mirror_rot), rotChannelsOrder, degrees=True)
                    frame[jointIndex:jointIndex+6] = [pos[0], pos[1], pos[2], newRot[0], newRot[1], newRot[2]]
                else:
                    pos = np.asarray(frame[jointIndex:jointIndex+3]) * np.asarray([-1 if posFlip == 3 else 1, -1 if posFlip == 4 else 1, -1 if posFlip == 5 else 1])
                    rot = R.from_euler(rotChannelsOrder, frame[jointIndex+3:jointIndex+6], degrees=True)
                    newRot = R.as_euler(R.from_matrix(mirror_rot @ rot.as_matrix() @ mirror_rot), rotChannelsOrder, degrees=True)
                    frame[jointIndex:jointIndex+6] = [newRot[0], newRot[1], newRot[2], pos[0], pos[1], pos[2]]
    
    bvhDataCopy.motion.frames = np.asarray(bvhDataCopy.motion.frames)
    for jointPair in jointPairs:
        joint1 = jointPair[0]
        joint2 = jointPair[1]
        jointIndex1 = bvhData.skeleton.getJointIndex(joint1)
        jointIndex2 = bvhData.skeleton.getJointIndex(joint2)
        jointChannelCount1 = bvhData.skeleton.getJoint(joint1).getChannelCount()
        jointChannelCount2 = bvhData.skeleton.getJoint(joint2).getChannelCount()

        if(jointChannelCount1 != jointChannelCount2):
            print(f"\033[1;33mWARNING\033[0m: joint pair {joint1}, {joint2} needs to have the same number of channels. Returning original BVH.")
            return bvhData
        
        block1 = copy.deepcopy(bvhDataCopy.motion.frames[:, jointIndex1:jointIndex1+jointChannelCount1])
        block2 = copy.deepcopy(bvhDataCopy.motion.frames[:, jointIndex2:jointIndex2+jointChannelCount2])

        bvhDataCopy.motion.frames[:, jointIndex1:jointIndex1+jointChannelCount1] = block2
        bvhDataCopy.motion.frames[:, jointIndex2:jointIndex2+jointChannelCount2] = block1
    bvhDataCopy.motion.frames = bvhDataCopy.motion.frames.tolist()
    return bvhDataCopy