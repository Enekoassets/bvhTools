import copy
from scipy.spatial.transform import Rotation as R
import numpy as np
from bvhTools.bvhDataTypes import BVHData

def centerSkeletonRoot(bvhData: BVHData, fkFrame: int = 0) -> BVHData:
    """Center a skeleton by putting its root in (0, 0, 0) at the specified frame.
    The entire animation is shifted in world space.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be centered.
        fkFrame : int
            Frame in which the root will be on (0, 0, 0).

    Returns
    -------
        BVHData
            The new centered BVHData object.
    """
    bvhDataCopy = copy.deepcopy(bvhData)
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonFeet(bvhData: BVHData, leftFootName: str = "LeftFoot", rightFootName: str = "RightFoot", fkFrame: int = 0) -> BVHData:
    """Center a skeleton by putting its feet in (0, 0, 0) at the specified frame.
    The entire animation is shifted in world space. This method uses the left
    and right feet to calculate the average length of both legs in a specific
    frame so the skeleton is centered using that average point. 

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be centered.
        leftFootName : str
            Name of the left foot joint. Used to calculate the standing point.
        rightFootName: str
            Name of the right foot joint. Used to calculate the standing point.
        fkFrame : int
            Frame in which the skeleton will stand on (0, 0, 0).

    Returns
    -------
        BVHData
            The new centered BVHData object.
    """
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

def centerSkeletonXZ(bvhData: BVHData, fkFrame: int = 0) -> BVHData:
    """Center a skeleton in the XZ plane by zeroing its X and Z components at the specified frame.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be centered.
        fkFrame : int
            Frame in which the skeleton will be centered horizontally.

    Returns
    -------
        BVHData
            The new centered BVHData object.
    """
    bvhDataCopy = copy.deepcopy(bvhData)
    frame = bvhDataCopy.motion.getFrame(fkFrame)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonAroundJoint(bvhData: BVHData, jointName: str, fkFrame: int = 0) -> BVHData:
    """Center a skeleton around a joint by locating that specified joint
    in (0, 0, 0) at the specified frame. The entire skeleton is shifted.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be centered.
        jointName : str
            Name of the joint that will be located in (0, 0, 0) in the specified frame.
        fkFrame : int
            Frame in which the skeleton will be centered horizontally.

    Returns
    -------
        BVHData
            The new centered BVHData object.
    """
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

def standSkeletonOnFloor(bvhData: BVHData, leftFootName: str = "LeftFoot", rightFootName: str = "RightFoot", fkFrame: int = 0) -> BVHData:
    """Change the Y component of an animation so it stands at ground level at
    the specified frame. The entire animation is shifted in world space. This
    method uses the left and right feet to calculate the average length of 
    both legs in a specific frame so the height is calculated using that 
    average point. 

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be modified.
        leftFootName : str
            Name of the left foot joint. Used to calculate the standing point.
        rightFootName: str
            Name of the right foot joint. Used to calculate the standing point.
        fkFrame : int
            Frame in which the skeleton will stand on the floor.

    Returns
    -------
        BVHData
            The new BVHData object that stands at height = 0.
    """
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

def rotateSkeletonLocal(bvhData: BVHData, angle: list[float], fkFrame: int = 0) -> BVHData:
    """Rotate a skeleton locally, around its own root joint. The
    method calculates the root position in a specific frame, and
    rotates the skeleton around that point. The entire animation
    is rotated.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be rotated.
        angle : list[float]
            Euler angles to rotate the skeleton. Format: [X, Y, Z].
        fkFrame : int
            Frame that will be used to calculate the root position.

    Returns
    -------
        BVHData
            The new rotated BVHData object.
    """
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

def rotateSkeletonWorld(bvhData: BVHData, angle: list[float]) -> BVHData:
    """Rotate a skeleton globally, around the world origin.
    The entire animation is rotated.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be rotated.
        angle : list[float]
            Euler angles to rotate the skeleton. Format: [X, Y, Z].

    Returns
    -------
        BVHData
            The new rotated BVHData object.
    """
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

def moveSkeleton(bvhData: BVHData, offsets: list[float]) -> BVHData:
    """Move a skeleton, by adding an offset to the root joint.
    The entire animation is shifted.

    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be moved.
        offsets : list[float]
            Position offset to be added. Format: [X, Y, Z].

    Returns
    -------
        BVHData
            The new moved BVHData object.
    """
    if(len(offsets) != 3):
        raise Exception("offsets must be a list of length 3")
    bvhDataCopy = copy.deepcopy(bvhData)
    rootIndex = bvhDataCopy.skeleton.getJointIndex(bvhDataCopy.skeleton.root.name)
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def mirrorSkeleton(bvhData: BVHData, flipAxis: str, jointPairs: list[list[str]]) -> BVHData:
    """Mirrors a skeleton, by flipping it on the selected axis
    and by switching the angles on the selected limb pairs.
    This method needs the skeleton to be symmetric on the selected 
    axis. The entire animation is mirrored.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH to be mirrored.
        flipAxis : str
            Axis for the mirroring. Options: [X, Y, Z].
        jointPairs: list[list[str]]
            The joint pairs to be exchanged. Example: [["leftArm", "rightArm"], ["leftLeg", "rightLeg"] ... ]

    Returns
    -------
        BVHData
            The new moved BVHData object.
        """
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