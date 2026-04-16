import os
import mrcfile
import numpy as np
from scipy.ndimage import zoom, gaussian_filter

# ================= CONFIG =================
CTF_STAR_FILE = "CtfFind/job999/micrographs_ctf.star"
FILAMENT_STAR_FILES = [
    "Extract/job999/particles.star",
    "Extract/job999/particles.star"
]

OUTPUT_DIR = "/file/path/here"
UPSAMPLE_FACTOR = 2
GAUSSIAN_SIGMA = 1.0
COPY_SUFFIX = "_sum.mrc"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ================= FUNCTIONS =================

def parse_micrographs(star_file):
    files = []
    headers = []
    data_started = False
    with open(star_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('_rln'):
                headers.append(line.split()[0])
            elif headers and line and not line.startswith('#') and not line.startswith('_'):
                data_started = True
            if data_started and line and not line.startswith('_') and not line.startswith('#'):
                parts = line.split()
                if len(parts) == len(headers):
                    entry = dict(zip(headers, parts))
                    files.append(entry.get('_rlnMicrographName'))
    return files

def parse_filaments(star_file):
    headers = []
    entries = []
    data_particles = False

    with open(star_file, 'r') as f:
        for line in f:
            line = line.strip()

            if line.startswith('data_particles'):
                data_particles = True
                continue
            if not data_particles:
                continue
            if line.startswith('loop_'):
                continue
            if line.startswith('_rln'):
                headers.append(line.split()[0])
                continue
            if line and not line.startswith('#'):
                parts = line.split()
                if len(parts) == len(headers):
                    entries.append(dict(zip(headers, parts)))

    micrograph_coords = {}
    for entry in entries:
        micro = entry['_rlnMicrographName']
        x = float(entry['_rlnCoordinateX'])
        y = float(entry['_rlnCoordinateY'])

        micrograph_coords.setdefault(micro, []).append((x, y))

    return micrograph_coords

def sum_mrc_filtered(mrc_file):
    with mrcfile.open(mrc_file, permissive=True) as mrc:
        data = mrc.data

        if data.ndim == 3:
            data = np.sum(data, axis=0)

        data = data.astype(np.float32)
        data = zoom(data, UPSAMPLE_FACTOR, order=1)
        data = gaussian_filter(data, sigma=GAUSSIAN_SIGMA)

        return data

# ================= MAIN =================

print("Parsing inputs...")

micrographs = parse_micrographs(CTF_STAR_FILE)
all_filament_coords = [parse_filaments(sf) for sf in FILAMENT_STAR_FILES]

# Merge coordinates
merged_coords = {}
for class_idx, coords_dict in enumerate(all_filament_coords):
    for micro, coords in coords_dict.items():
        merged_coords.setdefault(micro, [[] for _ in FILAMENT_STAR_FILES])
        merged_coords[micro][class_idx] = coords

print(f"Processing {len(merged_coords)} micrographs...")

for i, (micro, coords_lists) in enumerate(merged_coords.items()):

    if not os.path.exists(micro):
        print(f"Missing: {micro}")
        continue

    try:
        micro_sum = sum_mrc_filtered(micro)

        base = os.path.basename(micro).replace(".mrc", "")

        # Save MRC
        out_mrc = os.path.join(OUTPUT_DIR, base + COPY_SUFFIX)
        with mrcfile.new(out_mrc, overwrite=True) as mrc_out:
            mrc_out.set_data(micro_sum.astype(np.float32))

        # Save coords
        coord_file = os.path.join(OUTPUT_DIR, base + "_coords.txt")
        with open(coord_file, 'w') as f:
            for class_idx, coords in enumerate(coords_lists):
                for x, y in coords:
                    f.write(f"{class_idx}\t{x*UPSAMPLE_FACTOR}\t{y*UPSAMPLE_FACTOR}\n")

        if i % 50 == 0:
            print(f"{i} done...")

    except Exception as e:
        print(f"Error processing {micro}: {e}")

print("Batch processing complete.")
