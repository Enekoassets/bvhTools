<!-- omit from toc -->
<p align="center">
  <img src="docs/icon.svg" width="150"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/bvhTools/">
    <img src="https://img.shields.io/pypi/v/bvhTools?color=red&label=PyPI"/>
  </a>
  <a href="https://pypi.org/project/bvhTools/">
    <img src="https://img.shields.io/pypi/dm/bvhTools?color=yellow&label=Downloads"/>
  </a>
  <a href="https://github.com/enekoassets/bvhTools/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/enekoassets/bvhTools?color=green"/>
  </a>
  <a href="https://enekoassets.github.io/bvhTools/">
    <img src="https://img.shields.io/badge/docs-online-blue"/>
  </a>
</p>

**bvhTools** is a Python library to work with BVH (Biovision Hierarchy) files. It enables to load, modify and write BVH files in very few lines of code. This project is being developed in the context of a phD, so the library contains many BVH operations that I need to make often.

<!-- omit from toc -->
# 🌟 Functionalities
- 📖/✏️ Reading and writing BVH files
- 🏃 Performing Forward Kinematics
- 🤚 Manipulating animations (moving, rotating, mirroring)
- 🤸 Resampling and editing animations
- 🔪 Slicing (dividing and joining)
- 💀 Editing the skeleton
- 👀 Viewing animations
- 📊 Calculating metrics
- 📐 Converting between angle representations
- 📋 Writing data to CSV files
- 🖥️ CLI interface functions

# 📋 Documentation
The documentation to use this library can be found [here](https://enekoassets.github.io/bvhTools/).

# 🧰 Installation
To install and use **bvhTools**, just install it with pip.
```python
pip install bvhTools
```
The python package is still work in progress, so it may have some problems. In that case, you can open an issue or a pull request on GitHub.

If you find bvhTools useful, please give it a star! :)

# 🗺️ Roadmap

| Functionality | Status |
| --- | --- |
| Read / Write | 🟢 Completed |
| Forward Kinematics | 🟢 Completed |
| Basic visualization with matplotlib | 🟢 Completed |
| Slice / Join animations | 🟢 Completed |
| Rotate animations | 🟢 Completed |
| Move animations | 🟢 Completed |
| Skeleton Standing on floor | 🟢 Completed |
| Write to CSV | 🟢 Completed |
| Scale skeletons | 🟢 Completed |
| Remove limbs | 🟢 Completed |
| Print skeleton and motion summary | 🟢 Completed |
| Get hierarchy and joint information | 🟢 Completed |
| Metrics: speeds, accelerations, jerks | 🟢 Completed |
| Metrics: average speeds, accelerations, jerks | 🟢 Completed |
| Metrics: average pose | 🟢 Completed |
| Metrics: foot contact masks | 🟢 Completed |
| CLI functions for simple and fast editing | 🟢 Completed |
| Convert Scipy angles to 6D representation | 🟢 Completed |
| Resampling FPS (upsample, downsample by weighted average) | 🟢 Completed |
| Advanced visualization with raylib | 🟢 Completed |
| Mirror Skeletons | 🟢 Completed |
| Documentation | 🔄 Continuous |
| Edit rest pose | 🐣 Planned |
| Metrics: spectral analysis and fast fourier transform | 🐣 Planned |
| Metrics: foot sliding masks | 🐣 Planned |
| **Machine learning pipeline integration** | 🧑‍💻 Active |
| - ML pipeline: automatic dataset loading | 🟢 Completed |
| - ML pipeline: data normalization | 🟢 Completed |
| - ML pipeline: attaching labels | 🟢 Completed |
| - ML pipeline: attaching other data modalities | 🐣 Planned |
| - ML pipeline: windowing and lazy views | 🟢 Completed |
| - ML pipeline: data splits | 🟢 Completed |
| - ML pipeline: pytorch integration | 🟢 Completed |
| - ML pipeline: materializing datasets | 🟢 Completed |

Feel free to suggest more functionalities that you think might be helpful! Code contributions are also welcome!
