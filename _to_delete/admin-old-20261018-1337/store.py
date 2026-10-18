"""Reads and writes the site's content files.

Articles live in _posts/, standalone pages in pages/, and the header and footer
in _data/header.yml and _data/footer.yml. Everything is plain text in the
repository, so git is the history and the undo button.
"""

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import yaml

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
POST_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)$")
FRONT_RE = re.compile(r"\A---[ \t]*\n(.*?)^---[ \t]*$\n?", re.S | re.M)
URL_RE = re.compile(r"^(?:https?://|mailto:|/(?!/))[^\s\"'<>]+$")
REL_TOKENS = ("me", "noopener", "noreferrer", "nofollow")
PLAIN_SCALAR_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.\-]*$")
PLAIN_PATH_RE = re.compile(r"^/[A-Za-z0-9/_.\-]*$")

# Names that would collide with files the site already publishes.
RESERVED_SLUGS = {
    "archive", "authors", "tags", "feed", "images", "css", "admin", "404",
    "sitemap", "robots", "assets", "redirects", "index", "pages", "license",
}

ARTICLE_KEYS = ["title", "seo_title", "focus_keyword", "description", "author", "image", "tags", "date", "last_modified_at"]
PAGE_KEYS = ["title", "seo_title", "focus_keyword", "description", "layout", "permalink"]


class StoreError(Exception):
    """A problem the person editing should read about (bad input, conflict)."""


class Conflict(StoreError):
    """The file changed on disk since the edit form was opened."""


@dataclass
class Entry:
    kind: str  # "article" or "page"
    name: str  # file name without ".md"
    fields: dict
    extras: dict  # front matter keys the admin does not edit, kept as they are
    body: str
    etag: str
    path: Path
    slug: str = ""
    has_date: bool = False
    raw_date: object = None


def _etag(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _norm(value) -> str:
    return " ".join(str(value or "").split())


def _scalar(value: str) -> str:
    value = str(value)
    if PLAIN_PATH_RE.match(value):
        return value
    if PLAIN_SCALAR_RE.match(value) and value == value.strip() and value.lower() not in {"true", "false", "null", "yes", "no", "on", "off"}:
        return value
    return json.dumps(value, ensure_ascii=False)


def split_front_matter(text: str):
    text = text.replace("\r\n", "\n")
    match = FRONT_RE.match(text)
    if not match:
        return {}, text
    loaded = yaml.safe_load(match.group(1)) or {}
    if not isinstance(loaded, dict):
        raise StoreError("The front matter of this file is not a key/value list.")
    return loaded, text[match.end():]


def dump_front_matter(fields: dict, order: list, extras: dict) -> str:
    lines = ["---"]
    for key in order:
        value = fields.get(key)
        if value in (None, "", []):
            continue
        if key == "tags":
            lines.append("tags:")
            lines.extend(f"  - {_scalar(tag)}" for tag in value)
        elif key == "date":
            lines.append(f"date: {value.isoformat()}")
        elif key in ("author", "layout"):
            lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {_scalar(value)}")
    if extras:
        lines.append(yaml.safe_dump(extras, sort_keys=False, allow_unicode=True).rstrip())
    lines.append("---")
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, data) -> None:
    if isinstance(data, str):
        data = data.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def check_url(value: str, what: str) -> str:
    if not URL_RE.match(value) or len(value) > 500:
        raise StoreError(f"{what}: “{value}” is not a valid link. Use https://…, mailto:… or a path starting with /.")
    return value


def clean_rel(value: str) -> str:
    return " ".join(token for token in value.split() if token in REL_TOKENS)


