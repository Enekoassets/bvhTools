from scipy.spatial.transform import Rotation as R
import numpy as np
import copy
import re
from bvhTools.angleConversion import scipyToSixD

class Joint:
    def __init__(self, name, index, offset, channels, parent=None):
        self.name = name
        self.index = index
        self.motionIndex = -1
        self.offset = offset 
        self.channels = channels
        self.children = []
        self.parent = parent

    def _setOffset(self, offset):
        self.offset = offset

    def _setChannels(self, channels):
        self.channels = channels

    def _setParent(self, parent):
        self.parent = parent

    def _addChild(self, child):
        self.children.append(child)

    def getChannelCount(self) -> int:
        return len(self.channels)
    
    def getPositionChannelsOrder(self) -> str:
        if("position" not in self.channels[0] and len(self.channels) <= 3):
            print(f"\033[1;33mWARNING\033[0m: joint {self.name} has no position channels")
            return ""
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

    def getRotationChannelsOrder(self) -> str:
        if("rotation" not in self.channels[0] and len(self.channels) <= 3):
            print(f"\033[1;33mWARNING\033[0m: joint {self.name} has no rotation channels")
            return ""
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
            
    def getChannelIndex(self, channelName: str) -> int:
        if(channelName not in self.channels):
            print(f"\033[1;33mWARNING\033[0m: joint {self.name} does not have channel {channelName}")
            return -1
        return self.channels.index(channelName)
    
    def getRotationFromOffset(self, canonicalRotation: list[float]) -> list[float]:
        offset = np.array(self.offset)
        offsetNormalized = offset / np.linalg.norm(offset)
        axis = np.cross(canonicalRotation, offsetNormalized)
        angle = np.arccos(np.clip(np.dot(canonicalRotation, offsetNormalized), -1.0, 1.0))

        if(np.linalg.norm(axis) < 1e-6):
            return R.identity()
        else:
            axis = axis / np.linalg.norm(axis)
            return R.from_rotvec(angle * axis)

class Skeleton:
    def __init__(self, rootJoint):
        self.root = rootJoint
        self.joints = self._buildJointDict(rootJoint)
        self.jointIndexes = self._buildJointIndexDict(rootJoint, [0])
        self.hierarchyIndexes = self._buildHierarchyIndexDict(rootJoint, [0])
        self.parent = None
        
    def _setParent(self, parent):
        self.parent = parent

    def _buildJointDict(self, joint):
        jointDict = {joint.name: joint}
        for child in joint.children:
            jointDict.update(self._buildJointDict(child))
        return jointDict

    def _buildJointIndexDict(self, joint, currentChannelIndex=None, jointIndex = None):
        if currentChannelIndex is None:
            currentChannelIndex = [0]
        if jointIndex is None:
            jointIndex = [0]

        jointIndexDict = {joint.name: currentChannelIndex[0]}
        joint.motionIndex = currentChannelIndex[0]
        joint.index = jointIndex[0]
        currentChannelIndex[0] += joint.getChannelCount()
        jointIndex[0] += 1
        for child in joint.children:
            jointIndexDict.update(self._buildJointIndexDict(child, currentChannelIndex, jointIndex))
        return jointIndexDict

    def _buildHierarchyIndexDict(self, joint, currentChannelIndex=[0]):
        if(joint.parent != None):
            jointHierarchyIndexDict = {joint.name: joint.parent.index}
        else:
            jointHierarchyIndexDict = {joint.name: -1}
        for child in joint.children:
            jointHierarchyIndexDict.update(self._buildHierarchyIndexDict(child, currentChannelIndex))
        return jointHierarchyIndexDict

    def getJoint(self, jointName: str) -> Joint:
        return self.joints[jointName]

    def getJointIndex(self, jointName: str) -> int:
        return self.jointIndexes[jointName]

    def getJointIndexesList(self) -> list[int]:
        return list(self.jointIndexes.values())
    
    def getHierarchyIndex(self, jointName: str) -> int:
        return self.hierarchyIndexes[jointName]

    def getHierarchyIndexesList(self) -> list[int]:
        return list(self.hierarchyIndexes.values())

    def _printJoint(self, node, prefix='', verbose = False):
        if node.parent == None:
            if not verbose:
                print(f"\033[1;32m{node.name} {node.index}\033[0m")
            else:
                print(f"\033[1;32m{node.name} {node.index}\033[0m: \033[1;34mChannels\033[0m: \033[36m{node.channels}\033[0m, \033[1;33mOffset\033[0m: \033[33m{node.offset}\033[0m")
        children = node.children
        for i, child in enumerate(children):
            is_last = (i == len(children) - 1)
            connector = '└── ' if is_last else '├── '
            child_prefix = prefix + ('    ' if is_last else '│   ')
            if not verbose:
                print(f"\033[1;32m{prefix + connector + child.name} {child.index}\033[0m")
            else:
                print(f"\033[1;32m{prefix + connector + child.name} {child.index}\033[0m: \033[1;34mChannels\033[0m: \033[36m{child.channels}\033[0m, \033[1;33mOffset\033[0m: \033[33m{child.offset}\033[0m")
            self._printJoint(child, child_prefix, verbose=verbose)

    def printSkeleton(self, verbose:bool = False) -> None:
        self._printJoint(self.root, verbose=verbose)

