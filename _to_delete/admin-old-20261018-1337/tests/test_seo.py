import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import seo  # noqa: E402
from test_admin import BASE, AdminCase  # noqa: E402

PAGES = [
    {"title": "Davinci Resolve vs Kdenlive", "url": "/dr-vs-kdenlive/", "tags": ["Video editing"], "kind": "article"},
    {"title": "Why elementary OS Is Important", "url": "/eos/", "tags": [], "kind": "article"},
    {"title": "Kdenlive", "url": "/kdenlive/", "tags": [], "kind": "page"},
]


class DescriptionTests(unittest.TestCase):
    def test_uses_opening_paragraphs_not_headings_lists_or_links(self):
        body = ("## Heading\n\nI use Davinci Resolve for video editing, and it is great. See https://x.example/a now. "
                "A third sentence makes the text long enough to be useful.\n\n- bullet\n\nLater text.")
        text = seo.suggest_description("Title", body)
        self.assertTrue(text.startswith("I use Davinci Resolve"))
        self.assertNotIn("Heading", text)
        self.assertNotIn("bullet", text)
        self.assertNotIn("x.example", text)
        self.assertLessEqual(len(text), seo.DESCRIPTION_MAX)

    def test_long_single_sentence_is_cut_on_a_word(self):
        text = seo.suggest_description("T", "word " * 80)
        self.assertTrue(text.endswith("…"))
        self.assertLessEqual(len(text), seo.DESCRIPTION_MAX)

    def test_nothing_to_summarize(self):
        self.assertEqual(seo.suggest_description("T", "## only a heading\n\n![](/a.png)"), "")


class ImageTests(unittest.TestCase):
    BODY = ("## Setup\n\n![](/images/a/kde-plasma-desktop.png)\n\n<figure markdown=\"1\">\n\n![](/images/a/b.png)\n\n"
            "<figcaption>The *Plasma* panel</figcaption>\n</figure>\n\n<img src=\"/images/c.jpg\">\n\n"
            "![Has alt](/images/d.png)\n\n```\n![](/images/in-code.png)\n```\n")

    def test_finds_missing_alt_text_only(self):
        found = seo.analyze({"title": "T", "kind": "article"}, self.BODY, [])["alts"]
        self.assertEqual([a["src"] for a in found], ["/images/a/kde-plasma-desktop.png", "/images/a/b.png", "/images/c.jpg"])

    def test_alt_comes_from_the_caption_not_the_next_figure(self):
        found = {a["src"]: a for a in seo.analyze({"title": "T", "kind": "article"}, self.BODY, [])["alts"]}
        self.assertEqual(found["/images/a/b.png"]["text"], "The Plasma panel")
        self.assertEqual(found["/images/a/kde-plasma-desktop.png"]["from"], "its file name")
        self.assertEqual(found["/images/c.jpg"]["from"], "the heading above it")

    def test_apply_alt_to_markdown_and_html_images(self):
        out = seo.apply_alt(self.BODY, 1, "/images/a/b.png", 'A [panel] with "quotes"')
        self.assertIn("![A (panel) with 'quotes'](/images/a/b.png)", out)
        out = seo.apply_alt(self.BODY, 2, "/images/c.jpg", "Photo <of> things & more")
        self.assertIn('<img alt="Photo &lt;of&gt; things &amp; more" src="/images/c.jpg">', out)

    def test_apply_alt_refuses_when_images_moved(self):
        with self.assertRaises(ValueError):
            seo.apply_alt(self.BODY, 1, "/images/other.png", "x")


class MetaTests(unittest.TestCase):
    def test_missing_description_and_image_get_suggestions(self):
        body = "Plenty of words in this opening paragraph. And a second sentence follows it.\n\n![](/images/a/cover.png)\n"
        meta = {m["key"]: m for m in seo.analyze({"title": "A good title for the article", "kind": "article"}, body, [])["meta"]}
        self.assertEqual(meta["description"]["state"], "missing")
        self.assertTrue(meta["description"]["suggestion"])
        self.assertEqual(meta["image"]["state"], "missing")
        self.assertEqual(meta["image"]["suggestion"], "/images/a/cover.png")

    def test_existing_values_are_never_replaced(self):
        meta = {m["key"]: m for m in seo.analyze(
            {"title": "A good title for the article", "description": "Short", "image": "/images/x.png", "kind": "article"},
            "Body.", [])["meta"]}
        self.assertEqual(meta["description"]["suggestion"], "")
        self.assertEqual(meta["description"]["state"], "warn")
        self.assertEqual(meta["image"]["state"], "ok")

    def test_pages_have_no_featured_image_row(self):
        keys = [m["key"] for m in seo.analyze({"title": "A good title for the page", "kind": "page"}, "Body.", [])["meta"]]
        self.assertNotIn("image", keys)


