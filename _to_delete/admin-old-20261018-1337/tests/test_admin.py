import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from werkzeug.serving import make_server  # noqa: E402

import app as admin_app  # noqa: E402
from store import Store, split_front_matter  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
PORT = 4001
BASE = f"http://127.0.0.1:{PORT}"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class AdminCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.site = self.tmp / "site"
        self.site.mkdir()
        for name in ("_posts", "_data", "images"):
            if (REPO / name).exists():
                shutil.copytree(REPO / name, self.site / name, ignore=shutil.ignore_patterns("*.png", "*.jpg", "*.webp", "*.gif"))
        shutil.copytree(REPO / "_includes" / "svg", self.site / "_includes" / "svg")
        for name in ("_config.yaml", "index.html", "authors.md", "tags.md", "404.md"):
            shutil.copy(REPO / name, self.site / name)
        self.data = self.tmp / "data"
        admin_app.Credentials(self.data).set("admin", "correct horse battery")
        self.app = admin_app.create_app(self.site, self.data, PORT)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.store = Store(self.site)

    # helpers -------------------------------------------------------------
    def csrf(self):
        self.client.get("/login", base_url=BASE)
        with self.client.session_transaction(base_url=BASE) as s:
            return s["csrf"]

    def login(self):
        token = self.csrf()
        response = self.client.post("/login", base_url=BASE, data={
            "csrf_token": token, "username": "admin", "password": "correct horse battery"})
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction(base_url=BASE) as s:
            return s["csrf"]

    def post(self, path, token, data=None, **kw):
        return self.client.post(path, base_url=BASE, data={"csrf_token": token, **(data or {})}, **kw)

    def get(self, path, **kw):
        return self.client.get(path, base_url=BASE, **kw)


class SecurityTests(AdminCase):
    def test_everything_requires_login(self):
        for path in ("/", "/header", "/footer", "/publish", "/new/page", "/edit/article/x",
                     "/api/pages", "/media?path=/images/x.png"):
            response = self.get(path)
            self.assertEqual(response.status_code, 302, path)
            self.assertTrue(response.headers["Location"].endswith("/login"), path)

    def test_no_password_set_refuses_login(self):
        (self.data / "credentials.json").unlink()
        self.assertEqual(self.get("/login").status_code, 503)

    def test_wrong_password_then_lockout(self):
        token = self.csrf()
        for _ in range(5):
            response = self.post("/login", token, {"username": "admin", "password": "nope"})
            self.assertIn(b"Wrong user name or password", response.data)
        response = self.post("/login", token, {"username": "admin", "password": "correct horse battery"})
        self.assertIn(b"Too many wrong attempts", response.data)
        self.assertNotIn("user", self.session())

    def session(self):
        with self.client.session_transaction(base_url=BASE) as s:
            return dict(s)

    def test_post_without_csrf_token_is_rejected(self):
        self.login()
        self.assertEqual(self.client.post("/footer", base_url=BASE, data={"copyright": "x"}).status_code, 403)
        self.assertEqual(self.client.post("/login", base_url=BASE, data={"username": "admin", "password": "x"}).status_code, 403)

    def test_foreign_host_header_is_rejected(self):
        self.assertEqual(self.client.get("/login", base_url="http://evil.example:4001").status_code, 400)
        self.assertEqual(self.client.get("/login", base_url="http://127.0.0.1:9999").status_code, 400)
        self.assertEqual(self.client.get("/login", base_url="http://localhost:4001").status_code, 200)

    def test_non_loopback_client_is_rejected(self):
        response = self.client.get("/login", base_url=BASE, environ_overrides={"REMOTE_ADDR": "192.168.1.20"})
        self.assertEqual(response.status_code, 403)

    def test_cross_site_origin_is_rejected(self):
        token = self.login()
        response = self.post("/footer", token, {"copyright": "x"}, headers={"Origin": "https://evil.example"})
        self.assertEqual(response.status_code, 403)

    def test_cookie_and_headers(self):
        response = self.get("/login")
        cookie = response.headers.get("Set-Cookie", "")
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=Strict", cookie)
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])

    def test_secret_files_are_private(self):
        for name in ("credentials.json", "secret.key"):
            self.assertEqual((self.data / name).stat().st_mode & 0o777, 0o600, name)

    def test_server_binds_loopback_only(self):
        self.assertEqual(admin_app.HOST, "127.0.0.1")
        server = make_server(admin_app.HOST, 0, self.app)
        self.addCleanup(server.server_close)
        self.assertEqual(server.server_address[0], "127.0.0.1")

    def test_short_password_refused(self):
        with self.assertRaises(ValueError):
            admin_app.Credentials(self.data).set("admin", "short")