class MotionData:
    def __init__(self, numFrames, frameTime, frames):
        if(numFrames != len(frames)):
            print("\033[1;33mWARNING\033[0m: Number of frames does not match number of frames in data. Taking the length of the motion data.")
        self.numFrames = len(frames)
        self.frameTime = frameTime
        self.frames = frames
        self.representationCache = {}
        self.parent = None

    def _setParent(self, parent):
        self.parent = parent

    def addFrame(self, frameData: list[float]) -> None:
        self.frames.append(frameData)

    def getFrame(self, frameIndex: int) -> list[float]:
        return self.frames[frameIndex]
    
    def getFrameSlice(self, startFrame: int, endFrame: int) -> list[list[float]]:
        return self.frames[startFrame:endFrame]

    def getValues(self, valueIndex: int) -> list[float]:
        return [x[valueIndex] for x in self.frames]
    
    def getValuesSlice(self, valueIndex: int, startFrame: int, endFrame: int) -> list[list[float]]:
        return [x[valueIndex] for x in self.frames[startFrame:endFrame]]

    def getValueAtFrame(self, valueIndex: int, frame: int) -> float:
        return self.frames[frame][valueIndex]
    
    def getValuesByJoint(self, joint: Joint) -> list[list[float]]:
        jointIndex = joint.motionIndex
        return [x[jointIndex:jointIndex + joint.getChannelCount()] for x in self.frames]

    def printHead(self, headSize: int = 10, verbose: bool = False) -> None:
        print(f"\033[1;32mMOTION DATA\033[0m")
        print(f"\033[1;32mNumber of frames:\033[0m {self.numFrames}")
        print(f"\033[1;32mNumber of channels:\033[0m {len(self.frames[0])}")
        print(f"\033[1;32mFrame time:\033[0m {self.frameTime}")
        print(f"\033[1;32mMotion dataframe size:\033[0m {self.numFrames} x {len(self.frames[0])}")
        print(f"\033[1;32mHEAD\033[0m")
        for i in range(headSize):
            if not verbose:
                print(f"{self.frames[i][0:6]} ... {self.frames[i][-6:]}")
            else:
                print(f"{self.frames[i]}")

    def getFPS(self) -> float:
        return 1.0 / self.frameTime
    
    def getRepresentation(self, representation: str) -> list[list[float]]:
        representation = representation.lower()
        if not(representation == "euler" or representation == "quaternion" or representation == "sixd" or representation == "matrix" or representation == "rotvec" or representation == "mrp"):
            raise ValueError(f"The representation must be a string : [Euler, Quaternion, SixD, Matrix, RotVec, Mrp]")
        
        if(self.parent is None):
            raise PermissionError(f"You can't change the representation of motion without a parent skeleton")
        
        skeleton = self.parent.skeleton
        
        if(representation not in self.representationCache):
            newFrames = []
            for frame in self.frames:
                newFrame = []
                for joint in skeleton.joints.values():
                    if("EndSite" in joint.name):
                        continue
                    jointIndex = skeleton.getJointIndex(joint.name)
                    rotChannelsOrder = joint.getRotationChannelsOrder()
                    if(joint.getChannelCount() == 3):
                        rot = R.from_euler(rotChannelsOrder, frame[jointIndex:jointIndex+3], degrees=True)
                    else:
                        if(joint.getChannelIndex("Xposition") == 0 or joint.getChannelIndex("Xposition") == 1 or joint.getChannelIndex("Xposition") == 2):
                            pos = frame[jointIndex:jointIndex+3]
                            rot = R.from_euler(rotChannelsOrder, frame[jointIndex+3:jointIndex+6], degrees=True)
                        else:
                            pos = frame[jointIndex+3:jointIndex+6]
                            rot = R.from_euler(rotChannelsOrder, frame[jointIndex:jointIndex+3], degrees=True)
                    
                    if(representation == "quaternion"):
                        rot = rot.as_quat()
                    if(representation == "sixd"):
                        rot = scipyToSixD(rot)
                    if(representation == "matrix"):
                        rot = rot.as_matrix().flatten()
                    if(representation == "rotvec"):
                        rot = rot.as_rotvec()
                    if(representation == "mrp"):
                        rot = rot.as_mrp()
                    
                    if(joint.getChannelCount() == 3):
                        newFrame.extend(rot)
                    elif(joint.getChannelIndex("Xposition") == 0 or joint.getChannelIndex("Xposition") == 1 or joint.getChannelIndex("Xposition") == 2):
                        newFrame.extend(pos)
                        newFrame.extend(rot)
                    else:
                        newFrame.extend(rot)
                        newFrame.extend(pos)

                newFrames.append(newFrame)
                    
            self.representationCache[representation] = newFrames

        return self.representationCache[representation]
    
