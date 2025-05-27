import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, TextBox
from matplotlib import get_backend
import numpy as np

def showBvhAnimation(bvhData, showPoints = True, showLines = True, showQuivers = True, 
                     showLabels = False, pointColor = "#4287f5", pointMarker = "o", lineColor = "#666666", lineWidth = 2):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    manager = plt.get_current_fig_manager()
    backend = get_backend()

    # Try to maximize the window, but fail silently if it doesn't work
    try:
        if backend == 'TkAgg':
            try:
                manager.window.state('zoomed')  # Windows
            except Exception:
                manager.window.attributes('-zoomed', True)  # Linux (X11)
        elif backend == 'QtAgg':
            manager.window.showMaximized()
        elif backend == 'WXAgg':
            manager.frame.Maximize(True)
    except Exception as e:
        print(f"[Info] Could not maximize window: {e}")

    motionDims = bvhData.getMotionDims()
    maxDim = np.max(np.abs(motionDims))
    quiverSize = 0.05 * maxDim
    numFrames = bvhData.motion.numFrames
    frameTime = bvhData.motion.frameTime
    isPaused = [False]
    currentFrame = [0]
    ax.set_xlim3d(-maxDim, maxDim)
    ax.set_ylim3d(-maxDim, maxDim)
    ax.set_zlim3d(-maxDim, maxDim)

    parentList = bvhData.skeleton.getHierarchyIndexesList()
    labelList = list(bvhData.skeleton.joints.keys())

    def update(_):            
        for coll in ax.collections[:]:
            coll.remove()
        for line in ax.lines[:]:
            line.remove()
        for text in ax.texts[:]:
            text.remove()
        
        fkFrame = bvhData.getFKAtFrame(currentFrame[0])
        points = [x[1] for x in fkFrame.values()]
        if(showQuivers):
            ax.quiver(0, 0, 0, quiverSize, 0, 0, color='r', label='X')  # Red = X
            ax.quiver(0, 0, 0, 0, quiverSize, 0, color='g', label='Y')  # Green = Y
            ax.quiver(0, 0, 0, 0, 0, quiverSize, color='b', label='Z')  # Blue = Z

        if(showPoints):
            ax.scatter([-p[0] for p in points], [p[2] for p in points], [p[1] for p in points], c=pointColor, marker=pointMarker)
        
        if(showLabels):
            for index, point in enumerate(points):
                ax.text(-point[0], point[2], point[1], labelList[index])

        if(showLines):
            for index, parent in enumerate(parentList):
                if(parent!=-1):
                    ax.plot([-points[index][0], -points[parent][0]],
                            [points[index][2], points[parent][2]],
                            [points[index][1], points[parent][1]], color=lineColor, linewidth=lineWidth)

        if(not isPaused[0]):
            currentFrame[0] = (currentFrame[0] + 1) % numFrames
            label.set_text(f"Frame: {currentFrame[0]}")

    def togglePause(event):
        isPaused[0] = not isPaused[0]
        btnPlayPause.label.set_text("Play" if isPaused[0] else "Pause")
        textbox.set_val(str(currentFrame[0]))
        label.set_text(f"Frame: {currentFrame[0]}")

    def frameBack(event):
        isPaused[0] = True
        btnPlayPause.label.set_text("Play" if isPaused[0] else "Pause")
        currentFrame[0] -= 1
        if(currentFrame[0] < 0):
            currentFrame[0] = numFrames - 1
        textbox.set_val(str(currentFrame[0]))
        label.set_text(f"Frame: {currentFrame[0]}")

    def frameForward(event):
        isPaused[0] = True
        btnPlayPause.label.set_text("Play" if isPaused[0] else "Pause")
        currentFrame[0] += 1
        if(currentFrame[0] >= numFrames):
            currentFrame[0] = 0
        textbox.set_val(str(currentFrame[0]))
        label.set_text(f"Frame: {currentFrame[0]}")

    def faster(event):
        global anim
        newInterval = anim.event_source.interval * 0.5
        anim.event_source.stop()
        anim = animation.FuncAnimation(fig, update, frames=numFrames, interval=newInterval, repeat=True)
        plt.draw()

    def slower(event):
        global anim
        newInterval = anim.event_source.interval * 2
        anim.event_source.stop()
        anim = animation.FuncAnimation(fig, update, frames=numFrames, interval=newInterval, repeat=True)
        plt.draw()

    def goToFrame(text):
        if(int(text) < numFrames):
            currentFrame[0] = int(text)
        else:
            currentFrame[0] = numFrames - 1
        label.set_text(f"Frame: {currentFrame[0]}")

    global anim
    anim = animation.FuncAnimation(fig, update, frames=numFrames, interval=frameTime * 1000, repeat = True)

    axBtnPlayPause = plt.axes([0.45, 0.05, 0.1, 0.05])
    btnPlayPause = Button(axBtnPlayPause, "Pause")
    btnPlayPause.on_clicked(togglePause)

    axBtnBack = plt.axes([0.34, 0.05, 0.1, 0.05])
    btnBack = Button(axBtnBack, "Back")
    btnBack.on_clicked(frameBack)

    axBtnForward = plt.axes([0.56, 0.05, 0.1, 0.05])
    btnForward = Button(axBtnForward, "Forward")
    btnForward.on_clicked(frameForward)

    axBtnFaster = plt.axes([0.395, 0.9, 0.1, 0.05])
    btnFaster = Button(axBtnFaster, "Faster")
    btnFaster.on_clicked(faster)

    axBtnSlower = plt.axes([0.505, 0.9, 0.1, 0.05])
    btnSlower = Button(axBtnSlower, "Slower")
    btnSlower.on_clicked(slower)
    
    ax_textbox = plt.axes([0.8, 0.9, 0.1, 0.05])  # [x, y, width, height]
    textbox = TextBox(ax_textbox, "Go to frame: ")
    textbox.on_submit(goToFrame)

    label = fig.text(0.475, 0.85, "Frame: 0", fontsize=12)

    plt.show()