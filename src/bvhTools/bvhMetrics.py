import numpy as np
from scipy.spatial.transform import Rotation as R
import copy
from bvhTools.bvhDataTypes import BVHData
def getSpeeds(bvh: BVHData, timeDiff: float = -1, type: str = "vector") -> np.array:
    """Returns the speeds of all joints on all frames.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its speeds.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output speed type. Options: ["vector", "magnitude"]

    Returns
    -------
        np.array
            The calculated speeds. Its size will be [numJoints, numFrames-1] or [numJoints, numFrames-1, 3]
    """
    if bvh.motion.numFrames < 2:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 2 frames to calculate speeds. Returning empty array.")
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

    if type == "vector":
        return allSpeeds
    if type == "magnitude":
        return np.linalg.norm(allSpeeds, axis = 2)
    
    print(f"\033[1;33mWARNING\033[0m: The speed output type {type} is not valid. Available options: [vector, magnitude]. Returning vector.")
    return np.asarray(allSpeeds)

def getAccelerations(bvh: BVHData, timeDiff: float = -1, type: str = "vector") -> np.array:
    """Returns the accelerations of all joints on all frames.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its accelerations.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output acceleration type. Options: ["vector", "magnitude"]

    Returns
    -------
        np.array
            The calculated accelerations. Its size will be [numJoints, numFrames-2] or [numJoints, numFrames-2, 3]
    """
    if bvh.motion.numFrames < 3:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 3 frames to calculate accelerations. Returning empty array.")
        return np.empty((0,0))
    
    allSpeeds = getSpeeds(bvh, timeDiff)

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

    if type == "vector":
        return allAccelerations
    if type == "magnitude":
        return np.linalg.norm(allAccelerations, axis = 2)
    
    print(f"\033[1;33mWARNING\033[0m: The acceleration output type {type} is not valid. Available options: [vector, magnitude]. Returning vector.")
    return np.asarray(allAccelerations)

def getJerks(bvh: BVHData, timeDiff: float = -1, type: str = "vector") -> np.array:
    """Returns the jerks of all joints on all frames.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its jerks.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output jerk type. Options: ["vector", "magnitude"]

    Returns
    -------
        np.array
            The calculated jerks. Its size will be [numJoints, numFrames-3] or [numJoints, numFrames-3, 3]
    """
    if bvh.motion.numFrames < 4:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 4 frames to calculate jerks. Returning empty array.")
        return np.empty((0,0))
    
    allAccelerations = getAccelerations(bvh, timeDiff)

    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff

    allJerks = []
    lastAcceleration = allAccelerations[0]
    for frameIndex in range(1, len(allAccelerations)):
        currAcceleration = allAccelerations[frameIndex]
        jerks = (currAcceleration - lastAcceleration)/frameTime
        allJerks.append(jerks)
        lastAcceleration = currAcceleration

    if type == "vector":
        return allJerks
    if type == "magnitude":
        return np.linalg.norm(allJerks, axis = 2)
    
    print(f"\033[1;33mWARNING\033[0m: The acceleration output type {type} is not valid. Available options: [vector, magnitude]. Returning vector.")

    return np.asarray(allJerks) 

def getAvgSpeeds(bvh: BVHData, timeDiff: float = -1, type: str = "vector", mode: str = "perJoint") -> np.array:
    """Returns the average speeds, grouped by joint or by frames.
    If grouped by joints, each joint will have one speed, averaged
    through all frames. Else, each frame will have one speed,
    averaged using all joints.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average speeds.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output speed type. Options: ["vector", "magnitude"]
        mode: str = "perJoint"
            How to average the speeds. Options ["perJoint", "perFrame"]

    Returns
    -------
        np.array
            The calculated average speeds. Its size depends on the selected type and mode.
    """
    if bvh.motion.numFrames < 2:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 2 frames to calculate speeds. Returning empty array.")
        return np.empty(0)
    
    axis = 0 if mode == "perJoint" else 1

    allSpeeds = getSpeeds(bvh, timeDiff)
    if(type == "vector"):
        return np.mean(allSpeeds, axis = axis)
    if(type == "magnitude"):
        return np.mean(np.linalg.norm(allSpeeds, axis = 2), axis = axis)
    
    print(f"\033[1;33mWARNING\033[0m: The speed output type {type} is not valid. Available options: [vector, magnitude]. Returning mean vector.")
    return np.mean(allSpeeds, axis = axis)

