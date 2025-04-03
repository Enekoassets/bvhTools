from bvhDataTypes import Joint, Skeleton, MotionData, BVHData

def buildBvhStructure(header, motion, num_frames, frame_time):
    current_index = 0
    root_joint = None
    while(current_index < len(header)):
        if("ROOT" in header[current_index]):
            root_joint, newIndex = readJoint(header, current_index)
            current_index = newIndex
            break
        current_index += 1
    skeleton = Skeleton(root_joint)
    motionData = MotionData(num_frames=num_frames, frame_time=frame_time, frames = motion)
    bvh = BVHData(skeleton=skeleton, motion=motionData, header = header)
    return bvh

def readEndSite(header, current_index, parent):
    current_index += 1
    while(current_index < len(header)):
        if("{" in header[current_index]):
            current_index += 1
        if("OFFSET" in header[current_index]):
            offset = [float(x) for x in header[current_index].split(" ")[1:]]
            current_index += 1
        if("}" in header[current_index]):
            current_index += 1
            break
    
    endSite = Joint(name = f"{parent.name}_EndSite", offset=offset, channels = [], parent=parent)

    return endSite, current_index
        
def readJoint(header, current_index, parent=None):
    jointName = header[current_index].split(" ")[1]
    current_index += 1
    jointObject = Joint(name = jointName, offset=None, channels=[], parent = parent)

    while(current_index < len(header)):
        if("{" in header[current_index]):
            current_index += 1
        
        if("OFFSET" in header[current_index]):
            jointObject.setOffset([float(x) for x in header[current_index].rstrip().split(" ")[1:]])
            current_index += 1
        
        if("CHANNELS" in header[current_index]):
            jointObject.setChannels([str(x) for x in header[current_index].rstrip().split(" ")[2:]])
            current_index += 1
        
        if("JOINT" in header[current_index]):
            childJoint, current_index = readJoint(header, current_index, jointObject)
            jointObject.addChild(childJoint)

        if("End Site" in header[current_index]):
            endSite, current_index = readEndSite(header, current_index, jointObject)
            jointObject.addChild(endSite)
        
        if("}" in header[current_index]):
            current_index += 1
            break

    return jointObject, current_index

def readBvhFile(bvhPath):
    header = []
    motion = []
    num_frames = 0
    frame_time = 0.0

    with open(bvhPath, "r") as f:
        # read and process the header
        line = f.readline()
        while(True):
            if("MOTION" in line):
                break
            header.append(line.strip("\n"))
            line = f.readline()

        # read and process the motion data
        line = f.readline()
        while(line != ""):
            if("Frames:" in line):
                num_frames = int(line.split(" ")[1])
            elif("Frame Time:" in line):
                frame_time = float(line.split(" ")[2])
            else:
                motion.append([float(x) for x in line.rstrip().replace("\n", "").split(" ")])
            line = f.readline()
    bvhData = buildBvhStructure(header, motion, num_frames, frame_time)
    return bvhData

def writeBvhFile(bvhData, bvhPath, decimals = 6):
    with open(bvhPath, "w") as f:
        for line in bvhData.header:
            f.write(line)
            f.write("\n")
        f.write("MOTION\n")
        f.write("Frames: " + str(bvhData.motion.num_frames) + "\n")
        f.write("Frame Time: " + str(bvhData.motion.frame_time) + "\n")
        for frame in bvhData.motion.frames:
            strings = [f"{x:.6f}" for x in frame]
            for string in strings:
                f.write(string + " ")
            f.write("\n")

def writeBvhToCsv(bvhData, csvPath, decimals = 6):
    with open(csvPath, "w") as f:
        for joint in bvhData.skeleton.joints:
            jointObject = bvhData.skeleton.getJoint(joint)
            jointClasses = [jointObject.name +  "_" + str(channel) for channel in jointObject.channels]
            if(len(jointClasses) > 0):
                f.write(",".join(jointClasses) + ",")
        f.write("\n")
        for frame in bvhData.motion.frames:
            f.write(",".join([f"{x:.{decimals}f}" for x in frame]) + "\n")

def writePositionsToCsv(bvhData, csvPath, decimals = 6):
    with open(csvPath, "w") as f:
        fkFrame = bvhData.getFKAtFrame(0)
        f.write(",".join([str(x)+ "_x," + str(x)+"_y,"+ str(x)+"_z" for x in fkFrame.keys()]) + "\n")
        for frameIndex in range(bvhData.motion.num_frames):
            fkFrame = bvhData.getFKAtFrame(frameIndex)
            points = [x[1] for x in fkFrame.values()]
            f.write(",".join([f"{x[0]:.{decimals}f}, {x[1]:.{decimals}f}, {x[2]:.{decimals}f}" for x in points]) + "\n")