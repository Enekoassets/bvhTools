import copy
from bvhTools.bvhDataTypes import BVHData, MotionData

def getBvhSlice(bvhData, fromFrame, toFrame):
    if(fromFrame > toFrame):
        raise Exception("fromFrame must be less than toFrame")
    slicedBvh = BVHData(bvhData.skeleton, MotionData(toFrame - fromFrame, bvhData.motion.frameTime, bvhData.motion.getFrameSlice(fromFrame, toFrame)), bvhData.header)
    return slicedBvh

def getBvhSlices(bvhData, fromFrames, toFrames):
    if(len(fromFrames) != len(toFrames)):
        raise Exception("fromFrames and toFrames must be the same length")
    bvhsToReturn = []
    for fromFrame, toFrame in zip(fromFrames, toFrames):
        bvhsToReturn.append(getBvhSlice(bvhData, fromFrame, toFrame))
    return bvhsToReturn

def appendBvhSlices(baseBvh, bvhsToAppend):
    if(len(bvhsToAppend) == 0):
        raise Exception("You must provide at least one BVH to append")
    bvhData = copy.deepcopy(baseBvh)
    for bvh in bvhsToAppend:
        for frame in bvh.motion.frames:
            bvhData.motion.frames.append(frame)
        bvhData.motion.numFrames += bvh.motion.numFrames
    return bvhData
        
def groupBvhSlices(bvhsToGroup):
    if(len(bvhsToGroup) <= 1):
        raise Exception("You must provide at least two BVHs to append")
    bvhData = copy.deepcopy(bvhsToGroup[0])
    for bvh in bvhsToGroup[1:]:
        for frame in bvh.motion.frames:
            bvhData.motion.frames.append(frame)
        bvhData.motion.numFrames += bvh.motion.numFrames
    return bvhData