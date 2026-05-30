# 🤖 Machine Learning Integration <!-- {docsify-ignore} -->
**Note: You can find a jupyter notebook for the machine learning pipeline in the tutorials folder of the master branch.**

The library has direct integration into machine learning pipelines. This is the general process to follow:

1) Load the data from a folder/filelist/objects to a `BVHDataset` class.

2) [*OPTIONAL*] Attach labels to the loaded animations.

3) [*OPTIONAL*] Attach other data modalities to the loaded animations (text, audio). **Note: this feature has not yet been implemented**.

4) [*OPTIONAL*] Define train, validation and/or test splits.

5) Create a lazy view of the dataset in a `BVHDatasetView` class, by choosing windowing parameters, normalization method and internal angle representation. This class will not modify the original data, it is just a wrapper to efficiently access the sequences in the dataset with minimal memory overhead.

6) You can directly use this `BVHDatasetView` object inside a PyTorch pipeline.

7) [*OPTIONAL*] "Materialize" the dataset view: you can apply all the windowing, normalization and representation settings and load these new windows of motion directly into memory, by using a `BVHDatasetViewMaterialized` class. This class will contain actual numpy arrays of windows loaded in memory.

## ➡️ Getting started: ML pipeline process
### 1) 🔋 Loading the data: The `BVHDataset` class
The first step to use `bvhTools` in a machine learning pipeline is to load the data. To do that, you have to use the `BVHDataset` object. The `BVHDataset` object is just a list of `BVHData` objects that can be loaded in 3 different ways:

#### A) Loading the data from a folder
`BVHDataset.fromFolder(paths: str | List[str], recursive: bool = False, pattern: str = "") -> BVHDataset`

This is the easiest way to load bvh files in bulk. By providing the absolute path or paths as a strings or list of strings, **bvhTools** will automatically load all the files in the folder(s) and create a new `BVHDataset` object.

- The `recursive` flag can be set to True if you also want to automatically load the files in the subfolders of the specified folder(s).

- The `pattern` string can be used to filter the loaded data: if you specify a string as pattern, the method will only load the files that contain the pattern in the name.

*Note: if you need a more fine-grained loading, check the following sections to learn how to load files using a filelist or BVHData objects.*

#### B) Loading the data using a filelist txt file
`BVHDataset.fromFilelist(filelists: str | List[str]) -> BVHDataset`

This method permits to use a predefined file list (or multiple lists) to have complete control over the loaded files in the `BVHDataset` object. Then, you must provide the path(s) of the filelist(s) to the function.

The file list must contain the absolute file paths to work correctly. The following example is a possible file list txt file.

```
datasets/lafan1/walk01_subject1.bvh
datasets/lafan1/walk02_subject1.bvh
datasets/lafan1/walk01_subject2.bvh
datasets/lafan1/walk02_subject2.bvh
datasets/lafan1/aim01_subject1.bvh
datasets/lafan1/aim01_subject2.bvh
datasets/lafan1/obstacles01_subject1.bvh
```

#### C) Loading the data from BVHData objects
`BVHDataset.fromObjects(objects: BVHData | List[BVHData]) -> BVHDataset`

*Note: if a dataset is created from BVHData objects, labels can't be attached, since the labelling system uses the bvh file names as pointers to the files.*

The last option to create a `BVHDataset` object is to directly pass a list of preloaded `BVHData` objects (or a single `BVHData` object). This option permits to do have very fine grained control over the loaded data, as it is necessary to load the files one by one, and each one of them can have specific transformations separately. It is also useful for testing purposes.

### 2) 🏷️ [*OPTIONAL*] Attaching labels
`BVHDataset.attachLabels(path: str) -> None`

Labels can be attached to animation files, so each animation file has it's own label or label set. `bvhTools` permits two types of labels, sequence labels and temporal labels:

- **Sequence labels** are tied to an entire bvh file. They describe the motion of the entire file.