def getAvgAccelerations(bvh: BVHData, timeDiff: float = -1, type: str = "vector", mode: str = "perJoint") -> np.array:
    """Returns the average accelerations, grouped by joint or by
    frames. If grouped by joints, each joint will have one 
    acceleration, averaged through all frames. Else, each frame
    will have one acceleration, averaged using all joints.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average accelerations.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output acceleration type. Options: ["vector", "magnitude"]
        mode: str = "perJoint"
            How to average the accelerations. Options ["perJoint", "perFrame"]

    Returns
    -------
        np.array
            The calculated average accelerations. Its size depends on the selected type and mode.
    """
    if bvh.motion.numFrames < 3:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 3 frames to calculate accelerations. Returning empty array.")
        return np.empty(0)
    
    axis = 0 if mode == "perJoint" else 1

    allAccelerations = getAccelerations(bvh, timeDiff)
    if(type == "vector"):
        return np.mean(allAccelerations, axis = axis)
    if(type == "magnitude"):
        return np.mean(np.linalg.norm(allAccelerations, axis = 2), axis = axis)
    
    print(f"\033[1;33mWARNING\033[0m: The acceleration output type {type} is not valid. Available options: [vector, magnitude]. Returning mean vector.")
    return np.mean(allAccelerations, axis = axis)

def getAvgJerks(bvh: BVHData, timeDiff: float = -1, type: str = "vector", mode: str = "perJoint") -> np.array:
    """Returns the average jerks, grouped by joint or by frames.
    If grouped by joints, each joint will have one jerk, 
    averaged through all frames. Else, each frame will have one
    jerk, averaged using all joints.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average jerks.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output jerk type. Options: ["vector", "magnitude"]
        mode: str = "perJoint"
            How to average the jerks. Options ["perJoint", "perFrame"]

    Returns
    -------
        np.array
            The calculated average jerks. Its size depends on the selected type and mode.
    """
    if bvh.motion.numFrames < 4:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 4 frames to calculate jerks. Returning empty array.")
        return np.empty(0)
    
    axis = 0 if mode == "perJoint" else 1

    allJerks = getJerks(bvh, timeDiff)
    if(type == "vector"):
        return np.mean(allJerks, axis = axis)
    if(type == "magnitude"):
        return np.mean(np.linalg.norm(allJerks, axis = 2), axis = axis)
    
    print(f"\033[1;33mWARNING\033[0m: The jerk output type {type} is not valid. Available options: [vector, magnitude]. Returning mean vector.")
    return np.mean(allJerks, axis = axis)

def getAngularSpeeds(bvh: BVHData, timeDiff: float = -1, type: str = "vector") -> np.array:
    """Returns the angular speeds of all joints on all frames.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its angular speeds.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output angular speed type. Options: ["vector", "magnitude"]

    Returns
    -------
        np.array
            The calculated angular speeds. Its size will be [numJoints, numFrames-1] or [numJoints, numFrames-1, 3]
    """
    if bvh.motion.numFrames < 2:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 2 frames to calculate angular speeds. Returning empty array.")
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
            if joint.getChannelCount() == 6 and (joint.channels[0] == "Xposition" or joint.channels[0] == "Yposition" or joint.channels[0] == "Zposition"):
                motionIndex += 3
            rotations.append(R.from_euler(joint.getRotationChannelsOrder(), bvh.motion.frames[frameIndex][motionIndex:motionIndex+3], degrees=True))
        allFrameRotations.append(rotations)
        rotations = []
    allFrameRotations = np.asarray(allFrameRotations)
    for frameIndex in range(1, len(allFrameRotations)):
        allSpeeds.append([(r2 * r1.inv()).as_rotvec()/frameTime for r1, r2 in zip(allFrameRotations[frameIndex - 1], allFrameRotations[frameIndex])])

    if(type == "vector"):
        return np.asarray(allSpeeds)
    if(type == "magnitude"):
        return np.linalg.norm(allSpeeds, axis = 2)
    
    print(f"\033[1;33mWARNING\033[0m: The angular speed output type {type} is not valid. Available options: [vector, magnitude]. Returning vector.")
    return np.asarray(allSpeeds)

