import numpy as np
from scipy.spatial.transform import Rotation as R

def getSpeedVectors(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 2:
        return np.empty((0,0))

    allSpeeds = []
    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff
    lastFk = np.array([value[1] for value in bvh.getFKAtFrame(0).values()])
    for frameIndex in range(1, bvh.motion.numFrames):
        currFk = np.array([value[1] for value in bvh.getFKAtFrame(frameIndex).values()])
        speeds = (currFk - lastFk) / frameTime
        allSpeeds.append(speeds)
        lastFk = currFk

    return allSpeeds

def getAccelerationVectors(bvh, timeDiff = -1):
    allSpeeds = getSpeeds(bvh, timeDiff)

    if len(allSpeeds) < 2:
        return np.empty((0,0))

    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff

    allAccelerations = []
    lastSpeed = allSpeeds[0]
    for frameIndex in range(1, len(allSpeeds)):
        currSpeed = allSpeeds[frameIndex]
        accelerations = (currSpeed - lastSpeed)/frameTime
        allAccelerations.append(accelerations)
        lastSpeed = currSpeed

    return allAccelerations

def getJerkVectors(bvh, timeDiff = -1):
    allAccelerations = getAccelerations(bvh, timeDiff)

    if len(allAccelerations) < 2:
        return np.empty((0,0))

    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff

    alljerks = []
    lastAcceleration = allAccelerations[0]
    for frameIndex in range(1, len(allAccelerations)):
        currAcceleration = allAccelerations[frameIndex]
        jerks = (currAcceleration - lastAcceleration)/frameTime
        alljerks.append(jerks)
        lastAcceleration = currAcceleration

    return alljerks 

def getSpeeds(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 2:
        return np.empty((0,0))
    
    allSpeeds = getSpeedVectors(bvh, timeDiff)
    return np.linalg.norm(allSpeeds, axis = 2)

def getAccelerations(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 3:
        return np.empty((0,0))
    allAccelerations = getAccelerationVectors(bvh, timeDiff)
    return np.linalg.norm(allAccelerations, axis = 2)

def getJerks(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 4:
        return np.empty((0,0))
    allJerks = getJerkVectors(bvh, timeDiff)
    return np.linalg.norm(allJerks, axis = 2)

def getAvgSpeeds(bvh, timeDiff = -1, mode = "perJoint"):
    axis = 0 if mode == "perJoint" else 1
    if bvh.motion.numFrames < 2:
        return np.empty(0)

    allSpeeds = getSpeeds(bvh, timeDiff)
    return np.mean(allSpeeds, axis = axis)

def getAvgAccelerations(bvh, timeDiff = -1, mode = "perJoint"):
    axis = 0 if mode == "perJoint" else 1
    if bvh.motion.numFrames < 3:
        return np.empty(0)

    allAccelerations = getAccelerations(bvh, timeDiff)
    return np.mean(allAccelerations, axis = axis)

def getAvgJerks(bvh, timeDiff = -1, mode = "perJoint"):
    axis = 0 if mode == "perJoint" else 1
    if bvh.motion.numFrames < 4:
        return np.empty(0)

    allJerks = getJerks(bvh, timeDiff)
    return np.mean(allJerks, axis = axis)

def getAngularSpeedVectors(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 2:
        return np.empty((0,0,0))
    allFrameRotations = []
    allSpeeds = []
    rotations = []
    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff

    for frameIndex in range(bvh.motion.numFrames):
        for jointName in bvh.skeleton.joints:
            if("EndSite" in jointName):
                continue
            joint = bvh.skeleton.getJoint(jointName)
            motionIndex = joint.motionIndex
            if joint.getChannelCount() == 6 and (joint.channels[0] == "Xrotation" or joint.channels[0] == "Yrotation" or joint.channels[0] == "Zrotation"):
                motionIndex += 3
            rotations.append(R.from_euler(joint.getRotationChannelsOrder(), bvh.motion.frames[frameIndex][motionIndex:motionIndex+3], degrees=True))
        allFrameRotations.append(rotations)
        rotations = []
    allFrameRotations = np.asarray(allFrameRotations)
    for frameIndex in range(1, len(allFrameRotations)):
        allSpeeds.append([(r2 * r1.inv()).as_rotvec()/frameTime for r1, r2 in zip(allFrameRotations[frameIndex - 1], allFrameRotations[frameIndex])])

    return np.asarray(allSpeeds)

def getAngularAccelerationVectors(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 3:
        return np.empty((0,0,0))
    allSpeeds = getAngularSpeedVectors(bvh, timeDiff)
    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff
    allAccelerations = []
    for frameIndex in range(1, len(allSpeeds)):
        allAccelerations.append([(r2 - r1)/frameTime for r1, r2 in zip(allSpeeds[frameIndex - 1], allSpeeds[frameIndex])])

    return np.asarray(allAccelerations)

def getAngularJerkVectors(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 4:
        return np.empty((0,0,0))
    allAccelerations = getAngularAccelerationVectors(bvh, timeDiff)
    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff
    allJerks = []
    for frameIndex in range(1, len(allAccelerations)):
        allJerks.append([(r2 - r1)/frameTime for r1, r2 in zip(allAccelerations[frameIndex - 1], allAccelerations[frameIndex])])

    return np.asarray(allJerks)

def getAngularSpeeds(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 2:
        return np.empty((0,0))
    allSpeeds = getAngularSpeedVectors(bvh, timeDiff)
    return np.linalg.norm(allSpeeds, axis = 2)

def getAngularAccelerations(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 3:
        return np.empty((0,0))
    allAccelerations = getAngularAccelerationVectors(bvh, timeDiff)
    return np.linalg.norm(allAccelerations, axis = 2)

def getAngularJerks(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 4:
        return np.empty((0,0))
    allJerks = getAngularJerkVectors(bvh, timeDiff)
    return np.linalg.norm(allJerks, axis = 2)

def getAvgAngularSpeeds(bvh, timeDiff = -1, mode = "perJoint"):
    axis = 0 if mode == "perJoint" else 1
    if bvh.motion.numFrames < 2:
        return np.empty(0)

    allSpeeds = getAngularSpeeds(bvh, timeDiff)
    return np.mean(allSpeeds, axis = axis)

def getAvgAngularAccelerations(bvh, timeDiff = -1, mode = "perJoint"):
    axis = 0 if mode == "perJoint" else 1
    if bvh.motion.numFrames < 3:
        return np.empty(0)

    allAccelerations = getAngularAccelerations(bvh, timeDiff)
    return np.mean(allAccelerations, axis = axis)

def getAvgAngularJerks(bvh, timeDiff = -1, mode = "perJoint"):
    axis = 0 if mode == "perJoint" else 1
    if bvh.motion.numFrames < 4:
        return np.empty(0)

    allJerks = getAngularJerks(bvh, timeDiff)
    return np.mean(allJerks, axis = axis)

def getFootContactsSpeedMethod(bvh, footNames = ["LeftFoot", "RightFoot"], threshold = 0.1, timeDiff = -1):
    speedsPerFrame = getSpeeds(bvh, timeDiff)
    # duplicate first speed to match number of frames
    speedsPerFrame = np.insert(speedsPerFrame, 0, [speedsPerFrame[0]], axis = 0)
    jointNames = [joint for joint in bvh.skeleton.joints]
    footIndexes = [jointNames.index(footName) for footName in footNames]
    return np.array([(speedsPerFrame[:, footIndex] < threshold).tolist() for footIndex in footIndexes])

def getFootContactsHeightMethod(bvh, footNames = ["LeftFoot", "RightFoot"], threshold = 0.1, referenceFrame = 0):
    footContacts = []
    
    floorHeight = sum(bvh.getFKAtFrame(referenceFrame)[footName][1][1] for footName in footNames) / len(footNames)

    for frame in range(bvh.motion.numFrames):
        fkFrame = bvh.getFKAtFrame(frame)
        contacts = []
        for footName in footNames:
            contacts.append(fkFrame[footName][1][1] < (floorHeight + threshold))
        footContacts.append(contacts)

    return np.array(footContacts).T

def getFootSlide(bvh, footNames = ["LeftFoot", "RightFoot"], speedThreshold = 0.1, heightThreshold = 0.1, timeDiff = -1, referenceFrame = 0):
    speedFC = getFootContactsSpeedMethod(bvh, footNames, speedThreshold, timeDiff)
    heightFC = getFootContactsHeightMethod(bvh, footNames, heightThreshold, referenceFrame)
    return np.logical_and(np.logical_not(speedFC), heightFC)