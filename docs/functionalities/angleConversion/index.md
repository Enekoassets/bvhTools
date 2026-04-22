# 📐 Angle conversion<!-- {docsify-ignore} -->
**bvhTools** uses [Scipy's rotation module](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.html) for the internal representation of angles. We also suggest to use scipy to correctly control the formats (Euler, angle-axis, rotation matrices...) and convert from one to another.

However, in machine learning contexts, angle representations being continuous is very important. For this reason, rotation matrices are a good choice. However, a very extended practise is to use 6D representations for angles, based on a [paper by Zhou et al.](https://zhouyisjtu.github.io/project_rotation/rotation.html)

Scipy does not currently have the 6D representation available, so **bvhTools** offers 2 methods to use them: one to convert from scipy rotations to 6D and another to convert back from 6D to scipy rotations, using [Gram-Schmidt orthogonalization](https://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process).

### Scipy rotation to 6D representation
##### `scipyToSixD(scipyRotations: scipy.Rotation) -> numpy.array`

This method takes as input a Scipy rotation (which can contain just one rotation or many of them) and converts each one to the corresponding 6D representation, by striping the first two columns and concatenating them into a 6D vector each.

```python
from bvhTools.angleConversion import scipyToSixD
rotations = np.from_euler("XYZ", [[0, 90, 0], [123, 42.42, 0]], degrees = True) # Scipy's rotation object containing 2 rotations
sixDrotations = scipyToSixD(rotations) # This will return a numpy array with shape 2x6
```

### 6D representation to scipy rotation
##### `sixDToScipy(sixDRotations: List[float] | numpy.array[List[float]]) -> scipy.Rotation` 

This method takes as input a numpy array of 6D vectors (or a single 6D vector), maps each one to rotation space and returns a Scipy Rotation instance (containing 1 or more individual rotations). It uses Gram-Schmidt orthogonalization to ensure that the 6D vector is mapped to a plausibile rotation instance, by ensuring that the columns of the 3x3 rotation matrix are orthonormal.
```python
from bvhTools.angleConversion import sixDToScipy
sixDRotations = np.array([[0,0,−1,0,1,0], [0.739,0,−0.673,0.565,−0.544,0.621]]) # Numpy array containing 2 6D representations
rotations = sixDToScipy(sixDRotations) # This will return a Scipy's rotation object containing 2 rotations
```