def getAngularAccelerations(bvh: BVHData, timeDiff: float = -1, type: str = "vector") -> np.array:
    """Returns the angular accelerations of all joints on all frames.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its angular accelerations.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output angular acceleration type. Options: ["vector", "magnitude"]

    Returns
    -------
        np.array
            The calculated angular accelerations. Its size will be [numJoints, numFrames-2] or [numJoints, numFrames-2, 3]
    """
    if bvh.motion.numFrames < 3:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 3 frames to calculate angular accelerations. Returning empty array.")
        return np.empty((0,0,0))
    allSpeeds = getAngularSpeeds(bvh, timeDiff)
    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff
    allAccelerations = []
    for frameIndex in range(1, len(allSpeeds)):
        allAccelerations.append([(r2 - r1)/frameTime for r1, r2 in zip(allSpeeds[frameIndex - 1], allSpeeds[frameIndex])])

    if(type == "vector"):
        return np.asarray(allAccelerations)
    if(type == "magnitude"):
        return np.linalg.norm(allAccelerations, axis = 2)
    
    print(f"\033[1;33mWARNING\033[0m: The angular acceleration output type {type} is not valid. Available options: [vector, magnitude]. Returning vector.")
    return np.asarray(allAccelerations)

def getAngularJerks(bvh: BVHData, timeDiff: float = -1, type: str = "vector") -> np.array:
    """Returns the angular jerks of all joints on all frames.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its angular jerks.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output angular jerk type. Options: ["vector", "magnitude"]

    Returns
    -------
        np.array
            The calculated angular jerks. Its size will be [numJoints, numFrames-3] or [numJoints, numFrames-3, 3]
    """
    if bvh.motion.numFrames < 4:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 4 frames to calculate angular jerks. Returning empty array.")
        return np.empty((0,0,0))
    allAccelerations = getAngularAccelerations(bvh, timeDiff)
    if timeDiff == -1:
        frameTime = bvh.motion.frameTime
    else:
        frameTime = timeDiff
    allJerks = []
    for frameIndex in range(1, len(allAccelerations)):
        allJerks.append([(r2 - r1)/frameTime for r1, r2 in zip(allAccelerations[frameIndex - 1], allAccelerations[frameIndex])])

    if(type == "vector"):
        return np.asarray(allJerks)
    if(type == "magnitude"):
        return np.linalg.norm(allJerks, axis = 2)
    
    print(f"\033[1;33mWARNING\033[0m: The angular jerk output type {type} is not valid. Available options: [vector, magnitude]. Returning vector.")
    return np.asarray(allJerks)

def getAvgAngularSpeeds(bvh: BVHData, timeDiff: float = -1, type: str = "vector", mode: str = "perJoint") -> np.array:
    """Returns the average angular speeds, grouped by joint or by
    frames. If grouped by joints, each joint will have one speed,
    averaged through all frames. Else, each frame will have one
    speed, averaged using all joints.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average angular speeds.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output speed type. Options: ["vector", "magnitude"]
        mode: str = "perJoint"
            How to average the angular speeds. Options ["perJoint", "perFrame"]

    Returns
    -------
        np.array
            The calculated average angular speeds. Its size depends on the selected type and mode.
    """
    if bvh.motion.numFrames < 2:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 2 frames to calculate angular speeds. Returning empty array.")
        return np.empty(0)
    
    axis = 0 if mode == "perJoint" else 1

    allSpeeds = getAngularSpeeds(bvh, timeDiff, type)
    return np.mean(allSpeeds, axis = axis)

def getAvgAngularAccelerations(bvh: BVHData, timeDiff: float = -1, type: str = "vector", mode: str = "perJoint") -> np.array:
    """Returns the average angular accelerations, grouped by joint or by
    frames. If grouped by joints, each joint will have one speed,
    averaged through all frames. Else, each frame will have one
    acceleration, averaged using all joints.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average angular accelerations.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output speed type. Options: ["vector", "magnitude"]
        mode: str = "perJoint"
            How to average the angular accelerations. Options ["perJoint", "perFrame"]

    Returns
    -------
        np.array
            The calculated average angular accelerations. Its size depends on the selected type and mode.
    """
    if bvh.motion.numFrames < 3:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 3 frames to calculate angular accelerations. Returning empty array.")
        return np.empty(0)

    axis = 0 if mode == "perJoint" else 1

    allAccelerations = getAngularAccelerations(bvh, timeDiff, type)
    return np.mean(allAccelerations, axis = axis)