class LinkTests(unittest.TestCase):
    def test_links_to_titles_but_not_inside_code_links_headings_or_html(self):
        body = ("## Davinci Resolve in a heading\n\nI like Davinci Resolve a lot.\n\n"
                "`Davinci Resolve` in code and [Davinci Resolve](/other/) already linked.\n\n"
                "<p>Davinci Resolve in html</p>\n\n```\nDavinci Resolve in a fence\n```\n")
        found = seo.suggest_links(body, PAGES)
        self.assertEqual(len(found), 1)
        link = found[0]
        self.assertEqual((link["phrase"], link["url"]), ("Davinci Resolve", "/dr-vs-kdenlive/"))
        self.assertEqual(body[link["start"]:link["end"]], "Davinci Resolve")
        self.assertEqual(body[:link["start"]].count("Davinci Resolve"), 1)      # the one in the second paragraph, not the heading

    def test_skips_the_page_itself_and_pages_already_linked(self):
        body = "Davinci Resolve and Kdenlive and [more](/kdenlive/)."
        urls = [s["url"] for s in seo.suggest_links(body, PAGES, self_url="/dr-vs-kdenlive/")]
        self.assertEqual(urls, [])

    def test_common_single_words_are_not_anchors(self):
        pages = [{"title": "Why Windows is slow", "url": "/w/", "tags": ["Windows"]}]
        self.assertEqual(seo.suggest_links("I use Windows every day and it is slow.", pages), [])

    def test_apply_link_checks_the_text_has_not_moved(self):
        body = "I like Davinci Resolve."
        out = seo.apply_link(body, 7, 22, "Davinci Resolve", "/dr/")
        self.assertEqual(out, "I like [Davinci Resolve](/dr/).")
        with self.assertRaises(ValueError):
            seo.apply_link("Totally different text here.", 7, 22, "Davinci Resolve", "/dr/")


