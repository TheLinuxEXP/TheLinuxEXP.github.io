import sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
old_start = t.index("Open <http://127.0.0.1:4001/>.")
old_end = t.index("### Why nobody else can reach the admin")
new = '''Open <http://127.0.0.1:4001/>. From there you can create pages and articles, edit the header
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

'''
t = t[:old_start] + new + t[old_end:]
row = "| Admin libraries (Flask, PyYAML) | `./admin/update.sh` (upgrades, then runs the admin's tests) |\n"
extra = row + "| Visual editor library (markdown-it) | Replace `admin/static/vendor/markdown-it.min.js` with the new release's `dist/markdown-it.min.js`, then run `node admin/tests/editor_roundtrip.js` (opens every article and checks the editor writes it back unchanged; needs `npm i playwright`) |\n| Design system | Regenerate `admin/static/design/tokens.css` and copy `bundle.css` from the Planner Unifié design system |\n"
assert row in t
t = t.replace(row, extra, 1)
open(p, "w", encoding="utf-8").write(t)
print("patched", p)
