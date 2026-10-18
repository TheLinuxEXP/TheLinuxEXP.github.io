#!/usr/bin/env python3
"""Checks the SEO tags of a built site (the _site folder made by `jekyll build`).

    bundle exec jekyll build
    python3 _tools/check_seo.py            # checks ./_site
    python3 _tools/check_seo.py /path/to/_site

Prints one line per problem and a summary. Exits with 1 when something is wrong.
"""
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.links, self.jsonld = "", {}, {}, []
        self.h1, self.imgs_no_alt, self.charsets = 0, 0, 0
        self._in, self._buf = None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in = "title"
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in, self._buf = "ld", []
        elif tag == "meta":
            if "charset" in a:
                self.charsets += 1
            key = a.get("property") or a.get("name") or a.get("itemprop")
            if key:
                self.meta.setdefault(key, []).append(a.get("content", ""))
        elif tag == "link" and a.get("rel"):
            self.links[a["rel"]] = a.get("href", "")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img" and not (a.get("alt") or "").strip():
            self.imgs_no_alt += 1

    def handle_data(self, data):
        if self._in == "title":
            self.title += data
        elif self._in == "ld":
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in == "ld":
            self.jsonld.append("".join(self._buf))
        if tag in ("title", "script"):
            self._in = None


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if not root.is_dir():
        sys.exit(f"{root} not found. Run `bundle exec jekyll build` first.")
    problems, stats = [], Counter()
    for path in sorted(root.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "http-equiv=\"refresh\"" in text[:600] or "<head" not in text:
            continue                                   # redirect stubs, fragments
        rel = "/" + path.relative_to(root).as_posix()
        page = Page(); page.feed(text)
        stats["pages"] += 1
        noindex = any("noindex" in v for v in page.meta.get("robots", []))
        found = lambda msg: problems.append(f"{rel}: {msg}")
        if not page.title.strip(): found("no <title>")
        elif len(page.title.strip()) > 70: found(f"title is {len(page.title.strip())} characters")
        desc = (page.meta.get("description") or [""])[0]
        if not desc.strip(): found("no meta description")
        elif len(desc) > 200: found(f"meta description is {len(desc)} characters")
        if page.charsets != 1: found(f"{page.charsets} charset declarations")
        if "canonical" not in page.links: found("no canonical link")
        elif not page.links["canonical"].startswith("http"): found("canonical is not an absolute URL")
        for key in ("og:title", "og:description", "og:url", "og:type", "og:site_name"):
            if not page.meta.get(key): found(f"no {key}")
        if page.meta.get("og:type", [""])[0] == "article":
            stats["articles"] += 1
            for key in ("article:published_time", "article:modified_time"):
                if not page.meta.get(key): found(f"no {key}")
            if not page.meta.get("og:image"): stats["articles without og:image"] += 1
            if page.h1 != 1: found(f"{page.h1} <h1> elements (expected 1)")
            if not page.jsonld: found("no JSON-LD")
        for block in page.jsonld:
            try:
                data = json.loads(block)
                stats["json-ld blocks"] += 1
                if "BlogPosting" not in block and page.meta.get("og:type", [""])[0] == "article": found("JSON-LD has no BlogPosting")
            except ValueError as error:
                found(f"JSON-LD is not valid JSON ({error})")
        if noindex: stats["noindex pages"] += 1
        if page.imgs_no_alt: stats["images without alt"] += page.imgs_no_alt
    robots = root / "robots.txt"
    if not robots.is_file() or "Sitemap:" not in robots.read_text():
        problems.append("robots.txt is missing or has no Sitemap line")
    if not (root / "sitemap.xml").is_file():
        problems.append("sitemap.xml is missing")
    print("\n".join(problems) if problems else "No problem found.")
    print("\n" + ", ".join(f"{v} {k}" for k, v in stats.items()))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