class Store:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.posts_dir = self.root / "_posts"
        self.pages_dir = self.root / "pages"
        self.data_dir = self.root / "_data"
        self.svg_dir = self.root / "_includes" / "svg"
        self.images_dir = self.root / "images"

    # ---------------------------------------------------------------- paths
    def _dir(self, kind: str) -> Path:
        if kind == "article":
            return self.posts_dir
        if kind == "page":
            return self.pages_dir
        raise StoreError("Unknown content type.")

    def path_for(self, kind: str, name: str) -> Path:
        if not NAME_RE.match(name):
            raise StoreError("Invalid file name.")
        directory = self._dir(kind)
        path = (directory / f"{name}.md").resolve()
        if path.parent != directory.resolve():
            raise StoreError("Invalid file name.")
        return path

    # ------------------------------------------------------------- listings
    def authors(self) -> list:
        config = self.root / "_config.yaml"
        loaded = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
        return list((loaded.get("authors") or {}).keys())

    def article_slug(self, name: str) -> str:
        match = POST_DATE_RE.match(name)
        return match.group(2) if match else name

    def list_entries(self, kind: str) -> list:
        directory = self._dir(kind)
        if not directory.is_dir():
            return []
        entries = []
        for path in sorted(directory.glob("*.md")):
            try:
                entry = self.load(kind, path.stem)
            except (StoreError, yaml.YAMLError):
                continue
            entries.append(entry)
        if kind == "article":
            entries.sort(key=lambda e: str(e.fields.get("date") or e.name[:10]), reverse=True)
        return entries

    def used_slugs(self) -> set:
        slugs = {self.article_slug(p.stem).lower() for p in self.posts_dir.glob("*.md")}
        slugs |= {p.stem.lower() for p in self.pages_dir.glob("*.md")}
        slugs |= {p.name.split(".")[0].lower() for p in self.root.iterdir()}
        return slugs | RESERVED_SLUGS

    def check_new_slug(self, slug: str) -> str:
        slug = slug.strip().lower()
        if not SLUG_RE.match(slug) or len(slug) > 80:
            raise StoreError("The web address may only contain lowercase letters, digits and single dashes (e.g. my-new-page).")
        if slug in self.used_slugs():
            raise StoreError(f"“{slug}” is already used by another page, article or site file.")
        return slug

    # ----------------------------------------------------------- load / save
    def load(self, kind: str, name: str) -> Entry:
        path = self.path_for(kind, name)
        if not path.is_file():
            raise StoreError("This file does not exist.")
        raw = path.read_bytes()
        loaded, body = split_front_matter(raw.decode("utf-8"))
        keys = ARTICLE_KEYS if kind == "article" else PAGE_KEYS
        fields = {key: loaded.get(key) for key in keys}
        extras = {key: value for key, value in loaded.items() if key not in keys}
        raw_date = loaded.get("date")
        if kind == "article":
            fields["tags"] = [str(tag) for tag in (loaded.get("tags") or [])]
            fields["date"] = self._as_date(raw_date) or self._filename_date(name)
        entry = Entry(kind, name, fields, extras, body.lstrip("\n"), _etag(raw), path)
        entry.slug = self.article_slug(name) if kind == "article" else name
        entry.has_date = raw_date is not None
        entry.raw_date = raw_date
        return entry

    @staticmethod
    def _as_date(value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return None

    @staticmethod
    def _filename_date(name: str):
        match = POST_DATE_RE.match(name)
        return date.fromisoformat(match.group(1)) if match else None

    def save(self, entry: Entry, fields: dict, body: str, expected_etag: str) -> Entry:
        """Write an existing entry back. Only the edited keys are rewritten."""
        if entry.path.exists() and _etag(entry.path.read_bytes()) != expected_etag:
            raise Conflict("This file was changed outside the admin since you opened it. Reload it and redo your edit.")
        order = ARTICLE_KEYS if entry.kind == "article" else PAGE_KEYS
        merged = dict(fields)
        for key in ("title", "seo_title", "focus_keyword", "description", "image"):  # untouched values stay byte-for-byte as they were
            if key in merged and _norm(merged[key]) == _norm(entry.fields.get(key)):
                merged[key] = entry.fields.get(key)
        if entry.kind == "article":
            new_date = fields["date"]
            keep_original = self._as_date(entry.raw_date) == new_date and entry.raw_date is not None
            if keep_original:
                merged["date"] = entry.raw_date  # keeps a time of day if there was one
            elif not entry.has_date and new_date == self._filename_date(entry.name):
                merged["date"] = None  # the file name already holds the date
        merged["last_modified_at"] = entry.fields.get("last_modified_at")
        if entry.kind == "article" and self._content_changed(entry, fields, body):
            merged["last_modified_at"] = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        text = dump_front_matter(merged, order, entry.extras) + "\n" + self._normalize_body(body)
        atomic_write(entry.path, text)
        return self.load(entry.kind, entry.name)

    def _content_changed(self, entry: Entry, fields: dict, body: str) -> bool:
        """True when the person really changed something (not just re-saved the form as it was)."""
        for key, value in fields.items():
            old = entry.fields.get(key)
            if key == "tags":
                same = list(old or []) == list(value or [])
            elif key == "date":
                same = self._as_date(old) == value
            else:
                same = _norm(old) == _norm(value)
            if not same:
                return True
        return self._normalize_body(body) != self._normalize_body(entry.body)

    def create(self, kind: str, slug: str, fields: dict, body: str, when: date = None) -> Entry:
        slug = self.check_new_slug(slug)
        if kind == "article":
            when = when or date.today()
            name = f"{when.isoformat()}-{slug}"
            fields = {**fields, "date": when}
            order, extras = ARTICLE_KEYS, {}
        else:
            name = slug
            fields = {**fields, "layout": "page", "permalink": f"/{slug}/"}
            order, extras = PAGE_KEYS, {}
        path = self.path_for(kind, name)
        if path.exists():
            raise StoreError("This file already exists.")
        atomic_write(path, dump_front_matter(fields, order, extras) + "\n" + self._normalize_body(body))
        return self.load(kind, name)

    @staticmethod
    def _normalize_body(body: str) -> str:
        return body.replace("\r\n", "\n").replace("\r", "\n").strip("\n") + "\n"

    # ------------------------------------------------------ header / footer
    def icon_names(self) -> list:
        return sorted(p.stem for p in self.svg_dir.glob("*.svg"))

    def _load_data(self, name: str) -> dict:
        return yaml.safe_load((self.data_dir / name).read_text(encoding="utf-8")) or {}

    def load_header(self) -> dict:
        data = self._load_data("header.yml")
        data.setdefault("logo", {"url": "/", "new_tab": False})
        data.setdefault("links", [])
        data.setdefault("icons", [])
        return data

    def load_footer(self) -> dict:
        data = self._load_data("footer.yml")
        data.setdefault("copyright", "")
        data.setdefault("links", [])
        return data

    def save_header(self, logo_url: str, logo_new_tab: bool, links: list, icons: list) -> None:
        known_icons = set(self.icon_names())
        out_links = []
        for row in links:
            title, url = self._row_basics(row, "Menu link")
            out_links.append({"title": title, "url": url, "new_tab": bool(row.get("new_tab"))})
        out_icons = []
        for row in icons:
            title, url = self._row_basics(row, "Icon link")
            if row.get("icon") not in known_icons:
                raise StoreError(f"Icon link “{title}”: pick an icon from the list.")
            out_icons.append({
                "title": title, "url": url, "icon": row["icon"],
                "rel": clean_rel(row.get("rel", "")), "new_tab": bool(row.get("new_tab")),
            })
        data = {
            "logo": {"url": check_url(logo_url.strip(), "Logo link"), "new_tab": bool(logo_new_tab)},
            "links": out_links,
            "icons": out_icons,
        }
        self._write_data("header.yml", "Header (top navigation bar). Edited from the local admin, or by hand.\n"
                         "# icon: name of a file in _includes/svg/ (without .svg)", data)

    def save_footer(self, copyright_text: str, links: list) -> None:
        copyright_text = " ".join(copyright_text.split())
        if not copyright_text or len(copyright_text) > 120:
            raise StoreError("The copyright text is required (120 characters at most).")
        out_links = []
        for row in links:
            title, url = self._row_basics(row, "Footer link")
            out_links.append({"title": title, "url": url, "rel": clean_rel(row.get("rel", ""))})
        data = {"copyright": copyright_text, "links": out_links}
        self._write_data("footer.yml", "Footer. The year is added automatically before the text.", data)

    @staticmethod
    def _row_basics(row: dict, what: str):
        title = " ".join(row.get("title", "").split())
        if not title or len(title) > 80:
            raise StoreError(f"{what}: a title is required (80 characters at most).")
        return title, check_url(row.get("url", "").strip(), f"{what} “{title}”")

    def _write_data(self, name: str, comment: str, data: dict) -> None:
        body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False, width=200)
        atomic_write(self.data_dir / name, f"# {comment}\n{body}")
