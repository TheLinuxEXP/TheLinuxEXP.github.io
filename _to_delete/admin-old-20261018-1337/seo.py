"""SEO helpers for the editor's SEO tab.

Everything here is plain text analysis that runs on this computer: no network,
no AI. It looks at the Markdown of the article being edited and proposes

  * the meta tags the site's <head> uses (description, featured image) when they are missing,
  * alt text for images that have none,
  * links from phrases in the text to other pages and articles of the site.

Nothing is changed here. The editor shows the proposals and applies the ones
the person accepts.
"""

import re
from collections import Counter
from math import log

DESCRIPTION_MIN, DESCRIPTION_MAX = 70, 160
TITLE_MIN, TITLE_MAX = 25, 65
MAX_LINK_SUGGESTIONS = 12

STOP_WORDS = frozenset("""
a about above after again all also am an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers him his how
i if in into is it its just me more most my no nor not now of off on once only or other our out over own same she
should so some such than that the their them then there these they this those through to too under until up very
was we were what when where which while who whom why will with would you your yours
""".split())

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif")

FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,}).*?^(?P=fence)[ \t]*$", re.S | re.M)
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1", re.S)
MD_IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]\n]*)\]\((?P<src>[^)\s]+)(?:\s+\"[^\"]*\")?\)")
MD_LINK_RE = re.compile(r"\[(?:[^\]\n]|\\\])*\]\([^)\n]*\)")
REF_LINK_RE = re.compile(r"\[[^\]\n]*\]\[[^\]\n]*\]|^\[[^\]\n]+\]:.*$", re.M)
AUTOLINK_RE = re.compile(r"<(?:https?://|mailto:)[^>\s]+>|https?://[^\s<>\")]+")
HTML_TAG_RE = re.compile(r"<[A-Za-z/!][^>]*>")
LIQUID_RE = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S)
HTML_IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
ATTR_RE = r"""(?:\s|^){name}\s*=\s*(?:"([^"]*)"|'([^']*)')"""
HEADING_LINE_RE = re.compile(r"^ {0,3}#{1,6}[ \t].*$", re.M)
HTML_LINE_RE = re.compile(r"^[ \t]*<.*$", re.M)
WORD_RE = re.compile(r"[\w'’]+", re.U)


# --------------------------------------------------------------------------
# text helpers
# --------------------------------------------------------------------------
def _mask(text: str, pattern: re.Pattern, mask: bytearray) -> None:
    for match in pattern.finditer(text):
        mask[match.start():match.end()] = b"\x01" * (match.end() - match.start())


def protected_mask(text: str) -> bytearray:
    """1 where the text must never be turned into a link (code, links, HTML, headings...)."""
    mask = bytearray(len(text))
    for pattern in (FENCE_RE, INLINE_CODE_RE, MD_IMAGE_RE, MD_LINK_RE, REF_LINK_RE, AUTOLINK_RE,
                    HTML_TAG_RE, LIQUID_RE, HEADING_LINE_RE, HTML_LINE_RE):
        _mask(text, pattern, mask)
    return mask


def plain_text(markdown: str) -> str:
    """The readable text of a Markdown body, for summaries."""
    text = FENCE_RE.sub(" ", markdown)
    text = LIQUID_RE.sub(" ", text)
    text = MD_IMAGE_RE.sub(" ", text)
    text = re.sub(r"<(script|style|iframe)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"\[([^\]\n]*)\]\([^)\n]*\)", r"\1", text)
    text = AUTOLINK_RE.sub(" ", text)
    text = re.sub(r"^ {0,3}#{1,6}[ \t]+", "", text, flags=re.M)
    text = re.sub(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]+", "", text, flags=re.M)
    text = re.sub(r"^[ \t]*>+[ \t]?", "", text, flags=re.M)
    text = re.sub(r"[*_`~]+", "", text)
    text = re.sub(r"^\s*\|.*\|\s*$", " ", text, flags=re.M)
    return re.sub(r"\s+", " ", text).strip()


