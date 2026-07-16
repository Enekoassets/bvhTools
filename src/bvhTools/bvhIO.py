from bvhTools.bvhDataTypes import Joint, Skeleton, MotionData, BVHData

def _checkJointForPosition(joint, rootJoint, nonRootJointsWithPos):
    if joint != rootJoint and any(ch in joint.channels for ch in ["Xposition", "Yposition", "Zposition"]):
        nonRootJointsWithPos.append(joint.name)
    for child in joint.children:
        _checkJointForPosition(child, rootJoint, nonRootJointsWithPos)

def _buildBvhStructure(header, motion, numFrames, frameTime):
    currentIndex = 0
    jointIndex = 0
    rootJoint = None
    while(currentIndex < len(header)):
        if("ROOT" in header[currentIndex]):
            rootJoint, newIndex, jointIndex = _readJoint(header, currentIndex, jointIndex)
            currentIndex = newIndex
            break
        currentIndex += 1
    skeleton = Skeleton(rootJoint)
    # Check if any the BVH joints have position channels, and throw a warning if so
    nonRootJointsWithPos = []
    _checkJointForPosition(skeleton.root, rootJoint, nonRootJointsWithPos)
    if len(nonRootJointsWithPos) > 0:
        print(f"\033[1;33mWARNING\033[0m: The following joints have position channels: {', '.join(nonRootJointsWithPos)}. \nTheir positions will be ignored when calculating FK.\n")

    motionData = MotionData(numFrames=numFrames, frameTime=frameTime, frames = motion)
    bvh = BVHData(skeleton=skeleton, motion=motionData)
    return bvh

def _readEndSite(header, currentIndex, jointIndex, parent):
    currentIndex += 1
    while(currentIndex < len(header)):
        if("{" in header[currentIndex]):
            currentIndex += 1
        if("OFFSET" in header[currentIndex]):
            offset = [float(x) for x in header[currentIndex].lstrip().split(" ")[1:]]
            currentIndex += 1
        if("}" in header[currentIndex]):
            currentIndex += 1
            break
    
    endSite = Joint(name = f"{parent.name}_EndSite", index=jointIndex, offset=offset, channels = [], parent=parent)
    jointIndex += 1
    return endSite, currentIndex, jointIndex
        
def _readJoint(header, currentIndex, jointIndex, parent=None):
    jointName = header[currentIndex].lstrip().split(" ")[1]
    currentIndex += 1
    jointObject = Joint(name = jointName, index=jointIndex, offset=None, channels=[], parent = parent)
    jointIndex += 1
    while(currentIndex < len(header)):
        if("{" in header[currentIndex]):
            currentIndex += 1
        
        if("OFFSET" in header[currentIndex]):
            jointObject._setOffset([float(x) for x in header[currentIndex].lstrip().rstrip().split(" ")[1:]])
            currentIndex += 1
        
        if("CHANNELS" in header[currentIndex]):
            jointObject._setChannels([str(x) for x in header[currentIndex].lstrip().rstrip().split(" ")[2:]])
            currentIndex += 1
        
        if("JOINT" in header[currentIndex]):
            childJoint, currentIndex, jointIndex = _readJoint(header, currentIndex, jointIndex, jointObject)
            jointObject._addChild(childJoint)

        if("End Site" in header[currentIndex]):
            endSite, currentIndex, jointIndex = _readEndSite(header, currentIndex, jointIndex, jointObject)
            jointObject._addChild(endSite)
        
        if("}" in header[currentIndex]):
            currentIndex += 1
            break

    return jointObject, currentIndex, jointIndex

def readBvh(bvhPath: str) -> BVHData:
    """Read a BVH file given a path. This method creates a BVHData object, the base class for a BVH. 

    Parameters
    ----------
        bvhPath : str
            The path of the bvh file.

    Returns
    -------
        BVHData
            The base class that represents a BVH file inside bvhTools. It contains
            all the attributes of a BVH: hierarchy, motion, attributes.
    """
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
    bvhData = _buildBvhStructure(header, motion, numFrames, frameTime)
    return bvhData

def writeBvh(bvhData: BVHData, bvhPath: str, decimals: int = 6) -> None:
    """Write a BVH file given a BVHData object and an output path. 

    Parameters
    ----------
        bvhData : BVHData
            The object that is going to be written to the file.
        bvhPath : str
            The output path for the new file.
        decimals : int = 6
            Number of decimals for the motion data.
    """
    with open(bvhPath, "w") as f:
        for line in bvhData.getHeader():
            f.write(line)
            f.write("\n")
        for frame in bvhData.motion.frames:
            strings = [f"{x:.6f}" for x in frame]
            for string in strings:
                f.write(string + " ")
            f.write("\n")

def writeBvhToCsv(bvhData: BVHData, csvPath: str, decimals: int = 6) -> None:
    """Write a CSV file given a BVHData object and an output path. 
    This method directly writes out the position and Euler rotation channels.

    Parameters
    ----------
        bvhData : BVHData
            The object that is going to be written to the file.
        csvPath : str
            The output path for the new file.
        decimals : int = 6
            Number of decimals for the motion data.
    """
    with open(csvPath, "w") as f:
        for joint in bvhData.skeleton.joints:
            jointObject = bvhData.skeleton.getJoint(joint)
            jointClasses = [jointObject.name +  "_" + str(channel) for channel in jointObject.channels]
            if(len(jointClasses) > 0):
                f.write(",".join(jointClasses) + ",")
        f.write("\n")
        for frame in bvhData.motion.frames:
            f.write(",".join([f"{x:.{decimals}f}" for x in frame]) + "\n")

def writePositionsToCsv(bvhData: BVHData, csvPath: str, decimals: int = 6) -> None:
    """Write the joint positions to a CSV file given a BVHData object
    and an output path. This method computes forwartd kinematics and
    writes out position values for each joint.

    Parameters
    ----------
        bvhData : BVHData
            The object that is going to be written to the file.
        csvPath : str
            The output path for the new file.
        decimals : int = 6
            Number of decimals for the motion data.
    """
    with open(csvPath, "w") as f:
        fkFrame = bvhData.getFKAtFrame(0)
        f.write(",".join([str(x)+ "_x," + str(x)+"_y,"+ str(x)+"_z" for x in fkFrame.keys()]) + "\n")
        for frameIndex in range(bvhData.motion.numFrames):
            fkFrame = bvhData.getFKAtFrame(frameIndex)
            points = [x[1] for x in fkFrame.values()]
            f.write(",".join([f"{x[0]:.{decimals}f}, {x[1]:.{decimals}f}, {x[2]:.{decimals}f}" for x in points]) + "\n")