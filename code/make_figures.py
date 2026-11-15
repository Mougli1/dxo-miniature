"""Draw the figures of the notes: crops, zooms and side-by-side views, nothing else.

    python code/make_figures.py

Inputs:  screenshots/  PhotoLab screenshots: the lake photo, and the night photo with the tool's lines
         exports/      exports of the night photo
         test_images/  the four test images
Outputs: en/figures/*.png, with English labels
         (and fr/figures/*.png with French labels, if there is a fr/ folder next to en/)

Every enlarged area is framed in white on the picture it comes from.
Figures use Fira Sans when it is installed, DejaVu Sans otherwise.
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib import font_manager
from matplotlib.patches import Rectangle

from make_test_images import DISC_X, DISC_Y

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
SCREENSHOTS = ROOT / "screenshots"
TEST_IMAGES = ROOT / "test_images"


def font():
    """Fira Sans if available (installed, or a folder of .otf files given by FIG_FONT_DIR)."""
    folder = os.environ.get("FIG_FONT_DIR")
    if folder:
        for weight in ("Regular", "Italic", "Bold"):
            font_manager.fontManager.addfont(os.path.join(folder, f"FiraSans-{weight}.otf"))
    names = {f.name for f in font_manager.fontManager.ttflist}
    return "Fira Sans" if "Fira Sans" in names else "DejaVu Sans"


plt.rcParams.update({"font.family": font(), "font.size": 9, "axes.titlesize": 9})
OUTLINE = [pe.withStroke(linewidth=2, foreground="black")]

# ---------------------------------------------------------------- labels, in both languages
TEXT = {
    "fr": {
        "pct": "{} %",
        "lake_ref": "Flou 0/0, zones A à D",
        "lake_max": "Flou 100/100",
        "lake_cols": ["0/0", "51/51", "100/100", "100/0"],
        "night_ref": "Sans l'effet (N00)",
        "night_lines": "Dans PhotoLab : Flou 100/100, lignes de l'outil",
        "strips": [("N00", "N00\nsans l'effet"), ("N01", "N01\nFlou 50"), ("N02", "N02\nFlou 100")],
        "height": "hauteur dans l'image",
        "solid": "ligne pleine",
        "dashed": "ligne pointillée",
        "lamp": [("N00", "Sans l'effet"), ("N02", "Flou 100, « Circulaire »"), ("N05", "Flou 100, « 6 lamelles »")],
        "zoom": "le disque,\nagrandi",
    },
    "en": {
        "pct": "{}%",
        "lake_ref": "Blur 0/0, zones A to D",
        "lake_max": "Blur 100/100",
        "lake_cols": ["0/0", "51/51", "100/100", "100/0"],
        "night_ref": "Without the effect (N00)",
        "night_lines": "In PhotoLab: Blur 100/100, the tool's lines",
        "strips": [("N00", "N00\nwithout the effect"), ("N01", "N01\nBlur 50"), ("N02", "N02\nBlur 100")],
        "height": "height in the image",
        "solid": "solid line",
        "dashed": "dashed line",
        "lamp": [("N00", "Without the effect"), ("N02", "Blur 100, “Circular”"), ("N05", "Blur 100, “6 blades”")],
        "zoom": "the disc,\nenlarged",
    },
}


def no_axes(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ax.spines.values():
        side.set_visible(False)


def frame(ax, box, scale=1.0, lw=1.0):
    """Draw a white frame around box = (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = [v * scale for v in box]
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec="white", lw=lw))


def save(fig, lang, name):
    folder = ROOT / lang / "figures"
    folder.mkdir(exist_ok=True)
    fig.savefig(folder / name, dpi=220, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"wrote {lang}/figures/{name}")


# ====================================================================== photo 1: the lake
# PhotoLab screenshots. For each one: top-left corner of the photo inside the screenshot.
LAKE = [("lake_blur_000_000.png", 205, 6), ("lake_blur_051_051.png", 113, 0),
        ("lake_blur_100_100.png", 29, 4), ("lake_blur_100_000_9blades.png", 45, 4)]