class CheckTests(unittest.TestCase):
    def run_checks(self, fields=None, body="", **kw):
        base = {"title": "A long enough title for checks", "kind": "article"}
        base.update(fields or {})
        data = seo.analyze(base, body, PAGES, kw.pop("self_url", "/me/"), **kw)
        return {c["key"]: c for c in data["checks"]}

    def test_headings(self):
        c = self.run_checks(body="# H1\n\n## Fine\n\n#### Jump\n\n```\n# comment in code\n```\n")["headings"]
        self.assertEqual(c["state"], "warn")
        self.assertEqual(len(c["items"]), 2)
        ok = self.run_checks(body="Intro\n\n## One\n\n### Two\n")["headings"]
        self.assertEqual(ok["state"], "ok")

    def test_long_text_needs_subheadings(self):
        c = self.run_checks(body="word " * 600)["headings"]
        self.assertEqual(c["state"], "warn")
        self.assertIn("sub-headings", c["note"])

    def test_focus_keyword(self):
        body = "Kdenlive is a great editor.\n\n## Using Kdenlive\n\n![Kdenlive timeline](/images/a.png)\n"
        c = self.run_checks({"focus_keyword": "kdenlive", "title": "Kdenlive review", "description": "All about Kdenlive"},
                            body, slug="kdenlive-review")["keyword"]
        self.assertEqual(c["state"], "ok")
        self.assertTrue(all(i["ok"] for i in c["items"]))
        bad = self.run_checks({"focus_keyword": "gimp"}, body, slug="x")["keyword"]
        self.assertEqual(bad["state"], "warn")
        self.assertEqual(self.run_checks(body=body)["keyword"]["state"], "info")

    def test_links_broken_generic_and_counts(self):
        body = "See [here](/kdenlive/) and [gone](/nope/) and [x](https://example.com) and [y](/images/p.png)."
        with __import__("tempfile").TemporaryDirectory() as tmp:
            checks = self.run_checks(body=body, root=Path(tmp))
        self.assertTrue(checks["links"]["note"].startswith("2 to other pages of this site, 1 to other sites"))
        self.assertEqual([i["label"] for i in checks["broken"]["items"]], ["/nope/"])
        self.assertEqual(checks["anchors"]["items"][0]["label"], "here")

    def test_no_internal_links_and_inbound(self):
        c = self.run_checks(body="Plain text.", inbound=0)
        self.assertEqual(c["links"]["state"], "warn")
        self.assertEqual(c["inbound"]["state"], "warn")
        self.assertEqual(self.run_checks(body="x", inbound=3)["inbound"]["state"], "ok")
        self.assertNotIn("inbound", self.run_checks(body="x"))

    def test_slug_and_title(self):
        self.assertEqual(self.run_checks(slug="best-editor-2024")["slug"]["state"], "warn")
        self.assertEqual(self.run_checks(slug="best-editor")["slug"]["state"], "ok")
        self.assertNotIn("slug", self.run_checks(slug="best-editor-2024", slug_locked=True))
        self.assertEqual(self.run_checks({"seo_title": "Short"})["seo_title"]["state"], "warn")

    def test_image_weight_and_featured_size(self):
        import struct, tempfile, zlib
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "images").mkdir()
            def png(name, w, h, pad=0):
                def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
                (root / "images" / name).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                                                      + chunk(b"IDAT", b"x" * pad) + chunk(b"IEND", b""))
            png("big.png", 3000, 2000, 300 * 1024)
            png("cover.png", 1200, 630)
            png("tiny.png", 300, 200)
            c = self.run_checks({"image": "/images/cover.png"}, "![a](/images/big.png)", root=root)
            self.assertEqual(c["image_weight"]["state"], "warn")
            self.assertEqual(c["social_image"]["state"], "ok")
            self.assertEqual(self.run_checks({"image": "/images/tiny.png"}, "", root=root)["social_image"]["state"], "warn")
            self.assertEqual(seo.image_size(root / "images" / "big.png"), (3000, 2000))
            self.assertIsNone(seo.image_size(root / "missing.png"))

    def test_link_targets(self):
        self.assertEqual(seo.link_targets("[a](/x/#top) [b](/y) <a href='/z/'>z</a> [c](https://e.com) ```\n[d](/code/)\n```"),
                         {"/x/", "/y/", "/z/"})