def _sentences(text: str) -> list:
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-Z0-9\"“‘(])", text)
    return [part.strip() for part in parts if part.strip()]


def _words(text: str) -> list:
    return [w.lower().strip("'’") for w in WORD_RE.findall(text)]


def _keywords(text: str) -> list:
    return [w for w in _words(text) if len(w) > 2 and w not in STOP_WORDS and not w.isdigit()]


def _humanize(filename: str) -> str:
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", filename.rsplit("/", 1)[-1])
    stem = re.sub(r"[-_.]+", " ", stem)
    stem = re.sub(r"\b(?:img|image|screenshot|screen shot|dsc|pxl|photo)\b|\b\d{6,}\b", " ", stem, flags=re.I)
    return re.sub(r"\s+", " ", stem).strip()


def _looks_generic(name: str) -> bool:
    words = name.split()
    return len(name) < 4 or not words or all(w.isdigit() for w in words)


# --------------------------------------------------------------------------
# meta tags
# --------------------------------------------------------------------------
def suggest_description(title: str, body: str) -> str:
    """About 150 characters made of whole sentences from the start of the text."""
    paragraphs = []
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block or re.match(r"^(?:#|>|\||[-*+]\s|\d+[.)]\s|<|\{%|\{\{|!\[|```|~~~|\[[^\]]+\]:)", block):
            continue                       # headings, lists, quotes, tables, HTML, images and code are not the opening text
        paragraphs.append(block)
    marked = AUTOLINK_RE.sub("\x00", "\n\n".join(paragraphs[:4]))      # sentences holding a web address are not used
    text = plain_text(marked)
    if not text:
        return ""
    chosen = ""
    for sentence in _sentences(text):
        if "\x00" in sentence or sentence.rstrip(".!?…").lower() == (title or "").rstrip(".!?…").lower():
            continue
        candidate = f"{chosen} {sentence}".strip()
        if len(candidate) > DESCRIPTION_MAX:
            if not chosen:
                cut = candidate[:DESCRIPTION_MAX - 1].rsplit(" ", 1)[0].rstrip(" ,;:-–—")
                return cut + "…"
            break
        chosen = candidate
        if len(chosen) >= 110:
            break
    return chosen


def images_in(body: str) -> list:
    """Every image of the body, in order: Markdown ones and <img> tags (not those inside code)."""
    code = bytearray(len(body))
    _mask(body, FENCE_RE, code)
    _mask(body, INLINE_CODE_RE, code)
    found = []
    for match in MD_IMAGE_RE.finditer(body):
        if code[match.start()]:
            continue
        found.append({"kind": "markdown", "start": match.start(), "end": match.end(),
                      "src": match.group("src"), "alt": match.group("alt").strip(),
                      "alt_span": match.span("alt")})
    for match in HTML_IMG_RE.finditer(body):
        if code[match.start()]:
            continue
        tag = match.group(0)
        src = re.search(ATTR_RE.format(name="src"), tag, re.I)
        alt = re.search(ATTR_RE.format(name="alt"), tag, re.I)
        found.append({"kind": "html", "start": match.start(), "end": match.end(),
                      "src": (src.group(1) or src.group(2) or "") if src else "",
                      "alt": ((alt.group(1) or alt.group(2) or "").strip() if alt else ""),
                      "has_alt_attr": bool(alt), "alt_span": None})
    found.sort(key=lambda item: item["start"])
    return found


