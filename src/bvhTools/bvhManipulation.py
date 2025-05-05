import copy
from scipy.spatial.transform import Rotation as R

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