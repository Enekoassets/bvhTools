from bvhTools.bvhDataTypes import Joint, Skeleton, MotionData, BVHData

def checkJointForPosition(joint, rootJoint, nonRootJointsWithPos=[]):
    if joint != rootJoint and any(ch in joint.channels for ch in ["Xposition", "Yposition", "Zposition"]):
        nonRootJointsWithPos.append(joint.name)
    for child in joint.children:
        checkJointForPosition(child)

def buildBvhStructure(header, motion, numFrames, frameTime):
    currentIndex = 0
    rootJoint = None
    while(currentIndex < len(header)):
        if("ROOT" in header[currentIndex]):
            rootJoint, newIndex = readJoint(header, currentIndex)
            currentIndex = newIndex
            break
        currentIndex += 1
    skeleton = Skeleton(rootJoint)
    # Check if any the BVH joints have position channels, and throw a warning if so
    nonRootJointsWithPos = []
    checkJointForPosition(skeleton.root, rootJoint, nonRootJointsWithPos)
    if len(nonRootJointsWithPos) > 0:
        print(f"WARNING: The following joints have position channels, their positions will be ignored when calculating FK.")
        for jointName in nonRootJointsWithPos:
            print(f"\t{jointName}")
    motionData = MotionData(numFrames=numFrames, frameTime=frameTime, frames = motion)
    bvh = BVHData(skeleton=skeleton, motion=motionData, header = header)
    return bvh

def readEndSite(header, currentIndex, parent):
    currentIndex += 1
    while(currentIndex < len(header)):
        if("{" in header[currentIndex]):
            currentIndex += 1
        if("OFFSET" in header[currentIndex]):
            offset = [float(x) for x in header[currentIndex].split(" ")[1:]]
            currentIndex += 1
        if("}" in header[currentIndex]):
            currentIndex += 1
            break
    
    endSite = Joint(name = f"{parent.name}_EndSite", offset=offset, channels = [], parent=parent)

    return endSite, currentIndex
        
def readJoint(header, currentIndex, parent=None):
    jointName = header[currentIndex].split(" ")[1]
    currentIndex += 1
    jointObject = Joint(name = jointName, offset=None, channels=[], parent = parent)

    while(currentIndex < len(header)):
        if("{" in header[currentIndex]):
            currentIndex += 1
        
        if("OFFSET" in header[currentIndex]):
            jointObject.setOffset([float(x) for x in header[currentIndex].rstrip().split(" ")[1:]])
            currentIndex += 1
        
        if("CHANNELS" in header[currentIndex]):
            jointObject.setChannels([str(x) for x in header[currentIndex].rstrip().split(" ")[2:]])
            currentIndex += 1
        
        if("JOINT" in header[currentIndex]):
            childJoint, currentIndex = readJoint(header, currentIndex, jointObject)
            jointObject.addChild(childJoint)

        if("End Site" in header[currentIndex]):
            endSite, currentIndex = readEndSite(header, currentIndex, jointObject)
            jointObject.addChild(endSite)
        
        if("}" in header[currentIndex]):
            currentIndex += 1
            break

    return jointObject, currentIndex

def readBvh(bvhPath):
    header = []
    motion = []
    numFrames = 0
    frameTime = 0.0

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
                numFrames = int(line.split(" ")[1])
            elif("Frame Time:" in line):
                frameTime = float(line.split(" ")[2])
            else:
                motion.append([float(x) for x in line.rstrip().replace("\n", "").split(" ")])
            line = f.readline()
    bvhData = buildBvhStructure(header, motion, numFrames, frameTime)
    return bvhData

def writeBvh(bvhData, bvhPath, decimals = 6):
    with open(bvhPath, "w") as f:
        for line in bvhData.header:
            f.write(line)
            f.write("\n")
        f.write("MOTION\n")
        f.write("Frames: " + str(bvhData.motion.numFrames) + "\n")
        f.write("Frame Time: " + str(bvhData.motion.frameTime) + "\n")
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
        for frameIndex in range(bvhData.motion.numFrames):
            fkFrame = bvhData.getFKAtFrame(frameIndex)
            points = [x[1] for x in fkFrame.values()]
            f.write(",".join([f"{x[0]:.{decimals}f}, {x[1]:.{decimals}f}, {x[2]:.{decimals}f}" for x in points]) + "\n")