class BVHData:
    def __init__(self, skeleton, motion):
        self.skeleton = skeleton
        self.motion = motion
        self.skeletonDims = self._calculateSkeletonDims()
        self.motionDims = None
        self.motion._setParent(self)
        self.skeleton._setParent(self)
        
    def _getJointLocalTransformAtFrame(self, jointName, frame, rotationMode = "Euler"):
        joint = self.skeleton.getJoint(jointName)
        jointIndex = self.skeleton.getJointIndex(jointName)
        r = None
        Xpos, Ypos, Zpos = 0.0, 0.0, 0.0
        if("Xrotation" in joint.channels and "Yrotation" in joint.channels and "Zrotation" in joint.channels):
            rotOrder = joint.getRotationChannelsOrder()
            angles = []
            for axis in rotOrder:
                axisName = axis + "rotation"
                if(axisName in joint.channels):
                    idx = jointIndex + joint.channels.index(axisName)
                    angles.append(self.motion.getValueAtFrame(idx, frame))
            r = R.from_euler(rotOrder, angles, degrees=True)
        if("Xposition" in joint.channels and "Yposition" in joint.channels and "Zposition" in joint.channels):
            Xpos = self.motion.getValueAtFrame(jointIndex + joint.channels.index("Xposition"), frame)
            Ypos = self.motion.getValueAtFrame(jointIndex + joint.channels.index("Yposition"), frame)
            Zpos = self.motion.getValueAtFrame(jointIndex + joint.channels.index("Zposition"), frame)

        if(r is None):
            if(rotationMode == "Euler"):
                return R.identity().as_euler('XYZ', degrees=True), [Xpos, Ypos, Zpos]
            if(rotationMode == "Quaternion"):
                return R.identity().as_quat(), [Xpos, Ypos, Zpos]
            if(rotationMode == "Matrix"):
                return R.identity().as_matrix(), [Xpos, Ypos, Zpos]
        else:
            if(rotationMode == "Euler"):
                return r.as_euler('XYZ', degrees=True), [Xpos, Ypos, Zpos]
            if(rotationMode == "Quaternion"):
                return r.as_quat(), [Xpos, Ypos, Zpos]
            if(rotationMode == "Matrix"):
                return r.as_matrix(), [Xpos, Ypos, Zpos]

    def _calculateSkeletonDims(self):
        minX, minY, minZ = float('inf'), float('inf'), float('inf')
        maxX, maxY, maxZ = float('-inf'), float('-inf'), float('-inf')

        fkData0 = self.getFKAtFrame(0)
        for jointName, (rot, pos) in fkData0.items():
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

    def getSkeletonDim(self, dimName: str) -> float:
        if(dimName == "width"):
            return self.skeletonDims[0]
        if(dimName == "height"):
            return self.skeletonDims[1]
        if(dimName == "depth"):
            return self.skeletonDims[2]

    def getSkeletonDims(self) -> list[float]:
        return self.skeletonDims
    
    def _calculateMotionDims(self):
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

    def _getMotionDims(self):
        if(self.motionDims is None):
            self.motionDims = self._calculateMotionDims()
        return self.motionDims
    
    def _getChildFKAtFrame(self, joint, frame, parentTransform, fkFrame):
        localRot, localPos = self._getJointLocalTransformAtFrame(joint.name, frame, "Matrix")
        jointGlobalRot = np.matmul(parentTransform[0], localRot)
        rotatedOffset = np.matmul(parentTransform[0], joint.offset)
        if(any(ch in joint.channels for ch in ["Xposition", "Yposition", "Zposition"]) and joint == self.skeleton.root):
            jointGlobalPos = np.add(np.add(rotatedOffset, localPos), parentTransform[1])
        else:
            jointGlobalPos = np.add(rotatedOffset, parentTransform[1])
        fkFrame.update({joint.name: (jointGlobalRot, jointGlobalPos)})
        for child in joint.children:
            self._getChildFKAtFrame(child, frame, (jointGlobalRot, jointGlobalPos), fkFrame)

    def getFKAtFrame(self, frame: int) -> dict:
        rootJoint = self.skeleton.root
        rootLocalRot, rootLocalPos = self._getJointLocalTransformAtFrame(rootJoint.name, frame, "Matrix")
        fkFrame = {rootJoint.name: (rootLocalRot, rootLocalPos)}
        for child in rootJoint.children:
            self._getChildFKAtFrame(child, frame, (rootLocalRot, rootLocalPos), fkFrame)
        return fkFrame
    
    def getFKAtFrameNormalized(self, frame: int, skeletonDim: str = "height") -> dict:
        fkFrame = self.getFKAtFrame(frame)
        normalizer = self.getSkeletonDim(skeletonDim)
        for jointName, (rot, pos) in fkFrame.items():
            fkFrame[jointName] = (rot, pos / normalizer)
        return fkFrame
    
    def _writeJoint(self, joint, indent = 0):
        lines = []
        tab = '\t' * indent

        # An end site has to be written if and only if, the parent of the deleted joint has no children anymore
        # If we delete a joint, it's parent may still have children, so we don't need to write an end site
        if(joint.parent or "_EndSite" in joint.name):
            if(len(joint.parent.children) == 0 or "_EndSite" in joint.name):
                lines.append(f"{tab}End Site")
                lines.append(f"{tab}{{")
                lines.append(f"\t{tab}OFFSET {' '.join(f'{x:.6f}' for x in joint.offset)}")
                lines.append(f"{tab}}}")
                return lines

        prefix = "ROOT" if indent == 0 else "JOINT"
        lines.append(f"{tab}{prefix} {joint.name}")
        lines.append(f"{tab}{{")
        lines.append(f"\t{tab}OFFSET {' '.join(f'{x:.6f}' for x in joint.offset)}")
        if(len(joint.channels) > 0):
            lines.append(f"\t{tab}CHANNELS {len(joint.channels)} {' '.join(map(str, joint.channels))}")

        if(len(joint.children) > 0):
            for child in joint.children:
                lines.extend(self._writeJoint(child, indent + 1))

        lines.append(f"{tab}}}")
        return lines

    def getHeader(self) -> str:
        header = ["HIERARCHY"]
        header.extend(self._writeJoint(self.skeleton.root, 0))
        header.append("MOTION")
        header.append(f"Frames: {self.motion.numFrames}")
        header.append(f"Frame Time: {self.motion.frameTime}")
        return header
    
    def _rewriteHeaderOffsets(self):
        jointName = ""
        for lineIndex, line in enumerate(self.header):
            if("ROOT" in line or "JOINT" in line): 
                jointName = line.split(" ")[-1]
            if("End Site" in line):
                jointName = jointName + "_EndSite"
            
            if("OFFSET" in line):
                newValuesFormatted = ['{:+0.6f}'.format(v) if v < 0 else '{:0.6f}'.format(v) for v in self.skeleton.getJoint(jointName).offset]
                line = re.sub(r'([-+]?\d*\.\d{6})\s+([-+]?\d*\.\d{6})\s+([-+]?\d*\.\d{6})$', ' '.join(newValuesFormatted), line)
                self.header[lineIndex] = line

    def _getRestPoseJoint(self, joint, canonicalRotation, poseDict):
        poseDict.update({joint.name: joint.getRotationFromOffset(canonicalRotation)})
        for child in joint.children:
            if("EndSite" not in child.name):
                self._getRestPoseJoint(child, canonicalRotation, poseDict)

    def _getRestPose(self, canonicalAxis = "Y"):
        if(canonicalAxis == "X"):
            canonicalRotation = np.array([1, 0, 0])
        elif(canonicalAxis == "Y"):
            canonicalRotation = np.array([0, 1, 0])
        elif(canonicalAxis == "Z"):
            canonicalRotation = np.array([0, 0, 1])
        else:
            print("ERROR: Invalid canonical axis. The canonical axis has to be either X, Y or Z. Default: Y.")
        root = self.skeleton.root
        poseDict = dict()
        self._getRestPoseJoint(root, canonicalRotation, poseDict)
        return poseDict
    
    def _applyOffsetToChildren(self, joint, rNew):
        for child in joint.children:
            length = np.linalg.norm(child.offset)
            canonical = np.array([0, 1, 0])
            child.offset = rNew.apply(canonical * length)
            self._applyOffsetToChildren(child, rNew)

    def _applyRotationToItselfAndChildren(self, joint, oldPose, newPose, rNew):
        for frame in self.motion.frames:
            rotationChannels = [0, 1, 2] if("rotation" in joint.channels[0] or "rotation" in joint.channels[1] or "rotation" in joint.channels[2]) else [3, 4, 5]
            oldRotation = R.from_euler(joint.getRotationChannelsOrder(), [frame[self.skeleton.getJointIndex(joint.name) + rotationChannels[0]],
                                                                    frame[self.skeleton.getJointIndex(joint.name) + rotationChannels[1]],
                                                                    frame[self.skeleton.getJointIndex(joint.name) + rotationChannels[2]]], degrees=True)
            rOld = oldPose[joint.name]
            newRotation = (rNew * rOld.inv() * oldRotation).as_euler(joint.getRotationChannelsOrder(), degrees = True)
            
            print(f"Joint: {joint.name}")
            print(f"Old Pose: {rOld.as_matrix()}")
            print(f"New Pose: {rNew.as_matrix()}")
            print(f"Old Rotation: {oldRotation.as_euler(joint.getRotationChannelsOrder(), degrees=True)}")
            print(f"New Rotation: {newRotation}")
        
            frame[self.skeleton.getJointIndex(joint.name) + rotationChannels[0]] = newRotation[0]
            frame[self.skeleton.getJointIndex(joint.name) + rotationChannels[1]] = newRotation[1]
            frame[self.skeleton.getJointIndex(joint.name) + rotationChannels[2]] = newRotation[2]
        # for child in joint.children:
        #     if(not "_EndSite" in child.name):
        #         rNew = newPose[child.name]
        #         self._applyRotationToItselfAndChildren(child, oldPose, newPose, rNew)

    def _setRestPose(self, poseDict):
        oldPose = copy.deepcopy(self._getRestPose())
        newPose = {}
        for poseName, pose in poseDict.items():
            newPose[poseName] = R.from_euler('XYZ', poseDict[poseName], degrees=True)

        for joint in self.skeleton.joints.values():
            if(joint.name in poseDict.keys()):
                rNew = newPose[joint.name]
                self._applyOffsetToChildren(joint, rNew)
                # newPose = self._getRestPose()
                self._applyRotationToItselfAndChildren(joint, oldPose, newPose, rNew)

        self._rewriteHeaderOffsets()