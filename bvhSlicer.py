import copy
def getBvhSlice(bvhData, fromFrame, toFrame):
    if(fromFrame > toFrame):
        raise Exception("fromFrame must be less than toFrame")
    bvhDataCopy = copy.deepcopy(bvhData)
    bvhDataCopy.motion.frames = bvhData.motion.frames[fromFrame:toFrame]
    bvhDataCopy.motion.num_frames = toFrame - fromFrame
    return bvhDataCopy

def getBvhSlices(bvhData, fromFrames, toFrames):
    if(len(fromFrames) != len(toFrames)):
        raise Exception("fromFrames and toFrames must be the same length")
    bvhsToReturn = []
    for fromFrame, toFrame in zip(fromFrames, toFrames):
        bvhsToReturn.append(getBvhSlice(bvhData, fromFrame, toFrame))
    return bvhsToReturn