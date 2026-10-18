import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
marker = "### Why nobody else can reach the admin"
new = """  The tab also has **Search settings** (an optional *search title* and a *focus keyword*, saved in the article's
  front matter) and a **Checks** list: headings order, length, web address, where the focus keyword appears,
  image weight and size, featured image size, links to other pages, broken internal links, vague link text
  ("click here"), and whether any other article links to this one. The Content page marks articles that
  no other page links to. Saving an article also records `last_modified_at`, which the site publishes as the
  article's modified date.

### What the site publishes for search engines

`_includes/head.html` writes, on every page: the title (`seo_title` if set), the description, a canonical link,
Open Graph and X/Twitter tags, and `noindex` for archive pages 2+, embargoed posts and the 404 page.
Articles also get publication and modification dates and JSON-LD (`BlogPosting` + breadcrumbs); other pages get
`WebPage` + breadcrumbs, the home page `WebSite`. `robots.txt` points at the sitemap.
Optional front matter: `seo_title`, `noindex: true`, `canonical: <url>`. Optional in `_config.yaml`:
`default_image: https://thelinuxexp.com/images/...` for link previews of pages with no image.

After a build, check the result:

    bundle exec jekyll build
    python3 _tools/check_seo.py

"""
if "What the site publishes for search engines" in s:
    sys.exit("already patched")
assert marker in s
s = s.replace(marker, new + marker, 1)
open(p, "w", encoding="utf-8").write(s)
print("patched", p)
