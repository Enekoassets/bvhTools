import numpy as np
from scipy.spatial.transform import rotation as R

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

def getAvgSpeeds(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 2:
        return np.empty(0)

    allSpeeds = getSpeeds(bvh, timeDiff)
    return np.mean(allSpeeds, axis = 0)

def getAvgAccelerations(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 3:
        return np.empty(0)

    allAccelerations = getAccelerations(bvh, timeDiff)
    return np.mean(allAccelerations, axis = 0)

def getAvgJerks(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 4:
        return np.empty(0)

    allJerks = getJerks(bvh, timeDiff)
    return np.mean(allJerks, axis = 0)

def getAvgSpeedsPerFrame(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 2:
        return np.empty(0)

    allSpeeds = getSpeeds(bvh, timeDiff)
    return np.mean(allSpeeds, axis = 1)

def getAvgAccelerationsPerFrame(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 3:
        return np.empty(0)

    allAccelerations = getAccelerations(bvh, timeDiff)
    return np.mean(allAccelerations, axis = 1)

def getAvgJerksPerFrame(bvh, timeDiff = -1):
    if bvh.motion.numFrames < 4:
        return np.empty(0)

    allJerks = getJerks(bvh, timeDiff)
    return np.mean(allJerks, axis = 1)

def getAngularSpeedVectors(bvh):
    pass

def getAngularAccelerationVectors(bvh):
    pass

def getAngularJerkVectors(bvh):
    pass

def getAvgAngularSpeeds(bvh):
    pass

def getAvgAngularAccelerations(bvh):
    pass

def getAvgAngularJerks(bvh):
    pass

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