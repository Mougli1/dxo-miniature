"""Make the four test images of the folder test_images/.

    python code/make_test_images.py

gray.tif          a uniform gray, used as a control: it should come out unchanged
checkerboard.tif  black and white squares of 50 pixels
column.tif        15 identical white discs on black, in a column, one every 200 pixels
disc.tif          only the first disc of that column, near the top of the image

All four are 4000 x 3000 pixels, like the night photo. They are saved as TIFF,
because JPEG compression would already change the pixels.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageCms

OUT = Path(__file__).resolve().parents[1] / "test_images"
WIDTH, HEIGHT = 4000, 3000
RADIUS = 10                                  # radius of a disc, in pixels
DISC_X = WIDTH // 2                          # the discs are in the middle of the width
DISC_Y = list(range(100, HEIGHT, 200))       # 100, 300, ..., 2900: 15 discs

y, x = np.ogrid[:HEIGHT, :WIDTH]             # row and column number of every pixel


def black():
    return np.zeros((HEIGHT, WIDTH), np.uint8)


def inside_disc(cx, cy):
    """True for the pixels of the disc centred on pixel (cx, cy): 21 pixels across for RADIUS = 10."""
    return (x - cx) ** 2 + (y - cy) ** 2 < (RADIUS + 0.5) ** 2


def gray_image():
    return np.full((HEIGHT, WIDTH), 128, np.uint8)


def checkerboard_image(square=50):
    return np.where((x // square + y // square) % 2 == 0, 255, 0).astype(np.uint8)


def column_image():
    image = black()
    for cy in DISC_Y:
        image[inside_disc(DISC_X, cy)] = 255
    return image


def disc_image():
    image = black()
    image[inside_disc(DISC_X, DISC_Y[0])] = 255
    return image


def save(name, image):
    """Save a gray image as an RGB TIFF that carries the sRGB colour profile."""
    OUT.mkdir(exist_ok=True)
    rgb = np.stack([image, image, image], axis=-1)
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    Image.fromarray(rgb).save(OUT / name, compression="tiff_lzw", icc_profile=srgb)
    print(f"wrote test_images/{name}")


if __name__ == "__main__":
    save("gray.tif", gray_image())
    save("checkerboard.tif", checkerboard_image())
    save("column.tif", column_image())
    save("disc.tif", disc_image())
