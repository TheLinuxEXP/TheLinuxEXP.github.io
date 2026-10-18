import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
marker = "### What the site publishes for search engines"
new = """### Images: replace and make lighter

- In the visual editor, click a picture: **Replace image** swaps it for another file everywhere it is used in the
  text, and **Make lighter** converts it.
- In the SEO tab, *Image weight* lists the heavy images with **Make lighter** (or **Make all N lighter**) and **Replace…**.
- Converting is careful on purpose. Flat graphics become lossless WebP (not a pixel changes); screenshots and
  photos become WebP at quality 95 only if a check shows the result is visually the same, over the whole picture
  *and* in every part of it (small text cannot hide behind a big background); otherwise they stay lossless.
  Images wider than 2000 px are scaled down once. If a result is not at least 15 % smaller, it is not used.
  The featured image keeps its format (PNG or JPEG), because link previews do not accept WebP everywhere.
- The text (and the featured image field) are switched to the new file at once. The old file is **not** touched
  until you **save**: then every old file that nothing else uses is moved (not deleted) to
  `admin/.data/image-originals/`, outside the site, so it is not published or committed. Put it back by moving it
  to the same path under `images/`. A file still used by another article stays where it is.
- Converting needs the Pillow library; `./admin/start.sh` installs it the first time it is missing.

"""
if "### Images: replace and make lighter" in s:
    sys.exit("already patched")
assert marker in s
open(p, "w", encoding="utf-8").write(s.replace(marker, new + marker, 1))
print("patched", p)