def getAvgAngularJerks(bvh: BVHData, timeDiff: float = -1, type: str = "vector", mode: str = "perJoint") -> np.array:
    """Returns the average angular jerks, grouped by joint or by
    frames. If grouped by joints, each joint will have one speed,
    averaged through all frames. Else, each frame will have one
    jerk, averaged using all joints.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average angular jerks.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        type: str = "vector"
            The output speed type. Options: ["vector", "magnitude"]
        mode: str = "perJoint"
            How to average the angular jerks. Options ["perJoint", "perFrame"]

    Returns
    -------
        np.array
            The calculated average angular jerks. Its size depends on the selected type and mode.
    """
    if bvh.motion.numFrames < 4:
        print(f"\033[1;33mWARNING\033[0m: A Bvh must have at least 4 frames to calculate angular jerks. Returning empty array.")
        return np.empty(0)
    
    axis = 0 if mode == "perJoint" else 1

    allJerks = getAngularJerks(bvh, timeDiff, type)
    return np.mean(allJerks, axis = axis)

def getFootContactsSpeedMethod(bvh: BVHData, footNames: list[str] = ["LeftFoot", "RightFoot"], threshold: float = 0.1, timeDiff: float = -1) -> np.array:
    """Returns a mask containing the foot contacts. The mask will
    contain a 1 if there is a contact, 0 otherwise. This method
    uses a speed threshold to calculate the contacts: if a foot
    has a higher speed than the threshold it returns 1, else 0.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its foot contact mask.
        footNames: list[str] = ["LeftFoot", "RightFoot"]
            The names of the foot joints to calculate the foot contacts. Can be any number of joints.
        threshold: float = 0.1
            The speed threshold. If a speed is higher than this in a frame, the mask will contain a 1.
        timeDiff : float = -1
            Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.

    Returns
    -------
        np.array
            The calculated foot contacts. Its size is numFrames, since the first mask element is duplicated to match numFrames.
    """
    speedsPerFrame = getSpeeds(bvh, timeDiff)
    # duplicate first speed to match number of frames
    speedsPerFrame = np.insert(speedsPerFrame, 0, [speedsPerFrame[0]], axis = 0)
    jointNames = [joint for joint in bvh.skeleton.joints]
    footIndexes = [jointNames.index(footName) for footName in footNames]
    return np.array([(speedsPerFrame[:, footIndex] < threshold).tolist() for footIndex in footIndexes])

def getFootContactsHeightMethod(bvh: BVHData, footNames: list[str] = ["LeftFoot", "RightFoot"], threshold: float = 0.1, referenceFrame: int = 0) -> np.array:
    """Returns a mask containing the foot contacts. The mask will
    contain a 1 if there is a contact, 0 otherwise. This method
    uses a height threshold to calculate the contacts: if a foot
    has a higher y-value than the threshold it returns 1, else 0.
        
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its foot contact mask.
        footNames: list[str] = ["LeftFoot", "RightFoot"]
            The names of the foot joints to calculate the foot contacts. Can be any number of joints.
        threshold: float = 0.1
            The height threshold. If a height is higher than this in a frame, the mask will contain a 1.
        referenceFrame : int = 0
            The frame that will be used as height = 0. Usually a frame where the subject is standing on the floor.

    Returns
    -------
        np.array
            The calculated foot contacts. Its size is numFrames.
    """
    footContacts = []
    
    floorHeight = sum(bvh.getFKAtFrame(referenceFrame)[footName][1][1] for footName in footNames) / len(footNames)

    for frame in range(bvh.motion.numFrames):
        fkFrame = bvh.getFKAtFrame(frame)
        contacts = []
        for footName in footNames:
            contacts.append(fkFrame[footName][1][1] < (floorHeight + threshold))
        footContacts.append(contacts)

    return np.array(footContacts).T

