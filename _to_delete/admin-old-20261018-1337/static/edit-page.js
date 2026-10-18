"use strict";
/* The article / page editor: Write and SEO tabs, the visual editor, uploads and the SEO suggestions. */
(function () {
  const form = document.querySelector("form.edit");
  if (!form) return;
  const $ = (sel, root) => (root || form).querySelector(sel);
  const csrf = () => form.elements.csrf_token.value;
  const kind = form.dataset.kind;

  const h = (tag, attrs, children) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (k === "class") n.className = v;
      else if (k.startsWith("on") && typeof v === "function") n.addEventListener(k.slice(2), v);
      else if (v !== false && v !== null && v !== undefined) n.setAttribute(k, v);
    }
    for (const c of [].concat(children || [])) if (c !== null && c !== undefined) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    return n;
  };

  async function postJson(url, data) {
    const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf() }, body: JSON.stringify(data) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || `Request failed (${response.status}).`);
    return result;
  }

  async function upload(file) {
    const slug = form.elements.slug.value.trim();
    if (!slug) throw new Error("Fill in the web address first, then add the image.");
    const data = new FormData();
    data.append("file", file);
    data.append("kind", kind);
    data.append("slug", slug);
    const response = await fetch("/upload", { method: "POST", body: data, headers: { "X-CSRF-Token": csrf() } });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.error || "Upload failed.");
    return result.path;
  }

  let pagesCache = null;
  async function pages() {
    if (!pagesCache) {
      const response = await fetch("/api/pages");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      pagesCache = (await response.json()).pages;
    }
    return pagesCache;
  }

  /* ---------- unsaved changes ---------- */
  const state = $("[data-save-state]");
  let dirty = false, submitting = false;
  const markDirty = () => { if (!dirty) { dirty = true; state.textContent = "Unsaved changes"; } };
  form.addEventListener("input", markDirty);
  form.addEventListener("submit", () => { submitting = true; });
  window.addEventListener("beforeunload", (e) => { if (dirty && !submitting) { e.preventDefault(); e.returnValue = ""; } });

  /* ---------- editor ---------- */
  const editor = new window.MdEditor(form.elements.body, { ui: window.ui, upload, pages, onChange: markDirty,
    imageAction: (action, src) => (action === "replace" ? replaceImage(src) : convertImage(src)) });

  /* ---------- tabs ---------- */
  const tabs = [...form.querySelectorAll("[data-tab]")];
  function showTab(name) {
    tabs.forEach((t) => { const on = t.dataset.tab === name; t.classList.toggle("active", on); t.setAttribute("aria-selected", on ? "true" : "false"); });
    $("#panel-write").classList.toggle("hidden", name !== "write");
    $("#panel-seo").classList.toggle("hidden", name !== "seo");
  }
  tabs.forEach((t) => t.addEventListener("click", () => showTab(t.dataset.tab)));

  /* ---------- details column ---------- */
  const desc = form.elements.description;
  const descCount = $("[data-desc-count]");
  const updateDescCount = () => { descCount.textContent = desc.value.length ? `${desc.value.length} characters — search results show about 70 to 160.` : ""; };
  desc.addEventListener("input", updateDescCount);
  updateDescCount();

  const image = form.elements.image;
  const featured = $("[data-featured-preview]");
  function showFeatured() {
    if (!image || !featured) return;
    const v = image.value.trim();
    featured.classList.toggle("hidden", !v);
    if (v) featured.src = /^\/(?!\/)/.test(v) ? `/media?path=${encodeURIComponent(v)}` : v;
  }
  if (image) { image.addEventListener("input", showFeatured); showFeatured(); }
  const picker = $("#file-picker");
  const featuredButton = $('[data-action="featured-image"]');
  if (featuredButton) {
    featuredButton.addEventListener("click", () => {
      picker.value = "";
      picker.onchange = async () => {
        if (!picker.files.length) return;
        try { image.value = await upload(picker.files[0]); showFeatured(); markDirty(); } catch (e) { window.ui.toast(e.message); }
      };
      picker.click();
    });
  }

  /* ---------- SEO tab ---------- */
  const seoRun = $("[data-seo-run]");
  const seoBox = $("[data-seo-results]");
  const seoCount = $("[data-seo-count]");
  const dismissed = new Set();                 // link suggestions put aside during this visit
  let busy = false;

  const payload = () => ({
    kind, slug: form.elements.slug.value.trim(), title: form.elements.title.value,
    description: form.elements.description.value, image: image ? image.value : "", body: editor.markdown(),
    seo_title: form.elements.seo_title.value, focus_keyword: form.elements.focus_keyword.value,
  });
  const seoTitle = form.elements.seo_title, seoTitleCount = $("[data-seo-title-count]");
  const updateSeoTitle = () => { seoTitleCount.textContent = seoTitle.value.trim() ? `${seoTitle.value.trim().length} characters — about 25 to 65 display fully.` : ""; };
  seoTitle.addEventListener("input", updateSeoTitle); updateSeoTitle();

  async function analyze() {
    if (busy) return;
    busy = true; seoRun.disabled = true;
    try {
      render(await postJson("/seo/analyze", payload()));
      seoRun.lastChild.textContent = " Refresh suggestions";
    } catch (e) { window.ui.toast(e.message); } finally { busy = false; seoRun.disabled = false; }
  }
  seoRun.addEventListener("click", analyze);

  async function apply(change) {
    try {
      const result = await postJson("/seo/apply", { ...change, body: editor.markdown() });
      editor.setMarkdown(result.body);
      return true;
    } catch (e) { window.ui.toast(e.message); return false; }
  }

  /* ---------- swapping and converting images ---------- */
  const swapped = [];                                   // [old, new] pairs: old files are tidied away after saving
  const featuredNow = () => (image ? image.value.trim() : "");

  async function swapImage(oldSrc, newSrc) {
    if (editor.markdown().includes(oldSrc)) {
      const result = await postJson("/seo/apply", { op: "src", old: oldSrc, new: newSrc, body: editor.markdown() });
      editor.setMarkdown(result.body);
    }
    if (image && featuredNow() === oldSrc) { image.value = newSrc; showFeatured(); }
    swapped.push([oldSrc, newSrc]);
    form.elements.swapped.value = JSON.stringify(swapped);
    markDirty();
  }

  // Makes the image lighter (same picture, no visible loss) and uses the new file everywhere in this text.
  async function convertImage(src, quiet) {
    try {
      const result = await postJson("/images/optimize", { src, featured: featuredNow() === src });
      if (!result.changed) { if (!quiet) window.ui.toast(result.reason); return false; }
      await swapImage(src, result.src);
      const saved = Math.round(100 * (1 - result.new_kb / result.old_kb));
      const note = `${result.old_kb} KB → ${result.new_kb} KB (${saved} % lighter, ${result.format}${result.resized ? `, scaled to ${result.width} px wide` : ""}). Save to keep it.`;
      if (!quiet) window.ui.toast(note);
      return true;
    } catch (e) { window.ui.toast(e.message); return false; }
  }

  // Replaces an image by another file picked on this computer, everywhere it is used in this text.
  function replaceImage(src) {
    return new Promise((resolve) => {
      const picker = h("input", { type: "file", accept: "image/png,image/jpeg,image/gif,image/webp", class: "hidden" });
      document.body.appendChild(picker);
      picker.addEventListener("change", async () => {
        try {
          if (picker.files.length) {
            const path = await upload(picker.files[0]);
            await swapImage(src, path);
            window.ui.toast("Image replaced. Save to keep it.");
          }
        } catch (e) { window.ui.toast(e.message); }
        picker.remove(); resolve();
      });
      picker.addEventListener("cancel", () => { picker.remove(); resolve(); });
      picker.click();
    });
  }

  function row(children, cls) { return h("div", { class: "seo-row" + (cls ? " " + cls : "") }, children); }
  function status(kind, text) { return h("span", { class: "status " + kind }, text); }

  function render(data) {
    seoBox.classList.remove("hidden");
    // --- meta tags
    const meta = $("[data-seo-meta]"); meta.innerHTML = "";
    let todo = 0;
    for (const m of data.meta) {
      const label = { missing: "Missing", warn: "Check", ok: "OK" }[m.state];
      const parts = [h("div", { class: "seo-main" }, [
        h("div", { class: "seo-line" }, [h("strong", {}, m.label), status(m.state, label)]),
        m.state !== "missing" && m.current ? h("div", { class: "seo-value" }, m.current) : null,
        m.note ? h("div", { class: "muted seo-note" }, m.note) : null,
      ])];
      if (m.state === "missing") {
        todo++;
        if (m.suggestion) {
          const input = h("textarea", { rows: m.key === "description" ? "3" : "1", "aria-label": `Suggested ${m.label.toLowerCase()}` }, m.suggestion);
          input.value = m.suggestion;
          parts[0].appendChild(input);
          parts.push(h("button", { class: "btn small primary", type: "button", onclick: () => {
            const target = form.elements[m.key];
            if (!target) return;
            target.value = input.value.trim();
            target.dispatchEvent(new Event("input", { bubbles: true }));
            window.ui.toast(`${m.label} filled in. Save to keep it.`);
            analyze();
          } }, "Use this"));
        }
      } else if (m.state === "warn") todo++;
      meta.appendChild(row(parts));
    }

    // --- checks
    const checks = $("[data-seo-checks]"); checks.innerHTML = "";
    for (const c of data.checks) {
      if (c.state === "warn") todo++;
      const label = { ok: "OK", warn: "Check", info: "Tip" }[c.state];
      const detail = !c.items.length ? null
        : c.key === "image_weight"
          ? h("ul", { class: "seo-items" }, c.items.map((i) => h("li", { class: "seo-image-item" }, [
              h("span", {}, [h("code", {}, i.label), " ", h("span", { class: "muted" }, i.detail)]),
              h("span", { class: "seo-actions" }, [
                i.convertible ? h("button", { class: "btn small primary", type: "button", onclick: async () => { if (await convertImage(i.src)) analyze(); } }, "Make lighter") : null,
                h("button", { class: "btn small", type: "button", onclick: async () => { await replaceImage(i.src); analyze(); } }, "Replace…"),
              ]),
            ])))
        : c.key === "keyword"
          ? h("div", { class: "seo-chips" }, c.items.map((i) => h("span", { class: "status " + (i.ok ? "ok" : "warn") }, (i.ok ? "✓ " : "✗ ") + i.label)))
          : h("ul", { class: "seo-items" }, c.items.map((i) => h("li", {}, i.detail ? [h("code", {}, i.label), " ", h("span", { class: "muted" }, i.detail)] : i.label)));
      checks.appendChild(row([h("div", { class: "seo-main" }, [
        h("div", { class: "seo-line" }, [h("strong", {}, c.label), status(c.state, label)]),
        c.note ? h("div", { class: "seo-note" + (c.state === "ok" ? " muted" : "") }, c.note) : null,
        c.key === "image_weight" && c.items.filter((i) => i.convertible).length > 1
          ? h("div", {}, h("button", { class: "btn small primary", type: "button", onclick: async () => {
              let done = 0;
              for (const i of c.items) if (i.convertible && await convertImage(i.src, true)) done++;
              window.ui.toast(done ? `${done} image${done > 1 ? "s" : ""} made lighter. Save to keep it.` : "Nothing could be made lighter without losing quality.");
              analyze();
            } }, `Make all ${c.items.filter((i) => i.convertible).length} lighter`))
          : null,
        detail,
      ])]));
    }

    // --- alt text
    const alt = $("[data-seo-alt]"); alt.innerHTML = "";
    const allButton = $("[data-seo-alt-all]");
    if (!data.images) alt.appendChild(h("p", { class: "muted empty" }, "No images in the text yet."));
    else if (!data.alts.length) alt.appendChild(row([status("ok", "OK"), h("span", {}, `All ${data.images} image${data.images > 1 ? "s have" : " has"} a description.`)]));
    const inputs = [];
    for (const a of data.alts) {
      todo++;
      const thumb = h("img", { class: "seo-thumb", alt: "", src: /^\/(?!\/)/.test(a.src) ? `/media?path=${encodeURIComponent(a.src)}` : a.src });
      const input = h("input", { type: "text", maxlength: "200", "aria-label": `Alt text for ${a.src}` });
      input.value = a.text;
      inputs.push({ a, input });
      alt.appendChild(row([
        thumb,
        h("div", { class: "seo-main" }, [
          h("div", { class: "seo-line" }, [h("code", {}, a.src), status("missing", "No alt text")]),
          input,
          h("div", { class: "muted seo-note" }, `Suggested from ${a.from}. Edit it if it does not describe the picture.`),
        ]),
        h("button", { class: "btn small primary", type: "button", onclick: async () => { if (await apply({ op: "alt", index: a.index, src: a.src, alt: input.value })) analyze(); } }, "Apply"),
      ]));
    }
    allButton.classList.toggle("hidden", data.alts.length < 2);
    allButton.onclick = async () => {
      for (const { a, input } of inputs) if (!(await apply({ op: "alt", index: a.index, src: a.src, alt: input.value }))) return;
      analyze();
    };

    // --- links
    const links = $("[data-seo-links]"); links.innerHTML = "";
    const shown = data.links.filter((l) => !dismissed.has(l.phrase.toLowerCase() + "|" + l.url));
    if (!shown.length) links.appendChild(h("p", { class: "muted empty" }, data.links.length ? "No more suggestions." : "No phrase in the text matches the title of another page."));
    for (const l of shown) {
      todo++;
      links.appendChild(row([
        h("div", { class: "seo-main" }, [
          h("div", { class: "seo-context" }, [l.context.before, h("mark", {}, l.phrase), l.context.after]),
          h("div", { class: "seo-line" }, [h("span", { class: "muted" }, "links to"), h("strong", {}, l.title), h("code", {}, l.url)]),
        ]),
        h("div", { class: "seo-actions" }, [
          h("button", { class: "btn small primary", type: "button", onclick: async () => { if (await apply({ op: "link", start: l.start, end: l.end, phrase: l.phrase, url: l.url })) analyze(); } }, "Add link"),
          h("button", { class: "btn small", type: "button", onclick: () => { dismissed.add(l.phrase.toLowerCase() + "|" + l.url); render(data); } }, "Skip"),
        ]),
      ]));
    }
    seoCount.textContent = String(todo);
    seoCount.classList.toggle("hidden", !todo);
  }
})();
