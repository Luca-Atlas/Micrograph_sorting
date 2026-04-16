# Micrograph_sorting
Batch processing and interactive curation tools for cryo-EM micrographs. Generates filtered summed MRCs with particle coordinates from RELION STAR files, and enables rapid manual sorting via a Napari-based viewer with multi-class overlays and fast preloading.


This repository contains two Python scripts for high-throughput preprocessing and manual curation of cryo-EM micrographs with overlaid particle coordinates from multiple classes.

The batch_filtering script processes micrographs in bulk by summing image stacks (MRC format), applying Gaussian filtering, and exporting processed images alongside corresponding particle coordinate files. Particle coordinates are parsed from RELION STAR files and merged across classes. The script also supports automated filtering to remove micrographs with low particle counts prior to manual inspection.

The interactive_sorting script provides a fast, GPU-accelerated interface for visual inspection and classification of micrographs using Napari. Processed micrographs are displayed with overlaid particle coordinates (color-coded by class), and users can rapidly sort images into predefined categories via keyboard input. A background preloading system ensures minimal latency between images, enabling efficient curation of large datasets.

Together, these tools streamline the workflow from raw particle extraction to curated micrograph selection for downstream analysis and figure generation.
