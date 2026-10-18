# The Linux Experiment

A [Jekyll](https://jekyllrb.com) site (design adapted from the elementary OS blog),
built and hosted by GitHub Pages, with a **local-only admin** for editing it from your laptop.

```
_posts/      articles (Markdown)        pages/      standalone pages created in the admin
_data/       header.yml, footer.yml     _layouts/ _includes/ _sass/   the design
admin/       the local admin (Python)   _tools/     compare_builds.py
```

## First-time setup on the laptop (Debian / Ubuntu / TUXEDO OS)

```bash
sudo apt install ruby-dev build-essential zlib1g-dev   # Ruby headers + compiler: some gems build native code
cd ~/Projects/Website
bundle config set --local path vendor/bundle           # install gems inside the project, no sudo needed
bundle install
```

Never run `bundle install` with `sudo`: it leaves root-owned files behind. If that already happened:
`sudo chown -R "$USER": ~/Projects/Website`.

## Day to day

```bash
./admin/start.sh          # first run asks for an admin user name + password
```

Open <http://127.0.0.1:4001/>. From there you can create pages and articles, edit the header
and footer, upload images, insert YouTube videos, start a **private preview** of the whole site,
and **Publish** (git commit + push; GitHub then rebuilds the site).

The admin uses the **Planner Unifié** design system (`admin/static/design/`: `tokens.css` and `bundle.css`,
light and dark theme).

### Writing articles and pages

- **Visual editor**, adapted from the Planner's notes editor: format text, lists, quotes, code, tables, links,
  images and YouTube videos with the toolbar or Markdown shortcuts (`## `, `- `, `1. `, `> `, ` ``` `).
  The **Markdown** switch shows the raw text. A link button lists your other pages and articles.
- **Your Markdown stays as it is.** Only the blocks you touch are rewritten; everything else (including raw HTML,
  `<figure>` and Liquid blocks, shown as locked boxes) is saved byte for byte. If a change could ever lose text,
  the editor refuses to save and says why.
- **SEO tab**: *Generate SEO suggestions* reads the text as it is right now (saved or not) and proposes
  - the **meta tags** the site uses, only when missing: the description and the featured image;
  - **alt text** for images that have none (from the caption, the file name or the heading above);
  - **links to your other pages**, with the phrase in context and a one-click *Add link*.

  It is plain text analysis on this computer: no AI, no network. Nothing changes until you accept a suggestion
  (alt text is editable before you apply it).

  The tab also has **Search settings** (an optional *search title* and a *focus keyword*, saved in the article's
  front matter) and a **Checks** list: headings order, length, web address, where the focus keyword appears,
  image weight and size, featured image size, links to other pages, broken internal links, vague link text
  ("click here"), and whether any other article links to this one. The Content page marks articles that
  no other page links to. Saving an article also records `last_modified_at`, which the site publishes as the
  article's modified date.

### Images: replace and make lighter

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

### Why nobody else can reach the admin

- It listens on `127.0.0.1` only. The address is fixed in the code; there is no setting to change it.
- It is **not part of the website**: `admin/` is excluded from the Jekyll build, so it is never published.
- Requests whose `Host` header is not `127.0.0.1:4001` / `localhost:4001` are refused (blocks DNS-rebinding
  tricks from web pages), as are cross-site form posts (CSRF token + `Origin` check, `SameSite=Strict` cookie).
- Password stored as a salted scrypt hash in `admin/.data/` (git-ignored, mode 600); 5 wrong
  attempts lock the login for a minute.
- Do not forward port 4001 or run it behind a tunnel/reverse proxy; that would defeat the point.

## Updating the libraries

| What | Command |
|---|---|
| Jekyll and its plugins | `bundle update`, then `bundle exec jekyll build` to check |
| Admin libraries (Flask, PyYAML) | `./admin/update.sh` (upgrades, then runs the admin's tests) |
| Visual editor library (markdown-it) | Replace `admin/static/vendor/markdown-it.min.js` with the new release's `dist/markdown-it.min.js`, then run `node admin/tests/editor_roundtrip.js` (opens every article and checks the editor writes it back unchanged; needs `npm i playwright`) |
| Design system | Regenerate `admin/static/design/tokens.css` and copy `bundle.css` from the Planner Unifié design system |
| Both, automatically | Dependabot opens a weekly pull request (`.github/dependabot.yml`); the workflows build the site / run the admin tests on each one, so a failing update is visible before you merge it |

The old setup used the `github-pages` gem, which pins Jekyll 3.10. This one uses Jekyll 4.4
directly and is built by `.github/workflows/pages.yml`.

The SCSS still uses `@import`, which Dart Sass only warns about today (silenced in `_config.yaml`).
When a future Sass release removes it, replace the `@import` lines in `css/main.scss` with `@use`.

## One-time migration from the old repository

1. Unzip the overlay over your clone of `thelinuxexp.github.io`.
2. Remove what is no longer needed:
   ```bash
   git rm Gemfile.lock scripts/index.js     # old lockfile; unused script containing an API key
   git rm -r --cached _site                 # build output no longer belongs in git
   ```
3. `bundle install` and commit the new `Gemfile.lock`.
4. **Check nothing changed on the public pages** (recommended before switching):
   ```bash
   git stash -u                              # or use a second checkout of the old repo
   bundle exec jekyll build --destination /tmp/site-old
   git stash pop && bundle install
   bundle exec jekyll build --destination /tmp/site-new
   python3 _tools/compare_builds.py /tmp/site-old /tmp/site-new
   ```
   Expected differences: the `Jekyll v…` generator line in the feeds and tiny CSS formatting
   (new Sass compiler). Anything else is worth a look.
5. On GitHub: **Settings → Pages → Source: GitHub Actions**. The custom domain stays configured there.
6. Push to `main`.
7. In the Google Cloud console, delete or rotate the YouTube API key that was in `scripts/index.js`
   (it has been public in the repository).

## Using the admin inside the Planner

See `admin/INTEGRATION.md` (patch and steps in `admin/integration/`). The launcher is now `admin/serve.py`; `admin/start.sh` still works as before.
