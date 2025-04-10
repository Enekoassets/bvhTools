from scipy.spatial.transform import Rotation as R
import numpy as np

class Joint:
    def __init__(self, name, offset, channels, parent=None):
        self.name = name
        self.offset = offset 
        self.channels = channels
        self.children = []
        self.parent = parent

    def setOffset(self, offset):
        self.offset = offset

    def setChannels(self, channels):
        self.channels = channels

    def setParent(self, parent):
        self.parent = parent

    def addChild(self, child):
        self.children.append(child)

    def getChannelCount(self):
        return len(self.channels)
    
    def getPositionChannelsOrder(self):
        if("position" not in self.channels[0] and len(self.channels) <= 3):
            print(f"joint {self.name} has no position channels")
            return
        positionChannels = self.channels[0:3] if("position" in self.channels[0] or "position" in self.channels[1] or "position" in self.channels[2]) else self.channels[3:6]
        if(positionChannels[0] == "Xposition"):
            if(positionChannels[1] == "Yposition"):
                return "XYZ"
            if(positionChannels[1] == "Zposition"):
                return "XZY"
        if(positionChannels[0] == "Yposition"):
            if(positionChannels[1] == "Xposition"):
                return "YXZ"
            if(positionChannels[1] == "Zposition"):
                return "YZX"
        if(positionChannels[0] == "Zposition"):
            if(positionChannels[1] == "Xposition"):
                return "ZXY"
            if(positionChannels[1] == "Yposition"):
                return "ZYX"

    def getRotationChannelsOrder(self):
        if("rotation" not in self.channels[0] and len(self.channels) <= 3):
            print(f"joint {self.name} has no rotation channels")
            return
        rotationChannels = self.channels[0:3] if("rotation" in self.channels[0] or "rotation" in self.channels[1] or "rotation" in self.channels[2]) else self.channels[3:6]
        if(rotationChannels[0] == "Xrotation"):
            if(rotationChannels[1] == "Yrotation"):
                return "XYZ"
            if(rotationChannels[1] == "Zrotation"):
                return "XZY"
        if(rotationChannels[0] == "Yrotation"):
            if(rotationChannels[1] == "Xrotation"):
                return "YXZ"
            if(rotationChannels[1] == "Zrotation"):
                return "YZX"
        if(rotationChannels[0] == "Zrotation"):
            if(rotationChannels[1] == "Xrotation"):
                return "ZXY"
            if(rotationChannels[1] == "Yrotation"):
                return "ZYX"
            
    def getChannelIndex(self, channelName):
        return self.channels.index(channelName)

class Skeleton:
    def __init__(self, rootJoint):
        self.root = rootJoint
        self.joints = self.buildJointDict(rootJoint)
        self.jointIndexes = self.buildJointIndexDict(rootJoint, [0])

    def buildJointDict(self, joint):
        jointDict = {joint.name: joint}
        for child in joint.children:
            jointDict.update(self.buildJointDict(child))
        return jointDict

    def buildJointIndexDict(self, joint, currentChannelIndex=[0]):
        jointIndexDict = {joint.name: currentChannelIndex[0]}
        currentChannelIndex[0] += joint.getChannelCount()

        for child in joint.children:
            jointIndexDict.update(self.buildJointIndexDict(child, currentChannelIndex))
        return jointIndexDict

    def getJoint(self, jointName):
        return self.joints[jointName]

    def getJointIndex(self, jointName):
        return self.jointIndexes[jointName]

class MotionData:
    def __init__(self, numFrames, frameTime, frames):
        if(numFrames != len(frames)):
            print("WARNING: Number of frames does not match number of frames in data. Taking the length of the motion data.")
        self.numFrames = len(frames)
        self.frameTime = frameTime
        self.frames = frames

    def addFrame(self, frameData):
        self.frames.append(frameData)

    def getFrame(self, frameIndex):
        return self.frames[frameIndex]
    
    def getFrameSlice(self, startFrame, endFrame):
        return self.frames[startFrame:endFrame]

    def getRotations(self, rotationIndex):
        return [x[rotationIndex] for x in self.frames]

    def getRotationsSlice(self, startIndex, endIndex):
        return [x[startIndex:endIndex] for x in self.frames]

    def getRotationAtFrame(self, rotationIndex, frame):
        return self.frames[frame][rotationIndex]
    
    def getRotationSliceAtFrame(self, startIndex, endIndex, frame):
        return self.frames[frame][startIndex:endIndex]

    def getRotationAndFrameSlice(self, startIndex, endIndex, startFrame, endFrame):
        return self.frames[startFrame, endFrame][startIndex:endIndex]

