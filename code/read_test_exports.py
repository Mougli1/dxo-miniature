"""Read PhotoLab's exports of the test images (folder test_exports/) and print what the notes quote.

    python code/read_test_exports.py

Controls      Are the images exported without the effect the same as the originals?
              Is the gray still the same at Blur 100?
Checkerboard  Is the band between the two solid lines unchanged? What value does the blurred part take?
Column, disc  The width of every spot, in pixels. For the disc, also its full width and the value at its centre.
"""
from pathlib import Path

import numpy as np
from PIL import Image

from make_test_images import DISC_X, DISC_Y

ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "test_images"
EXPORTS = ROOT / "test_exports"


def read(path):
    """The pixels of an image: height x width x 3 values (red, green, blue), each from 0 to 255."""
    return np.asarray(Image.open(path).convert("RGB"))


def spot_width(image, cy):
    """Width of the spot centred on row cy: how many pixels of that row exceed half the value of the brightest one."""
    row = image[cy, :, 1].astype(int)           
    return int((row > row.max() / 2).sum())


if __name__ == "__main__":
    print("Controls")
    for name in ["gray", "checkerboard", "column", "disc"]:
        same = np.array_equal(read(EXPORTS / f"{name}_off.tif"), read(ORIGINALS / f"{name}.tif"))
        print(f"  {name}_off.tif has the same pixels as {name}.tif: {same}")
    same = np.array_equal(read(EXPORTS / "gray_100.tif"), read(ORIGINALS / "gray.tif"))
    print(f"  gray_100.tif has the same pixels as gray.tif: {same}")

    print("Checkerboard, Blur 100")
    original, blurred = read(ORIGINALS / "checkerboard.tif"), read(EXPORTS / "checkerboard_100.tif")
    band = slice(900, 2100)                      # the rows between the two solid lines (30 % and 70 % of 3000)
    print(f"  rows 900 to 2099 unchanged: {np.array_equal(blurred[band], original[band])}")
    print(f"  rows 899 and 2100 unchanged: {np.array_equal(blurred[[899, 2100]], original[[899, 2100]])}")
    top = blurred[:300]                          # above the top dashed line (10 % of 3000)
    low, high, usual = top.min(), top.max(), int(np.median(top))
    print(f"  rows 0 to 299: values from {low} to {high}, most of them {usual} (black is 0, white is 255)")

    print("Column: width of the 15 spots in pixels, from top to bottom")
    for name in ["column_off", "column_100", "column_100_line_moved"]:
        image = read(EXPORTS / f"{name}.tif")
        print(f"  {name + '.tif':27}", *[f"{spot_width(image, cy):3d}" for cy in DISC_Y])
    lower = slice(1000, None)                    # everything below the top third
    same = np.array_equal(read(EXPORTS / "column_100_line_moved.tif")[lower], read(EXPORTS / "column_100.tif")[lower])
    print(f"  rows 1000 to 2999 are the same in column_100_line_moved.tif and column_100.tif: {same}")

    print("Disc: width of the spot, full width (every pixel that is not black), value at the centre")
    for name in ["disc_off", "disc_025", "disc_050", "disc_075", "disc_100"]:
        image = read(EXPORTS / f"{name}.tif")
        row = image[DISC_Y[0], :, 1]
        print(f"  {name + '.tif':14} {spot_width(image, DISC_Y[0]):3d}  {int((row > 0).sum()):3d}  {row[DISC_X]:3d}")
    white = int((read(ORIGINALS / "disc.tif")[..., 1] == 255).sum())
    print(f"  disc.tif has {white} white pixels")
