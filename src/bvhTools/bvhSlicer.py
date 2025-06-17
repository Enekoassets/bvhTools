import copy
from bvhTools.bvhDataTypes import BVHData, MotionData

def getBvhSlice(bvhData, fromFrame, toFrame):
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

def getBvhSlices(bvhData, fromFrames, toFrames):
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

def appendBvhSlices(baseBvh, bvhsToAppend):
    if(len(bvhsToAppend) == 0):
        print(f"\033[1;33mWARNING\033[0m: You must provide at least one BVH to append. Returning original bvh.")
        return baseBvh
    bvhData = copy.deepcopy(baseBvh)
    for bvh in bvhsToAppend:
        for frame in bvh.motion.frames:
            bvhData.motion.frames.append(frame)
        bvhData.motion.numFrames += bvh.motion.numFrames
    return bvhData
        
def groupBvhSlices(bvhsToGroup):
    if(len(bvhsToGroup) <= 1):
        print(f"\033[1;33mWARNING\033[0m: You must provide at least two BVHs to append. Returning original bvh.")
        return bvhsToGroup[0]
    bvhData = copy.deepcopy(bvhsToGroup[0])
    for bvh in bvhsToGroup[1:]:
        for frame in bvh.motion.frames:
            bvhData.motion.frames.append(frame)
        bvhData.motion.numFrames += bvh.motion.numFrames
    return bvhData