LAKE_W, LAKE_H = 1349, 1004            # part of the photo visible in all four screenshots
LAKE_FULL_H = 1012                     # height of the whole photo at that display scale
ZONES = [("A", (950, 0, 1270, 160)), ("B", (620, 430, 940, 590)),
         ("C", (1000, 640, 1320, 800)), ("D", (80, 840, 400, 1000))]


def figures_lake(lang):
    t = TEXT[lang]
    lake = [Image.open(SCREENSHOTS / f).convert("RGB").crop((x0, y0, x0 + LAKE_W, y0 + LAKE_H))
            for f, x0, y0 in LAKE]

    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.5))
    for ax, im, title in zip(axs, [lake[0], lake[2]], [t["lake_ref"], t["lake_max"]]):
        ax.imshow(im)
        ax.set_title(title)
        no_axes(ax)
    for name, box in ZONES:
        frame(axs[0], box, lw=1.1)
        axs[0].text(box[0] + 12, box[1] + 14, name, color="white", fontsize=8, va="top", path_effects=OUTLINE)
    fig.tight_layout(pad=0.4)
    save(fig, lang, "fig_lake.png")

    fig, axs = plt.subplots(4, 4, figsize=(6.3, 3.55))
    for i, (name, box) in enumerate(ZONES):
        for j, im in enumerate(lake):
            axs[i, j].imshow(im.crop(box))
            no_axes(axs[i, j])
            if i == 0:
                axs[i, j].set_title(t["lake_cols"][j], fontsize=8)
        span = t["pct"].format(f"{100 * box[1] / LAKE_FULL_H:.0f}–{100 * box[3] / LAKE_FULL_H:.0f}")
        axs[i, 0].set_ylabel(f"{name} ({span})", fontsize=8)
    fig.tight_layout(pad=0.25, h_pad=0.25, w_pad=0.25)
    save(fig, lang, "fig_lake_zones.png")


# ====================================================================== photo 2: the night view
NIGHT = {"N00": "N00_sans_effet.jpg", "N01": "nuitN01_flou50.jpg",
         "N02": "nuitN02_flou100.jpg", "N05": "nuitN05_6lamelles.jpg"}
HEIGHT = 3000                                    # the exports are 4000 x 3000 pixels
STRIP = (3060, 0, 3460, 1050)                    # vertical strip, from the top edge down to 35 %: x0, y0, x1, y1
LAMP = (3188, 0, 3448, 260)                      # one lamp, at the top of that strip
CAPTURE = "night_blur_100_100_lines.jpg"         # PhotoLab screenshot with the tool's lines displayed
CAPTURE_PHOTO = (201, 1, 1278, 807)              # where the photo is inside that screenshot
LINES = [(0.10, "--"), (0.30, "-"), (0.70, "-"), (0.90, "--")]     # height of the tool's lines, read on the screenshot


def night(code):
    return Image.open(EXPORTS / NIGHT[code]).convert("RGB")


def figure_night(lang):
    """The photo without the effect, next to the PhotoLab screenshot that shows the tool's lines."""
    t = TEXT[lang]
    fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.5))

    photo = night("N00")
    scale = 1000 / photo.width
    axs[0].imshow(photo.resize((1000, round(photo.height * scale)), Image.LANCZOS))
    frame(axs[0], STRIP, scale)
    frame(axs[0], LAMP, scale)
    axs[0].set_title(t["night_ref"])

    capture = Image.open(SCREENSHOTS / CAPTURE).convert("RGB").crop(CAPTURE_PHOTO)
    axs[1].imshow(capture)
    for (height, style), name in zip(LINES, [t["dashed"], t["solid"], t["solid"], t["dashed"]]):
        axs[1].text(capture.width - 14, height * capture.height - 8, name, color="white", fontsize=7,
                    ha="right", va="bottom", path_effects=OUTLINE)
    axs[1].set_title(t["night_lines"])

    for ax in axs:
        no_axes(ax)
    fig.tight_layout(pad=0.4)
    save(fig, lang, "fig_night.png")


