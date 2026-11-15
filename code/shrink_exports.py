"""Turn PhotoLab's exports of the test images into small files, in the folder test_exports/.

    python code/shrink_exports.py off        (or 100, 050, ...: the end of the new names)

PhotoLab writes its exports next to the test images, as 16-bit TIFF files of 72 MB each
(test_images/disc_DxO.tif, and so on). This script saves each of them again as a compressed
8-bit TIFF (test_exports/disc_off.tif, and so on), then removes the big file.
"""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "test_exports"

if __name__ == "__main__":
    label = sys.argv[1]
    OUT.mkdir(exist_ok=True)
    for big in sorted((ROOT / "test_images").glob("*_DxO.tif")):
        small = OUT / big.name.replace("_DxO", "_" + label)
        image = Image.open(big)                       # Pillow reads the 16-bit values as 8-bit ones
        image.convert("RGB").save(small, compression="tiff_lzw", icc_profile=image.info.get("icc_profile"))
        big.unlink()
        print(f"wrote test_exports/{small.name}")