class ContentTests(AdminCase):
    def setUp(self):
        super().setUp()
        self.token = self.login()

    def test_dashboard_lists_all_real_articles(self):
        response = self.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b"/edit/article/"), len(list((REPO / "_posts").glob("*.md"))))

    def test_create_page(self):
        response = self.post("/new/page", self.token, {"title": "About me", "description": "Who I am", "slug": "about", "body": "Hello **there**"})
        self.assertEqual(response.status_code, 302)
        text = (self.site / "pages" / "about.md").read_text()
        self.assertEqual(text, '---\ntitle: About me\ndescription: Who I am\nlayout: page\npermalink: /about/\n---\n\nHello **there**\n')
        meta, body = split_front_matter(text)
        self.assertEqual(meta["permalink"], "/about/")

    def test_title_with_quotes_and_colon_stays_valid_yaml(self):
        self.post("/new/page", self.token, {"title": 'Say "hi": a test', "slug": "quotes", "body": "x"})
        meta, _ = split_front_matter((self.site / "pages" / "quotes.md").read_text())
        self.assertEqual(meta["title"], 'Say "hi": a test')

    def test_slug_rules(self):
        for slug in ("archive", "authors", "images", "has space", "../x", "-a", "ethics", "about-"):
            before = set(self.site.rglob("*.md"))
            response = self.post("/new/page", self.token, {"title": "T", "slug": slug, "body": "x"})
            self.assertEqual(response.status_code, 200, slug)  # form shown again with an error
            self.assertEqual(before, set(self.site.rglob("*.md")), slug)
        self.post("/new/page", self.token, {"title": "T", "slug": "dup", "body": "x"})
        response = self.post("/new/page", self.token, {"title": "T2", "slug": "dup", "body": "y"})
        self.assertIn(b"already used", response.data)

    def test_uppercase_slug_is_lowercased(self):
        self.post("/new/page", self.token, {"title": "T", "slug": "Hello", "body": "x"})
        self.assertTrue((self.site / "pages" / "hello.md").is_file())

    def test_create_article(self):
        response = self.post("/new/article", self.token, {
            "title": "My first", "description": "d", "slug": "my-first", "author": "nick",
            "image": "/images/posts/x/c.jpg", "tags": "Linux, Privacy", "date": "2026-10-18", "body": "Text"})
        self.assertEqual(response.status_code, 302)
        text = (self.site / "_posts" / "2026-10-18-my-first.md").read_text()
        self.assertEqual(text, '---\ntitle: My first\ndescription: d\nauthor: nick\nimage: /images/posts/x/c.jpg\ntags:\n  - Linux\n  - Privacy\ndate: 2026-10-18\n---\n\nText\n')
        meta, _ = split_front_matter(text)
        self.assertEqual(str(meta["date"]), "2026-10-18")

    def test_article_rejects_unknown_author_and_bad_date(self):
        base = {"title": "T", "slug": "okay", "author": "nick", "date": "2026-10-18", "body": "x"}
        for bad in ({"author": "mallory"}, {"date": "18/10/2026"}, {"image": "javascript:alert(1)"}):
            response = self.post("/new/article", self.token, {**base, **bad})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(list(self.site.glob("_posts/*-okay.md")))

    def test_unchanged_save_keeps_every_real_article_intact(self):
        """Opening and saving an existing article without touching it must not alter its content."""
        for path in sorted((REPO / "_posts").glob("*.md")):
            kind, name = "article", path.stem
            entry = self.store.load(kind, name)
            original_meta, original_body = split_front_matter(path.read_text(encoding="utf-8"))
            fields = dict(entry.fields)
            self.store.save(entry, fields, entry.body, entry.etag)
            new_meta, new_body = split_front_matter((self.site / "_posts" / f"{name}.md").read_text(encoding="utf-8"))
            self.assertEqual(new_body.strip("\n"), original_body.strip("\n"), name)
            for key, value in original_meta.items():
                self.assertEqual(new_meta.get(key), value, f"{name}: {key}")
            self.assertEqual(set(new_meta), set(original_meta), name)

    def test_edit_through_the_form(self):
        name = "2023-05-26-Ethics"
        page = self.get(f"/edit/article/{name}")
        self.assertEqual(page.status_code, 200)
        etag = self.store.load("article", name).etag
        response = self.post(f"/edit/article/{name}", self.token, {
            "title": "Ethics, revised", "description": "New description", "author": "nick",
            "image": "/images/posts/ethics/ethics.jpg", "tags": "Personal, Ethics", "date": "2023-05-26",
            "body": "New body", "etag": etag})
        self.assertEqual(response.status_code, 302)
        meta, body = split_front_matter((self.site / "_posts" / f"{name}.md").read_text())
        self.assertEqual((meta["title"], body.strip()), ("Ethics, revised", "New body"))

    def test_edit_conflict_is_detected(self):
        name = "2023-05-26-Ethics"
        stale = self.store.load("article", name).etag
        path = self.site / "_posts" / f"{name}.md"
        path.write_text(path.read_text() + "\nchanged elsewhere\n")
        response = self.post(f"/edit/article/{name}", self.token, {
            "title": "T", "author": "nick", "date": "2023-05-26", "body": "mine", "etag": stale})
        self.assertIn(b"changed outside the admin", response.data)
        self.assertIn("changed elsewhere", path.read_text())

    def test_path_traversal_is_refused(self):
        secret = self.tmp / "secret.md"
        secret.write_text("---\ntitle: s\n---\nx")
        for name in ("..%2F..%2Fsecret", "..%2Fsecret", "%2Fetc%2Fpasswd", "..", "a%2Fb"):
            self.assertEqual(self.get(f"/edit/page/{name}").status_code, 404, name)
            self.assertEqual(self.get(f"/edit/article/{name}").status_code, 404, name)

    def test_unknown_kind_is_404(self):
        self.assertEqual(self.get("/new/post").status_code, 404)