def figure_strips(lang):
    """The same vertical strip of the photo in three exports, with the height on the left axis."""
    t = TEXT[lang]
    x0, y0, x1, y1 = STRIP
    fig, axs = plt.subplots(1, 3, figsize=(5.2, 4.4), sharey=True)
    for ax, (code, title) in zip(axs, t["strips"]):
        ax.imshow(night(code).crop(STRIP), extent=(0, x1 - x0, y1, y0))
        for height, style in LINES[:2]:                                  # the two lines of the top side
            ax.axhline(height * HEIGHT, color="white", lw=1.0, ls=style)
        ax.set_title(title, fontsize=8)
        ax.set_xticks([])
        for side in ("top", "right", "bottom"):
            ax.spines[side].set_visible(False)
    ticks = [0, 10, 20, 30]
    axs[0].set_yticks([p * HEIGHT / 100 for p in ticks])
    axs[0].set_yticklabels([t["pct"].format(p) for p in ticks])
    axs[0].set_ylabel(t["height"])
    axs[0].text(12, 0.10 * HEIGHT - 12, t["dashed"], color="white", fontsize=7, va="bottom", path_effects=OUTLINE)
    axs[0].text(12, 0.30 * HEIGHT - 12, t["solid"], color="white", fontsize=7, va="bottom", path_effects=OUTLINE)
    fig.tight_layout(pad=0.4, w_pad=0.6)
    save(fig, lang, "fig_strips.png")


def figure_lamp(lang):
    """Zoom on one lamp: without the effect, then blurred with two different shapes."""
    t = TEXT[lang]
    fig, axs = plt.subplots(1, 3, figsize=(5.4, 2.0))
    for ax, (code, title) in zip(axs, t["lamp"]):
        ax.imshow(night(code).crop(LAMP))
        ax.set_title(title, fontsize=8)
        no_axes(ax)
    fig.tight_layout(pad=0.3)
    save(fig, lang, "fig_lamp.png")


# ====================================================================== the test images
def figure_test_images(lang):
    """The four test images, each one shown whole."""
    t = TEXT[lang]
    fig, axs = plt.subplots(1, 4, figsize=(6.3, 1.5))
    for ax, name in zip(axs, ["gray.tif", "checkerboard.tif", "column.tif", "disc.tif"]):
        image = np.asarray(Image.open(TEST_IMAGES / name))[..., 0]
        h, w = image.shape
        small = image.reshape(h // 10, 10, w // 10, 10).max(axis=(1, 3))  # 10 times smaller; max keeps the discs visible
        ax.imshow(small, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        ax.set_title(name, fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])

    # the disc is tiny at this scale: enlarge it in a corner of the last picture
    image = np.asarray(Image.open(TEST_IMAGES / "disc.tif"))[..., 0]
    cx, cy, half = DISC_X, DISC_Y[0], 30
    inset = axs[3].inset_axes([0.60, 0.08, 0.33, 0.44])
    inset.imshow(image[cy - half:cy + half, cx - half:cx + half], cmap="gray", vmin=0, vmax=255, interpolation="nearest")
    inset.set_xticks([])
    inset.set_yticks([])
    for side in inset.spines.values():
        side.set_color("0.6")
    axs[3].text(0.55, 0.30, t["zoom"], color="0.75", fontsize=6.5, ha="right", va="center", transform=axs[3].transAxes)
    fig.tight_layout(pad=0.3, w_pad=0.5)
    save(fig, lang, "fig_test_images.png")


if __name__ == "__main__":
    for lang in TEXT:
        if not (ROOT / lang).is_dir():           # only the languages that have a notes folder
            continue
        figures_lake(lang)
        figure_night(lang)
        figure_strips(lang)
        figure_lamp(lang)
        figure_test_images(lang)
