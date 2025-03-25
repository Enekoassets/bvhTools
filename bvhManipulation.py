import copy

def centerSekeletonRoot(bvhData, fk_frame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    frame = bvhDataCopy.motion.get_frame(fk_frame)
    rootIndex = bvhDataCopy.skeleton.get_joint_index(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonFeet(bvhData, leftFootName = "LeftFoot", rightFootName = "RightFoot", fk_frame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    if(leftFootName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Left foot name ({leftFootName}) not found in skeleton")
    if(rightFootName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Right foot name ({rightFootName}) not found in skeleton")

    avgFootHeight = (bvhDataCopy.get_FK_at_frame(fk_frame)[leftFootName][1][1] + bvhDataCopy.get_FK_at_frame(fk_frame)[rightFootName][1][1]) / 2
    avgRootHeight = bvhDataCopy.get_FK_at_frame(fk_frame)[bvhDataCopy.skeleton.root.name][1][1]
    frame = bvhDataCopy.motion.get_frame(fk_frame)
    rootIndex = bvhDataCopy.skeleton.get_joint_index(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]), -float(frame[rootIndex + 1]) + (avgRootHeight - avgFootHeight), -float(frame[rootIndex + 2])]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy

def centerSkeletonAroundJoint(bvhData, jointName, fk_frame=0):
    bvhDataCopy = copy.deepcopy(bvhData)
    if(jointName not in bvhDataCopy.skeleton.joints):
        raise Exception(f"Selected joint ({jointName}) not found in skeleton")
    
    forward_frame = bvhDataCopy.get_FK_at_frame(fk_frame)
    frame = bvhDataCopy.motion.get_frame(fk_frame)
    jointOffsets = forward_frame[jointName][1] - forward_frame[bvhDataCopy.skeleton.root.name][1]
    rootIndex = bvhDataCopy.skeleton.get_joint_index(bvhDataCopy.skeleton.root.name)
    offsets = [-float(frame[rootIndex]) - jointOffsets[0], -float(frame[rootIndex + 1]) - jointOffsets[1], -float(frame[rootIndex + 2]) - jointOffsets[2]]
    for frame in bvhDataCopy.motion.frames:
        frame[rootIndex] += offsets[0]
        frame[rootIndex+1] += offsets[1]
        frame[rootIndex+2] += offsets[2]

    return bvhDataCopy
