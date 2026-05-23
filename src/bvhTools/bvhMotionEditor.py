import copy
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp
import math
from bvhTools.bvhDataTypes import BVHData

def resampleFPS(bvh: BVHData, fps: int) -> BVHData:
    bvhCopy = copy.deepcopy(bvh)
    currentFps = 1.0/bvhCopy.motion.frameTime
    newFrames = []
    bvhCopy.motion.numFrames = round(bvh.motion.numFrames * (fps / currentFps))
    bvhCopy.motion.frameTime = round(1/fps, 6)
    for frameIndex in range(bvhCopy.motion.numFrames):
        frameLocation = frameIndex / (bvhCopy.motion.numFrames - 1) * (bvh.motion.numFrames - 1)
        t_1 = math.floor(frameLocation)
        t_percent = frameLocation - t_1
        if(abs(t_percent) < 1e-8):
            frame = bvh.motion.frames[t_1]
        else:
            vec1 = bvh.motion.frames[t_1]
            vec2 = bvh.motion.frames[t_1 + 1]
            frame = []
            for joint in bvh.skeleton.joints:
                if("_EndSite" in joint):
                    continue
                channels = bvh.skeleton.getJoint(joint).channels
                rotationChannelOrder = bvh.skeleton.getJoint(joint).getRotationChannelsOrder()
                motionIndex = bvh.skeleton.getJoint(joint).motionIndex
                if("Xposition" in channels and "Yposition" in channels and "Zposition" in channels):
                    frame.extend([x * (1- t_percent) + y * t_percent for x, y in zip(vec1[motionIndex:motionIndex + 3], vec2[motionIndex:motionIndex + 3])])
                    r1 = R.from_euler(rotationChannelOrder,vec1[motionIndex+3:motionIndex+6], degrees=True)
                    r2 = R.from_euler(rotationChannelOrder,vec2[motionIndex+3:motionIndex+6], degrees=True)
                else:
                    r1 = R.from_euler(rotationChannelOrder,vec1[motionIndex:motionIndex+3], degrees=True)
                    r2 = R.from_euler(rotationChannelOrder,vec2[motionIndex:motionIndex+3], degrees=True)
                keyRots = R.concatenate([r1, r2])
                keyTimes = [0, 1]
                slerp = Slerp(keyTimes, keyRots)
                interpRot = slerp(t_percent)
                frame.extend(interpRot.as_euler(rotationChannelOrder, degrees=True))
        newFrames.append(frame)
    bvhCopy.motion.frames = newFrames
    return bvhCopy