class HeaderFooterTests(AdminCase):
    def setUp(self):
        super().setUp()
        self.token = self.login()

    def header_form(self, **over):
        data = {
            "logo_url": "https://thelinuxexp.github.io",
            "links-0-title": "Linux Videos", "links-0-url": "https://www.youtube.com/thelinuxexperiment", "links-0-new_tab": "on",
            "icons-0-title": "RSS Feed", "icons-0-url": "/feed.xml", "icons-0-icon": "rss-square", "icons-0-rel": "",
            "icons-1-title": "Mastodon", "icons-1-url": "https://mastodon.social/@x", "icons-1-icon": "mastodon",
            "icons-1-rel": "me bogus", "icons-1-new_tab": "on",
        }
        data.update(over)
        return data

    def test_repo_header_and_footer_load_and_reload_unchanged(self):
        header, footer = self.store.load_header(), self.store.load_footer()
        self.store.save_header(header["logo"]["url"], header["logo"]["new_tab"], header["links"], header["icons"])
        self.store.save_footer(footer["copyright"], footer["links"])
        self.assertEqual(self.store.load_header(), header)
        self.assertEqual(self.store.load_footer(), footer)

    def test_save_header_and_order(self):
        response = self.post("/header", self.token, self.header_form())
        self.assertEqual(response.status_code, 302)
        data = yaml.safe_load((self.site / "_data" / "header.yml").read_text())
        self.assertEqual([i["title"] for i in data["icons"]], ["RSS Feed", "Mastodon"])
        self.assertEqual(data["icons"][1]["rel"], "me")  # unknown rel token dropped
        self.assertEqual(data["links"][0]["new_tab"], True)

    def test_rows_keep_page_order_not_index_order(self):
        form = self.header_form()
        reordered = {k: v for k, v in form.items() if not k.startswith("icons-")}
        reordered.update({k: v for k, v in form.items() if k.startswith("icons-1-")})
        reordered.update({k: v for k, v in form.items() if k.startswith("icons-0-")})
        self.post("/header", self.token, reordered)
        data = yaml.safe_load((self.site / "_data" / "header.yml").read_text())
        self.assertEqual([i["title"] for i in data["icons"]], ["Mastodon", "RSS Feed"])

    def test_dangerous_links_and_unknown_icons_are_refused(self):
        original = (self.site / "_data" / "header.yml").read_text()
        for over in ({"links-0-url": "javascript:alert(1)"}, {"links-0-url": "//evil.example"},
                     {"links-0-url": 'https://x.com/"><script>'}, {"icons-0-icon": "../../etc/passwd"}):
            response = self.post("/header", self.token, self.header_form(**over))
            self.assertEqual(response.status_code, 200, over)
            self.assertEqual((self.site / "_data" / "header.yml").read_text(), original, over)

    def test_save_footer(self):
        response = self.post("/footer", self.token, {
            "copyright": "The Linux Experiment", "links-0-title": "Contact", "links-0-url": "mailto:a@b.c", "links-0-rel": "",
            "links-1-title": "Mastodon", "links-1-url": "https://mastodon.social/@x", "links-1-rel": "me"})
        self.assertEqual(response.status_code, 302)
        data = yaml.safe_load((self.site / "_data" / "footer.yml").read_text())
        self.assertEqual(data["links"][1], {"title": "Mastodon", "url": "https://mastodon.social/@x", "rel": "me"})

    def test_pages_render_with_all_rows(self):
        html = self.get("/header").data.decode()
        header = self.store.load_header()
        self.assertEqual(html.count("data-row>"), len(header["links"]) + len(header["icons"]) + 2)  # +2: the "add" templates
        self.assertEqual(self.get("/footer").status_code, 200)


