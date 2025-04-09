<!-- omit from toc -->
# bvhTools
**bvhTools** is a Python library to work with BVH (Biovision Hierarchy) files. It enables to load, modify and write BVH files in very few lines of code. This project is being developed in the context of a phD, so the library contains many BVH operations that I need to make often.

<!-- omit from toc -->
# 🌟 Functionalities
- Reading and writing BVH files
- Performing Forward Kinematics
- Manipulating BVH files (moving and rotating skeletons)
- BVH Slicing (partitioning and putting together motion data)
- BVH viewing using matplotlib
- Writing data to CSV files (world positions or  local positions + rotations)

<!-- omit from toc -->
# Index
- [📖 Reading and ✏️ writing BVH files](./functionalities/readWrite/index.md)
- [🏃 Forward Kinematics](#-forward-kinematics)
- [🤚 BVH manipulation](#-bvh-manipulation)
  - [Centering the skeleton root](#centering-the-skeleton-root)
  - [Centering the skeleton feet](#centering-the-skeleton-feet)
  - [Centering the skeleton on the X and Z axes](#centering-the-skeleton-on-the-x-and-z-axes)
  - [Centering the skeleton around a specific joint](#centering-the-skeleton-around-a-specific-joint)
  - [Moving the skeleton around (adding an offset to the animation)](#moving-the-skeleton-around-adding-an-offset-to-the-animation)
  - [Rotating the BVH in world coords](#rotating-the-bvh-in-world-coords)
  - [Rotating the BVH in local coords](#rotating-the-bvh-in-local-coords)
- [🔪 BVH slicing](#-bvh-slicing)
- [👀 BVH viewer](#-bvh-viewer)
- [📋 Writing data to CSV files](#-writing-data-to-csv-files)
  - [Writing positions and rotations to the CSV](#writing-positions-and-rotations-to-the-csv)
  - [Writing position data to the CSV (FK)](#writing-position-data-to-the-csv-fk)