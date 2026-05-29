from bvhTools.bvhDataTypes import BVHData
from bvhTools.bvhIO import readBvh
import numpy as np
import os
import yaml
from scipy.spatial.transform import Rotation as R
from scipy.stats import iqr as IQR
from copy import copy

class BVHDataset:
    def __init__(self, files, filenames = None):
        self.files = files
        self.filenames = filenames
        self.labels = None
        self.timeUnit = None
        self.splits = None
        self.fileToSplit = None

    def __len__(self):
        return len(self.files)

    @classmethod
    def fromFolder(cls, paths: str | list[str], recursive: bool = False, pattern: str = "") -> "BVHDataset":
        if not (isinstance(paths, str) or (isinstance(paths, list) and all(isinstance(path, str) for path in paths))):
            raise TypeError(f"You must provide the folder path(s). Expected type for paths: str | List[str]. Received type: {type(paths).__name__}")
        
        objects = []
        filenames = []

        if isinstance(paths, (str)):
            paths = [paths]
        
        for path in paths:
            if not recursive:
                for filename in sorted(os.listdir(path)):
                    if filename.endswith(".bvh"):
                        if (pattern == "" or pattern in filename):
                            objects.append(readBvh(os.path.join(path, filename)))
                            filenames.append(os.path.join(path, filename))
            else:
                for (root, dirs, filenames) in os.walk(path):
                    dirs.sort()
                    for filename in sorted(filenames):
                        if filename.endswith(".bvh"):
                            if(pattern == "" or pattern in filename):
                                objects.append(readBvh(os.path.join(root, filename)))
                                filenames.append(os.path.join(root, filename))

        return cls(objects, filenames)

    @classmethod
    def fromObjects(cls, objects: BVHData | list[BVHData]) -> "BVHDataset":
        if not (isinstance(objects, BVHData) or (isinstance(objects, list) and all(isinstance(obj, BVHData) for obj in objects))):
            raise TypeError(f"You must provide the BVHData object(s). Expected type for objects: BVHData | List[BVHData]. Received type: {type(objects).__name__}")
        
        if isinstance(objects, BVHData):
            objects = [objects]

        return cls(objects)

    @classmethod
    def fromFilelist(cls, filelists: str | list[str]) -> "BVHDataset":
        if not (isinstance(filelists, str) or (isinstance(filelists, list) and all(isinstance(filelist, str) for filelist in filelists))):
            raise TypeError(f"You must provide the paths of the filelist(s). Expected type for filelists: str | List[str]. Received type: {type(filelists).__name__}")

        objects = []
        filenames = []

        for filelist in filelists:
            with open(filelist, "r") as f:
                line = f.readline()
                if not line.startswith("#"):
                    objects.append(readBvh(line))
                    filenames.append(line)

        return cls(objects, filenames)        

    def defineSplits(self, path: str) -> None:
        if(self.filenames is None):
            raise PermissionError("You can't define splits in a dataset loaded from objects, since file names are not available. Load the dataset from folder or from a filelist.")
        
        with open(path, "r") as f:
            splitsFile = yaml.safe_load(f)
        
        if(splitsFile is None):
            raise ValueError("Splits file is empty or invalid YAML.")
        if(not isinstance(splitsFile, dict)):
            raise TypeError("Splits file must define a dictionary at the top level.")
        
        self.splitRule = splitsFile.get("splitRule", "none")
        if(self.splitRule not in ["files", "pattern"]):
            raise ValueError(f"Invalid splitRule: {self.splitRule}. Possible values: [files, pattern]")
        
        splits = splitsFile["splits"]
        self.splits = {}
        self.fileToSplit = {}
        if(self.splitRule == "files"):
            for splitName, splitFiles in splits.items():
                self.splits[splitName] = list(splitFiles)
                for file in splitFiles:
                    if(type(file) is not str):
                        raise TypeError(f"File {file} must be a string.")
                    if(file in self.fileToSplit):
                        raise ValueError(f"File {file} is already defined in a split.")
                    self.fileToSplit[file] = splitName
            for filename in self.filenames:
                if(not any(filename in splitFiles for splitFiles in splits.values())):
                    raise ValueError(f"File {filename} is not specified in any splits.")

        elif(self.splitRule == "pattern"):
            for filename in self.filenames:
                fileInSplit = 0
                for splitName, splitPatterns in splits.items():
                    if(any(pattern in filename for pattern in splitPatterns)):
                        if splitName not in self.splits:
                            self.splits[splitName] = []
                        self.splits[splitName].append(filename)
                        self.fileToSplit[filename] = splitName
                        fileInSplit += 1
                if(fileInSplit > 1):
                    raise ValueError(f"File {filename} is in more than one split.")
                elif(fileInSplit == 0):
                    raise ValueError(f"File {filename} is not specified in any splits.")

    def attachLabels(self, path: str) -> None:
        if(self.filenames is None):
            raise PermissionError("You can't attach labels to a dataset loaded from objects, since they can't be linked. Load the dataset from folder or from a filelist.")
        
        with open(path, "r") as f:
            labels = yaml.safe_load(f)
        
        if(labels is None):
            raise ValueError("Label file is empty or invalid YAML.")
        if(not isinstance(labels, dict)):
            raise TypeError("Label file must define a dictionary at the top level.")
        
        self.timeUnit = labels.get("timeUnit", "frames")
        if(self.timeUnit not in ["seconds", "frames"]):
            raise ValueError(f"Invalid timeUnit: {self.timeUnit}. Possible values: [seconds, frames]")
        
        self.temporalRule = labels.get("temporalRule", "first")
        if(self.temporalRule not in ["first", "coverage", "all"]):
            raise ValueError(f"Invalid temporalRule: {self.temporalRule}. Possible values: [first, coverage, all]")
        
        for key, value in labels.items():
            if("timeUnit" in key):
                continue
            if("temporalRule" in key):
                continue

            if(key not in self.filenames):
                raise ValueError(f"{key} does not exist in this BVHDataset object.")
            if(not isinstance(value, dict)):
                raise ValueError(f"{key} must have a correct structure.")
            if("sequence" in value):
                if(not isinstance(value["sequence"], dict)):
                    raise ValueError(f"Error in {key}: sequence must have a correct structure.")
                
            if("temporal" in value):
                if(not isinstance(value["temporal"], list)):
                    raise ValueError(f"Error in {key}: temporal label must have a correct structure.")
                for tempLabel in value["temporal"]:
                    if not isinstance(tempLabel, dict):
                        raise ValueError(f"Error in file {key}: temporal label must have a correct structure.")
                    if "start" not in tempLabel:
                        raise ValueError(f"Error in {key}: all temporal labels must have a start.")
                    start = tempLabel["start"]
                    if(self.timeUnit == "frames"):
                        if(not isinstance(start, int)):
                            raise TypeError(f"Error in {key}: frames must be of type int.")
                    if(self.timeUnit == "seconds"):
                        if(not isinstance(start, (float, int))):
                            raise TypeError(f"Error in {key}: seconds must be of type float.")
                    if(len(tempLabel) <= 1):
                        raise ValueError(f"Error in {key}: all temporal labels must have at least one label.")
                starts = [tempLabel["start"] for tempLabel in value["temporal"]]
                if(starts[0]!= 0):
                    raise ValueError(f"Error in {key}: first temporal label must start at 0.")
                if(starts != sorted(starts)):
                    raise ValueError(f"Error in {key}: all temporal labels must be ordered.")

        for filename in self.filenames:
            if filename not in labels:
                print(f"\033[1;33mWARNING\033[0m: file {filename} has no specified labels. Attaching empty label.")
                labels[filename] = {}
        
        self.labels = labels

    def attachAudio(self):
        raise NotImplementedError("This functionality is not implemented yet.")
        if(self.filenames is None):
            raise PermissionError("You can't attach audio to a dataset loaded from objects, since they can't be linked. Load the dataset from folder or from a filelist.")
    
    def attachText(self):
        raise NotImplementedError("This functionality is not implemented yet.")
        if(self.filenames is None):
            raise PermissionError("You can't attach text to a dataset loaded from objects, since they can't be linked. Load the dataset from folder or from a filelist.")

    def view(self, windowLength: int, stride: int, representation: str = "euler") -> "BVHDatasetView":
        return BVHDatasetView(self, windowLength, stride, representation)