class UploadTests(AdminCase):
    def setUp(self):
        super().setUp()
        self.token = self.login()

    def upload(self, filename, content, slug="my-page", kind="page"):
        return self.client.post("/upload", base_url=BASE, headers={"X-CSRF-Token": self.token}, content_type="multipart/form-data",
                                data={"file": (io.BytesIO(content), filename), "slug": slug, "kind": kind})

    def test_png_is_stored_under_images(self):
        response = self.upload("My Photo!.PNG", PNG)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["path"], "/images/pages/my-page/my-photo.png")
        self.assertTrue((self.site / "images" / "pages" / "my-page" / "my-photo.png").is_file())
        self.assertEqual(self.upload("My Photo!.PNG", PNG).json["path"], "/images/pages/my-page/my-photo-2.png")

    def test_article_images_go_under_posts(self):
        self.assertEqual(self.upload("a.png", PNG, slug="my-post", kind="article").json["path"], "/images/posts/my-post/a.png")

    def test_rejects_wrong_types_and_bad_slugs(self):
        self.assertEqual(self.upload("evil.png", b"MZ\x90\x00 not an image").status_code, 400)
        self.assertEqual(self.upload("x.svg", b"<svg onload=alert(1)/>").status_code, 400)
        self.assertEqual(self.upload("x.html", b"<script>").status_code, 400)
        self.assertEqual(self.upload("a.png", PNG, slug="../../etc").status_code, 400)
        self.assertEqual(self.upload("a.png", PNG, slug="").status_code, 400)
        self.assertEqual(self.upload("a.png", PNG, kind="other").status_code, 400)

    def test_filename_cannot_escape_the_folder(self):
        response = self.upload("../../../../evil.png", PNG)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["path"].startswith("/images/pages/my-page/"))
        self.assertFalse((self.tmp / "evil.png").exists())


class PublishTests(AdminCase):
    def setUp(self):
        super().setUp()
        self.token = self.login()
        self.remote = self.tmp / "remote.git"
        git(self.tmp, "init", "--bare", "-b", "main", str(self.remote))
        git(self.site, "init", "-b", "main")
        (self.site / ".gitignore").write_text("*.json\n")
        git(self.site, "add", "-A")
        git(self.site, "commit", "-m", "init")
        git(self.site, "remote", "add", "origin", str(self.remote))
        git(self.site, "push", "-u", "origin", "main")

    def test_nothing_to_publish(self):
        self.assertIn(b"Nothing to publish", self.get("/publish").data)

    def test_commit_and_push(self):
        self.post("/new/page", self.token, {"title": "About", "slug": "about", "body": "x"})
        self.assertIn(b"pages/about.md", self.get("/publish").data)
        response = self.post("/publish", self.token, {"message": "New page: About", "push": "1"})
        self.assertIn(b"Published", response.data)
        log = subprocess.run(["git", "log", "--oneline", "main"], cwd=self.remote, capture_output=True, text=True).stdout
        self.assertIn("New page: About", log)
        self.assertIn(b"Nothing to publish", self.get("/publish").data)

    def test_commit_only_does_not_push(self):
        self.post("/new/page", self.token, {"title": "About", "slug": "about", "body": "x"})
        self.post("/publish", self.token, {"message": "Local only"})
        log = subprocess.run(["git", "log", "--oneline", "main"], cwd=self.remote, capture_output=True, text=True).stdout
        self.assertNotIn("Local only", log)

    def test_message_required_and_no_shell_injection(self):
        self.post("/new/page", self.token, {"title": "About", "slug": "about", "body": "x"})
        response = self.post("/publish", self.token, {"message": "   "})
        self.assertIn(b"did not complete", response.data)
        self.post("/publish", self.token, {"message": "$(touch /tmp/pwned-by-test); `id` --amend"})
        self.assertFalse(Path("/tmp/pwned-by-test").exists())
        subject = subprocess.run(["git", "log", "-1", "--format=%s"], cwd=self.site, capture_output=True, text=True).stdout.strip()
        self.assertTrue(subject.startswith("$(touch"))


class PreviewTests(AdminCase):
    def test_preview_is_bound_to_loopback(self):
        from publishing import PREVIEW_HOST
        self.assertEqual(PREVIEW_HOST, "127.0.0.1")

    def test_start_without_ruby_gives_a_clear_message(self):
        token = self.login()
        old_path = os.environ["PATH"]
        os.environ["PATH"] = str(self.tmp)
        try:
            response = self.post("/preview/start", token, follow_redirects=True)
        finally:
            os.environ["PATH"] = old_path
        self.assertIn(b"bundle", response.data)


if __name__ == "__main__":
    unittest.main()
