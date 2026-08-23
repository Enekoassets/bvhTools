import copy
from bvhTools.bvhDataTypes import BVHData, MotionData

def getBvhSlice(bvhData: BVHData, fromFrame: int, toFrame: int) -> BVHData:
    """Returns an animation slice of a selected BVH. It returns a new
    BVHData object with just the selected frame section as motion.
    This method can be used to create sub-animations and treat them as
    new BVH objects. The objects can later be modified or written to
    file as any other BVH. The indexing follows regular Python indexing.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH that will be used to extract the animation slice.
        fromFrame: int
            The index of the starting frame of the new slice (inclusive). 0 <= fromFrame <= numFrames
        toFrame: int
            The index of the ending frame of the new slice (exclusive). fromFrame <= toFrame <= numFrames
    Returns
    -------
        BVHData
            The new BVH with the selected animation slice but same skeleton.
    """
    if(fromFrame > toFrame):
        print(f"\033[1;33mWARNING\033[0m: fromFrame ({fromFrame}) must be less than toFrame ({toFrame}). Returning original bvh.")
        return bvhData
    if(fromFrame < 0 or fromFrame > bvhData.motion.numFrames):
        print(f"\033[1;33mWARNING\033[0m: fromFrame ({fromFrame}) is less than zero or out of range. Returning original bvh.")
        return bvhData
    if (toFrame < 0 or toFrame > bvhData.motion.numFrames):
        print(f"\033[1;33mWARNING\033[0m: toFrame ({toFrame}) is less than zero or out of range. Returning original bvh.")
    slicedBvh = BVHData(bvhData.skeleton, MotionData(toFrame - fromFrame, bvhData.motion.frameTime, bvhData.motion.getFrameSlice(fromFrame, toFrame)))
    return slicedBvh

def getBvhSlices(bvhData: BVHData, fromFrames: list[int], toFrames: list[int]) -> list[BVHData]:
    """Returns several animation slices from a selected BVH. It returns
    a list of BVHData objects, each one with the selected frame section
    as motino. This method can be used to create sub-animations and
    treat them as new BVH objects. The objects can later be modified or
    written to file as any other BVH. The indexing follows regular
    Python indexing.
    
    Parameters
    ----------
        bvhData : BVHData
            Input BVH that will be used to extract the animation slices.
        fromFrame: list[int]
            List containing the indexes of the starting frames of the new slices (inclusive). 0 <= fromFrame <= numFrames
        toFrame: list[int]
            List containing the indexes of the ending frames of the new slices (exclusive). fromFrame <= toFrame <= numFrames
    Returns
    -------
        list[BVHData]
            A list with the new BVH objects with the selected animation slices but same skeleton.
    """
    if(len(fromFrames) != len(toFrames)):
        print(f"\033[1;33mWARNING\033[0m: fromFrames ({len(fromFrames)}) and toFrames ({len(toFrames)}) must be the same length. Returning original bvh.")
        return bvhData
    if(any(f < 0 for f in fromFrames) or any(f > bvhData.motion.numFrames for f in fromFrames)):
        oor = [f for f in fromFrames if f < 0 or f > bvhData.motion.numFrames]
        print(f"\033[1;33mWARNING\033[0m: some fromFrame ({oor}) is out of range. Returning original bvh.")
        return bvhData
    if(any(f < 0 for f in toFrames) or any(f > bvhData.motion.numFrames for f in toFrames)):
        oor = [f for f in toFrames if f < 0 or f > bvhData.motion.numFrames]
        print(f"\033[1;33mWARNING\033[0m: some toFrame ({oor}) is out of range. Returning original bvh.")
        return bvhData
    bvhsToReturn = []
    for fromFrame, toFrame in zip(fromFrames, toFrames):
        bvhsToReturn.append(getBvhSlice(bvhData, fromFrame, toFrame))
    return bvhsToReturn

def appendBvhSlices(baseBvh: BVHData, bvhsToAppend: list[BVHData]) -> BVHData:
    """Appends any number of BVH files with different motion but
    same skeleton to a base BVH. The order of the appended motion
    is unchanged. This method is used to group many motions into
    one BVH file, by appending them to the first BVH.
    
    Parameters
    ----------
        baseBvh : BVHData
            Base BVH file, to which the other motion will be appended.
        bvhsToAppend : list[BVHData]
            List of BVH files, whose motion will be appended to the base BVH.
    Returns
    -------
        BVHData
            A single BVH containing the motion of all the BVH files.
    """
    if(len(bvhsToAppend) == 0):
        print(f"\033[1;33mWARNING\033[0m: You must provide at least one BVH to append. Returning original bvh.")
        return baseBvh
    bvhData = copy.deepcopy(baseBvh)
    for bvh in bvhsToAppend:
        for frame in bvh.motion.frames:
            bvhData.motion.frames.append(frame)
        bvhData.motion.numFrames += bvh.motion.numFrames
    return bvhData
        
def groupBvhSlices(bvhsToGroup: list[BVHData]) -> BVHData:
    """Appends any number of BVH files with different motion but
    same skeleton. It uses the skeleton of the first provided BVH.
    This method is used to group many motions into one BVH file.
    
    Parameters
    ----------
        bvhsToGroup : list[BVHData]
            List of BVH files, whose motion will be grouped together.
    Returns
    -------
        BVHData
            A single BVH containing the motion of all the BVH files.
    """
    if(len(bvhsToGroup) <= 1):
        print(f"\033[1;33mWARNING\033[0m: You must provide at least two BVHs to append. Returning original bvh.")
        return bvhsToGroup[0]
    bvhData = copy.deepcopy(bvhsToGroup[0])
    for bvh in bvhsToGroup[1:]:
        for frame in bvh.motion.frames:
            bvhData.motion.frames.append(frame)
        bvhData.motion.numFrames += bvh.motion.numFrames
    return bvhData