from scipy.spatial.transform import Rotation as R
import numpy as np

class Joint:
    def __init__(self, name, offset, channels, parent=None):
        self.name = name
        self.offset = offset 
        self.channels = channels
        self.children = []
        self.parent = parent

    def set_offset(self, offset):
        self.offset = offset

    def set_channels(self, channels):
        self.channels = channels

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)

    def get_channel_count(self):
        return len(self.channels)

class Skeleton:
    def __init__(self, root_joint):
        self.root = root_joint
        self.joints = self.build_joint_dict(root_joint)
        self.joint_indexes = self.build_joint_index_dict(root_joint, [0])

    def build_joint_dict(self, joint):
        joint_dict = {joint.name: joint}
        for child in joint.children:
            joint_dict.update(self.build_joint_dict(child))
        return joint_dict

    def build_joint_index_dict(self, joint, current_channel_index=[0]):
        joint_index_dict = {joint.name: current_channel_index[0]}
        current_channel_index[0] += joint.get_channel_count()

        for child in joint.children:
            joint_index_dict.update(self.build_joint_index_dict(child, current_channel_index))
        return joint_index_dict

    def get_joint(self, joint_name):
        return self.joints[joint_name]

    def get_joint_index(self, joint_name):
        return self.joint_indexes[joint_name]

class MotionData:
    def __init__(self, num_frames, frame_time, frames):
        self.num_frames = num_frames
        self.frame_time = frame_time
        self.frames = frames

    def add_frame(self, frame_data):
        self.frames.append(frame_data)

    def get_frame(self, frame_index):
        return self.frames[frame_index]
    
    def get_frame_slice(self, start_frame, end_frame):
        return self.frames[start_frame:end_frame]

    def get_rotations(self, rotation_index):
        return [x[rotation_index] for x in self.frames]

    def get_rotations_slice(self, start_index, end_index):
        return [x[start_index:end_index] for x in self.frames]

    def get_rotation_at_frame(self, rotation_index, frame):
        return self.frames[frame][rotation_index]
    
    def get_rotation_slice_at_frame(self, start_index, end_index, frame):
        return self.frames[frame][start_index:end_index]

    def get_rotation_and_frame_slice(self, start_index, end_index, start_frame, end_frame):
        return self.frames[start_frame, end_frame][start_index:end_index]

class BVHData:
    def __init__(self, skeleton, motion, header):
        self.header = header
        self.skeleton = skeleton
        self.motion = motion
        self.skeleton_dims = self.calculate_skeleton_dims()

    def get_joint_local_transform_at_frame(self, joint_name, frame, rotationMode = "Euler"):
        joint = self.skeleton.get_joint(joint_name)
        jointIndex = self.skeleton.get_joint_index(joint_name)
        r = None
        Xrot, Yrot, Zrot = None, None, None
        Xpos, Ypos, Zpos = 0.0, 0.0, 0.0
        if("Xrotation" in joint.channels and "Yrotation" in joint.channels and "Zrotation" in joint.channels):
            Xrot = self.motion.get_rotation_at_frame(jointIndex + joint.channels.index("Xrotation"), frame)
            Yrot = self.motion.get_rotation_at_frame(jointIndex + joint.channels.index("Yrotation"), frame)
            Zrot = self.motion.get_rotation_at_frame(jointIndex + joint.channels.index("Zrotation"), frame)
            r = R.from_euler('xyz', [Xrot, Yrot, Zrot], degrees=True)
        if("Xposition" in joint.channels and "Yposition" in joint.channels and "Zposition" in joint.channels):
            Xpos = self.motion.get_rotation_at_frame(jointIndex + joint.channels.index("Xposition"), frame)
            Ypos = self.motion.get_rotation_at_frame(jointIndex + joint.channels.index("Yposition"), frame)
            Zpos = self.motion.get_rotation_at_frame(jointIndex + joint.channels.index("Zposition"), frame)

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

    def calculate_skeleton_dims(self):
        min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
        max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')

        fk_data_0 = self.get_FK_at_frame(0)
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

    def get_skeleton_dim(self, dimName):
        if(dimName == "width"):
            return self.skeleton_dims[0]
        if(dimName == "height"):
            return self.skeleton_dims[1]
        if(dimName == "depth"):
            return self.skeleton_dims[2]

    def get_skeleton_dims(self):
        return self.skeleton_dims

    def get_child_FK_at_frame(self, joint, frame, parent_transform, fk_frame):
        local_rot, local_pos = self.get_joint_local_transform_at_frame(joint.name, frame, "Matrix")
        joint_global_rot = np.matmul(parent_transform[0], local_rot)
        rotated_offset = np.matmul(parent_transform[0], joint.offset)
        joint_global_pos = np.add(np.add(rotated_offset, local_pos), parent_transform[1])
        fk_frame.update({joint.name: (joint_global_rot, joint_global_pos)})
        for child in joint.children:
            self.get_child_FK_at_frame(child, frame, (joint_global_rot, joint_global_pos), fk_frame)

    def get_FK_at_frame(self, frame):
        root_joint = self.skeleton.root
        root_local_rot, root_local_pos = self.get_joint_local_transform_at_frame(root_joint.name, frame, "Matrix")
        fk_frame = {root_joint.name: (root_local_rot, root_local_pos)}
        for child in root_joint.children:
            self.get_child_FK_at_frame(child, frame, (root_local_rot, root_local_pos), fk_frame)
        return fk_frame
    
    def get_FK_at_frame_normalized(self, frame, skeletonDim = "height"):
        fk_frame = self.get_FK_at_frame(frame)
        normalizer = self.get_skeleton_dim(skeletonDim)
        for joint_name, (rot, pos) in fk_frame.items():
            fk_frame[joint_name] = (rot, pos / normalizer)
        return fk_frame