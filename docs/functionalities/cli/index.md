# 🖥️ CLI functions<!-- {docsify-ignore} -->
**bvhTools** provides a **Command Line Interface (CLI)** to be able to make some operations very easily, from the command line of your system, without the need to create and execute python scripts.

To directly use **bvhTools** from your **CLI**, use the command *bvhToolsCli*. 

You can use *bvhToolsCli --help* to directly print usage information. Otherwise, the information on how to use **bvhToolsCli** is on this page of the docs.

## 🪛 Available commands
These are the commands that are available to use from the CLI:
- 🎯 [Center](#-center)
- 🔃 [Rotate](#-rotate)
- 👀 [View](#-view)
- 🔪 [Slice](#-slice)
- 📋 [Csv](#-csv)
  
### 🎯 Center
```
bvhToolsCli center --bvhFile {path} --outputFile {path} --centeringOption {feet, root, xz}
```
The center command **reads** an input BVH file, **centers** it (centers the skeleton's feet, root or just in the X and Z axes without changing the Y value) and **writes** the resulting BVH to a new output file. The way of centering (feet, root or XZ) can be specified with the *--centeringOption* argument.
#### Example
```
bvhToolsCli center --bvhFile input.bvh --outputFile output.bvh --centeringOption feet
```
### 🔃 Rotate
```
bvhToolsCli rotate --bvhFile {path}, --outputFile {path} --rotationOption {local, world} --angles {X_angle Y_angle Z_angle}
```
The rotate command **reads** an input BVH file, **rotates** it (in local or world space, given the X, Y and Z rotations) and **writes** the resulting BVH to a new output file. The local/world option can be specified with the *--rotationOption* argument.
#### Example:
```
python3 bvhToolsCli.py rotate --bvhFile input.bvh --outputFile output.bvh --rotationOption local --angles 45 0 -90
```
### 👀 View
```
bvhToolsCli view --bvhFile {path} [--noPoints] [--noLines] [--noLabels]
```
The view command **opens** a BVH file, and shows the animation in matplotlib. By default, it shows the joint points, the lines connecting them and the labels. These options can be turned off with their respective flags, *--noPoints*, *--noLines* and *--noLabels*.
#### Example
```
bvhToolsCli view --bvhFile input.bvh --noLabels
```
### 🔪 Slice
```
bvhToolsCli slice --bvhFile {path} --outputFile {path} --startFrame {start} --endFrame {end}
```
The rotate command **reads** an input BVH file, takes a **slice** of the motion and **writes** the resulting BVH to a new output file.
#### Example
```
bvhToolsCli slice --bvhFile input.bvh --outputFile output.bvh --startFrame 100 --endFrame 500
```
### 📋 Csv
```
bvhToolsCli csv --bvhFile {path} --outputFile {path} --csvOption {positions, bvh}
```
The csv command **reads** an input BVH file and **writes** it's contents to a csv file. It can write either the entire bvh or the global positions after performing forward kinematics, this can be specified with the *--csvOption* argument.
#### Example
```
bvhToolsCli csv --bvhFile input.bvh --outputFile output.csv --csvOption positions
```