def _context_for(body: str, image: dict) -> dict:
    """The caption and the nearest heading around an image."""
    after = body[image["end"]:image["end"] + 400]
    stop = re.search(r"!\[|<img\b|<figure\b|^ {0,3}#{1,6}[ \t]", after, re.M | re.I)
    after = after[:stop.start()] if stop else after          # a caption after the NEXT image is not ours
    caption = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", after, re.S | re.I)
    before = body[:image["start"]]
    headings = re.findall(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t#]*$", before, re.M)
    return {"caption": plain_text(caption.group(1)) if caption else "",
            "heading": re.sub(r"[*_`]", "", headings[-1]).strip() if headings else ""}


def suggest_alt(title: str, body: str, image: dict) -> dict:
    """A short description for the image from its caption, file name or surroundings."""
    context = _context_for(body, image)
    name = _humanize(image["src"])
    if context["caption"]:
        return {"text": _shorten(context["caption"], 125), "from": "its caption"}
    if not _looks_generic(name):
        words = name[0].upper() + name[1:] if name else name
        return {"text": _shorten(words, 125), "from": "its file name"}
    if context["heading"]:
        return {"text": _shorten(context["heading"], 125), "from": "the heading above it"}
    return {"text": _shorten(title or "", 125), "from": "the article title"}


def _shorten(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:-–—") + "…"


# --------------------------------------------------------------------------
# internal links
# --------------------------------------------------------------------------
def _ngrams(words: list, low: int = 1, high: int = 5):
    for size in range(high, low - 1, -1):
        for start in range(0, len(words) - size + 1):
            yield start, size, words[start:start + size]


def _anchor_candidates(page: dict, frequency: Counter, total: int, tag_uses: Counter) -> list:
    """Phrases that could point to this page: its title, the part of it before a colon,
    multi-word tags and runs of meaningful words from the title."""
    rare = max(2, round(total * 0.07))           # a single word is only an anchor when few pages use it
    phrases = {}

    def add(phrase: str, weight: float):
        phrase = " ".join(phrase.split()).strip(" -–—:,.?!()\"“”")
        if len(phrase) < 4:
            return
        words = phrase.split()
        if words[0].lower() in STOP_WORDS or words[-1].lower() in STOP_WORDS:
            return
        key = phrase.lower()
        if key not in phrases or phrases[key][1] < weight:
            phrases[key] = (phrase, weight)

    title = page["title"]
    add(title, 3.0)
    for part in re.split(r"\s[:\-–—|]\s|:\s", title):
        if part != title:
            add(part, 2.4)
    for tag in page.get("tags", []):
        if len(tag.split()) >= 2 and tag_uses[tag.lower()] <= 2:     # a tag many pages share is a topic, not one page
            add(tag, 1.0)
    words = title.split()
    for word in words[1:]:
        bare = re.sub(r"^\W+|\W+$", "", word)
        if len(bare) >= 3 and (bare.isupper() or re.search(r"[a-z][A-Z]", bare)):
            add(bare, 1.4)                        # acronyms and CamelCase names: KDE, GNOME, YouTube
    for _start, size, grams in _ngrams(words, 2, 4):
        clean = [re.sub(r"^\W+|\W+$", "", g) for g in grams]
        if any(not c or c.lower() in STOP_WORDS for c in clean):
            continue                              # runs of meaningful words only
        add(" ".join(clean), 0.8 + 0.2 * size)
    scored = []
    for phrase, weight in phrases.values():
        keywords = _keywords(phrase)
        if not keywords:
            continue
        if len(phrase.split()) == 1:
            # one word is only an anchor when it is a name (KDE, YouTube, Kdenlive) used by few pages, or the whole title
            name_like = phrase == title or bool(re.search(r"[A-Z].*[A-Z]|\d", phrase))
            if not name_like or len(phrase) < 3 or frequency.get(keywords[0], 0) > rare:
                continue
        rarity = sum(log(1 + total / max(1, frequency.get(k, 1))) for k in keywords)
        scored.append((phrase, weight * (1 + rarity / 4)))
    return scored


def suggest_links(body: str, pages: list, self_url: str = "", title: str = "") -> list:
    """Phrases of `body` that could link to other pages. Each suggestion carries the
    exact position of the phrase so the editor can turn it into a link in one click."""
    pages = [p for p in pages if p.get("url") and p["url"] != self_url and p.get("title")]
    if not pages or not body.strip():
        return []
    document_frequency = Counter()
    page_keywords = {}
    for page in pages:
        keywords = set(_keywords(page["title"]) + [w for t in page.get("tags", []) for w in _keywords(t)])
        page_keywords[page["url"]] = keywords
        document_frequency.update(keywords)
    total = len(pages)
    tag_uses = Counter(tag.lower() for page in pages for tag in set(page.get("tags", [])))
    body_words = Counter(_keywords(plain_text(body) + " " + title))
    mask = protected_mask(body)
    linked = {m.group(1).split("#")[0] for m in re.finditer(r"\]\(([^)\s]+)", body)}
    linked |= {m.group(1).split("#")[0] for m in re.finditer(r"href=[\"']([^\"']+)", body)}
    suggestions = []
    for page in pages:
        if page["url"] in linked or page["url"].rstrip("/") in linked:
            continue
        related = sum(1 for k in page_keywords[page["url"]] if body_words[k])
        best = None
        for phrase, weight in _anchor_candidates(page, document_frequency, total, tag_uses):
            pattern = re.compile(r"(?<![\w])" + re.escape(phrase).replace(r"\ ", r"\s+") + r"(?![\w])", re.I)
            for match in pattern.finditer(body):
                if any(mask[match.start():match.end()]):
                    continue
                # the phrase must not start or end inside a word-joining character such as a hyphen or slash
                before = body[match.start() - 1:match.start()]
                after = body[match.end():match.end() + 1]
                if (before and before in "-/_") or (after and after in "-/_"):
                    continue
                score = weight * (1 + 0.15 * related)
                if best is None or score > best["score"]:
                    best = {"start": match.start(), "end": match.end(), "phrase": match.group(0),
                            "score": round(score, 2)}
                break                       # first usable occurrence of this phrase
        if best:
            best.update(url=page["url"], title=page["title"], kind=page.get("kind", ""))
            suggestions.append(best)
    # strongest first; two suggestions may not overlap
    suggestions.sort(key=lambda s: -s["score"])
    chosen = []
    for s in suggestions:
        if any(s["start"] < c["end"] and c["start"] < s["end"] for c in chosen):
            continue
        chosen.append(s)
        if len(chosen) >= MAX_LINK_SUGGESTIONS:
            break
    chosen.sort(key=lambda s: s["start"])
    for s in chosen:
        s["context"] = _context_snippet(body, s["start"], s["end"])
    return chosen


def _context_snippet(body: str, start: int, end: int, width: int = 60) -> dict:
    """A few words around the phrase, never crossing into another line."""
    line_start = body.rfind("\n", 0, start) + 1
    line_end = body.find("\n", end)
    line_end = len(body) if line_end < 0 else line_end
    left, right = body[max(line_start, start - width):start], body[end:min(line_end, end + width)]
    cut_left, cut_right = start - width > line_start, end + width < line_end
    if cut_left:
        left = left.split(" ", 1)[-1]
    if cut_right:
        right = right.rsplit(" ", 1)[0]
    return {"before": ("…" if cut_left else "") + left, "after": right + ("…" if cut_right else "")}


def apply_link(body: str, start: int, end: int, phrase: str, url: str) -> str:
    """Turns body[start:end] into a Markdown link. Refuses if the text moved meanwhile."""
    if body[start:end] != phrase:
        raise ValueError("The text changed since the suggestion was made. Run the analysis again.")
    return body[:start] + f"[{phrase}]({url})" + body[end:]


# --------------------------------------------------------------------------
# the whole analysis
# --------------------------------------------------------------------------
def analyze(fields: dict, body: str, pages: list, self_url: str = "", slug: str = "",
            root=None, inbound=None, slug_locked: bool = False) -> dict:
    title = " ".join(str(fields.get("title") or "").split())
    description = " ".join(str(fields.get("description") or "").split())
    image = str(fields.get("image") or "").strip()
    kind = fields.get("kind", "article")
    imgs = images_in(body)

    meta = []
    if description:
        note = None
        if len(description) < DESCRIPTION_MIN:
            note = f"Short ({len(description)} characters). Search results show about {DESCRIPTION_MIN}–{DESCRIPTION_MAX}."
        elif len(description) > DESCRIPTION_MAX:
            note = f"Long ({len(description)} characters). Search results cut it after about {DESCRIPTION_MAX}."
        meta.append({"key": "description", "label": "Description", "state": "ok" if not note else "warn",
                     "current": description, "suggestion": "", "note": note})
    else:
        meta.append({"key": "description", "label": "Description", "state": "missing", "current": "",
                     "suggestion": suggest_description(title, body),
                     "note": "Without it, every search result and link preview shows the site's generic description."})
    if title and not (TITLE_MIN <= len(title) <= TITLE_MAX):
        meta.append({"key": "title", "label": "Title length", "state": "warn", "current": title, "suggestion": "",
                     "note": f"{len(title)} characters. Titles of {TITLE_MIN}–{TITLE_MAX} characters display fully in search results."})
    if kind == "article":
        if image:
            meta.append({"key": "image", "label": "Featured image", "state": "ok", "current": image, "suggestion": "", "note": None})
        else:
            first = next((i["src"] for i in imgs if i["src"].lower().split("?")[0].endswith(IMAGE_EXTENSIONS)), "")
            meta.append({"key": "image", "label": "Featured image", "state": "missing", "current": "",
                         "suggestion": first,
                         "note": "Shown on link previews (X, Discord, Mastodon...)." + ("" if first else " The text has no image to reuse yet.")})

    alts = []
    for number, item in enumerate(imgs):
        if item["alt"]:
            continue
        proposal = suggest_alt(title, body, item)
        alts.append({"index": number, "src": item["src"], "kind": item["kind"], "start": item["start"],
                     "end": item["end"], "text": proposal["text"], "from": proposal["from"],
                     "decorative_marked": item["kind"] == "html" and item.get("has_alt_attr", False)})

    return {"meta": meta, "alts": alts, "images": len(imgs),
            "links": suggest_links(body, pages, self_url, title),
            "checks": audit(fields, body, pages, imgs, slug, root, inbound, slug_locked)}



# --------------------------------------------------------------------------
# checks: things to look at, with no automatic fix
# --------------------------------------------------------------------------
IMAGE_CONVERTIBLE = frozenset({".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"})
THIN_WORDS = 300
IMAGE_HEAVY_KB = 200
GENERIC_ANCHORS = frozenset({"click here", "here", "this", "this link", "link", "read more", "more",
                             "this article", "this post", "this video", "check it out", "learn more"})
LINK_RE = re.compile(r"""(?<!!)\[(?P<text>[^\]\n]*)\]\((?P<url>[^)\s]+)(?:\s+"[^"]*")?\)""")
HREF_RE = re.compile(r"""<a\b[^>]*?\bhref\s*=\s*["'](?P<url>[^"']+)["']""", re.I)
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$", re.M)
KNOWN_PATHS = {"/", "/archive/", "/tags/", "/authors/", "/feed.xml", "/feed.json", "/sitemap.xml", "/robots.txt"}


def _code_mask(body: str) -> bytearray:
    mask = bytearray(len(body))
    _mask(body, FENCE_RE, mask)
    _mask(body, INLINE_CODE_RE, mask)
    return mask


def links_in(body: str) -> list:
    """[{'text', 'url'}] for every Markdown and HTML link outside code."""
    mask = _code_mask(body)
    found = [(m.start(), m.group("text").strip(), m.group("url")) for m in LINK_RE.finditer(body) if not mask[m.start()]]
    found += [(m.start(), "", m.group("url")) for m in HREF_RE.finditer(body) if not mask[m.start()]]
    found.sort()
    return [{"text": t, "url": u} for _, t, u in found]


def internal_path(url: str):
    """'/page/' for a link to this site, otherwise None."""
    if not url.startswith("/") or url.startswith("//") or "{" in url:
        return None
    return re.split(r"[?#]", url, maxsplit=1)[0] or None


def link_targets(body: str) -> set:
    return {p.rstrip("/") + "/" if "." not in p.rsplit("/", 1)[-1] else p
            for p in (internal_path(l["url"]) for l in links_in(body)) if p}


def image_size(path):
    """(width, height) of a PNG, JPEG, GIF or WebP file, read from its header, or None."""
    try:
        with open(path, "rb") as handle:
            head = handle.read(32)
            if head.startswith(b"\x89PNG\r\n\x1a\n"):
                return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
            if head[:6] in (b"GIF87a", b"GIF89a"):
                return int.from_bytes(head[6:8], "little"), int.from_bytes(head[8:10], "little")
            if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
                kind = head[12:16]
                if kind == b"VP8X":
                    return 1 + int.from_bytes(head[24:27], "little"), 1 + int.from_bytes(head[27:30], "little")
                if kind == b"VP8L":
                    bits = int.from_bytes(head[21:25], "little")
                    return 1 + (bits & 0x3FFF), 1 + ((bits >> 14) & 0x3FFF)
                if kind == b"VP8 ":
                    return int.from_bytes(head[26:28], "little") & 0x3FFF, int.from_bytes(head[28:30], "little") & 0x3FFF
                return None
            if head[:2] == b"\xff\xd8":
                handle.seek(2)
                while True:
                    marker = handle.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    length = int.from_bytes(handle.read(2), "big")
                    if marker[1] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                        data = handle.read(5)
                        return int.from_bytes(data[3:5], "big"), int.from_bytes(data[1:3], "big")
                    handle.seek(length - 2, 1)
    except OSError:
        return None
    return None


def _local_file(root, src: str):
    if root is None or not src.startswith("/") or src.startswith("//"):
        return None
    path = (root / re.split(r"[?#]", src, maxsplit=1)[0].lstrip("/")).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path if path.is_file() else None


def _check(key, label, state, note, items=None):
    return {"key": key, "label": label, "state": state, "note": note, "items": items or []}


def _has_words(text: str, words: list) -> bool:
    found = set(_words(text))
    return all(w in found for w in words)


def audit(fields: dict, body: str, pages: list, imgs: list, slug: str, root, inbound, slug_locked: bool = False) -> list:
    out = []
    title = " ".join(str(fields.get("title") or "").split())
    seo_title = " ".join(str(fields.get("seo_title") or "").split())
    description = " ".join(str(fields.get("description") or "").split())
    keyword = " ".join(str(fields.get("focus_keyword") or "").split())
    kind = fields.get("kind", "article")
    text = plain_text(body)
    words = _words(text)

    # SEO title
    if seo_title:
        n = len(seo_title)
        out.append(_check("seo_title", "Search title", "ok" if TITLE_MIN <= n <= TITLE_MAX else "warn",
                          f"{n} characters. Shown in search results and browser tabs instead of the article title."
                          + ("" if TITLE_MIN <= n <= TITLE_MAX else f" Aim for {TITLE_MIN}–{TITLE_MAX}.")))

    # headings
    heads = [(len(m.group(1)), m.group(2)) for m in HEADING_RE.finditer(_blank_code(body))]
    problems = []
    if any(level == 1 for level, _ in heads):
        problems.append("The page title is already the H1. Use “##” for section headings.")
    previous = 1
    for level, name in heads:
        if level > previous + 1 and level > 2:
            problems.append(f"“{_shorten(name, 50)}” jumps from H{previous} to H{level}. Don’t skip a level.")
        previous = level
    if len(words) >= 500 and not any(level == 2 for level, _ in heads):
        problems.append("Long text without sub-headings. Add “##” headings: search engines and readers scan them.")
    out.append(_check("headings", "Headings", "warn" if problems else "ok",
                      problems[0] if len(problems) == 1 else (f"{len(problems)} things to fix." if problems
                      else (f"{len(heads)} headings, in order." if heads else "No sub-headings (fine for a short text).")),
                      [{"label": p} for p in problems] if len(problems) > 1 else []))

    # length
    if kind == "article":
        thin = len(words) < THIN_WORDS
        out.append(_check("length", "Length", "warn" if thin else "ok",
                          f"About {len(words)} words." + (" Short articles rarely rank; aim for at least 300." if thin else "")))

    # address
    if slug and not slug_locked:    # an existing address never changes, so there is nothing to advise
        problems = []
        parts = [p for p in slug.split("-") if p]
        if len(slug) > 60 or len(parts) > 7:
            problems.append("Long. Short addresses (3–5 words) are easier to read and share.")
        if re.search(r"(?:^|-)(?:19|20)\d\d(?:-|$)", slug):
            problems.append("Contains a year, which makes the article look out of date later.")
        out.append(_check("slug", "Web address", "warn" if problems else "ok",
                          " ".join(problems) or f"/{slug}/ is short and clear.",
                          []))

    # focus keyword
    if keyword:
        kw = _words(keyword)
        first = " ".join(words[:100])
        h2 = " ".join(name for level, name in heads if level >= 2)
        alts = " ".join(i["alt"] for i in imgs if i["alt"])
        rows = [("Title", _has_words(seo_title or title, kw)),
                ("Description", _has_words(description, kw)),
                ("First paragraph", _has_words(first, kw)),
                ("A sub-heading", _has_words(h2, kw)),
                ("Web address", bool(slug) and all(w in slug.lower().split("-") for w in kw) if slug else False),
                ("An image’s alt text", _has_words(alts, kw))]
        if kind != "article":
            rows = [r for r in rows if r[0] != "Web address"]
        missing = [name for name, ok in rows if not ok]
        out.append(_check("keyword", "Focus keyword", "ok" if len(missing) <= 1 else "warn",
                          f"“{keyword}” appears in {len(rows) - len(missing)} of {len(rows)} key places."
                          + (f" Missing from: {', '.join(missing).lower()}." if missing else ""),
                          [{"label": name, "ok": ok} for name, ok in rows]))
    else:
        out.append(_check("keyword", "Focus keyword", "info",
                          "Type the phrase you want this page to be found for (above, in the SEO tab) to check that it appears in the title, description, first paragraph, a heading, the address and an image."))

    # images: weight, format, featured image size
    heavy, seen = [], set()
    featured_src = str(fields.get("image") or "").strip()
    for src, is_featured in [(i["src"], False) for i in imgs] + ([(featured_src, True)] if featured_src else []):
        file = _local_file(root, src)
        if not file or src in seen:
            if file and is_featured:
                for row in heavy:
                    if row["src"] == src:
                        row["featured"] = True
            continue
        seen.add(src)
        kb = file.stat().st_size // 1024
        ext = file.suffix.lower()
        convertible = ext in IMAGE_CONVERTIBLE
        detail = None
        if kb > IMAGE_HEAVY_KB:
            detail = f"{kb} KB" + ("" if ext in (".webp", ".avif") else ", WebP would be smaller")
        elif kb > 100 and ext in (".png", ".bmp"):
            detail = f"{kb} KB PNG, WebP would be smaller"
        if detail:
            heavy.append({"label": src, "detail": detail + (" (featured image)" if is_featured else ""), "src": src,
                          "featured": is_featured, "convertible": convertible})
    if imgs or heavy:
        out.append(_check("image_weight", "Image weight", "warn" if heavy else "ok",
                          (f"{len(heavy)} image{'s' if len(heavy) != 1 else ''} could load faster." if heavy
                           else "No image looks too heavy."), heavy))
    featured = featured_src
    file = _local_file(root, featured) if featured else None
    if file:
        size = image_size(file)
        if size:
            w, h = size
            ratio = w / h if h else 0
            if w < 600:
                state, note = "warn", f"{w}×{h}. Too small for a link preview; use at least 1200×630."
            elif w < 1200:
                state, note = "info", f"{w}×{h}. Works, but 1200×630 looks sharper in link previews."
            elif not 1.5 <= ratio <= 2.2:
                state, note = "info", f"{w}×{h}. Link previews are cropped to about 1.9:1 (1200×630); the edges of this image may be cut."
            else:
                state, note = "ok", f"{w}×{h}."
            out.append(_check("social_image", "Featured image size", state, note))

    # links
    links = links_in(body)
    known = {p["url"] for p in pages} | KNOWN_PATHS
    internal = [l for l in links if internal_path(l["url"]) and not internal_path(l["url"]).startswith("/images/")]
    external = [l for l in links if re.match(r"https?://", l["url"], re.I)]
    out.append(_check("links", "Links", "ok" if internal else "warn",
                      f"{len(internal)} to other pages of this site, {len(external)} to other sites."
                      + ("" if internal else " Link to related articles: it keeps readers on the site and helps search engines find your pages.")))
    broken = []
    for l in internal:
        path = internal_path(l["url"])
        normal = path if path in known else path.rstrip("/") + "/"
        if normal in known or _local_file(root, path) or (root is None):
            continue
        broken.append({"label": l["url"], "detail": l["text"] or "link"})
    if internal:
        out.append(_check("broken", "Links to this site", "warn" if broken else "ok",
                          (f"{len(broken)} link{'s' if len(broken) != 1 else ''} to an address that does not exist (or only redirects)." if broken
                           else "All point to an existing page."), broken))
    generic = [{"label": l["text"], "detail": l["url"]} for l in links if l["text"].lower().strip(" .!") in GENERIC_ANCHORS]
    if generic:
        out.append(_check("anchors", "Link text", "warn",
                          "Describe where the link goes (“the Kdenlive review”), not “click here”.", generic))

    # who links here
    if inbound is not None and kind == "article":
        out.append(_check("inbound", "Pages linking here", "ok" if inbound else "warn",
                          (f"{inbound} other page{'s' if inbound != 1 else ''} link{'s' if inbound == 1 else ''} to this one in their text." if inbound
                           else "No other article or page links to this one in its text. Add a link from a related article.")))
    return out


def _blank_code(body: str) -> str:
    """The body with code blocks replaced by spaces (same length), so '#' comments are not headings."""
    mask = _code_mask(body)
    return "".join(" " if m and c != "\n" else c for c, m in zip(body, mask))


def replace_src(body: str, old: str, new: str) -> str:
    """Points every use of the image `old` (Markdown or HTML, never inside code) at `new`."""
    mask = _code_mask(body)
    pattern = re.compile(r"(?<![\w/.\-])" + re.escape(old) + r"(?![\w/\-]|\.\w)")
    count = 0
    def swap(match):
        nonlocal count
        if mask[match.start()]:
            return match.group(0)
        count += 1
        return new
    out = pattern.sub(swap, body)
    if not count:
        raise ValueError("That image is no longer in the text.")
    return out


def apply_alt(body: str, index: int, src: str, alt: str) -> str:
    """Writes `alt` into the index-th image of `body` (checked against its source)."""
    alt = " ".join(alt.replace("[", "(").replace("]", ")").replace('"', "'").split())
    imgs = images_in(body)
    if index >= len(imgs) or imgs[index]["src"] != src:
        raise ValueError("The images changed since the analysis. Run it again.")
    item = imgs[index]
    if item["kind"] == "markdown":
        a, b = item["alt_span"]
        return body[:a] + alt + body[b:]
    tag = body[item["start"]:item["end"]]
    safe = alt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if re.search(ATTR_RE.format(name="alt"), tag, re.I):
        tag = re.sub(r"""(\salt\s*=\s*)(?:"[^"]*"|'[^']*')""", lambda m: f'{m.group(1)}"{safe}"', tag, count=1, flags=re.I)
    else:
        tag = re.sub(r"<img\b", f'<img alt="{safe}"', tag, count=1, flags=re.I)
    return body[:item["start"]] + tag + body[item["end"]:]