class StoreSeoFieldsTests(AdminCase):
    def test_search_fields_roundtrip_and_modified_date(self):
        entry = self.store.list_entries("article")[0]
        fields = dict(entry.fields)
        # a save that changes nothing leaves the date alone
        saved = self.store.save(entry, fields, entry.body, entry.etag)
        self.assertFalse(saved.fields.get("last_modified_at"))
        fields.update(seo_title="A search title that is fine", focus_keyword="linux")
        saved = self.store.save(saved, fields, saved.body, saved.etag)
        self.assertEqual(saved.fields["seo_title"], "A search title that is fine")
        self.assertEqual(saved.fields["focus_keyword"], "linux")
        self.assertRegex(saved.fields["last_modified_at"], r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d [+-]\d{4}$")
        self.assertEqual(saved.extras, entry.extras)


def make_png(path, size=(400, 300), photo=False):
    from PIL import Image, ImageDraw
    import random
    img = Image.new("RGB", size, (30, 60, 120))
    if photo:
        rnd = random.Random(1)
        px = img.load()
        for x in range(size[0]):
            for y in range(size[1]):
                px[x, y] = (rnd.randrange(256), (x * 255) // size[0], (y * 255) // size[1])
    else:
        d = ImageDraw.Draw(img)
        for i in range(0, size[1], 20):
            d.text((10, i), "Readable text line %d" % i, fill=(240, 240, 240))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


class ImageToolsTests(AdminCase):
    def setUp(self):
        super().setUp()
        self.token = self.login()
        self.dir = self.site / "images" / "posts" / "t"
        make_png(self.dir / "shot.png", (1600, 900))

    def api(self, path, payload):
        return self.client.post(path, base_url=BASE, data=json.dumps(payload),
                                headers={"Content-Type": "application/json", "X-CSRF-Token": self.token})

    def test_screenshot_becomes_lossless_webp_next_to_the_original(self):
        from PIL import Image, ImageChops
        data = self.api("/images/optimize", {"src": "/images/posts/t/shot.png"}).get_json()
        self.assertTrue(data["changed"], data)
        self.assertEqual(data["src"], "/images/posts/t/shot.webp")
        self.assertTrue((self.dir / "shot.png").exists())             # the original is not touched
        self.assertLess(data["new_kb"], data["old_kb"])
        a, b = Image.open(self.dir / "shot.png").convert("RGB"), Image.open(self.dir / "shot.webp").convert("RGB")
        self.assertIsNone(ImageChops.difference(a, b).getbbox())      # identical pixels

    def test_wide_image_is_scaled_down_and_noise_photo_stays_safe(self):
        import images
        make_png(self.dir / "huge.png", (3000, 2000))
        result = images.optimize(self.dir / "huge.png")
        self.assertTrue(result["resized"])
        self.assertEqual(result["size"][0], images.MAX_WIDTH)
        make_png(self.dir / "noise.png", (600, 400), photo=True)
        out = images.optimize(self.dir / "noise.png")
        if out["changed"]:
            from PIL import Image
            self.assertGreaterEqual(images._psnr(Image.open(self.dir / "noise.png"), Image.open(out["path"])), images.MIN_PSNR)

    def test_not_worth_it_and_refusals(self):
        import images
        from PIL import Image
        Image.new("RGB", (8, 8), "white").save(self.dir / "tiny.png")
        self.assertFalse(images.optimize(self.dir / "tiny.png")["changed"])
        (self.dir / "x.webp").write_bytes(b"RIFF")
        self.assertFalse(images.optimize(self.dir / "x.webp")["changed"])
        for bad in ("/images/../_config.yaml", "/_config.yaml", "/images/missing.png", "images/x.png"):
            self.assertEqual(self.api("/images/optimize", {"src": bad}).status_code, 404, bad)

    def test_featured_image_keeps_its_format(self):
        from PIL import Image
        noise = Image.effect_noise((2600, 1300), 40)
        Image.merge("RGB", (noise, noise.transpose(Image.FLIP_LEFT_RIGHT), noise.transpose(Image.FLIP_TOP_BOTTOM))).save(self.dir / "cover.jpg", quality=100)
        data = self.api("/images/optimize", {"src": "/images/posts/t/cover.jpg", "featured": True}).get_json()
        self.assertTrue(data["changed"], data)
        self.assertTrue(data["src"].endswith(".jpg"))                 # not WebP: link previews must keep working
        self.assertNotEqual(data["src"], "/images/posts/t/cover.jpg")
        self.assertEqual(data["width"], 2000)

    def test_swap_in_text_and_tidy_up_after_save(self):
        body = "![A shot](/images/posts/t/shot.png)\n\n<img src=\"/images/posts/t/shot.png\">\n"
        new = self.api("/images/optimize", {"src": "/images/posts/t/shot.png"}).get_json()["src"]
        out = self.api("/seo/apply", {"op": "src", "body": body, "old": "/images/posts/t/shot.png", "new": new}).get_json()["body"]
        self.assertEqual(out.count("shot.webp"), 2)
        self.assertNotIn("shot.png", out)
        self.assertEqual(self.api("/seo/apply", {"op": "src", "body": "nothing", "old": "/images/posts/t/shot.png", "new": new}).status_code, 409)
        self.assertEqual(self.api("/seo/apply", {"op": "src", "body": body, "old": "/images/posts/t/shot.png", "new": "/etc/passwd"}).status_code, 409)
        # save an article that uses the new file: the old one is moved out of the site
        entry = self.store.list_entries("article")[0]
        post = {"csrf_token": self.token, "etag": entry.etag, "title": entry.fields["title"], "description": "d" * 80,
                "author": entry.fields["author"], "image": "", "tags": "", "date": str(entry.fields["date"]),
                "body": out, "slug": entry.slug, "swapped": json.dumps([["/images/posts/t/shot.png", new]])}
        response = self.client.post(f"/edit/article/{entry.name}", base_url=BASE, data=post, follow_redirects=True)
        self.assertIn(b"no longer used", response.data)
        self.assertFalse((self.dir / "shot.png").exists())
        self.assertTrue((self.dir / "shot.webp").exists())
        self.assertTrue(list((self.data / "image-originals").rglob("shot.png")))

    def test_original_stays_when_something_else_still_uses_it(self):
        entry = self.store.list_entries("article")[0]
        other = self.store.list_entries("article")[1]
        self.store.save(other, dict(other.fields), other.body + "\n![x](/images/posts/t/shot.png)\n", other.etag)
        new = self.api("/images/optimize", {"src": "/images/posts/t/shot.png"}).get_json()["src"]
        post = {"csrf_token": self.token, "etag": entry.etag, "title": entry.fields["title"], "description": "d" * 80,
                "author": entry.fields["author"], "image": "", "tags": "", "date": str(entry.fields["date"]),
                "body": f"![x]({new})\n", "slug": entry.slug, "swapped": json.dumps([["/images/posts/t/shot.png", new]])}
        self.client.post(f"/edit/article/{entry.name}", base_url=BASE, data=post, follow_redirects=True)
        self.assertTrue((self.dir / "shot.png").exists())

    def test_image_checks_offer_actions(self):
        make_png(self.dir / "big.png", (1800, 1200), photo=True)
        self.assertGreater((self.dir / "big.png").stat().st_size, 200 * 1024)
        data = self.api("/seo/analyze", {"kind": "article", "slug": "x", "title": "T", "description": "", "image": "/images/posts/t/big.png",
                                         "body": "![](/images/posts/t/big.png)"}).get_json()
        weight = next(c for c in data["checks"] if c["key"] == "image_weight")
        item = weight["items"][0]
        self.assertEqual((item["src"], item["featured"], item["convertible"]), ("/images/posts/t/big.png", True, True))


class RouteTests(AdminCase):
    def setUp(self):
        super().setUp()
        self.token = self.login()

    def api(self, path, payload):
        return self.client.post(path, base_url=BASE, data=json.dumps(payload),
                                headers={"Content-Type": "application/json", "X-CSRF-Token": self.token})

    def test_analyze_returns_all_three_parts(self):
        response = self.api("/seo/analyze", {"kind": "article", "slug": "new-one", "title": "A good title for the article",
                                             "description": "", "image": "", "body": "Hello there, this is a body.\n\n![](/images/x/pic.png)\n"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(set(data), {"meta", "alts", "images", "links", "checks"})
        self.assertEqual(len(data["alts"]), 1)

    def test_apply_link_and_alt(self):
        body = "I like Davinci Resolve.\n\n![](/images/x/pic.png)\n"
        out = self.api("/seo/apply", {"op": "link", "body": body, "start": 7, "end": 22, "phrase": "Davinci Resolve", "url": "/dr/"})
        self.assertEqual(out.get_json()["body"].splitlines()[0], "I like [Davinci Resolve](/dr/).")
        out = self.api("/seo/apply", {"op": "alt", "body": body, "index": 0, "src": "/images/x/pic.png", "alt": "A picture"})
        self.assertIn("![A picture](/images/x/pic.png)", out.get_json()["body"])

    def test_apply_refuses_stale_or_foreign_links(self):
        stale = self.api("/seo/apply", {"op": "link", "body": "other", "start": 0, "end": 5, "phrase": "Davinci", "url": "/dr/"})
        self.assertEqual(stale.status_code, 409)
        for url in ("https://evil.example/", "//evil.example/", "/a)b", 'javascript:alert(1)'):
            bad = self.api("/seo/apply", {"op": "link", "body": "Davinci", "start": 0, "end": 7, "phrase": "Davinci", "url": url})
            self.assertEqual(bad.status_code, 409, url)

    def test_json_endpoints_need_the_csrf_header(self):
        response = self.client.post("/seo/analyze", base_url=BASE, data=json.dumps({"body": "x"}),
                                    headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 403)

    def test_pages_list_and_media(self):
        pages = self.get("/api/pages").get_json()["pages"]
        self.assertTrue(any(p["url"].startswith("/") and p["title"] for p in pages))
        image = next((p for p in (self.site / "images").rglob("*") if p.suffix == ".png" and p.is_file()), None)
        if image is None:
            image = self.site / "images" / "t.png"
            image.parent.mkdir(exist_ok=True)
            image.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
        relative = "/" + image.relative_to(self.site).as_posix()
        self.assertEqual(self.get("/media", query_string={"path": relative}).status_code, 200)
        for bad in ("/images/../_config.yaml", "/_config.yaml", "/images/x.md", "images/x.png"):
            self.assertEqual(self.get("/media", query_string={"path": bad}).status_code, 404, bad)

    def test_edit_page_loads_the_editor_and_seo_tab(self):
        page = self.get("/new/article").data
        for needle in (b"md-editor.js", b"markdown-it.min.js", b'data-tab="seo"', b"Generate SEO suggestions"):
            self.assertIn(needle, page)


if __name__ == "__main__":
    unittest.main()
