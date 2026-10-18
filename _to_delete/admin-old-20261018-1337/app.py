"""Local-only admin for the site. Runs on this laptop, reachable only from this laptop.

    python3 admin/app.py set-password     choose the admin user name and password
    python3 admin/app.py                  start the admin on http://127.0.0.1:4001/
"""

import getpass
import hmac
import json
import os
import re
import secrets
import shutil
import sys
import time
from datetime import date
from pathlib import Path

from werkzeug.serving import make_server
from flask import (Flask, abort, flash, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)

import images
import seo
from auth import Credentials, LoginThrottle, load_secret_key
from publishing import PublishError, Preview, changed_files, commit_and_push
from store import Conflict, Store, StoreError

HOST = "127.0.0.1"  # fixed on purpose: there is no setting that exposes the admin to a network
DEFAULT_PORT = 4001
PREVIEW_PORT = 4000
LOOPBACK = {"127.0.0.1", "::1"}
PUBLIC_ENDPOINTS = {"login", "static"}
UPLOAD_TYPES = {
    ".png": [b"\x89PNG\r\n\x1a\n"],
    ".jpg": [b"\xff\xd8\xff"],
    ".jpeg": [b"\xff\xd8\xff"],
    ".gif": [b"GIF87a", b"GIF89a"],
    ".webp": [b"RIFF"],
}
UPLOAD_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,99}$")
YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def create_app(site_root, data_dir=None, port=DEFAULT_PORT, preview_port=PREVIEW_PORT):
    site_root = Path(site_root).resolve()
    data_dir = Path(data_dir) if data_dir else site_root / "admin" / ".data"
    store = Store(site_root)
    credentials = Credentials(data_dir)
    throttle = LoginThrottle()
    preview = Preview(site_root, data_dir / "jekyll.log", preview_port)
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=load_secret_key(data_dir),
        SESSION_COOKIE_NAME="tle_admin",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
        PERMANENT_SESSION_LIFETIME=8 * 3600,
        MAX_CONTENT_LENGTH=25 * 1024 * 1024,
    )

    # ------------------------------------------------------------ security
    def csrf_token() -> str:
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        return session["csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def guard():
        if request.remote_addr not in LOOPBACK:
            abort(403)
        if request.host not in allowed_hosts:  # blocks DNS-rebinding attacks from web pages
            abort(400)
        if request.method == "POST":
            origin = request.headers.get("Origin")
            if origin and origin.removeprefix("http://") not in allowed_hosts:
                abort(403)
            sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token") or ""
            if not hmac.compare_digest(sent, session.get("csrf", "")):
                abort(403)
        if request.endpoint not in PUBLIC_ENDPOINTS and not session.get("user"):
            return redirect(url_for("login"))

    @app.after_request
    def headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data: https:; "
            "connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"
        return response

    # --------------------------------------------------------------- login
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if not credentials.exists():
            return render_template("login.html", no_password=True), 503
        if request.method == "POST":
            wait = throttle.seconds_left()
            if wait:
                flash(f"Too many wrong attempts. Try again in {wait} seconds.", "error")
            elif credentials.verify(request.form.get("username", ""), request.form.get("password", "")):
                throttle.succeeded()
                session.clear()
                session.permanent = True
                session["user"] = request.form["username"].strip()
                session["csrf"] = secrets.token_hex(16)  # fresh token for the new session
                return redirect(url_for("dashboard"))
            else:
                throttle.failed()
                flash("Wrong user name or password.", "error")
        return render_template("login.html", no_password=False)

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # ----------------------------------------------------------- dashboard
    @app.get("/")
    def dashboard():
        articles = store.list_entries("article")
        counts = inbound_counts()
        orphans = [e for e in articles if not counts.get(f"/{e.slug}/")]
        return render_template(
            "dashboard.html",
            orphans=orphans,
            articles=articles,
            pages=store.list_entries("page"),
            preview=preview,
        )

    # -------------------------------------------------- articles and pages
    SKIP_DIRS = {"images", "admin", "_site", "vendor", ".git", ".jekyll-cache", ".bundle", "node_modules", "_transfer", "_to_delete"}
    TEXT_SUFFIXES = {".md", ".markdown", ".html", ".yml", ".yaml", ".json", ".xml", ".scss", ".css", ".txt", ".js"}

    def image_file(src: str):
        """The file behind a site image path such as /images/posts/x/a.png, or None."""
        if not src.startswith("/images/"):
            return None
        path = (store.root / src.lstrip("/")).resolve()
        try:
            path.relative_to(store.images_dir.resolve())
        except ValueError:
            return None
        return path if path.is_file() else None

    def still_used(src: str) -> bool:
        """Is `src` mentioned by any text file of the site (articles, pages, data, layouts...)?"""
        for folder, dirs, files in os.walk(store.root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if Path(name).suffix.lower() in TEXT_SUFFIXES:
                    try:
                        if src in (Path(folder) / name).read_text(encoding="utf-8", errors="ignore"):
                            return True
                    except OSError:
                        return True        # unreadable: assume it is used
        return False

    def retire_originals() -> str:
        """After a save: image files that were swapped for a lighter or different one and are not used
        anywhere any more are moved (not deleted) to the admin's data folder, so the site does not keep them."""
        try:
            pairs = json.loads(request.form.get("swapped") or "[]")
        except ValueError:
            return ""
        moved, freed = 0, 0
        for pair in pairs[:60] if isinstance(pairs, list) else []:
            if not (isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair)):
                continue
            old, new = pair
            source, replacement = image_file(old), image_file(new)
            if not source or not replacement or source == replacement or still_used(old):
                continue
            target = data_dir / "image-originals" / source.relative_to(store.root)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                target = target.with_name(f"{target.stem}-{int(time.time())}{target.suffix}")
            freed += source.stat().st_size
            shutil.move(str(source), str(target))
            moved += 1
        if not moved:
            return ""
        return f" {moved} original image{'s' if moved != 1 else ''} no longer used ({freed // 1024} KB) moved out of the site, to admin/.data/image-originals."

    def parse_fields(kind: str) -> dict:
        form = request.form
        title = " ".join(form.get("title", "").split())
        if not title or len(title) > 200:
            raise StoreError("The title is required (200 characters at most).")
        fields = {"title": title, "description": " ".join(form.get("description", "").split())[:400],
                  "seo_title": " ".join(form.get("seo_title", "").split())[:120],
                  "focus_keyword": " ".join(form.get("focus_keyword", "").split())[:80]}
        if kind == "article":
            author = form.get("author", "")
            if author not in store.authors():
                raise StoreError("Pick an author from the list.")
            image = form.get("image", "").strip()
            if image and not re.match(r"^(?:https?://|/(?!/))[^\s\"'<>]+$", image):
                raise StoreError("The featured image must be a link (https://…) or a path starting with /.")
            try:
                when = date.fromisoformat(form.get("date", ""))
            except ValueError:
                raise StoreError("The date must look like 2026-10-18.")
            tags = [" ".join(t.split()) for t in form.get("tags", "").split(",")]
            fields.update(author=author, image=image, date=when, tags=[t for t in tags if t])
        return fields

    def kind_or_404(kind: str) -> str:
        if kind not in ("article", "page"):
            abort(404)
        return kind

    @app.route("/new/<kind>", methods=["GET", "POST"])
    def new(kind):
        kind_or_404(kind)
        form_values = {"title": "", "description": "", "seo_title": "", "focus_keyword": "", "slug": "", "author": store.authors()[0],
                       "image": "", "tags": "", "date": date.today().isoformat(), "body": ""}
        if request.method == "POST":
            form_values.update({k: request.form.get(k, "") for k in form_values})
            try:
                fields = parse_fields(kind)
                entry = store.create(kind, request.form.get("slug", ""), fields,
                                     request.form.get("body", ""), fields.get("date"))
            except StoreError as error:
                flash(str(error), "error")
            else:
                flash("Saved. Use “Preview” to see it, then “Publish” when you are happy." + retire_originals(), "ok")
                return redirect(url_for("edit", kind=kind, name=entry.name))
        return render_template("edit.html", kind=kind, entry=None, values=form_values,
                               authors=store.authors(), etag="")

    @app.route("/edit/<kind>/<name>", methods=["GET", "POST"])
    def edit(kind, name):
        kind_or_404(kind)
        try:
            entry = store.load(kind, name)
        except StoreError:
            abort(404)
        values = {
            "title": entry.fields.get("title") or "", "description": entry.fields.get("description") or "",
            "seo_title": entry.fields.get("seo_title") or "", "focus_keyword": entry.fields.get("focus_keyword") or "",
            "slug": entry.slug, "author": entry.fields.get("author") or store.authors()[0],
            "image": entry.fields.get("image") or "", "tags": ", ".join(entry.fields.get("tags") or []),
            "date": str(entry.fields.get("date") or ""), "body": entry.body,
        }
        etag = entry.etag
        if request.method == "POST":
            values.update({k: request.form.get(k, "") for k in ("title", "description", "seo_title", "focus_keyword", "author", "image", "tags", "date", "body")})
            etag = request.form.get("etag", "")
            try:
                fields = parse_fields(kind)
                entry = store.save(entry, fields, request.form.get("body", ""), etag)
            except Conflict as error:
                flash(str(error), "error")
            except StoreError as error:
                flash(str(error), "error")
            else:
                flash("Saved." + retire_originals(), "ok")
                return redirect(url_for("edit", kind=kind, name=name))
        return render_template("edit.html", kind=kind, entry=entry, values=values,
                               authors=store.authors(), etag=etag)

    @app.post("/upload")
    def upload():
        kind = request.form.get("kind", "")
        slug = request.form.get("slug", "").strip()
        file = request.files.get("file")
        if kind not in ("article", "page") or not UPLOAD_SLUG_RE.match(slug) or file is None:
            return jsonify(error="Fill in the web address (slug) first, then choose an image."), 400
        suffix = Path(file.filename or "").suffix.lower()
        head = file.stream.read(12)
        file.stream.seek(0)
        if suffix not in UPLOAD_TYPES or not any(head.startswith(sig) for sig in UPLOAD_TYPES[suffix]) \
                or (suffix == ".webp" and head[8:12] != b"WEBP"):
            return jsonify(error="Only PNG, JPEG, GIF and WebP images are accepted."), 400
        stem = re.sub(r"[^a-z0-9]+", "-", Path(file.filename).stem.lower()).strip("-") or "image"
        folder = store.images_dir / ("posts" if kind == "article" else "pages") / slug
        folder.mkdir(parents=True, exist_ok=True)
        target, counter = folder / f"{stem}{suffix}", 2
        while target.exists():
            target, counter = folder / f"{stem}-{counter}{suffix}", counter + 1
        file.save(target)
        return jsonify(path="/" + target.relative_to(store.root).as_posix())

    # ------------------------------------------------------ header / footer
    def parse_rows(prefix: str, fields: tuple) -> list:
        order, pattern = [], re.compile(rf"^{prefix}-(\d+)-")
        for key in request.form.keys():
            match = pattern.match(key)
            if match and match.group(1) not in order:
                order.append(match.group(1))
        rows = []
        for index in order:
            row = {f: request.form.get(f"{prefix}-{index}-{f}", "").strip() for f in fields}
            row["new_tab"] = f"{prefix}-{index}-new_tab" in request.form
            if row["title"] or row["url"]:
                rows.append(row)
        return rows

    @app.route("/header", methods=["GET", "POST"])
    def header():
        data = store.load_header()
        if request.method == "POST":
            data = {
                "logo": {"url": request.form.get("logo_url", ""), "new_tab": "logo_new_tab" in request.form},
                "links": parse_rows("links", ("title", "url")),
                "icons": parse_rows("icons", ("title", "url", "icon", "rel")),
            }
            try:
                store.save_header(data["logo"]["url"], data["logo"]["new_tab"], data["links"], data["icons"])
            except StoreError as error:
                flash(str(error), "error")
            else:
                flash("Header saved.", "ok")
                return redirect(url_for("header"))
        return render_template("header.html", data=data, icons=store.icon_names())

    @app.route("/footer", methods=["GET", "POST"])
    def footer():
        data = store.load_footer()
        if request.method == "POST":
            data = {"copyright": request.form.get("copyright", ""), "links": parse_rows("links", ("title", "url", "rel"))}
            try:
                store.save_footer(data["copyright"], data["links"])
            except StoreError as error:
                flash(str(error), "error")
            else:
                flash("Footer saved.", "ok")
                return redirect(url_for("footer"))
        return render_template("footer.html", data=data)

    # --------------------------------------------- editor helpers and SEO tab
    MEDIA_TYPES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".avif", ".ico"}

    def site_pages() -> list:
        """Every article and standalone page, as the links the editor can point to."""
        pages = []
        for kind in ("article", "page"):
            for entry in store.list_entries(kind):
                url = (entry.fields.get("permalink") or "").strip() if kind == "page" else ""
                pages.append({"title": " ".join(str(entry.fields.get("title") or entry.slug).split()),
                              "url": url or f"/{entry.slug}/", "kind": kind,
                              "tags": entry.fields.get("tags") or [], "name": entry.name})
        return pages

    def inbound_counts(skip=None) -> dict:
        """{url: number of other articles/pages whose text links to it}."""
        counts = {}
        for kind in ("article", "page"):
            for entry in store.list_entries(kind):
                if skip == (kind, entry.name):
                    continue
                own = (entry.fields.get("permalink") or "").strip() if kind == "page" else ""
                own = own or f"/{entry.slug}/"
                for target in seo.link_targets(entry.body):
                    if target != own:
                        counts[target] = counts.get(target, 0) + 1
        return counts

    def request_has_entry(kind: str, slug: str) -> bool:
        """True when the page being edited already exists on disk (a new one has no one linking to it yet)."""
        return any(e.slug == slug for e in store.list_entries(kind))

    @app.get("/media")
    def media():
        """Site images, so the editor can show them. Only files under images/."""
        wanted = request.args.get("path", "")
        if not wanted.startswith("/images/") or Path(wanted).suffix.lower() not in MEDIA_TYPES:
            abort(404)
        return send_from_directory(store.images_dir, wanted[len("/images/"):], max_age=0)

    @app.get("/api/pages")
    def api_pages():
        return jsonify(pages=[{k: p[k] for k in ("title", "url", "kind")} for p in site_pages()])

    def seo_input():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("body"), str):
            abort(400)
        return data

    @app.post("/images/optimize")
    def images_optimize():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            abort(400)
        path = image_file(str(data.get("src") or ""))
        if not path:
            return jsonify(error="That image file was not found in the images folder."), 404
        try:
            result = images.optimize(path, keep_format=bool(data.get("featured")))
        except images.ImageError as error:
            return jsonify(error=str(error)), 422
        if not result["changed"]:
            return jsonify(changed=False, reason=result["reason"])
        return jsonify(changed=True, src="/" + result["path"].relative_to(store.root).as_posix(),
                       old_kb=max(1, result["old_bytes"] // 1024), new_kb=max(1, result["new_bytes"] // 1024),
                       format=result["format"], resized=result["resized"],
                       width=result["size"][0], height=result["size"][1])

    @app.post("/seo/analyze")
    def seo_analyze():
        data = seo_input()
        fields = {k: str(data.get(k) or "") for k in ("title", "description", "image", "seo_title", "focus_keyword")}
        kind = "page" if data.get("kind") == "page" else "article"
        slug = str(data.get("slug") or "")
        self_url = str(data.get("url") or "") or (f"/{slug}/" if slug else "")
        pages = [p for p in site_pages() if p["url"] != self_url]
        exists = bool(slug) and request_has_entry(kind, slug)
        inbound = inbound_counts().get(self_url, 0) if self_url and exists else None
        return jsonify(seo.analyze({**fields, "kind": kind}, data["body"], pages, self_url,
                                   slug=slug, root=store.root, inbound=inbound, slug_locked=exists))

    @app.post("/seo/apply")
    def seo_apply():
        data = seo_input()
        try:
            if data.get("op") == "link":
                url = str(data.get("url") or "")
                if not re.match(r"^/(?!/)[^\s\"'<>()]*$", url):
                    raise ValueError("Not a link to a page of this site.")
                body = seo.apply_link(data["body"], int(data["start"]), int(data["end"]), str(data["phrase"]), url)
            elif data.get("op") == "src":
                old, new = str(data.get("old") or ""), str(data.get("new") or "")
                if not old.startswith("/images/") or not image_file(new):
                    raise ValueError("Both images must be files of this site's images folder.")
                body = seo.replace_src(data["body"], old, new)
            elif data.get("op") == "alt":
                body = seo.apply_alt(data["body"], int(data["index"]), str(data["src"]), str(data["alt"]))
            else:
                abort(400)
        except (ValueError, KeyError, TypeError) as error:
            return jsonify(error=str(error)), 409
        return jsonify(body=body)

    # ------------------------------------------------- preview and publish
    @app.post("/preview/<action>")
    def preview_control(action):
        if action == "start":
            try:
                preview.start()
                flash("Preview starting: it can take a few seconds to build.", "ok")
            except PublishError as error:
                flash(str(error), "error")
        elif action == "stop":
            preview.stop()
            flash("Preview stopped.", "ok")
        else:
            abort(404)
        return redirect(url_for("dashboard"))

    @app.route("/publish", methods=["GET", "POST"])
    def publish():
        output = ""
        if request.method == "POST":
            try:
                output = commit_and_push(site_root, request.form.get("message", ""), push="push" in request.form)
                flash("Published. GitHub is rebuilding the site; it is live in a minute or two."
                      if "push" in request.form else "Committed locally (not pushed).", "ok")
            except PublishError as error:
                flash("Publishing did not complete.", "error")
                output = str(error)
        try:
            files = changed_files(site_root)
        except PublishError as error:
            files, output = [], output or str(error)
        return render_template("publish.html", files=files, output=output)

    return app


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    site_root = Path(__file__).resolve().parent.parent
    data_dir = Path(__file__).resolve().parent / ".data"
    if argv[:1] == ["set-password"]:
        username = input("Admin user name [admin]: ").strip() or "admin"
        password = getpass.getpass("Password (10+ characters): ")
        if password != getpass.getpass("Repeat password: "):
            sys.exit("The two passwords differ; nothing was saved.")
        try:
            Credentials(data_dir).set(username, password)
        except ValueError as error:
            sys.exit(str(error))
        print("Saved. Start the admin with: python3 admin/app.py")
        return
    port = int(os.environ.get("TLE_ADMIN_PORT", DEFAULT_PORT))
    app = create_app(site_root, data_dir, port)
    if not Credentials(data_dir).exists():
        sys.exit("No password yet. Run first: python3 admin/app.py set-password")
    print(f"Admin: http://{HOST}:{port}/   (only reachable from this computer; Ctrl+C to stop)")
    server = make_server(HOST, port, app, threaded=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
