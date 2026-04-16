import os
import shutil

# ================= CONFIG =================
INPUT_DIR = "/file/path/here"
THRESHOLD = 50 #micrographs with fewer particles than this number will be discarded.

NOTGOOD_DIR = os.path.join(INPUT_DIR, "notgood")
os.makedirs(NOTGOOD_DIR, exist_ok=True)

# ================= FUNCTIONS =================

def count_particles(coord_file):
    count = 0
    with open(coord_file, 'r') as f:
        for line in f:
            if line.strip():
                count += 1
    return count

# ================= MAIN =================

files = [f for f in os.listdir(INPUT_DIR) if f.endswith("_coords.txt")]

moved = 0

for coord_file in files:
    coord_path = os.path.join(INPUT_DIR, coord_file)

    particle_count = count_particles(coord_path)

    if particle_count < THRESHOLD:
        base = coord_file.replace("_coords.txt", "")

        mrc_file = base + "_sum.mrc"
        mrc_path = os.path.join(INPUT_DIR, mrc_file)

        # Move coord file
        shutil.move(coord_path, os.path.join(NOTGOOD_DIR, coord_file))

        # Move mrc file if it exists
        if os.path.exists(mrc_path):
            shutil.move(mrc_path, os.path.join(NOTGOOD_DIR, mrc_file))
        else:
            print(f"Warning: missing MRC for {base}")

        moved += 1
        print(f"{base} → notgood ({particle_count} particles)")

print(f"\nDone. Moved {moved} micrographs with < {THRESHOLD} particles.")
