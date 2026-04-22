# 🤸 Motion editor <!-- {docsify-ignore} -->
The **bvhMotionEditor** class enables to modify aspects related to the motion in the BVH file. It's main difference from the **bvhManipulation** class is that the manipulation class changes the aspects of the animation that change the position or the direction of the entire skeleton, meaning that they change more than the motion only (even if internally the change is just the values on the motion frames), you could argue that they change the entire skeleton.

On the other hand, the motion editor changes aspects just related to the motion, such as the FPS of an animation.

## ⏱️ Resampling the FPS of an animation
##### `resampleFPS(bvh: BVHData, fps: int) -> BVHData`
This function changes the FPS of an animation, by resampling the curve of the original BVH motion section. It returns a new **BVHData** object, with the new animation. It essentially does 3 things:
- It changes the frameTime value of the BVH header.
- It calculates the new motion section: it can either upsample or downsample the original motion. It will resample the original motion curve, by using weighted linear interpolation.
- It changes the numFrames value with the new amount of frames.

```python
from bvhTools.bvhMotionEditor import resampleFPS
# Say that the original BVH is 30 FPS and has 3000 frames
bvh60fps = resampleFPS(bvhData, 60) # It will return an upsampled animation, with 6000 frames
bvh25fps = resampleFPS(bvhData, 25) # It will return a downsampled animation, with 2500 frames
```
