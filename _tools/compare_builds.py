#!/usr/bin/env python3
"""Compare two built copies of the site (the old one and the new one).

    # old site (its own Gemfile with the github-pages gem)
    bundle exec jekyll build --destination /tmp/site-old
    # new site
    bundle exec jekyll build --destination /tmp/site-new
    python3 _tools/compare_builds.py /tmp/site-old /tmp/site-new

Whitespace between tags and the cache-busting "?v=" on the stylesheet link are
ignored. Anything else that differs is printed.
"""
import difflib
import re
import sys
from pathlib import Path

TEXT = {".html", ".xml", ".json", ".css", ".txt"}
IGNORE_FILES = {"sitemap.xml"}  # contains the build time


def normalize(text: str) -> list:
    text = re.sub(r"\?v=\d+", "", text)
    text = re.sub(r">\s*<", ">\n<", text)
    text = re.sub(r"[ \t]+", " ", text)
    return [line.strip() for line in text.splitlines() if line.strip()]


def main(old: Path, new: Path) -> int:
    old_files = {p.relative_to(old) for p in old.rglob("*") if p.is_file()}
    new_files = {p.relative_to(new) for p in new.rglob("*") if p.is_file()}
    problems = 0
    for rel in sorted(old_files - new_files):
        print(f"MISSING in new site: {rel}")
        problems += 1
    for rel in sorted(new_files - old_files):
        print(f"EXTRA in new site:   {rel}")
    for rel in sorted(old_files & new_files):
        if rel.name in IGNORE_FILES:
            continue
        a, b = old / rel, new / rel
        if rel.suffix in TEXT:
            left, right = normalize(a.read_text(errors="replace")), normalize(b.read_text(errors="replace"))
            if left != right:
                problems += 1
                print(f"\nDIFFERENT: {rel}")
                for line in list(difflib.unified_diff(left, right, "old", "new", lineterm="", n=0))[:40]:
                    print("  " + line)
        elif a.read_bytes() != b.read_bytes():
            problems += 1
            print(f"DIFFERENT (binary): {rel}")
    print(f"\n{len(old_files & new_files)} files compared, {problems} with differences.")
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
