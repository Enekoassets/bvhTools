import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
def showBvhAnimation(bvhData):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    motionDims = bvhData.getMotionDims()
    numFrames = bvhData.motion.num_frames
    frameTime = bvhData.motion.frame_time
    isPaused = [False]
    currentFrame = [0]
    def update(_):            
        ax.clear()
        ax.set_xlim3d(motionDims[0], motionDims[1])
        ax.set_ylim3d(motionDims[4], motionDims[5])
        ax.set_zlim3d(-200, 200)
        fk_frame = bvhData.getFKAtFrame(currentFrame[0])
        points = [x[1] for x in fk_frame.values()]

        x_vals = [p[0] for p in points]
        y_vals = [p[1] for p in points]
        z_vals = [p[2] for p in points]

        ax.scatter(x_vals, z_vals, y_vals, c="b", marker="o")
        if(not isPaused[0]):
            currentFrame[0] = (currentFrame[0] + 1) % numFrames

    def togglePause(event):
        isPaused[0] = not isPaused[0]
        btnPlayPause.label.set_text("Play" if isPaused[0] else "Pause")

    def frameBack(event):
        isPaused[0] = True
        currentFrame[0] -= 1

    def frameForward(event):
        isPaused[0] = True
        currentFrame[0] += 1

    anim = animation.FuncAnimation(fig, update, frames=numFrames, interval=frameTime * 1000, repeat = True)

    axBtnPlayPause = plt.axes([0.1, 0.1, 0.1, 0.05])
    btnPlayPause = Button(axBtnPlayPause, "Pause")
    btnPlayPause.on_clicked(togglePause)

    axBtnBack = plt.axes([0.21, 0.1, 0.1, 0.05])
    btnBack = Button(axBtnBack, "Back")
    btnBack.on_clicked(frameBack)

    axBtnForward = plt.axes([0.32, 0.1, 0.1, 0.05])
    btnForward = Button(axBtnForward, "Forward")
    btnForward.on_clicked(frameForward)

    plt.show()