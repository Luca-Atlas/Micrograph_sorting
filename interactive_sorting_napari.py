import os
import shutil
import mrcfile
import numpy as np
import napari
from concurrent.futures import ThreadPoolExecutor

# ================= CONFIG =================
INPUT_DIR = "/file/path/to/summed_mrcs"

OUTPUT_DIRS = {
    "i": os.path.join(INPUT_DIR, "interesting"),
    "g": os.path.join(INPUT_DIR, "good"),
    "n": os.path.join(INPUT_DIR, "notgood"),
}

COLORS = ["red", "blue"] #or whatever colours you want

LOW_PERC = 0.5
HIGH_PERC = 99.5

PRELOAD_AHEAD = 3
MAX_WORKERS = 4

for d in OUTPUT_DIRS.values():
    os.makedirs(d, exist_ok=True)

# ================= FUNCTIONS =================

def load_coords(coord_file):
    coords_by_class = {0: [], 1: []}
    with open(coord_file, 'r') as f:
        for line in f:
            c, x, y = line.strip().split()
            coords_by_class[int(c)].append((float(x), float(y)))
    return coords_by_class

def relion_contrast(data):
    vmin = np.percentile(data, LOW_PERC)
    vmax = np.percentile(data, HIGH_PERC)
    return vmin, vmax

def load_data(mrc_file, coord_file):
    with mrcfile.open(mrc_file, permissive=True) as mrc:
        data = mrc.data.copy()
    coords = load_coords(coord_file)
    return data, coords

def move_files(base_name, key):
    dest = OUTPUT_DIRS[key]

    mrc_src = os.path.join(INPUT_DIR, base_name + "_sum.mrc")
    coord_src = os.path.join(INPUT_DIR, base_name + "_coords.txt")

    shutil.move(mrc_src, os.path.join(dest, os.path.basename(mrc_src)))
    shutil.move(coord_src, os.path.join(dest, os.path.basename(coord_src)))

# ================= PRELOAD =================

executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
cache = {}
futures = {}

def get_paths(files, idx):
    mrc_file = os.path.join(INPUT_DIR, files[idx])
    base = files[idx].replace("_sum.mrc", "")
    coord_file = os.path.join(INPUT_DIR, base + "_coords.txt")
    return mrc_file, coord_file, base

def preload(files, idx):
    if idx >= len(files):
        return
    if idx in cache or idx in futures:
        return

    mrc_file, coord_file, _ = get_paths(files, idx)

    if os.path.exists(coord_file):
        futures[idx] = executor.submit(load_data, mrc_file, coord_file)

# ================= MAIN =================

files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith("_sum.mrc")])

viewer = napari.Viewer()

image_layer = None
points_layers = [None, None]

index = 0

print("\nControls:")
print("  I = interesting")
print("  G = good")
print("  N = not good")
print("  Q = quit\n")

# Correct function signature
def update_view(data, coords, base):
    global image_layer, points_layers

    vmin, vmax = relion_contrast(data)

    # Update image
    if image_layer is None:
        image_layer = viewer.add_image(data, contrast_limits=(vmin, vmax), name=base)
    else:
        image_layer.data = data
        image_layer.contrast_limits = (vmin, vmax)
        image_layer.name = base

    # Update points
    for i in range(2):
        if coords[i]:
            pts = np.array([(y, x) for x, y in coords[i]])  # swap axes for Napari
        else:
            pts = np.empty((0, 2))

        if points_layers[i] is None:
            points_layers[i] = viewer.add_points(
                pts,
                size=100,
                face_color=COLORS[i],
                opacity=0.9,
                name=f"class_{i}"
            )
        else:
            points_layers[i].data = pts
            points_layers[i].size = 100
            
def next_image():
    global index

    index += 1
    if index >= len(files):
        print("Done.")
        napari.utils.notifications.show_info("Finished sorting")
        return

    load_and_display(index)

def load_and_display(idx):
    global cache, futures

    # preload queue
    for i in range(idx, idx + PRELOAD_AHEAD + 1):
        preload(files, i)

    # get data
    if idx in cache:
        data, coords = cache.pop(idx)
    elif idx in futures:
        data, coords = futures.pop(idx).result()
    else:
        mrc_file, coord_file, _ = get_paths(files, idx)
        data, coords = load_data(mrc_file, coord_file)

    # move finished futures to cache
    done_keys = []
    for k, f in futures.items():
        if f.done():
            cache[k] = f.result()
            done_keys.append(k)
    for k in done_keys:
        futures.pop(k)

    _, _, base = get_paths(files, idx)

    update_view(data, coords, base)

def handle_key(key):
    _, _, base = get_paths(files, index)
    move_files(base, key)
    print(f"{base} → {key}")
    next_image()

# ================= KEY BINDINGS =================

@viewer.bind_key('i')
def mark_interesting(viewer):
    handle_key('i')

@viewer.bind_key('g')
def mark_good(viewer):
    handle_key('g')

@viewer.bind_key('n')
def mark_bad(viewer):
    handle_key('n')

@viewer.bind_key('q')
def quit_app(viewer):
    napari.utils.notifications.show_info("Exiting")
    viewer.close()

# ================= START =================

load_and_display(index)

napari.run()
