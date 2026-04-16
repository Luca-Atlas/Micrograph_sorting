# Micrograph_sorting
Batch processing and interactive curation tools for cryo-EM micrographs. Generates filtered summed MRCs with particle coordinates from RELION STAR files, and enables rapid manual sorting via a Napari-based viewer with multi-class overlays and fast preloading.


This repository contains two Python scripts for high-throughput preprocessing and manual curation of cryo-EM micrographs with overlaid particle coordinates from multiple classes.

The batch_filtering script processes micrographs in bulk by summing image stacks (MRC format), applying Gaussian filtering, and exporting processed images alongside corresponding particle coordinate files. Particle coordinates are parsed from RELION STAR files and merged across classes. 

(Optional) The filter_fewerthan50particles script also supports automated filtering to remove micrographs with low particle counts prior to manual inspection. The threshold of 50 can be edited within the script.

The interactive_sorting_napari script provides a fast, GPU-accelerated interface for visual inspection and classification of micrographs using Napari. Processed micrographs are displayed with overlaid particle coordinates (color-coded by class), and users can rapidly sort images into predefined categories via keyboard input. A background preloading system ensures minimal latency between images, enabling efficient curation of large datasets.

Together, these tools streamline the workflow from raw particle extraction to curated micrograph selection for downstream analysis and figure generation.

# Dependencies

The analysis and visualization scripts were developed in a Python 3.10 environment using standard scientific and visualization libraries. Core dependencies include NumPy for array operations, SciPy for image filtering and interpolation, and Matplotlib for initial visualization. MRC file handling is performed using the mrcfile package.

Interactive micrograph inspection is implemented using Napari, which provides GPU-accelerated rendering and layer-based visualization. Background preloading of micrographs is handled via Python’s built-in concurrent.futures module.

The full environment can be reproduced using conda as follows:

conda create -n cryoem-curation python=3.10
conda activate cryoem-curation
pip install numpy scipy matplotlib mrcfile napari[all]

# Instructions for use

0. Configure file paths (required)

Before using each script you must edit the file paths to match your system and RELION project structure.

CTF_STAR_FILE = "CtfFind/job999/micrographs_ctf.star"
FILAMENT_STAR_FILES = [
    "Extract/job999/particles.star",
    "Extract/job999/particles.star"
]

OUTPUT_DIR = "/file/path/here"


1. Batch filtering and preparation

$ python batch_filtering.py

This will:
- parse micrograph paths from RELION CTF star files
- extract the particle coordinates from one or more particle star files
- Sum mrc stacks
- Upsample and Gaussian filter

Outputs:
- *_sum.mrc (processed micrographs)
- *_coords.txt (particle coordinates per class)

2. Remove sparse micrographs (Optional)

$ python filter_fewerthan50particles.py

This will count particles from the coords.txt file and move micrographs (and the corresponding coord.txt files) with 50 or fewer particles into the notgood directory. This threshold can be edited in the script.

3. Interactive sorting (Napari)

$ python filter_fewerthan50particles.py

This will open the summed mrc files with the particle coordinates overlaid. The keyboard can then be used to manully sort between micrographs into different directories.

Controls:

I → move to interesting/
G → move to good/
N → move to notgood/
Q → quit viewer

# Notes
SSD storage is strongly recommended for optimal performance
Napari benefits from GPU acceleration but runs on CPU-only systems

Coordinate files are stored as:

class_index   x   y
Coordinates are automatically transformed for correct display in Napari
