## 🏃 Forward Kinematics <!-- {docsify-ignore} -->
The forward kinematics module returns a **Dict** object containing the global positions and rotations of the skeleton in a specific frame.

```python
fk = bvhData.getFKAtFrame(42)
```

It can also return the normalized FK positions (the rotations remain the same). The normalization dimension is the height of the skeleton by default, but the options are ["height", "width", "depth"].

```python
fk = bvhData.getFKAtFrameNormalized(42)
```