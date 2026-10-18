/* Visual Markdown editor for the site admin.
 *
 * Adapted from the Planner's notes editor (Notes & Scripts): the Markdown is rendered with
 * markdown-it into a contentEditable surface and written back as Markdown. To keep your
 * articles untouched, saving is *block-level*: every top-level block (paragraph, list, table,
 * raw HTML...) you did not edit is written back byte-for-byte from the original text; only the
 * blocks you changed are re-serialized. Raw HTML and Liquid blocks (<figure>, YouTube includes,
 * iframes...) are shown as locked boxes and are never rewritten.
 *
 * It enhances a <textarea>: the textarea stays in the form and always holds the current
 * Markdown, so saving works like any other form field. "Markdown" mode simply shows it.
 *
 *     const editor = new MdEditor(textarea, { ui, upload, pages });
 */
(function () {
  "use strict";

  /* ------------------------------------------------------------------ *
   * tiny helpers
   * ------------------------------------------------------------------ */
  function h(tag, attrs, children) {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "class") n.className = v;
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else if (v !== false && v !== null && v !== undefined) n.setAttribute(k, v);
    }
    for (const c of [].concat(children || [])) {
      if (c === null || c === undefined) continue;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    }
    return n;
  }
  const escHtml = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  const ICONS = {
    undo: '<path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/>',
    redo: '<path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 2.7"/>',
    bold: '<path d="M6 4h8a4 4 0 0 1 0 8H6zM6 12h9a4 4 0 0 1 0 8H6z"/>',
    italic: '<path d="M19 4h-9M14 20H5M15 4 9 20"/>',
    strike: '<path d="M16 4H9a3 3 0 0 0-2.83 4M14 12a4 4 0 0 1 0 8H6M4 12h16"/>',
    code: '<path d="m16 18 6-6-6-6M8 6l-6 6 6 6"/>',
    link: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    page: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M10 9H8M16 13H8M16 17H8"/>',
    image: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/>',
    video: '<rect x="2" y="5" width="20" height="14" rx="3"/><path d="m10 9 5 3-5 3z"/>',
    ul: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    ol: '<path d="M10 6h11M10 12h11M10 18h11M4 6h1v4M4 10h2M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/>',
    quote: '<path d="M3 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2H4c-1.25 0-2 .75-2 2v6c0 1.25.75 2 2 2h4M15 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2h-4c-1.25 0-2 .75-2 2v6c0 1.25.75 2 2 2h4"/>',
    codeblock: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="m10 10-2 2 2 2M14 10l2 2-2 2"/>',
    table: '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    hr: '<path d="M5 12h14"/>',
    rowAdd: '<path d="M3 5h18v6H3zM3 15h8M7 12v6M15 17h6"/>',
    colAdd: '<path d="M5 3v18h6V3zM15 3h6M18 3v8M14 15h8"/>',
    trash: '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6"/>',
  };
  function icon(name, size) {
    const s = document.createElement("span");
    s.className = "ico";
    s.innerHTML = `<svg viewBox="0 0 24 24" width="${size || 16}" height="${size || 16}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ""}</svg>`;
    return s;
  }

  /* ------------------------------------------------------------------ *
   * Markdown -> HTML (markdown-it + source map)
   * ------------------------------------------------------------------ */
  // Site images live at /images/... : the admin shows them through its own /media route.
  function displaySrc(src) {
    return /^\/(?!\/)/.test(src) ? `/media?path=${encodeURIComponent(src)}` : src;
  }

  const YOUTUBE_RE = /youtube\.html\s+id\s*=|youtube\.com\/embed\//;
  const YOUTUBE_ID_RE = /assign\s+id\s*=\s*["']([\w-]{11})["']|youtube\.com\/embed\/([\w-]{11})/;

  let MD = null;
  function md() {
    if (MD) return MD;
    // kramdown (the site) does not break lines on a single newline, so neither do we
    const m = window.markdownit({ html: true, breaks: false, linkify: true, typographer: false });
    m.linkify.set({ fuzzyLink: false, fuzzyEmail: false, fuzzyIP: false });   // only real http(s):// URLs

    // remember which source lines each top-level block came from
    m.core.ruler.push("srcmap", (state) => {
      if (state.env.noMap) return;
      for (const t of state.tokens) {
        if (t.level === 0 && t.map && (t.nesting === 1 || t.nesting === 0) && t.type !== "inline") {
          t.attrSet("data-md", t.map[0] + ":" + t.map[1]);
        }
      }
    });
    const mapAttr = (t, env) => (t.level === 0 && t.map && !env.noMap ? ` data-md="${t.map[0]}:${t.map[1]}"` : "");
    const defFence = m.renderer.rules.fence;
    m.renderer.rules.fence = (tokens, i, o, env, self) => {
      const html = defFence(tokens, i, o, env, self);
      const t = tokens[i];
      return t.level === 0 && t.map && !env.noMap ? html.replace(/^<pre/, `<pre data-md="${t.map[0]}:${t.map[1]}"`) : html;
    };
    m.renderer.rules.code_block = (tokens, i, o, env) =>
      `<pre${mapAttr(tokens[i], env)}><code>${escHtml(tokens[i].content)}</code></pre>\n`;
    // Raw HTML / Liquid blocks: shown as a locked box, written back untouched.
    m.renderer.rules.html_block = (tokens, i, o, env) => {
      const t = tokens[i];
      return rawBlockHtml(t.content.replace(/\n+$/, ""), mapAttr(t, env));
    };
    // images: remember the original src, show the file through /media
    const defImage = m.renderer.rules.image;
    m.renderer.rules.image = (tokens, i, o, env, self) => {
      const t = tokens[i];
      const src = t.attrGet("src") || "";
      t.attrSet("data-src", src);
      t.attrSet("src", displaySrc(src));
      return defImage(tokens, i, o, env, self);
    };
    MD = m;
    return m;
  }

  function rawBlockHtml(raw, extraAttrs) {
    const yt = YOUTUBE_ID_RE.exec(raw);
    const label = YOUTUBE_RE.test(raw) ? `YouTube video${yt ? " " + (yt[1] || yt[2]) : ""}` : "";
    const shown = raw.length > 400 ? raw.slice(0, 400) + "…" : raw;
    const inner = label
      ? `<span class="md-html-label">${escHtml(label)}</span>`
      : `<span class="md-html-label">HTML block</span><code>${escHtml(shown)}</code>`;
    return `<div class="md-html" contenteditable="false" data-raw="${escHtml(raw)}"${extraAttrs || ""}>${inner}</div>\n`;
  }

  // Allowlist sanitizer. Notes may contain raw HTML (markdown-it html:true) and
  // note files can come from anywhere, so nothing outside this list survives:
  // unknown elements are unwrapped (their text is kept), dangerous ones are
  // dropped with their content, unknown attributes are removed, and URLs must
  // use a safe scheme (checked AFTER stripping the control characters and
  // whitespace browsers ignore, e.g. "jav&#x09;ascript:").
  const SAN_DROP = new Set(["SCRIPT", "STYLE", "IFRAME", "FRAME", "FRAMESET", "OBJECT", "EMBED", "APPLET", "LINK", "META", "BASE", "FORM", "TEMPLATE", "NOSCRIPT", "SVG", "MATH", "TITLE", "HEAD", "SELECT", "TEXTAREA", "BUTTON", "CANVAS", "DIALOG", "PORTAL", "SLOT"]);
  const SAN_TAGS = new Set(("A ABBR B BDI BDO BLOCKQUOTE BR CAPTION CITE CODE COL COLGROUP DATA DD DEL DETAILS DFN DIV DL DT EM FIGCAPTION FIGURE H1 H2 H3 H4 H5 H6 HR I IMG INS KBD LI MARK OL P PRE Q RP RT RUBY S SAMP SECTION ARTICLE ASIDE HEADER FOOTER NAV SMALL SPAN STRONG SUB SUMMARY SUP TABLE TBODY TD TFOOT TH THEAD TIME TR U UL VAR WBR INPUT AUDIO VIDEO SOURCE CENTER FONT").split(" "));
  const SAN_ATTRS = new Set(["class", "title", "alt", "lang", "dir", "colspan", "rowspan", "align", "valign", "width", "height", "open", "start", "reversed", "type", "checked", "disabled", "datetime", "cite", "controls", "loop", "muted", "poster", "color", "size", "face", "href", "src", "style", "contenteditable", "role"]);
  const SAN_URL_ATTRS = new Set(["href", "src", "cite", "poster"]);
  function safeUrl(v, attr) {
    const c = String(v).replace(/[\u0000-\u0020\u007f-\u009f\u00ad\u200b-\u200f\u2028\u2029\ufeff]/g, "").toLowerCase();
    if (c === "") return true;
    if (/^data:image\/(png|jpe?g|gif|webp|avif|bmp);/.test(c)) return attr !== "href";
    const m = /^([a-z][a-z0-9+.-]*):/.exec(c);
    if (!m) return true;                                   // relative / #anchor / //host
    if (attr === "href") return ["http", "https", "mailto", "tel"].includes(m[1]);
    return ["http", "https"].includes(m[1]);
  }
  function safeStyle(v) {
    const c = String(v).replace(/\/\*[\s\S]*?\*\//g, "").replace(/\\/g, "").toLowerCase();
    return !/(url\s*\(|expression|javascript:|@import|behavior|-moz-binding|image-set|position\s*:\s*(fixed|sticky))/.test(c);
  }
  function sanitizeNode(parent) {
    for (const n of [...parent.childNodes]) {
      if (n.nodeType === 3) continue;
      if (n.nodeType !== 1) { n.remove(); continue; }       // comments, PIs
      const tag = n.tagName.toUpperCase();
      if (SAN_DROP.has(tag) || n.namespaceURI !== "http://www.w3.org/1999/xhtml") { n.remove(); continue; }
      if (!SAN_TAGS.has(tag)) {                              // unwrap: keep the text
        sanitizeNode(n);
        while (n.firstChild) parent.insertBefore(n.firstChild, n);
        n.remove();
        continue;
      }
      for (const a of [...n.attributes]) {
        const name = a.name.toLowerCase();
        const ok = (SAN_ATTRS.has(name) || /^data-[a-z0-9-]+$/.test(name)) &&
          !(SAN_URL_ATTRS.has(name) && !safeUrl(a.value, name)) &&
          !(name === "style" && !safeStyle(a.value));
        if (!ok) n.removeAttribute(a.name);
      }
      if (tag === "INPUT") {                                 // only the task-list checkbox
        if ((n.getAttribute("type") || "").toLowerCase() !== "checkbox") { n.remove(); continue; }
      }
      if (tag === "A") {
        if (n.getAttribute("target")) n.removeAttribute("target");
        n.setAttribute("rel", "noopener noreferrer");
      }
      if (tag === "SOURCE" && !n.hasAttribute("src")) { n.remove(); continue; }
      sanitizeNode(n);
    }
  }
  function sanitizeInto(container, html) {
    const tpl = document.createElement("template");
    tpl.innerHTML = html;
    sanitizeNode(tpl.content);
    container.innerHTML = "";
    container.appendChild(tpl.content);
  }

  const BLOCK_TAGS = new Set(["P", "DIV", "H1", "H2", "H3", "H4", "H5", "H6", "UL", "OL", "LI", "BLOCKQUOTE", "PRE", "TABLE", "HR", "FIGURE", "SECTION", "ARTICLE", "DETAILS", "ASIDE", "HEADER", "FOOTER", "NAV", "DL"]);

  function escText(s) {
    return s
      .replace(/ /g, " ")
      .replace(/\\(?=[\\`*_{}\[\]()#+\-.!|<>~])/g, "\\\\")
      .replace(/([*`])/g, "\\$1")
      .replace(/(?<![\p{L}\p{N}])_|_(?![\p{L}\p{N}])/gu, "\\_")
      .replace(/~~/g, "\\~~")
      .replace(/<(?=[A-Za-z\/!])/g, "\\<");
  }
  function escLineStarts(s) {
    return s.split("\n").map((l) => l
      .replace(/^(\s*)(#{1,6})(\s)/, "$1\\$2$3")
      .replace(/^(\s*)([-+*])(\s)/, "$1\\$2$3")
      .replace(/^(\s*)(\d+)([.)])(\s)/, "$1$2\\$3$4")
      .replace(/^(\s*)>/, "$1\\>")).join("\n");
  }
  function wrapInline(marker, inner) {
    const m = /^(\s*)([\s\S]*?)(\s*)$/.exec(inner);
    if (!m[2]) return inner;
    return m[1] + marker + m[2] + marker + m[3];
  }

  function inlineNodes(nodes, ctx) {
    let out = "";
    for (const n of nodes) out += inlineNode(n, ctx || {});
    return out;
  }
  function inlineNode(n, ctx) {
    if (n.nodeType === 3) {
      let t = n.nodeValue;
      const prev = n.previousSibling;
      if (prev && prev.nodeName === "BR") t = t.replace(/^\s*\n\s*/, "");
      t = t.replace(/\s*\n\s*/g, " ");
      return ctx.raw ? t.replace(/ /g, " ") : escText(t);
    }
    if (n.nodeType !== 1) return "";
    const tag = n.tagName;
    const kids = () => inlineNodes(n.childNodes, ctx);
    switch (tag) {
      case "BR": {
        if (ctx.table) {
          let nx = n.nextSibling;
          while (nx && nx.nodeType === 3 && !nx.nodeValue.trim()) nx = nx.nextSibling;
          return nx ? "<br>" : "";
        }
        return ctx.heading ? " " : "  \n";
      }
      case "STRONG": case "B": return wrapInline("**", kids());
      case "EM": case "I": return wrapInline("*", kids());
      case "DEL": case "S": case "STRIKE": return wrapInline("~~", kids());
      case "CODE": {
        const t = n.textContent.replace(/ /g, " ");
        if (!t) return "";
        const ticks = "`".repeat((Math.max(0, ...(t.match(/`+/g) || []).map((x) => x.length)) || 0) + 1);
        const pad = /^`|`$/.test(t) ? " " : "";
        return ticks + pad + t + pad + ticks;
      }
      case "A": {
        const href = n.getAttribute("href") || "";
        const text = kids();
        if (!href) return text;
        if (text === href && !n.getAttribute("title")) return href;       // a bare URL stays a bare URL on save
        const dest = /[\s()]/.test(href) ? `<${href}>` : href;
        const title = n.getAttribute("title");
        return `[${text}](${dest}${title ? ` "${title.replace(/"/g, '\\"')}"` : ""})`;
      }
      case "IMG": {
        const src = n.getAttribute("data-src") || n.getAttribute("src") || "";
        const alt = (n.getAttribute("alt") || "").replace(/[\[\]]/g, "");
        const dest = /[\s()]/.test(src) ? `<${src}>` : src;
        const title = n.getAttribute("title");
        return `![${alt}](${dest}${title ? ` "${title.replace(/"/g, '\\"')}"` : ""})`;
      }
      case "INPUT": return "";
      case "U": case "MARK": case "SUP": case "SUB": case "KBD": {
        const t = tag.toLowerCase();
        return `<${t}>${kids()}</${t}>`;
      }
      case "SPAN": case "FONT": {
        const st = n.style || {};
        let inner = kids();
        if (st.fontWeight === "bold" || parseInt(st.fontWeight, 10) >= 600) inner = wrapInline("**", inner);
        if (st.fontStyle === "italic") inner = wrapInline("*", inner);
        if ((st.textDecorationLine || st.textDecoration || "").includes("line-through")) inner = wrapInline("~~", inner);
        return inner;
      }
      default:
        if (BLOCK_TAGS.has(tag)) return kids();
        return kids();
    }
  }

  function trimBlankLines(s) { return s.replace(/^\s*\n/, "").replace(/\s+$/, "").replace(/^[ \t]+(?=\S)/, (m) => m); }

  // Serializes a list of sibling nodes (mixed text/inline/block) to Markdown.
  function blocksOf(nodes, opts) {
    opts = opts || {};
    const out = [];
    let run = [];
    const flush = () => {
      if (!run.length) return;
      let s = inlineNodes(run, {});
      run = [];
      s = s.replace(/^\s+/, "").replace(/\s+$/, "");
      if (s) out.push(escLineStarts(s));
    };
    for (const n of nodes) {
      if (n.nodeType === 1 && (BLOCK_TAGS.has(n.tagName) || n.tagName === "DETAILS")) {
        flush();
        const s = blockEl(n);
        if (s !== "") out.push(s);
      } else if (n.nodeType === 3 || n.nodeType === 1) {
        run.push(n);
      }
    }
    flush();
    return out.join(opts.sep || "\n\n");
  }

  function indentLines(text, pad, firstPrefix) {
    const lines = text.split("\n");
    return lines.map((l, i) => (i === 0 ? firstPrefix + l : (l === "" ? "" : pad + l))).join("\n");
  }

  function blockEl(el) {
    const tag = el.tagName;
    if (/^H[1-6]$/.test(tag)) {
      const t = inlineNodes(el.childNodes, { heading: true }).replace(/\s+/g, " ").trim();
      return t ? "#".repeat(+tag[1]) + " " + t : "";
    }
    switch (tag) {
      case "P": {
        const s = inlineNodes(el.childNodes, {}).replace(/^\s+/, "").replace(/\s+$/, "");
        return s ? escLineStarts(s) : "";
      }
      case "DIV":
        if (el.classList.contains("md-html")) return el.hasAttribute("data-raw") ? el.getAttribute("data-raw") : el.innerHTML.trim();
        return blocksOf(el.childNodes);
      case "BLOCKQUOTE": {
        const inner = blocksOf(el.childNodes);
        if (!inner) return "";
        return inner.split("\n").map((l) => (l ? "> " + l : ">")).join("\n");
      }
      case "UL": case "OL": return listEl(el);
      case "LI": return blocksOf(el.childNodes, { sep: "\n" });
      case "PRE": return preEl(el);
      case "HR": return "---";
      case "TABLE": return tableEl(el);
      default:
        return el.outerHTML.trim();
    }
  }

  function listEl(el) {
    const ordered = el.tagName === "OL";
    let n = parseInt(el.getAttribute("start") || "1", 10);
    if (!(n >= 0)) n = 1;
    // Browsers (Chromium's Tab = "indent") nest a sub-list as a <ul>/<ol> sitting DIRECTLY inside the parent list,
    // after the <li> it belongs to, instead of inside it. Those lists are attached to the preceding item here;
    // ignoring them used to drop every sub-bullet when the note was saved.
    const items = [];
    const extra = new Map();            // <li> (or null for a leading orphan list) -> sub-lists that follow it
    for (const c of el.children) {
      if (c.tagName === "LI") items.push(c);
      else if (c.tagName === "UL" || c.tagName === "OL") {
        const owner = items.length ? items[items.length - 1] : null;
        if (!extra.has(owner)) extra.set(owner, []);
        extra.get(owner).push(c);
        if (!items.length) items.push(null);        // an item with no text of its own
      }
    }
    const loose = items.some((li) => li && [...li.children].some((c) => c.tagName === "P"));
    const parts = [];
    for (const li of items) {
      // the checkbox sits straight in the <li> of a tight list, but inside its <p> in a loose one (items separated by blank lines)
      const isCb = (c) => c.nodeType === 1 && c.tagName === "INPUT" && c.type === "checkbox";
      const firstP = li && [...li.children].find((c) => c.tagName === "P");
      const cb = li && ([...li.childNodes].find(isCb) || (firstP && [...firstP.childNodes].find(isCb)));
      const rest = li ? [...li.childNodes].filter((c) => c !== cb) : [];
      let content = blocksOf(rest, { sep: loose ? "\n\n" : "\n" });
      if (cb) content = (cb.checked ? "[x]" : "[ ]") + (content ? " " + content : "");
      for (const sub of extra.get(li) || []) {
        const subText = listEl(sub);
        if (subText) content += (content ? "\n" : "") + subText;
      }
      const marker = ordered ? `${n}. ` : "- ";
      n++;
      parts.push(content ? indentLines(content, " ".repeat(marker.length), marker) : marker.trimEnd());
    }
    return parts.join(loose ? "\n\n" : "\n");
  }

  function preEl(el) {
    const code = el.querySelector("code");
    let t = (code || el).textContent.replace(/ /g, " ").replace(/\n$/, "");
    const m = code && /(?:^|\s)language-([\w+#.-]+)/.exec(code.className || "");
    const longest = Math.max(2, ...(t.match(/`{3,}/g) || []).map((x) => x.length));
    const fence = "`".repeat(longest + 1);
    return `${fence}${m ? m[1] : ""}\n${t}\n${fence}`;
  }

  function tableEl(el) {
    const rows = [...el.querySelectorAll("tr")];
    if (!rows.length) return "";
    const cellText = (c) => inlineNodes(c.childNodes, { table: true }).replace(/\s+/g, " ").replace(/\|/g, "\\|").trim();
    const grid = rows.map((r) => [...r.children].filter((c) => /^T[HD]$/.test(c.tagName)));
    const cols = Math.max(...grid.map((r) => r.length));
    const aligns = [];
    for (let i = 0; i < cols; i++) {
      const c = grid[0][i];
      const a = c && ((c.style && c.style.textAlign) || c.getAttribute("align") || "");
      aligns.push(a === "center" ? ":---:" : a === "right" ? "---:" : a === "left" ? ":---" : "---");
    }
    const line = (cells) => "| " + Array.from({ length: cols }, (_, i) => (cells[i] ? cellText(cells[i]) : "")).join(" | ") + " |";
    const out = [line(grid[0]), "| " + aligns.join(" | ") + " |"];
    for (const r of grid.slice(1)) out.push(line(r));
    return out.join("\n");
  }

  // The text a person can see in a container, without spaces / zero-width characters (formatting is ignored on purpose).
  function textSig(root) { return root.textContent.replace(/[\s\u200b\u00a0\ufeff]+/g, ""); }

  // Counts of what carries no text of its own: task checkboxes (with their state), pictures, links, table rows, bullets, code blocks.
  function structSig(root) {
    const n = (sel) => root.querySelectorAll(sel).length;
    const cbs = [...root.querySelectorAll("input[type=checkbox]")].map((i) => (i.checked ? "x" : "o")).join("");
    // an empty bullet / code block (just typed "- " or "```", nothing after it yet) holds nothing that could be lost: not counted
    const filled = (sel) => [...root.querySelectorAll(sel)].filter((e) => /\S/.test(e.textContent.replace(/[\u200b\ufeff]/g, "")) || e.querySelector("img, input, table")).length;
    return `checkboxes ${cbs || "-"}, images ${n("img")}, links ${n("a[href]")}, rows ${n("tr")}, bullets ${filled("li")}, code ${filled("pre")}`;
  }

  // A readable plain-text outline of the editor (bullets indented by depth): used to rescue the text when the editor cannot
  // be converted to Markdown without losing some of it.
  function outlineText(root) {
    const own = (el) => { const c = el.cloneNode(true); c.querySelectorAll("ul, ol").forEach((x) => x.remove()); return c.textContent.replace(/[\u200b\ufeff]/g, "").replace(/\s+/g, " ").trim(); };
    const lines = [];
    for (const el of root.querySelectorAll("li, p, h1, h2, h3, h4, h5, h6, pre, tr, div.md-html")) {
      if (el.tagName === "P" && el.closest("li")) continue;                       // counted with its list item
      if (el.tagName === "LI") {
        let d = 0; for (let a = el.parentElement; a && a !== root; a = a.parentElement) if (a.tagName === "UL" || a.tagName === "OL") d++;
        const t = own(el); if (t) lines.push("  ".repeat(Math.max(0, d - 1)) + "- " + t);
      } else if (el.tagName === "TR") {
        lines.push("| " + [...el.children].map((c) => own(c)).join(" | ") + " |");
      } else if (el.tagName === "PRE") {
        lines.push("```", el.textContent.replace(/\n$/, ""), "```");
      } else if (/^H[1-6]$/.test(el.tagName)) {
        const t = own(el); if (t) lines.push("#".repeat(+el.tagName[1]) + " " + t);
      } else if (el.closest("li, td, th") ) {
        continue;
      } else {
        const t = own(el); if (t) lines.push(t);
      }
    }
    return lines.join("\n");
  }


  /* ------------------------------------------------------------------ *
   * the editor
   * ------------------------------------------------------------------ */
  const BLOCK_SEL = "p,h1,h2,h3,h4,h5,h6,div";

  class MdEditor {
    /**
     * @param {HTMLTextAreaElement} textarea  holds the Markdown; stays in the form
     * @param {object} opts  ui (toast/prompt/form/modal), upload(file) -> Promise<path>,
     *                       pages() -> Promise<[{title,url}]>, onChange()
     */
    constructor(textarea, opts) {
      this.src = textarea;
      this.ui = opts.ui;
      this.upload = opts.upload;
      this.pages = opts.pages;
      this.onChange = opts.onChange || (() => {});
      this.imageAction = opts.imageAction || null;   // (action, src) for the picture selected in the text
      this.selImg = null;
      this.mode = "rich";
      this.text = textarea.value;     // the Markdown the blocks were mapped from
      this.lines = [];
      this.blocks = {};
      this.blockList = [];
      this.timer = null;
      this.blocked = null;            // set when what is on screen cannot be written back without losing text
      this.build();
      this.load(textarea.value);
    }

    /* ---------- layout ---------- */
    build() {
      this.root = h("div", { class: "mde" });
      this.src.before(this.root);
      this.src.classList.add("mde-source");
      this.editor = h("div", { class: "md-editor", contenteditable: "true", spellcheck: "true", role: "textbox", "aria-multiline": "true", "aria-label": "Article text" });
      this.warnEl = h("div", { class: "mde-warn hidden", role: "alert" });
      this.countEl = h("div", { class: "mde-count" });
      this.toolbar = this.buildToolbar();
      this.surface = h("div", { class: "mde-surface" }, [this.editor, this.src]);
      this.root.append(this.toolbar, this.warnEl, this.surface, this.countEl);
      this.bind();
    }

    buildToolbar() {
      const tb = h("div", { class: "mde-toolbar", role: "toolbar", "aria-label": "Formatting" });
      const btn = (ic, title, fn, key) =>
        h("button", { class: "mde-btn", type: "button", title, "aria-label": title, "data-cmd": key || "",
          onmousedown: (e) => e.preventDefault(),
          onclick: () => { if (this.mode === "rich") { this.editor.focus(); fn(); this.touch(); } } }, [icon(ic)]);
      const sep = () => h("span", { class: "mde-sep" });
      this.headingSel = h("select", { class: "mde-select", title: "Paragraph style", "aria-label": "Paragraph style",
        onmousedown: () => this.saveRange(),
        onchange: () => { this.restoreRange(); this.editor.focus(); this.formatBlock(this.headingSel.value); this.touch(); } },
        [["p", "Paragraph"], ["h2", "Heading 2"], ["h3", "Heading 3"], ["h4", "Heading 4"], ["h1", "Heading 1"]]
          .map(([v, l]) => h("option", { value: v }, l)));
      this.imageTools = h("span", { class: "mde-group hidden", "aria-label": "Selected image" }, [
        h("button", { class: "mde-btn txt", type: "button", title: "Replace this image with another file", onmousedown: (e) => e.preventDefault(), onclick: () => this.imageOp("replace") }, [icon("image"), "Replace image"]),
        h("button", { class: "mde-btn txt", type: "button", title: "Make this image lighter without hurting quality", onmousedown: (e) => e.preventDefault(), onclick: () => this.imageOp("optimize") }, "Make lighter"),
      ]);
      this.tableTools = h("span", { class: "mde-group hidden" }, [
        sep(),
        btn("rowAdd", "Add row below", () => this.tableOp("row+")),
        btn("colAdd", "Add column right", () => this.tableOp("col+")),
        h("button", { class: "mde-btn txt", type: "button", title: "Delete row", onmousedown: (e) => e.preventDefault(), onclick: () => { this.tableOp("row-"); this.touch(); } }, "− row"),
        h("button", { class: "mde-btn txt", type: "button", title: "Delete column", onmousedown: (e) => e.preventDefault(), onclick: () => { this.tableOp("col-"); this.touch(); } }, "− column"),
        btn("trash", "Delete table", () => this.tableOp("del")),
      ]);
      this.richTools = [
        btn("undo", "Undo (Ctrl+Z)", () => document.execCommand("undo")),
        btn("redo", "Redo (Ctrl+Shift+Z)", () => document.execCommand("redo")),
        sep(), this.headingSel, sep(),
        btn("bold", "Bold (Ctrl+B)", () => document.execCommand("bold"), "bold"),
        btn("italic", "Italic (Ctrl+I)", () => document.execCommand("italic"), "italic"),
        btn("strike", "Strikethrough", () => document.execCommand("strikeThrough"), "strikeThrough"),
        btn("code", "Inline code (Ctrl+E)", () => this.inlineCode()),
        sep(),
        btn("link", "Link (Ctrl+K)", () => this.linkDialog()),
        btn("page", "Link to a page of this site", () => this.pageLink()),
        h("button", { class: "mde-btn", type: "button", title: "Image", "aria-label": "Image", onmousedown: (e) => { e.preventDefault(); this.saveRange(); }, onclick: () => this.imageDialog() }, [icon("image")]),
        h("button", { class: "mde-btn", type: "button", title: "YouTube video", "aria-label": "YouTube video", onmousedown: (e) => { e.preventDefault(); this.saveRange(); }, onclick: () => this.youtubeDialog() }, [icon("video")]),
        sep(),
        btn("ul", "Bulleted list", () => document.execCommand("insertUnorderedList"), "insertUnorderedList"),
        btn("ol", "Numbered list", () => document.execCommand("insertOrderedList"), "insertOrderedList"),
        btn("quote", "Quote", () => this.toggleQuote()),
        btn("codeblock", "Code block", () => this.codeBlock()),
        btn("table", "Table", () => this.insertTable()),
        btn("hr", "Horizontal rule", () => this.insertHr()),
        this.tableTools,
        this.imageTools,
      ];
      this.richTools.forEach((n) => tb.appendChild(n));
      this.modeSeg = h("div", { class: "seg mde-mode", role: "group", "aria-label": "Editing mode" }, [
        this.richBtn = h("button", { class: "seg-btn active", type: "button", onclick: () => this.setMode("rich") }, "Visual"),
        this.mdBtn = h("button", { class: "seg-btn", type: "button", onclick: () => this.setMode("md") }, "Markdown"),
      ]);
      tb.appendChild(h("span", { class: "mde-spacer" }));
      tb.appendChild(this.modeSeg);
      return tb;
    }

    /* ---------- text in / out ---------- */
    load(markdown) {
      this.text = markdown;
      this.lines = markdown.split("\n");
      this.src.value = markdown;
      this.hideWarning();
      this.applyModeVisibility();
      this.renderRich(markdown);
      this.updateCount();
    }

    renderRich(body) {
      sanitizeInto(this.editor, md().render(body, {}));
      this.blocks = {}; this.blockList = [];
      [...this.editor.children].forEach((c) => {
        const key = c.getAttribute("data-md");
        if (!key) return;
        const [start, end] = key.split(":").map(Number);
        const b = { key, idx: this.blockList.length, start, end };
        this.blocks[key] = b; this.blockList.push(b);
        c.dataset.base = blockEl(c);
      });
      if (!this.editor.children.length) this.editor.innerHTML = "<p><br></p>";
    }

    // The current content as Markdown.
    markdown() {
      if (this.mode === "md") return this.src.value;
      const items = [];
      const seen = new Set();
      let run = [];
      const flushRun = () => {
        if (!run.length) return;
        const s = blocksOf(run);
        run = [];
        if (s) items.push({ idx: null, text: s });
      };
      for (const n of this.editor.childNodes) {
        if (n.nodeType === 1 && BLOCK_TAGS.has(n.tagName)) {
          flushRun();
          const key = n.getAttribute("data-md");
          const meta = key && !seen.has(key) ? this.blocks[key] : null;
          if (key) seen.add(key);
          const cur = blockEl(n);
          if (meta && cur === n.dataset.base) {
            items.push({ idx: meta.idx, text: this.lines.slice(meta.start, meta.end).join("\n"), src: true });
          } else if (cur !== "") {
            items.push({ idx: meta ? meta.idx : null, text: cur });
          }
        } else if (n.nodeType === 3 || n.nodeType === 1) {
          run.push(n);
        }
      }
      flushRun();
      let body;
      if (!this.blockList.length) {
        body = items.length ? items.map((i) => i.text).join("\n\n") + "\n" : this.lines.join("\n");
      } else {
        const first = this.blockList[0], last = this.blockList[this.blockList.length - 1];
        const lead = this.lines.slice(0, first.start);
        const tail = this.lines.slice(last.end);
        body = lead.length ? lead.join("\n") + "\n" : "";
        items.forEach((it, i) => {
          if (i > 0) {
            const prev = items[i - 1];
            if (prev.idx !== null && it.idx !== null && it.idx === prev.idx + 1) {
              const gap = this.lines.slice(this.blockList[prev.idx].end, this.blockList[it.idx].start);
              // Adjacent original blocks: put back the lines that sat between them. A list's source range ends AFTER its
              // trailing blank line, so when that list was edited (re-serialized) the blank line is gone with it.
              if (gap.length) body += "\n" + gap.join("\n") + "\n";
              else if (prev.src && it.src) body += "\n";
              else body += /\n$/.test(prev.text) ? "\n" : "\n\n";
            } else body += "\n\n";
          }
          body += it.text;
        });
        body += tail.length ? "\n" + tail.join("\n") : "";
        if (!items.length) body = lead.join("\n") + (tail.length ? "\n" + tail.join("\n") : "");
      }
      return body;
    }

    // Replaces the whole text (used by the SEO tab to apply a suggestion).
    setMarkdown(markdown) {
      this.load(markdown);
      this.touch(true);
    }

    // Compares what the person sees with what `content` would show once reopened. null = identical; otherwise how much
    // text would be lost. This is the safety net: a serializer bug can never silently eat text.
    verify(content) {
      if (this.mode !== "rich") return null;
      const tmp = document.createElement("div");
      sanitizeInto(tmp, md().render(content, { noMap: true }));
      const a = textSig(this.editor), b = textSig(tmp);
      if (a !== b) {
        let i = 0; while (i < a.length && i < b.length && a[i] === b[i]) i++;
        return { missing: Math.max(0, a.length - b.length), at: a.slice(Math.max(0, i - 15), i + 40) };
      }
      const x = structSig(this.editor), y = structSig(tmp);
      if (x !== y) return { missing: 0, at: `${x} → ${y}`.slice(0, 60) };
      return null;
    }

    // Called before the form is sent. Returns false when saving must wait for a decision.
    commit(force) {
      clearTimeout(this.timer);
      let content;
      try { content = this.markdown(); } catch (e) { this.showWarning({ missing: 0, at: "", error: e.message }); return false; }
      if (!force) {
        const bad = this.verify(content);
        if (bad) { this.showWarning(bad); return false; }
      }
      this.hideWarning();
      this.src.value = content;
      return true;
    }

    showWarning(info) {
      const what = info.missing ? `about ${info.missing} characters` : "some content";
      this.blocked = info;
      this.warnEl.classList.remove("hidden");
      this.warnEl.innerHTML = "";
      this.warnEl.append(
        h("div", {}, `Not saved: the editor can't write this text back to Markdown without losing ${what}` +
          (info.at ? ` (near “${info.at.slice(0, 40)}”)` : "") + ". Everything is still on screen and the file on disk is untouched."),
        h("div", { class: "btn-row" }, [
          h("button", { class: "btn small", type: "button", onclick: () => this.setMode("md") }, "Edit as Markdown instead"),
          h("button", { class: "btn small danger", type: "button", onclick: () => { if (this.commit(true)) this.src.form.requestSubmit(); } }, "Save anyway"),
        ]));
    }
    hideWarning() { this.blocked = null; this.warnEl.classList.add("hidden"); this.warnEl.innerHTML = ""; }

    touch(now) {
      this.updateCount();
      clearTimeout(this.timer);
      const run = () => {
        if (this.mode === "rich") { try { this.src.value = this.markdown(); } catch (e) { /* kept as is until the next edit */ } }
        this.onChange();
      };
      if (now) run(); else this.timer = setTimeout(run, 200);
      this.updateToolbarState();
    }

    updateCount() {
      const text = this.mode === "rich" ? (this.editor.innerText || "") : this.src.value;
      const words = (text.match(/[\p{L}\p{N}][\p{L}\p{N}'’-]*/gu) || []).length;
      this.countEl.textContent = `${words.toLocaleString("en-GB")} words`;
    }

    /* ---------- mode ---------- */
    applyModeVisibility() {
      const rich = this.mode === "rich";
      this.editor.classList.toggle("hidden", !rich);
      this.src.classList.toggle("hidden", rich);
      this.toolbar.classList.toggle("disabled", !rich);
      this.richBtn.classList.toggle("active", rich);
      this.mdBtn.classList.toggle("active", !rich);
      this.root.classList.toggle("is-markdown", !rich);
    }

    async setMode(mode) {
      if (mode === this.mode) return;
      const content = this.markdown();                      // from the mode we are leaving
      if (mode === "md") {
        const bad = this.verify(content);
        if (bad && !(await this.ui.confirm({ title: "Some text would be lost", confirmLabel: "Switch anyway", danger: true,
          message: `The Markdown view cannot show about ${bad.missing || "some"} characters of this text (near “${bad.at.slice(0, 40)}”). Switch anyway?` }))) return;
        this.mode = "md";
        this.src.value = content;
        this.applyModeVisibility();
        this.hideWarning();
        this.src.focus();
      } else {
        this.mode = "rich";
        this.load(content);
        this.touch(true);
      }
    }

    /* ---------- editor commands ---------- */
    saveRange() { const s = getSelection(); this._range = s.rangeCount ? s.getRangeAt(0).cloneRange() : null; }
    restoreRange() {
      if (!this._range) return;
      const s = getSelection(); s.removeAllRanges(); s.addRange(this._range);
    }
    inEditor(node) { return node && this.editor.contains(node); }
    closest(sel) {
      const s = getSelection();
      if (!s.rangeCount) return null;
      let n = s.anchorNode;
      if (n && n.nodeType === 3) n = n.parentNode;
      if (!this.inEditor(n)) return null;
      return n.closest(sel);
    }

    formatBlock(tag) {
      const inPre = this.closest("pre");
      if (inPre && tag !== "pre") {
        const text = inPre.textContent.replace(/\n$/, "");
        const p = document.createElement(tag === "p" ? "p" : tag);
        p.textContent = text || "";
        if (!text) p.innerHTML = "<br>";
        inPre.replaceWith(p);
        const r = document.createRange(); r.selectNodeContents(p); r.collapse(false);
        const s = getSelection(); s.removeAllRanges(); s.addRange(r);
        return;
      }
      document.execCommand("formatBlock", false, tag);
    }

    inlineCode() {
      const code = this.closest("code");
      if (code && !code.closest("pre")) {
        code.replaceWith(document.createTextNode(code.textContent));
        return;
      }
      const text = getSelection().toString() || "code";
      document.execCommand("insertHTML", false, `<code>${escHtml(text)}</code>&#8203;`);
    }

    toggleQuote() {
      if (this.closest("blockquote")) document.execCommand("outdent");
      else document.execCommand("formatBlock", false, "blockquote");
    }

    codeBlock() {
      const pre = this.closest("pre");
      if (pre) { this.formatBlock("p"); return; }
      const sel = getSelection();
      let text = sel.toString();
      if (!text) {
        const b = this.closest(BLOCK_SEL);
        text = b && b !== this.editor ? b.textContent : "";
        if (b && b !== this.editor) { const r = document.createRange(); r.selectNodeContents(b); sel.removeAllRanges(); sel.addRange(r); }
      }
      document.execCommand("insertHTML", false, `<pre><code>${escHtml(text || "")}${text ? "" : "<br>"}</code></pre><p><br></p>`);
    }

    insertHr() { document.execCommand("insertHTML", false, "<hr><p><br></p>"); }

    insertTable() {
      const row = (tag) => `<tr>${[1, 2, 3].map(() => `<${tag}><br></${tag}>`).join("")}</tr>`;
      document.execCommand("insertHTML", false, `<table><thead>${row("th")}</thead><tbody>${row("td")}${row("td")}</tbody></table><p><br></p>`);
      const fresh = [...this.editor.querySelectorAll("table")].find((x) => !x.hasAttribute("data-md"));
      const c = fresh && fresh.querySelector("th");
      if (c) this.focusCell(c);
    }

    tableOp(op) {
      const cell = this.closest("td,th");
      const table = this.closest("table");
      if (!cell || !table) return;
      const row = cell.parentElement;
      const col = [...row.children].indexOf(cell);
      const mk = (tag) => { const c = document.createElement(tag); c.innerHTML = "<br>"; return c; };
      if (op === "row+") {
        const nr = document.createElement("tr");
        [...row.children].forEach(() => nr.appendChild(mk("td")));
        if (row.parentElement.tagName === "THEAD") {
          const body = table.tBodies[0] || table.appendChild(document.createElement("tbody"));
          body.insertBefore(nr, body.firstChild);
        } else row.after(nr);
      } else if (op === "col+") {
        table.querySelectorAll("tr").forEach((r) => {
          const ref = r.children[col];
          const c = mk(r.parentElement.tagName === "THEAD" || (ref && ref.tagName === "TH") ? "th" : "td");
          if (ref) ref.after(c); else r.appendChild(c);
        });
      } else if (op === "row-") {
        if (table.querySelectorAll("tr").length <= 1) { table.remove(); return; }
        if (row.parentElement.tagName === "THEAD") {
          const nx = table.tBodies[0] && table.tBodies[0].rows[0];
          if (nx) { [...nx.children].forEach((c) => { const th = mk("th"); th.innerHTML = c.innerHTML; c.replaceWith(th); }); row.parentElement.appendChild(nx); }
        }
        row.remove();
      } else if (op === "col-") {
        if (row.children.length <= 1) { table.remove(); return; }
        table.querySelectorAll("tr").forEach((r) => r.children[col] && r.children[col].remove());
      } else if (op === "del") { table.remove(); }
      if (!this.editor.lastElementChild || this.editor.lastElementChild.tagName === "TABLE") {
        this.editor.appendChild(Object.assign(document.createElement("p"), { innerHTML: "<br>" }));
      }
    }

    async linkDialog() {
      this.saveRange();
      const a = this.closest("a");
      const cur = a ? a.getAttribute("href") : "";
      const url = await this.ui.prompt({ title: a ? "Edit link" : "Insert link", label: "Address", message: "Leave empty to remove the link.", value: cur || "https://", confirmLabel: "OK" });
      if (url === null) return;
      this.editor.focus(); this.restoreRange();
      const v = url.trim();
      if (!v || v === "https://") { if (a) document.execCommand("unlink"); this.touch(); return; }
      if (getSelection().isCollapsed && !a) document.execCommand("insertHTML", false, `<a href="${escHtml(v)}">${escHtml(v)}</a>`);
      else if (a) a.setAttribute("href", v);
      else document.execCommand("createLink", false, v);
      this.touch();
    }

    // Link to another page or article of the site (a path such as /my-article/).
    async pageLink() {
      this.saveRange();
      let pages = [];
      try { pages = await this.pages(); } catch (e) { this.ui.toast("Could not list the pages: " + e.message); return; }
      const picked = await this.ui.choose({ title: "Link to a page", placeholder: "Find a page or article…",
        items: pages.map((p) => ({ label: p.title, hint: p.url, value: p })) });
      if (!picked) return;
      this.editor.focus(); this.restoreRange();
      if (getSelection().isCollapsed) document.execCommand("insertHTML", false, `<a href="${escHtml(picked.url)}">${escHtml(picked.title)}</a>&nbsp;`);
      else document.execCommand("createLink", false, picked.url);
      this.touch();
    }

    /* ---------- images and video ---------- */
    async imageDialog() {
      const input = h("input", { type: "file", accept: "image/png,image/jpeg,image/gif,image/webp", class: "hidden" });
      document.body.appendChild(input);
      const file = await new Promise((resolve) => {
        input.addEventListener("change", () => resolve(input.files[0] || null));
        input.addEventListener("cancel", () => resolve(null));
        input.click();
      });
      input.remove();
      if (file) await this.insertImageFile(file);
    }

    async insertImageFile(file) {
      let path;
      try { path = await this.upload(file); } catch (e) { this.ui.toast(e.message); return; }
      const base = (file.name || "").replace(/\.[^.]+$/, "").replace(/[-_]+/g, " ");
      const values = await this.ui.form({ title: "Insert image", confirmLabel: "Insert", fields: [
        { name: "alt", label: "Alt text", value: "", help: "Describes the image for screen readers and search engines. Leave empty to add it later from the SEO tab.", placeholder: base },
        { name: "caption", label: "Caption (optional)", value: "" },
      ] });
      this.editor.focus(); this.restoreRange();
      if (!values) { return; }
      this.insertImage(path, values.alt.trim(), values.caption.trim());
    }

    insertImage(src, alt, caption) {
      const img = `<img src="${escHtml(displaySrc(src))}" data-src="${escHtml(src)}" alt="${escHtml(alt || "")}">`;
      if (!caption) {                            // a picture on its own line, after the paragraph being written
        const p = document.createElement("p"); p.innerHTML = img;
        this.insertBlocks([p]);
        this.touch();
        return;
      }
      const open = this.rawBlock('<figure markdown="1">');
      const p = document.createElement("p"); p.innerHTML = img;
      const close = this.rawBlock(`<figcaption>${caption.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</figcaption>\n</figure>`);
      this.insertBlocks([open, p, close]);
      this.touch();
    }

    async youtubeDialog() {
      const answer = await this.ui.prompt({ title: "Insert YouTube video", label: "YouTube link or video ID", value: "", confirmLabel: "Insert" });
      if (!answer) return;
      const m = answer.trim().match(/(?:v=|youtu\.be\/|embed\/|shorts\/)([A-Za-z0-9_-]{11})|^([A-Za-z0-9_-]{11})$/);
      const id = m && (m[1] || m[2]);
      if (!id) { this.ui.toast("That does not look like a YouTube link."); return; }
      this.editor.focus(); this.restoreRange();
      this.insertBlocks([this.rawBlock(`<aside>\n{% assign id = "${id}" %}\n{% include youtube.html id=id %}\n</aside>`)]);
      this.touch();
    }

    // A locked raw-HTML/Liquid block, written back exactly as given.
    rawBlock(raw) {
      const tpl = document.createElement("template");
      tpl.innerHTML = rawBlockHtml(raw, "");
      return tpl.content.firstElementChild;
    }

    insertBlocks(nodes) {
      const sel = getSelection();
      let ref = null;
      if (sel.rangeCount && this.inEditor(sel.anchorNode)) {
        ref = sel.anchorNode.nodeType === 3 ? sel.anchorNode.parentNode : sel.anchorNode;
        while (ref && ref.parentNode !== this.editor) ref = ref.parentNode;
      }
      const empty = ref && ref.tagName === "P" && !ref.querySelector("img") && !ref.textContent.replace(/[​\s]/g, "");
      let anchor = ref && ref !== this.editor ? ref : this.editor.lastElementChild;
      for (const n of nodes) {
        if (anchor) anchor.after(n); else this.editor.appendChild(n);
        anchor = n;
      }
      if (empty && ref.parentNode) ref.remove();
      const last = this.editor.lastElementChild;
      if (!last || last.tagName !== "P") {
        const p = document.createElement("p"); p.innerHTML = "<br>";
        this.editor.appendChild(p);
      }
      const tail = this.editor.lastElementChild;
      const r = document.createRange(); r.setStart(tail, 0); r.collapse(true);
      sel.removeAllRanges(); sel.addRange(r);
    }

    /* ---------- events ---------- */
    bind() {
      const ed = this.editor;
      try { document.execCommand("defaultParagraphSeparator", false, "p"); document.execCommand("styleWithCSS", false, false); } catch (e) { /* not supported */ }
      ed.addEventListener("input", (e) => { this.normalizeRoot(); this.autoFormat(e); this.autoLink(e); this.touch(); });
      ed.addEventListener("click", (e) => this.onClick(e));
      ed.addEventListener("keydown", (e) => this.onKey(e));
      ed.addEventListener("paste", (e) => this.onPaste(e));
      ed.addEventListener("copy", (e) => this.onCopy(e, false));
      ed.addEventListener("cut", (e) => this.onCopy(e, true));
      ed.addEventListener("drop", (e) => this.onDrop(e));
      this.src.addEventListener("input", () => { this.updateCount(); this.onChange(); });
      this.src.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") { e.preventDefault(); this.src.form.requestSubmit(); }
        if (e.key === "Tab") { e.preventDefault(); const s = this.src; s.setRangeText("  ", s.selectionStart, s.selectionEnd, "end"); this.onChange(); }
      });
      document.addEventListener("selectionchange", () => { if (this.mode === "rich" && this.root.isConnected) this.updateToolbarState(); });
      const form = this.src.form;
      if (form) {
        form.addEventListener("submit", (e) => { if (!this.commit(false)) e.preventDefault(); });
      }
    }

    updateToolbarState() {
      if (this.mode !== "rich") return;
      const s = getSelection();
      const inside = s.rangeCount && this.inEditor(s.anchorNode);
      this.tableTools.classList.toggle("hidden", !(inside && this.closest("table")));
      if (!inside) return;
      const blk = this.closest("h1,h2,h3,h4,h5,h6");
      this.headingSel.value = blk ? blk.tagName.toLowerCase() : "p";
      this.toolbar.querySelectorAll("[data-cmd]").forEach((b) => {
        const c = b.getAttribute("data-cmd");
        if (!c) return;
        let on = false; try { on = document.queryCommandState(c); } catch (e) { /* ignore */ }
        b.classList.toggle("on", !!on);
      });
    }

    selectImage(img) {
      if (this.selImg && this.selImg !== img) this.selImg.classList.remove("selected");
      this.selImg = img;
      if (img) img.classList.add("selected");
      this.imageTools.classList.toggle("hidden", !img || !this.imageAction);
    }

    async imageOp(action) {
      const img = this.selImg;
      const src = img && img.getAttribute("data-src");
      if (!src || !this.imageAction) return;
      await this.imageAction(action, src);
      this.selectImage(null);
    }

    onClick(e) {
      const pic = e.target.closest && e.target.closest("img");
      this.selectImage(pic && this.editor.contains(pic) && !pic.closest(".md-html") && /^\/images\//.test(pic.getAttribute("data-src") || "") ? pic : null);
      const a = e.target.closest && e.target.closest("a");
      if (!a || !this.editor.contains(a)) return;
      // a plain click opens an outside link (Alt+click puts the caret inside it instead)
      const sel = getSelection();
      if (!e.altKey && (e.ctrlKey || e.metaKey || !sel || sel.isCollapsed)) {
        e.preventDefault();
        const href = a.getAttribute("href") || "";
        if (/^https?:/i.test(href)) window.open(href, "_blank", "noopener");
        else if (href) this.ui.toast(`Link to ${href} on this site`);
      }
    }

    onKey(e) {
      const mod = e.ctrlKey || e.metaKey;
      if (mod && e.key.toLowerCase() === "s") { e.preventDefault(); this.src.form.requestSubmit(); return; }
      if (mod && e.key.toLowerCase() === "k") { e.preventDefault(); this.linkDialog(); return; }
      if (mod && e.shiftKey && e.key.toLowerCase() === "x") { e.preventDefault(); document.execCommand("strikeThrough"); this.touch(); return; }
      if (mod && e.key.toLowerCase() === "e") { e.preventDefault(); this.inlineCode(); this.touch(); return; }
      const li = this.closest("li");
      if (e.key === "Tab") {
        e.preventDefault();
        if (li) { document.execCommand(e.shiftKey ? "outdent" : "indent"); this.touch(); }
        else if (this.closest("pre")) document.execCommand("insertText", false, "  ");
        else if (this.closest("td,th")) this.moveCell(e.shiftKey ? -1 : 1);
        return;
      }
      if (e.key === "Enter" && !e.shiftKey && !mod) {
        const qp = this.closest("blockquote p, blockquote div");
        if (qp && !qp.textContent.replace(/​/g, "").trim()) {
          e.preventDefault();
          document.execCommand("outdent");
          this.touch(); return;
        }
        const pre = this.closest("pre");
        if (pre) {
          // Enter on an empty last line leaves the code block
          const t = pre.textContent;
          const s = getSelection();
          const r = s.getRangeAt(0);
          const x = document.createRange(); x.selectNodeContents(pre); x.setStart(r.endContainer, r.endOffset);
          const atEnd = x.toString().replace(/\n$/, "") === "";
          if (atEnd && /\n$/.test(t.replace(/​/g, ""))) {
            e.preventDefault();
            const code = pre.querySelector("code") || pre;
            code.textContent = t.replace(/\n+$/, "");
            if (!code.textContent) code.appendChild(document.createElement("br"));
            const p = document.createElement("p"); p.innerHTML = "<br>";
            pre.after(p);
            const nr = document.createRange(); nr.setStart(p, 0); nr.collapse(true); s.removeAllRanges(); s.addRange(nr);
            this.touch();
          } else { e.preventDefault(); this.newlineInPre(pre); this.touch(); }
          return;
        }
        const blk = this.closest("p,div");
        if (blk && blk !== this.editor && !this.closest("li,td,th,blockquote")) {
          const txt = blk.textContent.replace(/​/g, "").trim();
          if (/^```[\w+#.-]*$/.test(txt)) {                 // ``` + Enter starts a code block
            e.preventDefault();
            const lang = txt.slice(3);
            blk.outerHTML = `<pre><code${lang ? ` class="language-${escHtml(lang)}"` : ""}><br></code></pre>`;
            const target = [...this.editor.querySelectorAll("pre")].find((x) => !x.hasAttribute("data-md") && x.textContent === "");
            if (target) { const nr = document.createRange(); nr.selectNodeContents(target.querySelector("code")); nr.collapse(true); const s = getSelection(); s.removeAllRanges(); s.addRange(nr); }
            this.touch(); return;
          }
          if (/^(---|\*\*\*|___)$/.test(txt)) {             // --- + Enter inserts a rule
            e.preventDefault();
            blk.outerHTML = "<hr><p><br></p>";
            const hr = [...this.editor.querySelectorAll("hr")].find((x) => !x.hasAttribute("data-md"));
            const p = hr && hr.nextElementSibling;
            if (p) { const nr = document.createRange(); nr.setStart(p, 0); nr.collapse(true); const s = getSelection(); s.removeAllRanges(); s.addRange(nr); }
            this.touch(); return;
          }
        }
      }
    }

    // Wraps loose text/inline nodes sitting directly in the editor into <p>, keeping the caret.
    normalizeRoot() {
      const ed = this.editor;
      const loose = [...ed.childNodes].some((n) => (n.nodeType === 3 && n.nodeValue.trim()) || (n.nodeType === 1 && !BLOCK_TAGS.has(n.tagName) && n.tagName !== "BR"));
      const brRoot = [...ed.childNodes].some((n) => n.nodeType === 1 && n.tagName === "BR");
      if (!loose && !brRoot) return;
      const sel = getSelection();
      const keep = sel.rangeCount && this.inEditor(sel.anchorNode) ? { n: sel.anchorNode, o: sel.anchorOffset } : null;
      let run = [];
      const flush = (before) => {
        if (!run.length) return;
        const p = document.createElement("p");
        ed.insertBefore(p, before);
        run.forEach((x) => p.appendChild(x));
        run = [];
      };
      for (const n of [...ed.childNodes]) {
        const isBlock = n.nodeType === 1 && BLOCK_TAGS.has(n.tagName);
        if (isBlock) { flush(n); continue; }
        if (n.nodeType === 3 && !n.nodeValue.trim() && !run.length) continue;
        run.push(n);
      }
      flush(null);
      if (keep) {
        try { const r = document.createRange(); r.setStart(keep.n, keep.o); r.collapse(true); sel.removeAllRanges(); sel.addRange(r); } catch (e) { /* caret stays */ }
      }
    }

    newlineInPre(pre) {
      const s = getSelection();
      const r = s.getRangeAt(0);
      r.deleteContents();
      const nl = document.createTextNode("\n");
      r.insertNode(nl);
      const code = pre.querySelector("code") || pre;
      if (!code.lastChild || code.lastChild.nodeName !== "BR") code.appendChild(document.createElement("br"));
      r.setStartAfter(nl); r.collapse(true);
      s.removeAllRanges(); s.addRange(r);
    }

    moveCell(dir) {
      const cell = this.closest("td,th"); if (!cell) return;
      const cells = [...cell.closest("table").querySelectorAll("th,td")];
      const i = cells.indexOf(cell) + dir;
      if (i >= cells.length) { this.tableOp("row+"); const next = [...cell.closest("table").querySelectorAll("th,td")]; if (next[cells.length]) this.focusCell(next[cells.length]); return; }
      if (i >= 0) this.focusCell(cells[i]);
    }
    focusCell(c) { const r = document.createRange(); r.selectNodeContents(c); r.collapse(true); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }

    // "## " -> heading, "- " -> list, "1. " -> numbered, "> " -> quote
    autoFormat(e) {
      if (!e || e.inputType !== "insertText" || !(e.data === " " || e.data === " ")) return;
      const blk = this.closest("p,div");
      if (!blk || blk === this.editor || blk.closest("pre,li,td,th")) return;
      const txt = blk.textContent.replace(/ /g, " ").replace(/​/g, "");
      let m, act = null;
      const caretIn = (node) => { const r = document.createRange(); r.setStart(node, 0); r.collapse(true); const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r); };
      const makeList = (tag, start) => {
        const list = document.createElement(tag);
        if (start && start !== 1) list.setAttribute("start", String(start));
        const li = document.createElement("li");
        li.appendChild(document.createElement("br"));
        list.appendChild(li);
        blk.replaceWith(list);
        const r = document.createRange(); r.setStart(li, 0); r.collapse(true);
        const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
      };
      if ((m = /^(#{1,6}) $/.exec(txt))) act = () => { blk.innerHTML = "<br>"; caretIn(blk); this.formatBlock("h" + m[1].length); };
      else if (/^[-*+] $/.test(txt)) act = () => makeList("ul");
      else if ((m = /^(\d+)[.)] $/.exec(txt))) act = () => makeList("ol", parseInt(m[1], 10));
      else if (/^> $/.test(txt)) act = () => {
        const q = document.createElement("blockquote"); const p = document.createElement("p"); p.innerHTML = "<br>"; q.appendChild(p);
        blk.replaceWith(q); caretIn(p);
      };
      if (act) act();
    }

    // --- bare https:// addresses become real links as soon as they are typed or pasted ---
    autoLink(e) {
      if (this.mode !== "rich" || !e) return;
      const t = e.inputType;
      if (t === "insertText" && e.data && /^\s$/.test(e.data)) {
        // a space typed right after a link that was still "open" ends it: move the space out of the link
        const s = getSelection();
        const n = s && s.anchorNode;
        const a = n && n.parentElement && n.parentElement.closest("a");
        if (a && this.editor.contains(a) && n.nodeType === 3 && /\s$/.test(n.textContent) && a.lastChild === n) {
          const sp = n.textContent.match(/\s+$/)[0];
          n.textContent = n.textContent.slice(0, -sp.length);
          const after = document.createTextNode(sp);
          a.after(after);
          const r = document.createRange(); r.setStart(after, sp.length); r.collapse(true); s.removeAllRanges(); s.addRange(r);
        }
        this.autoLinkNear(false);
      } else if (t === "insertParagraph" || t === "insertLineBreak") {
        this.autoLinkNear(false, true);
      }
    }

    autoLinkNear(whole, previous) {
      const s = getSelection();
      if (!s || !s.rangeCount || !this.inEditor(s.anchorNode)) return;
      let top = s.anchorNode.nodeType === 3 ? s.anchorNode.parentNode : s.anchorNode;
      while (top && top.parentNode !== this.editor) top = top.parentNode;
      if (!top) return;
      const blocks = new Set([top]);
      if (previous && top.previousElementSibling) blocks.add(top.previousElementSibling);
      if (whole) for (let b = top.previousElementSibling, i = 0; b && i < 30; b = b.previousElementSibling, i++) blocks.add(b);
      for (const b of blocks) if (b.matches && !b.matches("pre, .md-html")) this.linkifyNode(b);
    }

    linkifyNode(root) {
      const rej = "a, pre, code, .md-html, [contenteditable=false]";
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
        acceptNode: (n) => (n.parentElement && !n.parentElement.closest(rej) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT),
      });
      const nodes = []; for (let n = walker.nextNode(); n; n = walker.nextNode()) nodes.push(n);
      const sel = getSelection();
      let cn = sel && sel.rangeCount ? sel.anchorNode : null, co = sel && sel.rangeCount ? sel.anchorOffset : 0;
      let moved = false;
      for (const node of nodes) {
        const text = node.textContent;
        const found = [];
        const re = /\bhttps?:\/\/[^\s<>"']+/gi;
        let m;
        while ((m = re.exec(text))) {
          const url = m[0].replace(/[.,;:!?)\]]+$/, "");
          if (url.length > 8) found.push([m.index, m.index + url.length, url]);
        }
        for (let k = found.length - 1; k >= 0; k--) {
          const [st, en, url] = found[k];
          const tail = node.splitText(en);
          const mid = node.splitText(st);
          if (cn === node && co > en) { cn = tail; co -= en; moved = true; }
          const a = document.createElement("a");
          a.setAttribute("href", url);
          a.textContent = url;
          mid.replaceWith(a);
          if (cn === node && co > st) { cn = a.firstChild; co = Math.min(co - st, url.length); moved = true; }
        }
      }
      if (moved && cn) {
        const r = document.createRange();
        try { r.setStart(cn, co); r.collapse(true); sel.removeAllRanges(); sel.addRange(r); } catch (e) { /* caret stays */ }
      }
    }

    // Copy / cut: besides the plain text, the clipboard gets the selection as clean HTML so that pasting it back keeps the formatting.
    onCopy(e, cut) {
      const sel = getSelection();
      if (!e.clipboardData || !sel || sel.isCollapsed || !sel.rangeCount) return;
      for (let i = 0; i < sel.rangeCount; i++) if (!this.editor.contains(sel.getRangeAt(i).commonAncestorContainer)) return;
      if (this.closest("pre")) return;
      const wrap = document.createElement("div");
      for (let i = 0; i < sel.rangeCount; i++) wrap.appendChild(sel.getRangeAt(i).cloneContents());
      this.cleanClip(wrap);
      if (!wrap.textContent && !wrap.querySelector("img, hr")) return;
      e.clipboardData.setData("text/html", `<div data-mde-copy="1">${wrap.innerHTML}</div>`);
      e.clipboardData.setData("text/plain", sel.toString());
      e.preventDefault();
      if (cut) { document.execCommand("delete"); this.touch(); }
    }

    // A pasted copy is a new block, not the original one: drop the links to the source lines.
    cleanClip(root) {
      root.querySelectorAll("[data-md], [data-base]").forEach((n) => { n.removeAttribute("data-md"); n.removeAttribute("data-base"); });
    }

    async onPaste(e) {
      const cd = e.clipboardData;
      if (!cd) return;
      const files = [...(cd.files || [])].filter((f) => f.type.startsWith("image/"));
      if (files.length) { e.preventDefault(); this.saveRange(); for (const f of files) await this.insertImageFile(f); return; }
      const clip = cd.getData("text/html");
      if (clip && clip.includes("data-mde-copy") && !this.closest("pre")) {
        const tmp = document.createElement("div");
        sanitizeInto(tmp, clip);
        const root = tmp.querySelector("[data-mde-copy]");
        if (root) {
          e.preventDefault();
          const out = document.createElement("div");
          sanitizeInto(out, root.innerHTML);
          this.cleanClip(out);
          document.execCommand("insertHTML", false, out.innerHTML);
          this.autoLinkNear(true);
          this.touch();
          return;
        }
      }
      const text = cd.getData("text/plain");
      if (!text) return;
      e.preventDefault();
      const looksMd = /\n\s*\n|^\s*(#{1,6}\s|[-*+]\s|\d+[.)]\s|>\s|```|\|.*\|)/m.test(text) || /\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\)/.test(text);
      if (this.closest("pre") || !looksMd) {
        const inPre = !!this.closest("pre");
        document.execCommand("insertText", false, text);
        if (!inPre) { this.autoLinkNear(true); this.touch(); }
        return;
      }
      const tmp = document.createElement("div");
      sanitizeInto(tmp, md().render(text, { noMap: true }));
      document.execCommand("insertHTML", false, tmp.innerHTML);
      this.touch();
    }

    async onDrop(e) {
      const files = [...((e.dataTransfer && e.dataTransfer.files) || [])].filter((f) => f.type.startsWith("image/"));
      if (!files.length) return;
      e.preventDefault();
      this.saveRange();
      for (const f of files) await this.insertImageFile(f);
    }
  }

  window.MdEditor = MdEditor;
  // exposed for the tests
  window.MdEditor._internals = { md, blockEl, blocksOf, sanitizeInto, structSig, textSig, outlineText, displaySrc };
})();