class BVHDatasetView:
    def __init__(self, baseDataset, windowLength, stride, representation):
        self.baseDataset = baseDataset
        self.windowLength = windowLength
        self.stride = stride
        self.setRepresentation(representation)
        self.precomputedIndexes, self.precomputedSplitIndexes = self._precomputeIndexes()
        self.activeSplit = "all"
        self.normalizationStatistics = None
        self.normalizationMode = ""
        self.temporalLabels = self._assignTemporalLabels()

    def _assignTemporalLabels(self):
        assignedLabels = []
        for precomputedIndex in self.precomputedIndexes:
            fileIndex, startFrame, _ = precomputedIndex
            endFrame = startFrame + self.windowLength

            fileName = self.baseDataset.filenames[fileIndex]

            fileLabels = self.baseDataset.labels.get(fileName, [])
            temporalLabels = fileLabels.get("temporal",[])

            if(self.baseDataset.timeUnit == "seconds"):
                fps =  1 / (self.baseDataset.files[fileIndex].motion.frameTime)
                startTime = startFrame / fps
                endTime = endFrame / fps
            else:
                startTime = startFrame
                endTime = endFrame
            
            activeLabels = [label for label in temporalLabels if label["start"] <= startTime]
            
            if not activeLabels:
                assignedLabels.append(None)
                continue
            if(self.baseDataset.temporalRule == "first"):
                assignedLabels.append(activeLabels[-1])
            elif(self.baseDataset.temporalRule == "all"):
                labelsInWindow = [label for label in temporalLabels if startTime <= label["start"] < endTime]
                assignedLabels.append([activeLabels[-1]] + labelsInWindow)
            elif(self.baseDataset.temporalRule == "coverage"):
                segments = []

                for i, label in enumerate(temporalLabels):
                    segStart = label["start"]
                    segEnd = temporalLabels[i+1]["start"] if i < len(temporalLabels) - 1 else float("inf")

                    overlapStart = max(segStart, startTime)
                    overlapEnd = min(segEnd, endTime)

                    if(overlapStart < overlapEnd):
                        coverage = overlapEnd - overlapStart
                        segments.append((coverage, label))
                
                if segments:
                    bestLabel = max(segments, key = lambda x: x[0])[1]
                    assignedLabels.append(bestLabel)
                else:
                    assignedLabels.append(activeLabels[-1])

        return assignedLabels

    def _precomputeIndexes(self):
        precomputedIndexes = []
        precomputedSplitIndexes = {}
        for fileIndex, file in enumerate(self.baseDataset.files):
            frameCount = file.motion.numFrames
            if(self.baseDataset.splits is None):
                split = None
            else:
                fileName = self.baseDataset.filenames[fileIndex]
                split = self.baseDataset.fileToSplit[fileName]
                if(split not in precomputedSplitIndexes):
                    precomputedSplitIndexes[split] = []
            for x in range(0, frameCount - self.windowLength, self.stride):
                precomputedIndexes.append([fileIndex, x, split])
                if(self.baseDataset.splits is not None):
                    precomputedSplitIndexes[split].append([fileIndex, x])

        return precomputedIndexes, precomputedSplitIndexes

    def setSplit(self, split: str) -> None:
        if len(self.precomputedSplitIndexes) == 0:
            raise ValueError(f"This BVHDatasetView object does not have any split defined.")
        if not split in self.precomputedSplitIndexes.keys() and not split == "all":
            raise ValueError(f"Split '{split}' does not exist in this BVHDatasetView object. Available splits: {list(self.precomputedSplitIndexes.keys())}")
        self.activeSplit = split

    def makeSplit(self, split: str) -> "BVHDatasetView":
        if len(self.precomputedSplitIndexes) == 0:
            raise ValueError(f"This BVHDatasetView object does not have any split defined.")
        if not split in self.precomputedSplitIndexes.keys():
            raise ValueError(f"Split {split} does not exist in this BVHDatasetView object. Available splits: {list(self.precomputedSplitIndexes.keys())}")
        newView = BVHDatasetView.__new__(BVHDatasetView)

        newView.baseDataset = self.baseDataset
        newView.precomputedIndexes = self.precomputedIndexes
        newView.precomputedSplitIndexes = self.precomputedSplitIndexes
        newView.windowLength = self.windowLength
        newView.stride = self.stride
        newView.representation = self.representation
        newView.normalizationMode = self.normalizationMode
        newView.normalizationStatistics = self.normalizationStatistics
        newView.temporalLabels = self.temporalLabels
        newView.activeSplit = split

        return newView

    def setRepresentation(self, representation: str) -> None:
        representation = representation.lower()
        if not(representation == "euler" or representation == "quaternion" or representation == "sixd" or representation == "matrix" or representation == "rotvec" or representation == "mrp"):
            raise ValueError(f"The representation must be a string : [Euler, Quaternion, SixD, Matrix, RotVec, Mrp]")
        self.representation = representation
        self.normalizationMode = ""
        self.normalizationStatistics = None

        if(representation != "euler"):
            [bvh.motion.getRepresentation(representation) for bvh in self.baseDataset.files] # Fill the representation cache
    
    def normalize(self, mode: str) -> None:
        self.normalizationMode = mode
        frames = []
        for file in self.baseDataset.files:
            if(self.representation == "euler"):
                frames.extend(file.motion.frames)
            else:
                frames.extend(file.motion.representationCache[self.representation])

        frames = np.array(frames)

        if(mode == "zscore"):
            std = np.std(frames, axis=0)
            mean = np.mean(frames, axis=0)
            self.normalizationStatistics = {"std": std.tolist(),
                                            "mean": mean.tolist()}
        elif(mode == "minmax"):
            minVal = np.min(frames, axis=0)
            maxVal = np.max(frames, axis=0)
            self.normalizationStatistics = {"min": minVal.tolist(),
                                            "max": maxVal.tolist()}
        elif(mode == "maxabs"):
            maxabs = np.max(np.abs(frames), axis=0)
            self.normalizationStatistics = {"maxabs": maxabs.tolist()}
        elif(mode == "robust"):
            median = np.median(frames, axis=0)
            iqr = IQR(frames, axis = 0)
            self.normalizationStatistics = {"median": median.tolist(),
                                            "iqr": iqr.tolist()}

    def denormalize(self) -> None:
        self.normalizationMode = ""
        self.normalizationStatistics = {}

    def setNormalizationStatistics(self, mode: str, normalizationStatistics: dict[str, list[float]]) -> None:
        if not(mode == "zscore" or mode == "minmax" or mode == "maxabs" or mode == "robust"):
            raise ValueError(f"The normalization mode must be a string : [zscore, minmax, maxabs, robust]")
        if mode == "zscore" and not(normalizationStatistics["mean"] and normalizationStatistics["std"]):
            raise ValueError(f"Zscore normalization needs to have: [mean, std]")
        if mode == "minmax" and not(normalizationStatistics["mean"] and normalizationStatistics["std"]):
            raise ValueError(f"Minmax normalization needs to have: [mean, std]")
        if mode == "maxabs" and not(normalizationStatistics["maxabs"]):
            raise ValueError(f"Maxabs normalization needs to have: [maxabs]")
        if mode == "robust" and not(normalizationStatistics["median"] and normalizationStatistics["iqr"]):
            raise ValueError(f"Robust normalization needs to have: [median, iqr]")
        
        self.normalizationMode = mode
        self.normalizationStatistics = normalizationStatistics

    def getNormalizationStatistics(self) -> tuple[str, dict[str, list[float]]]:
        return self.normalizationMode, self.normalizationStatistics
    
    def __len__(self) -> int:
        if(self.activeSplit == "all"):
            return len(self.precomputedIndexes)
        else:
            return len(self.precomputedSplitIndexes[self.activeSplit])

    def __getitem__(self, index: int) -> dict:
        if(self.activeSplit == "all"):
            fileIndex, startFrame, _ = self.precomputedIndexes[index]
        else:
            fileIndex, startFrame = self.precomputedSplitIndexes[self.activeSplit][index]
        if(self.representation == "euler"):
            item = np.array(self.baseDataset.files[fileIndex].motion.frames[startFrame:startFrame+self.windowLength])
        else:
            item = np.array(self.baseDataset.files[fileIndex].motion.representationCache[self.representation][startFrame:startFrame+self.windowLength])

        if(self.normalizationMode!=""):
            if(self.normalizationMode=="zscore"):
                item = (item - np.array(self.normalizationStatistics["mean"])) / np.array(self.normalizationStatistics["std"])
            elif(self.normalizationMode == "minmax"):
                item = (item - np.array(self.normalizationStatistics["min"])) / (np.array(self.normalizationStatistics["max"]) - np.array(self.normalizationStatistics["min"]))
            elif(self.normalizationMode == "maxabs"):
                item = item / np.array(self.normalizationStatistics["maxabs"])
            elif(self.normalizationMode == "robust"):
                item = (item - np.array(self.normalizationStatistics["median"])) / np.array(self.normalizationStatistics["iqr"])
        
        sequenceLabel = None
        temporalLabel = None
        if(self.baseDataset.labels is not None):
            fileName = self.baseDataset.filenames[fileIndex]
            file_labels = self.baseDataset.labels.get(fileName, {})
            
            sequenceLabel = file_labels.get("sequence", None)
            
            if(self.temporalLabels is not None):
                temporalLabel = self.temporalLabels[index]
        
        return {
                "motion": item,
                "labels": {
                    "sequence": sequenceLabel,
                    "temporal": temporalLabel
                }
            }
    
    def materialize(self) -> "BVHDatasetViewMaterialized":
        return BVHDatasetViewMaterialized(self)