- **Temporal labels** contain specific timestamps, and they are used for more fine-grained descriptions of the motion. For this reason, each temporal label needs to have one start point. The end point of the label will be the start point of the next temporal label, or, by default, the end of the animation sequence. You can decide how to return temporal labels using different rules, explained [in the temporal label yaml example](#yaml-file-example-of-sequence-labels).

When using bvhTools, the labels have to be defined in a **yaml** file. The path of this yaml file has to be passed to the `attachLabels` function. The labels in the file will be returned by the `__getitem__` method, explained in [section 5](#5--using-the-data-view-in-your-ml-pipeline).

```python
dataset.attachLabels("path/to/label/file.yaml")
```

In the yaml file, first you have to put the absolute motion file path as the first key, which will have the labels inside. A yaml file can have sequence labels, temporal labels, or both. The next three examples show the three possibilities:

#### YAML file example of sequence labels
```
actions/gun_1.bvh:
  sequence:
    action: gun_hold
    speed: fast
actions/gun_2.bvh:
  sequence:
    action: gun_hold
    speed: slow
actions/walk_01.bvh:
  sequence:
    action: walk
    speed: slow
actions/run_01.bvh:
  sequence:
    action: run
    speed: fast
```

#### YAML file example of temporal labels
If you are using temporal labels, you have to define if the start timestamps are defined using frames or seconds, by first defining the `timeUnit` attribute (if it is not defined, it's "`frames`" by default).

Then, you have to choose how will the labels be returned if a window contains more than one label. There are three available options: `first`, `coverage`, `all`. 

- `first`: `__getitem__` will return the label corresponding to the first frame of the sequence.  
- `coverage`: `__getitem__` will return the label that covers most time inside the window. In case that two labels have the same coverage, it will return the first one of the two.
- `all`: `__getitem__` will return all the labels present in the time window.

In other words, by defining the `temporalRule` attribute (if it is not defined, it's "`first`" by default) you can choose what labels to return when a window has more than one temporal label in its time span.

```
timeUnit: frames
temporalRule: all
actions/gun_01.bvh:
  temporal:
    - start: 0
      label: aim
    - start: 900
      label: shoot
    - start: 1200
      label: aim
actions/gun_02.bvh:
  temporal:
    - start: 0
      label: aim
```

#### YAML file example of mixed labels
A single yaml file can contain both types of labels, and the BVHDataset class will return them as separate attributes.
```
timeUnit: seconds
temporalRule: coverage
actions/gun_01.bvh:
  sequence:
    action: gun_hold
    speed: fast
  temporal:
    - start: 0.0
      label: aim
      speed: fast
    - start: 30.0
      label: shoot
      speed: fast
    - start: 40.0
      label: aim
      speed: slow
actions_gun_02.bvh:
  sequence:
    action: gun_hold
    speed: slow
  temporal:
    - start: 0.0
      label: aim
      speed: slow
```

### 3) 📎 [*OPTIONAL*] Attaching other data modalities [NOT IMPLEMENTED YET]

#### A) 📖 Attaching text

#### B) 🎵 Attaching audio

### 4) ✂️ Defining splits
`defineSplits(path: str) -> None`

**bvhTools** enables to do training, validation and test splits (or however you want to call the splits, you can also make any number of splits) using yaml files. The splits are done file-wise: since it is not desirable to have similar time windows in different splits to avoid data leaking, each file can only go in one split. The splits can have any arbitrary name, and you can have as many splits as you like.

*Note: If you need to have one part of a file in a split and another part in another one, check the [splitting BVH files](../slicing/index.md) section, to divide the file in parts.*

First, you have to define the yaml files containing the splits. There are two options or rules to make the splits, `splitRule: files` and `splitRule: pattern`. Both cases are explained below with examples.
- `splitRule: files` You define each file individually in each split. 

  *Note: this means that a file might not be in any split or that in may be in more than one split. You will receive a warning in those cases.*
  ```
  splitRule: files
  splits:
    train:
      - actions/gun_1_subject1.bvh
      - actions/gun_2_subject1.bvh
      - actions/gun_1_subject2.bvh
      - actions/gun_2_subject2.bvh
      - actions/aim_1_subject3.bvh
    validation:
      - actions/gun_1_subject4.bvh
    test:
      - actions/gun_1_subject5.bvh
  ```

- `splitRule: pattern` You define patterns for each split, then, the files that have that pattern in the name will be introduced in the split.

  *Note: this means that a file might not be in any split or that in may be in more than one split. You will receive a warning in those cases.*
  ```
  splitRule: pattern
  splits:
    train:
      - subject1
      - subject2
      - subject3
    validation:
      - subject4
    test:
      - subject5
  ```

After making the splits, each file remains marked with its corresponding split. Next, you can create a data view in the next step and you can select the split for the dataview. This way, the dataset view object will represent a specific split. You have to use the `BVHDatasetView.selectSplit(splitName: str)` for that. The other option is to use the `BVHDatasetView.createSplits()` to create n `BVHDatasetView` objects, each containing one split. This is explained [here](#selecting-a-split-or-create-all-splits) more in detail.

### 5) 🪟 Creating a data view
`BVHDataset.view(windowLength: int, stride: int, representation: str = "euler") -> BVHDatasetView`

#### Windowing
After loading the data, and optionally attaching labels or other data modalities, you can create a view of the data using the `view` function in the `BVHDataset` class. The new `BVHDatasetView` object will return a dictionary with a motion window (numpy array) in the `__getitem__` function, as well as labels. This is explained in more detail in [section 5](#5--using-the-data-view-in-your-ml-pipeline).

For this, you need to define two main parameters: `windowLength` and `stride`. The window length defines the number of frames in each window, and the stride defines the jump in frames done from the beggining of one window to the next one.

#### Internal representation
You can optionally convert the internal Euler angles of the bvh files to other representations with the `representation` parameter. The available options are:
- `euler`: Original representation in bvh files
- `quaternion`: 4-d quaternion representation
- `sixd`:  6-d representation by [Zhou et al](https://zhouyisjtu.github.io/project_rotation/rotation.html)
- `matrix`: 9-d matrix representation
- `rotvec`: 3-d rotation vector representation
- `mrp`: 3-d modified Rodrigues' parameter representation ([Scipy reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.as_mrp.html))

The internal representation can also be changed after the view has been done. This can be done with the `setRepresentation(representation: str)` function.

**Important note: if the internal representation is changed AFTER normalizing the data, it has to be normalized again, since it is impossible to compute normalization statistics in one representation and use them on another representation.**

#### Normalization
`BVHDatasetView.normalize(mode: str)`

You can normalize the data in the view with the normalize function. This function computes the normalization statistics based on all the frames of the original bvh list. In the lazy view, the data itself is never normalized; instead, the normalization statistics and mode are saved in the object, and when the data instances are returned, they will be automatically normalized.

The `mode` parameter controls what normalization method to use. These are the available options:

- `zscore`:
$$
x' = \frac{x - \overline{x}}{\sigma}
$$
- `minmax`:
$$
x' = \frac{x - x_{min}}{x_{max} - x_{min}}
$$
- `maxabs`:
$$
x' = \frac{x}{|x_{max}|}
$$
- `robust`:
$$
x' = \frac{x - median}{IQR}
$$

`BVHDatasetView.denormalize() -> None`

This function resets the normalization mode and the normalization statistics, basically making the data unnormalized.

##### Fine control over normalization
You can also have more control over the nomalization by setting the normalization statistics by hand. This enables, for example, to calculate normalization statistics onnce in dataset, save the statistics in a file, and then load the saved information to reduce computation.

To do that, you can use the following two functions to get and set normalization statistics:

`BVHDatasetView.setNormalizationStatistics(mode: str, normalizationStatistics: Dict) -> None`

Normalizes the data in the provided mode and using the provided statistics.

*Note: It is important that the mode and statistics need to coincide. (e.g. you can't ask for min-max normalization and provide z-score statistics).*

*Note: The normalization statistics and internal representation need to coincide. (e.g. you can't ask to normalize something that is in quaternion form and provide statistics calculated using Euler representation).*

`BVHDatasetView.getNormalizationStatistics() -> str, Dict`

It returns the normalization mode and the normalization statistics dictionary of a BVHDatasetView object.

The `setNormalizationStatistics` method is basically calling the `normalize` function, but with precomputed statistics, instead of calculating over the data. The next example computes statistics in a dataset and then normalizes another dataset using those:

```python
normMode, normStats = oneDatasetView.getNormalizationStatistics()
anotherDatasetView.setNormalizationStatistics(normMode, normStats)
```

#### Selecting or creating a split
If splits have been defined when the `BVHDataset` class was created, you can use these splits in the new `BVHDatasetView` object. There are two ways to work with the splits:

1) `BVHDatasetView.setSplit(split: str) -> None`

With this method, you can set the `BVHDatasetView` object to behave like a specific split, by providing the name of the split. The object will still keep all the data and references inside, but it will behave like if the files, data windows and labels outside the split do not exist. Thanks to this, the normalization and denormalization still work using all the data in the dataset.

```python
# say we have a BVHDatasetView object with 100 data windows marked as train and 50 as test
bvhData = dataset.view(128, 64) # This view will have 150 windows
bvhData.setSplit("train") # Now, the same object will have 100 windows
bvhData.setSplit("test") # Now, the same object will have 50 windows
bvhData.setSplit("all")# Now, the same object will have 150 windows again
bvhData.setSplit("foo") # Error, the split does not exist
```

2) `BVHDatasetView.makeSplit(split: str) -> BVHDatasetView`
```python
# say we have a BVHDatasetView object with 100 data windows marked as train and 50 as test
bvhData = dataset.view(128, 64) # This view will have 150 windows
trainSplit = bvhData.makeSplit("train") # trainSplit will have 100 windows
testSplit = bvhData.makeSplit("test") # testSplit will have 50 windows
fooSplit = bvhData.makeSplit("foo") # Error, the split does not exist
```
If you need to have many objects, each one representing one split, you can make splits. This method will return a copy (shallow copy that saves the original references) that represents the specific split.

**Note: if you need the `BVHDatasetView` class to represent the whole dataset again, you can pass the string 'all' as argument to the `setSplit()` function.**

### 6) 🦾 Using the data view in your ML pipeline
The newly created `BVHDatasetView` class has the `__getitem__` function which returns each instance of the dataset. It returns a dictionary with this structure:
```
{
  "motion": motion: numpy.array,
  "labels": {
      "sequence": sequenceLabel: Dict,
      "temporal": temporalLabel: Dict
  }
}
```
**Note: this will be expanded in the future to return other extra data modalities.**

If there are no labels attached to the motion, the labels section will be empty dictionaries. If there is one type of labels attached, the other label dictionary will be empty.

The labels return type is a dictionary, with the keys and values specified for all the labels related to the motion window. 

#### A) 🔥 PyTorch
The `BVHDatasetView` class is directly usable with PyTorch, since it implements the `__getitem__` and `__len__` functions. In this case, `__len__` returns the number of windows in the dataset view. To properly work with torch and bvhTools, you have to import torch.

### 7) 🔨 [*OPTIONAL*] Materializing the dataset
`BVHDatasetView.materialize() -> BVHDatasetViewMaterialized`

If instead of a lazy view, you are interesting on having all the data loaded on memory you can materialize the `BVHDatasetView` with the `materialize` function. This function basically applies all the windowing, internal representation choice and normalization and loads the numpy arrays in memory and encapsulates them in a `BVHDatasetViewMaterialized` object.

Once the internal representation and windowing has been applied, this can't be reverted. however, the normalization can be undone and redone as needed.

The materialized dataset can be written to a numpy file using `BVHDatasetViewMaterialized.writeDataViewToFile(path:str)`

## 🗂️ Classes and methods
These are the classes and their internal methods regarding the machine learning pipeline component.

### BVHDataset
```
BVHDataset 
  ├── files (List[BVHData])
  ├── filenames (List[str])
  ├── filenames (Dict)
  ├── labels (Dict)
  ├── timeUnit (str)
  ├── splits (Dict)
  └── fileToSplit (Dict)
```
#### Functions
##### `fromFolder(paths: str | List[str], recursive: bool = False, pattern: str = "") -> BVHDataset`
Creates a `BVHDataset` object from a folder/folders.
##### `fromObjects(objects: BVHData | List[BVHData]) -> BVHDataset`
Creates a `BVHDataset` object from a BVHData object/objects.
##### `fromFilelist(filelists: str | List[str]) -> BVHDataset`
Creates a `BVHDataset` object from a filelist/filelists.
##### `attachLabels(path: str) -> None`
Attaches sequence and/or temporal labels to a BVHDataset object from a yaml file.
##### `attachAudio() -> None`
[Not implemented]
##### `attachText() -> None`
[Not implemented]
##### `defineSplits(path: str) -> None`
Defines data splits on a BVHDataset object based on a yaml file.
##### `view(windowLength: int, stride: int, representation: str = "euler") -> BVHDatasetView`
Creates a lazy view (`BVHDatasetView` object) from a the `BVHDataset` object by specifying a window size, stride and internal representation.

### BVHDatasetView
```
BVHDatasetView 
  ├── baseDataset (BVHDataset)
  ├── windowLength (int)
  ├── stride (int)
  ├── precomputedIndexes (List[int, int]) # used to index items faster
  ├── normalizationStatistics (Dict)
  ├── normalizationMode (str)
  └── temporalLabels (Dict)
```
#### Functions
##### `setRepresentation(representation: str) -> None`
Changes the internal angle representation of the animations.
##### `normalize(mode: str) -> None`
Calculates the internal normalization statistics so `__getitem__` returns normalized data.
##### `denormalize() -> None`
Removes internal normalization statistics so `__getitem__` returns unnormalized data.
##### `setSplit(split: str) -> None`
Sets the active split for a specific BVHDatasetView object. (The object will behave like that split)
##### `makeSplit(split: str) -> BVHDatasetView`
Creates a new BVHDatasetView object and sets the active split for it.
##### `setNormalizationStatistics(mode: str, normalizationStatistics: Dict) -> None`
Sets the internal normalization statistics so `__getitem__` returns normalized data.
##### `getNormalizationStatistics() -> str, Dict`
Gets the current normalization mode and normalization statistics of the `BVHDatasetView` object.
##### `materialize() -> BVHDatasetViewMaterialized`
Materializes the current `BVHDatasetView` object and loads all the sequences in memory.
### BVHDatasetViewMaterialized
```
BVHDatasetViewMaterialized 
  ├── windowLength (int)
  ├── stride (int)
  ├── normalizationStatistics (Dict)
  ├── normalizationMode (str)
  ├── isNormalized (bool)
  ├── representation (str)
  └── dataView (List[List[float]])
```
#### Functions
##### `writeDataViewToFile(path: str) -> None`
Writes the materialized anmation sequences to a numpy file.
##### `normalize() -> None`
Normalizes all the frame data using the current normalization statistics.
##### `denormalize() -> None`
Denormalizes all the frame data.
##### `setNormalizationStatistics(mode: str, normalizationStatistics: Dict) -> None`
Sets a specific normalization mode and normalization statistics. (Does not normalize the data)
##### `getNormalizationStatistics() -> str, Dict`
Returns the current normalization mode and normalization statistics.