class BVHData:
    def __init__(self, skeleton, motion, header):
        self.header = header
        self.skeleton = skeleton
        self.motion = motion
        self.skeletonDims = self.calculateSkeletonDims()
        self.motionDims = self.calculateMotionDims()
        
    def getJointLocalTransformAtFrame(self, jointName, frame, rotationMode = "Euler"):
        joint = self.skeleton.getJoint(jointName)
        jointIndex = self.skeleton.getJointIndex(jointName)
        r = None
        Xrot, Yrot, Zrot = None, None, None
        Xpos, Ypos, Zpos = 0.0, 0.0, 0.0
        if("Xrotation" in joint.channels and "Yrotation" in joint.channels and "Zrotation" in joint.channels):
            Xrot = self.motion.getRotationAtFrame(jointIndex + joint.channels.index("Xrotation"), frame)
            Yrot = self.motion.getRotationAtFrame(jointIndex + joint.channels.index("Yrotation"), frame)
            Zrot = self.motion.getRotationAtFrame(jointIndex + joint.channels.index("Zrotation"), frame)
            r = R.from_euler('xyz', [Xrot, Yrot, Zrot], degrees=True)
        if("Xposition" in joint.channels and "Yposition" in joint.channels and "Zposition" in joint.channels):
            Xpos = self.motion.getRotationAtFrame(jointIndex + joint.channels.index("Xposition"), frame)
            Ypos = self.motion.getRotationAtFrame(jointIndex + joint.channels.index("Yposition"), frame)
            Zpos = self.motion.getRotationAtFrame(jointIndex + joint.channels.index("Zposition"), frame)

        if(r is None):
            if(rotationMode == "Euler"):
                return R.identity().as_euler('xyz', degrees=True), [Xpos, Ypos, Zpos]
            if(rotationMode == "Quaternion"):
                return R.identity().as_quat(), [Xpos, Ypos, Zpos]
            if(rotationMode == "Matrix"):
                return R.identity().as_matrix(), [Xpos, Ypos, Zpos]
        else:
            if(rotationMode == "Euler"):
                return r.as_euler('xyz', degrees=True), [Xpos, Ypos, Zpos]
            if(rotationMode == "Quaternion"):
                return r.as_quat(), [Xpos, Ypos, Zpos]
            if(rotationMode == "Matrix"):
                return r.as_matrix(), [Xpos, Ypos, Zpos]

    def calculateSkeletonDims(self):
        minX, minY, minZ = float('inf'), float('inf'), float('inf')
        maxX, maxY, maxZ = float('-inf'), float('-inf'), float('-inf')

        fk_data_0 = self.getFKAtFrame(0)
        for jointName, (rot, pos) in fk_data_0.items():
            # Extract the position of each joint
            x, y, z = pos
            
            # Update the min and max values for each axis (X, Y, Z)
            minX = min(minX, x)
            minY = min(minY, y)
            minZ = min(minZ, z)

            maxX = max(maxX, x)
            maxY = max(maxY, y)
            maxZ = max(maxZ, z)

        # Calculate height, width, and depth
        height = maxY - minY  # Difference in the Y-axis (vertical)
        width = maxX - minX   # Difference in the X-axis (horizontal)
        depth = maxZ - minZ   # Difference in the Z-axis (depth)

        return [height, width, depth]

    def getSkeletonDim(self, dimName):
        if(dimName == "width"):
            return self.skeletonDims[0]
        if(dimName == "height"):
            return self.skeletonDims[1]
        if(dimName == "depth"):
            return self.skeletonDims[2]

    def getSkeletonDims(self):
        return self.skeletonDims
    
    def calculateMotionDims(self):
        minX, minY, minZ = float('inf'), float('inf'), float('inf')
        maxX, maxY, maxZ = float('-inf'), float('-inf'), float('-inf')

        for frameIndex in range(self.motion.numFrames):
            fkDataRoot = self.getFKAtFrame(frameIndex)[self.skeleton.root.name][1]
            # Extract the position of each joint
            x, y, z = fkDataRoot
            
            # Update the min and max values for each axis (X, Y, Z)
            minX = min(minX, x)
            minY = min(minY, y)
            minZ = min(minZ, z)

            maxX = max(maxX, x)
            maxY = max(maxY, y)
            maxZ = max(maxZ, z)

        return [minX, maxX, minY, maxY, minZ, maxZ]

    def getMotionDims(self):
        return self.motionDims
    
    def getChildFKAtFrame(self, joint, frame, parentTransform, fkFrame):
        localRot, localPos = self.getJointLocalTransformAtFrame(joint.name, frame, "Matrix")
        jointGlobalRot = np.matmul(parentTransform[0], localRot)
        rotatedOffset = np.matmul(parentTransform[0], joint.offset)
        jointGlobalPos = np.add(np.add(rotatedOffset, localPos), parentTransform[1])
        fkFrame.update({joint.name: (jointGlobalRot, jointGlobalPos)})
        for child in joint.children:
            self.getChildFKAtFrame(child, frame, (jointGlobalRot, jointGlobalPos), fkFrame)

    def getFKAtFrame(self, frame):
        rootJoint = self.skeleton.root
        rootLocalRot, rootLocalPos = self.getJointLocalTransformAtFrame(rootJoint.name, frame, "Matrix")
        fkFrame = {rootJoint.name: (rootLocalRot, rootLocalPos)}
        for child in rootJoint.children:
            self.getChildFKAtFrame(child, frame, (rootLocalRot, rootLocalPos), fkFrame)
        return fkFrame
    
    def getFKAtFrameNormalized(self, frame, skeletonDim = "height"):
        fkFrame = self.getFKAtFrame(frame)
        normalizer = self.getSkeletonDim(skeletonDim)
        for jointName, (rot, pos) in fkFrame.items():
            fkFrame[jointName] = (rot, pos / normalizer)
        return fkFrame