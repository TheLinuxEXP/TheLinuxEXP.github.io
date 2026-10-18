"""Makes site images lighter without making them worse.

The rules are conservative on purpose, because screenshots must stay crisp and legible:

  * flat graphics and diagrams (few distinct colours) become *lossless* WebP: not one pixel changes;
  * photos, and screenshots with gradients or a wallpaper, become WebP at quality 95, and only when the result
    passes a check: PSNR of at least 42 dB overall AND at least 32 dB in every part of the picture, so
    small text cannot be hidden by a large smooth background. Otherwise they stay lossless;
  * images wider than MAX_WIDTH are scaled down once (a 4000 px screenshot is never shown that big);
  * a result that is not at least MIN_SAVING smaller is thrown away and the original is kept;
  * for the featured image (used by link previews, where WebP is not accepted everywhere)
    the format is kept: PNG stays PNG, JPEG stays JPEG.

The original file is never touched here: the new file is written beside it.
"""

import io
from math import log10
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageOps, ImageStat
    HAVE_PILLOW = True
except ImportError:          # the admin still starts; converting just says what to install
    HAVE_PILLOW = False

MAX_WIDTH = 2000
MIN_BYTES = 20 * 1024        # smaller files are not worth touching
MIN_SAVING = 0.15           # keep the result only if it is at least 15 % smaller
FLAT_COLORS = 2000          # up to this many distinct colours = flat graphic / diagram: always lossless
PHOTO_QUALITY = 95
MIN_PSNR = 42.0
MIN_TILE_PSNR = 32.0
CONVERTIBLE = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


class ImageError(Exception):
    """Something the person should read (unsupported file, animated image...)."""


def _psnr(a, b) -> float:
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    rms = sum(ImageStat.Stat(diff).rms) / 3
    return 99.0 if rms == 0 else 20 * log10(255 / rms)


def _worst_tile_psnr(a, b, grid: int = 8) -> float:
    width, height = a.size
    worst = 99.0
    for i in range(grid):
        for j in range(grid):
            box = (i * width // grid, j * height // grid, (i + 1) * width // grid, (j + 1) * height // grid)
            if box[2] > box[0] and box[3] > box[1]:
                worst = min(worst, _psnr(a.crop(box), b.crop(box)))
    return worst


def _encode(img, fmt: str, **options) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, fmt, **options)
    return buffer.getvalue()


def _unique(path: Path) -> Path:
    candidate, number = path, 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{number}{path.suffix}")
        number += 1
    return candidate


def optimize(path: Path, keep_format: bool = False) -> dict:
    """Writes a lighter copy of `path` next to it. Returns what happened:
    {"changed": True, "path": Path, ...} or {"changed": False, "reason": "..."}."""
    if not HAVE_PILLOW:
        raise ImageError("Converting images needs the Pillow library. Stop the admin and start it again with ./admin/start.sh: it installs it.")
    suffix = path.suffix.lower()
    if suffix == ".webp":
        return {"changed": False, "reason": "Already a WebP image."}
    if suffix not in CONVERTIBLE:
        return {"changed": False, "reason": f"{suffix or 'This file type'} is not converted."}
    original_size = path.stat().st_size
    if original_size < MIN_BYTES:
        return {"changed": False, "reason": f"Already small ({max(1, original_size // 1024)} KB)."}
    try:
        img = Image.open(path)
        img.load()
    except Exception as error:   # Pillow raises many kinds of errors for broken files
        raise ImageError(f"This image could not be read ({error.__class__.__name__}).") from error
    if getattr(img, "n_frames", 1) > 1:
        return {"changed": False, "reason": "Animated images are left as they are."}
    img = ImageOps.exif_transpose(img) or img
    width, height = img.size
    resized = False
    if width > MAX_WIDTH:
        img = img.resize((MAX_WIDTH, max(1, round(height * MAX_WIDTH / width))), Image.LANCZOS)
        resized = True
    has_alpha = img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info
    work = img.convert("RGBA" if has_alpha else "RGB")
    flat = work.getcolors(maxcolors=FLAT_COLORS) is not None   # None when there are more colours

    if keep_format:
        if suffix in (".jpg", ".jpeg"):
            data, label, out_suffix = _encode(work.convert("RGB"), "JPEG", quality=90, optimize=True, progressive=True), "JPEG, quality 90", ".jpg"
        else:
            data, label, out_suffix = _encode(work, "PNG", optimize=True), "PNG, lossless", ".png"
    elif flat:
        data, label, out_suffix = _encode(work, "WEBP", lossless=True, quality=75, method=4), "lossless WebP", ".webp"
    else:
        lossy = _encode(work, "WEBP", quality=PHOTO_QUALITY, method=6, alpha_quality=100)
        decoded = Image.open(io.BytesIO(lossy))
        if _psnr(work, decoded) >= MIN_PSNR and _worst_tile_psnr(work, decoded) >= MIN_TILE_PSNR:
            data, label = lossy, f"WebP, quality {PHOTO_QUALITY}"
        else:                                   # not visually identical: keep every pixel instead
            data, label = _encode(work, "WEBP", lossless=True, quality=75, method=4), "lossless WebP"
        out_suffix = ".webp"

    if len(data) > original_size * (1 - MIN_SAVING):
        saving = "" if len(data) >= original_size else f" (only {round(100 * (1 - len(data) / original_size))} % smaller)"
        return {"changed": False, "reason": f"Converting would not make it much lighter{saving}, so it is left as it is."}
    target = path.with_suffix(out_suffix)
    if target == path or target.exists():
        target = _unique(path.with_name(path.stem + "-optimized" + out_suffix) if target == path else target)
    target.write_bytes(data)
    return {"changed": True, "path": target, "old_bytes": original_size, "new_bytes": len(data),
            "format": label, "resized": resized, "size": img.size, "old_size": (width, height)}
