from scipy.spatial.transform import Rotation as R
import numpy as np

def scipyToSixD(scipyRotations):
    matrix = scipyRotations.as_matrix()
    if(matrix.shape == (3, 3)):
        return matrix[:, :2].flatten(order = 'F')
    elif(matrix.ndim == 3 and matrix.shape[1:] == (3, 3)):
        return matrix[:, :, :2].transpose(0, 2, 1).reshape(len(matrix), 6)
    else:
        print(f"\033[1;33mWARNING\033[0m: You must provide a 3x3 or Nx3x3 matrix to convert to 6D. Returning original matrix.")
        return matrix

def sixDToScipy(sixDRotations):
    sixDRotations = np.array(sixDRotations)
    if(sixDRotations.ndim == 1 and sixDRotations.shape[0] == 6):
        a1 = sixDRotations[0:3]
        a2 = sixDRotations[3:6]
        b1 = a1 / np.linalg.norm(a1)
        b2 = (a2 - (np.dot(b1, a2)) * b1) / (np.linalg.norm(a2 - (np.dot(b1, a2)) * b1) + 1e-8)
        b3 = np.cross(b1, b2)
        return R.from_matrix(np.column_stack((b1, b2, b3)))
    elif(sixDRotations.ndim == 2 and sixDRotations.shape[1] == 6):
        rotations = []
        for vector in sixDRotations:
            a1 = vector[0:3]
            a2 = vector[3:6]
            b1 = a1 / np.linalg.norm(a1)
            b2 = (a2 - (np.dot(b1, a2)) * b1) / (np.linalg.norm(a2 - (np.dot(b1, a2)) * b1) + 1e-8)
            b3 = np.cross(b1, b2)
            rotations.append(R.from_matrix(np.column_stack((b1, b2, b3))))
        return R.from_matrix(np.stack(rotations))
    else:
        print(f"\033[1;33mWARNING\033[0m: You must provide a 6D or Nx6D matrix to convert to scipy rotation. Returning original matrix.")
        return sixDRotations