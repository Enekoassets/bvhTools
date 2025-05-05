import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, TextBox
import numpy as np

def showBvhAnimation(bvhData):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    fig.canvas.manager.window.showMaximized()

    motionDims = bvhData.getMotionDims()
    maxDim = np.max(np.abs(motionDims))
    numFrames = bvhData.motion.numFrames
    frameTime = bvhData.motion.frameTime
    isPaused = [False]
    currentFrame = [0]
    ax.set_xlim3d(-maxDim, maxDim)
    ax.set_ylim3d(-maxDim, maxDim)
    ax.set_zlim3d(-maxDim, maxDim)

    def update(_):            
        for coll in ax.collections:
            coll.remove()
        
        fkFrame = bvhData.getFKAtFrame(currentFrame[0])
        points = [x[1] for x in fkFrame.values()]
        ax.quiver(0, 0, 0, 50, 0, 0, color='r', label='X')  # Red = X
        ax.quiver(0, 0, 0, 0, 50, 0, color='g', label='Y')  # Green = Y
        ax.quiver(0, 0, 0, 0, 0, 50, color='b', label='Z')  # Blue = Z
        ax.scatter([-p[0] for p in points], [p[2] for p in points], [p[1] for p in points], c="b", marker="o")
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