def getFootSlide(bvh: BVHData, footNames: list[str] = ["LeftFoot", "RightFoot"], speedThreshold: float = 0.1, heightThreshold: float = 0.1, timeDiff: float = -1, referenceFrame: int = 0) -> np.array:
    """Experimental. Returns a mask containing foot slide. The 
    mask will have a 1 if there is foot slide, 0 otherwise. This
    method uses two masks internally: a foot contact mask using
    the speed method, and another foot contact mask using the 
    height method. If a joint has a contact according to height
    but not according to speed, it counts as a foot slide frame.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its foot contact mask.
        footNames: list[str] = ["LeftFoot", "RightFoot"]
            The names of the foot joints to calculate the foot slide. Can be any number of joints.
        speedThreshold: float = 0.1
            The speed threshold. If a speed is higher than this in a frame, it counts as if it was moving.
        heightThreshold: float = 0.1
            The height threshold. If a height is higher than this in a frame, it counts as not on the floor.
        timeDiff : float = -1
                    Time difference between frames (1/frames per second). Leave at -1 to get the fps from the BVH file itself.
        referenceFrame : int = 0
            The frame that will be used as height = 0. Usually a frame where the subject is standing on the floor.

    Returns
    -------
        np.array
            The calculated foot slides. Its size is numFrames.
    """
    speedFC = getFootContactsSpeedMethod(bvh, footNames, speedThreshold, timeDiff)
    heightFC = getFootContactsHeightMethod(bvh, footNames, heightThreshold, referenceFrame)
    return np.logical_and(np.logical_not(speedFC), heightFC)

def getAvgPose(bvh: BVHData) -> BVHData:
    """Returns the average pose of an animation sequence. This
    method calculates the angles of the average pose by
    averaging over all quaternions, whose signs have been first
    corrected. The root position average is calculated using
    a simple average over the X, Y and Z elements.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to calculate its average pose.

    Returns
    -------
        BVHData
            The calculated average pose, It is a BVHData object containing one single frame.
    """
    bvhCopy = copy.deepcopy(bvh)
    avgPose = []
    for jointName in bvh.skeleton.joints:
        if(not "_EndSite" in jointName):
            joint = bvh.skeleton.getJoint(jointName)
            motionIndex = joint.motionIndex
            if(joint.getChannelCount() == 3): # if the joint has no position channels
                quatFrames = []
                for frame in bvh.motion.frames:
                    rot = R.from_euler(joint.getRotationChannelsOrder(), frame[motionIndex:motionIndex + 3], degrees = True)
                    quat = rot.as_quat()
                    if(len(quatFrames) > 1 and np.dot(quat, quatFrames[-1]) < 0):
                        quat = -quat
                    quatFrames.append(quat)
                avgQuat = np.mean(quatFrames, axis = 0)
                avgQuat /= np.linalg.norm(avgQuat)
                avgPose.append(R.from_quat(avgQuat).as_euler(joint.getRotationChannelsOrder(), degrees = True))
            else: # the joint has position and rotation channels
                positionsOffset = 0
                rotationsOffset = 3
                quatFrames = []
                posFrames = []
                if(joint.channels[0] == "Xrotation" or joint.channels[0] == "Yrotation" or joint.channels[0] == "Zrotation"):
                    positionsOffset = 3
                    rotationsOffset = 0
                for frame in bvh.motion.frames:
                    pos = frame[motionIndex+positionsOffset:motionIndex+positionsOffset+3]
                    rot = R.from_euler(joint.getRotationChannelsOrder(), frame[motionIndex+rotationsOffset:motionIndex+rotationsOffset + 3], degrees = True)
                    quat = rot.as_quat()
                    if(len(quatFrames) > 1 and np.dot(quat, quatFrames[-1]) < 0):
                        quat = -quat
                    posFrames.append(pos)
                    quatFrames.append(quat)
                avgQuat = np.mean(quatFrames, axis = 0)
                avgPos = np.mean(posFrames, axis = 0)
                avgQuat /= np.linalg.norm(avgQuat)
                if (positionsOffset == 0): # positions are first
                    avgPose.append(avgPos)
                    avgPose.append(R.from_quat(avgQuat).as_euler(joint.getRotationChannelsOrder(), degrees = True))
                else:
                    avgPose.append(R.from_quat(avgQuat).as_euler(joint.getRotationChannelsOrder(), degrees = True))
                    avgPose.append(avgPos)
    bvhCopy.motion.frames = [np.asarray(avgPose).flatten()]
    bvhCopy.motion.numFrames = 1
    return bvhCopy