class BVHDatasetViewMaterialized:
    def __init__(self, view):
        self.windowLength = view.windowLength
        self.stride = view.stride
        self.normalizationStatistics = view.normalizationStatistics
        self.normalizationMode = view.normalizationMode
        self.isNormalized = not view.normalizationMode == ""
        self.representation = view.representation
        self.dataView = self._createDataView(view)

    def __len__(self) -> int:
        return len(self.dataView)
    
    def __getitem__(self, index: int) -> np.array:
        return self.dataView[index]

    @property
    def shape(self) -> tuple[int, ...]:
        return self.dataView.shape

    def _createDataView(self, view):
        return [x for x in view]

    def writeDataViewToFile(self, path: str) -> None:
        np.save(path, self.dataView)

    def normalize(self) -> None:
        if(self.normalizationMode == ""):
            raise AttributeError("The normalization mode has not been set for this BVHDatasetViewMaterialized object. You can't normalize the data.")
        self.isNormalized = True
        if(self.normalizationMode == "zscore"):
            self.dataView = (self.dataView - self.normalizationStatistics["mean"]) / self.normalizationStatistics["std"]
        elif(self.normalizationMode == "minmax"):
            self.dataView = (self.dataView - self.normalizationStatistics["min"]) / (self.normalizationStatistics["max"] - self.normalizationStatistics["min"])
        elif(self.normalizationMode == "maxabs"):
            self.dataView = self.dataView / self.normalizationStatistics["maxabs"]
        elif(self.normalizationMode == "robust"):
            self.dataView = (self.dataView -self.normalizationStatistics["median"]) / self.normalizationStatistics["iqr"]

    def denormalize(self) -> None:
        if(not self.isNormalized):
            raise AttributeError("This data is not normalized. You can't denormalize twice.")
        if self.normalizationMode == "":
            raise AttributeError("The normalization mode has not been set for this BVHDatasetViewMaterialized object. You can't denormalize the data.")
        else:
            self.isNormalized = False
            if self.normalizationMode == "zscore":
                self.dataView = (self.dataView * self.normalizationStatistics["std"]) + self.normalizationStatistics["mean"]
            elif(self.normalizationMode == "minmax"):
                item = (item * (self.normalizationStatistics["max"] - self.normalizationStatistics["min"])) + self.normalizationStatistics["min"]
            elif(self.normalizationMode == "maxabs"):
                item = item * self.normalizationStatistics["maxabs"]
            elif(self.normalizationMode == "robust"):
                item = (item * self.normalizationStatistics["iqr"]) + self.normalizationStatistics["median"]

    def setNormalizationStatistics(self, mode: str, normalizationStatistics: dict[str, list[float]]) -> None:
        if self.isNormalized:
            raise ValueError(f"The data is currently normalized and you are trying to change normalization statistics. You would not be able to denormalize this data. Please, denormalize first.")
        if not(mode == "zscore" or mode == "minmax" or mode == "maxabs" or mode == "robust"):
            raise ValueError(f"The normalization mode must be a string : [zscore, minmax, maxabs, robust]")
        if mode == "zscore" and (not normalizationStatistics["mean"] or normalizationStatistics["std"]):
            raise ValueError(f"Zscore normalization needs to have: [mean, std]")
        if mode == "minmax" and (not normalizationStatistics["mean"] or normalizationStatistics["std"]):
            raise ValueError(f"Minmax normalization needs to have: [mean, std]")
        if mode == "maxabs" and (not normalizationStatistics["maxabs"]):
            raise ValueError(f"Maxabs normalization needs to have: [maxabs]")
        if mode == "robust" and (not normalizationStatistics["median"] or normalizationStatistics["iqr"]):
            raise ValueError(f"Robust normalization needs to have: [median, iqr]")
        
        self.normalizationMode = mode
        self.normalizationStatistics = normalizationStatistics

    def getNormalizationStatistics(self) -> tuple[str, dict[str, list[float]]]:
        return self.normalizationMode, self.normalizationStatistics