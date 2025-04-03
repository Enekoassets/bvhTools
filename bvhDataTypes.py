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

class Skeleton:
    def __init__(self, root_joint):
        self.root = root_joint
        self.joints = self.buildJointDict(root_joint)
        self.joint_indexes = self.buildJointIndexDict(root_joint, [0])

    def buildJointDict(self, joint):
        joint_dict = {joint.name: joint}
        for child in joint.children:
            joint_dict.update(self.buildJointDict(child))
        return joint_dict

    def buildJointIndexDict(self, joint, current_channel_index=[0]):
        joint_index_dict = {joint.name: current_channel_index[0]}
        current_channel_index[0] += joint.getChannelCount()

        for child in joint.children:
            joint_index_dict.update(self.buildJointIndexDict(child, current_channel_index))
        return joint_index_dict

    def getJoint(self, joint_name):
        return self.joints[joint_name]

    def getJointIndex(self, joint_name):
        return self.joint_indexes[joint_name]

class MotionData:
    def __init__(self, num_frames, frame_time, frames):
        if(num_frames != len(frames)):
            print("WARNING: Number of frames does not match number of frames in data. Taking the length of the motion data.")
        self.num_frames = len(frames)
        self.frame_time = frame_time
        self.frames = frames

    def addFrame(self, frame_data):
        self.frames.append(frame_data)

    def getFrame(self, frame_index):
        return self.frames[frame_index]
    
    def getFrameSlice(self, start_frame, end_frame):
        return self.frames[start_frame:end_frame]

    def getRotations(self, rotation_index):
        return [x[rotation_index] for x in self.frames]

    def getRotationsSlice(self, start_index, end_index):
        return [x[start_index:end_index] for x in self.frames]

    def getRotationAtFrame(self, rotation_index, frame):
        return self.frames[frame][rotation_index]
    
    def getRotationSliceAtFrame(self, start_index, end_index, frame):
        return self.frames[frame][start_index:end_index]

    def getRotationAndFrameSlice(self, start_index, end_index, start_frame, end_frame):
        return self.frames[start_frame, end_frame][start_index:end_index]

class BVHData:
    def __init__(self, skeleton, motion, header):
        self.header = header
        self.skeleton = skeleton
        self.motion = motion
        self.skeleton_dims = self.calculateSkeletonDims()
        self.motion_dims = self.calculateMotionDims()
        
    def getJointLocalTransformAtFrame(self, joint_name, frame, rotationMode = "Euler"):
        joint = self.skeleton.getJoint(joint_name)
        jointIndex = self.skeleton.getJointIndex(joint_name)
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
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

        fk_data_0 = self.getFKAtFrame(0)
        for joint_name, (rot, pos) in fk_data_0.items():
            # Extract the position of each joint
            x, y, z = pos
            
            # Update the min and max values for each axis (X, Y, Z)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            min_z = min(min_z, z)

            max_x = max(max_x, x)
            max_y = max(max_y, y)
            max_z = max(max_z, z)

        # Calculate height, width, and depth
        height = max_y - min_y  # Difference in the Y-axis (vertical)
        width = max_x - min_x   # Difference in the X-axis (horizontal)
        depth = max_z - min_z   # Difference in the Z-axis (depth)

        return [height, width, depth]

    def getSkeletonDim(self, dimName):
        if(dimName == "width"):
            return self.skeleton_dims[0]
        if(dimName == "height"):
            return self.skeleton_dims[1]
        if(dimName == "depth"):
            return self.skeleton_dims[2]

    def getSkeletonDims(self):
        return self.skeleton_dims
    
    def calculateMotionDims(self):
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

        for frameIndex in range(self.motion.num_frames):
            fk_data_root = self.getFKAtFrame(frameIndex)[self.skeleton.root.name][1]
            # Extract the position of each joint
            x, y, z = fk_data_root
            
            # Update the min and max values for each axis (X, Y, Z)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            min_z = min(min_z, z)

            max_x = max(max_x, x)
            max_y = max(max_y, y)
            max_z = max(max_z, z)

        return [min_x, max_x, min_y, max_y, min_z, max_z]

    def getMotionDims(self):
        return self.motion_dims
    
    def getChildFKAtFrame(self, joint, frame, parent_transform, fkFrame):
        local_rot, local_pos = self.getJointLocalTransformAtFrame(joint.name, frame, "Matrix")
        joint_global_rot = np.matmul(parent_transform[0], local_rot)
        rotated_offset = np.matmul(parent_transform[0], joint.offset)
        joint_global_pos = np.add(np.add(rotated_offset, local_pos), parent_transform[1])
        fkFrame.update({joint.name: (joint_global_rot, joint_global_pos)})
        for child in joint.children:
            self.getChildFKAtFrame(child, frame, (joint_global_rot, joint_global_pos), fkFrame)

    def getFKAtFrame(self, frame):
        root_joint = self.skeleton.root
        root_local_rot, root_local_pos = self.getJointLocalTransformAtFrame(root_joint.name, frame, "Matrix")
        fkFrame = {root_joint.name: (root_local_rot, root_local_pos)}
        for child in root_joint.children:
            self.getChildFKAtFrame(child, frame, (root_local_rot, root_local_pos), fkFrame)
        return fkFrame
    
    def getFKAtFrameNormalized(self, frame, skeletonDim = "height"):
        fkFrame = self.getFKAtFrame(frame)
        normalizer = self.getSkeletonDim(skeletonDim)
        for joint_name, (rot, pos) in fkFrame.items():
            fkFrame[joint_name] = (rot, pos / normalizer)
        return fkFrame