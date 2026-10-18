"use strict";
/* Small dialogs and messages in the Planner Unifié style: modal, toast, form/prompt/confirm/choose. */
(function () {
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

  let toastTimer = null;
  function toast(message, ms) {
    document.querySelectorAll(".toast-host").forEach((n) => n.remove());
    const host = h("div", { class: "toast-host", role: "status" }, [h("div", { class: "toast" }, message)]);
    document.body.appendChild(host);
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => host.remove(), ms || 3500);
  }

  // One modal at a time: opening another replaces the first. Resolves with the value given to done().
  let current = null;
  function modal({ title, content, buttons, wide }) {
    if (current) current.close(null);
    return new Promise((resolve) => {
      const previous = document.activeElement;
      const overlay = h("div", { class: "overlay" });
      const box = h("div", { class: "modal" + (wide ? " modal-wide" : ""), role: "dialog", "aria-modal": "true", "aria-label": title });
      const api = {
        close(value) {
          if (current === api) current = null;
          overlay.remove();
          document.removeEventListener("keydown", onKey, true);
          if (previous && previous.focus) previous.focus();
          resolve(value);
        },
      };
      const onKey = (e) => { if (e.key === "Escape") { e.preventDefault(); api.close(null); } };
      document.addEventListener("keydown", onKey, true);
      overlay.addEventListener("mousedown", (e) => { if (e.target === overlay) api.close(null); });
      box.append(h("h2", {}, title), content);
      if (buttons) box.append(h("div", { class: "btn-row" }, buttons(api)));
      overlay.appendChild(box);
      document.body.appendChild(overlay);
      current = api;
      const first = box.querySelector("input, select, textarea") || box.querySelector(".btn.primary");
      if (first) first.focus();
    });
  }

  // fields: [{name, label, value, help, placeholder, type}] -> {name: value} or null
  function form({ title, fields, confirmLabel, message, danger }) {
    const inputs = {};
    const body = h("form", { class: "ui-form", novalidate: "novalidate" });
    if (message) body.appendChild(h("p", { class: "muted ui-message" }, message));
    for (const f of fields) {
      const input = h("input", { type: f.type || "text", name: f.name, value: f.value || "", placeholder: f.placeholder || "", autocomplete: "off" });
      inputs[f.name] = input;
      input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); body.dispatchEvent(new Event("submit", { cancelable: true })); } });
      body.appendChild(h("div", { class: "field" }, [h("label", {}, f.label), input, f.help ? h("small", { class: "muted" }, f.help) : null]));
    }
    return modal({
      title, content: body,
      buttons: (api) => {
        const ok = h("button", { class: "btn " + (danger ? "danger" : "primary"), type: "submit" }, confirmLabel || "OK");
        const done = () => api.close(Object.fromEntries(Object.entries(inputs).map(([k, v]) => [k, v.value])));
        body.addEventListener("submit", (e) => { e.preventDefault(); done(); });
        ok.addEventListener("click", (e) => { e.preventDefault(); done(); });
        return [h("button", { class: "btn", type: "button", onclick: () => api.close(null) }, "Cancel"), ok];
      },
    });
  }

  async function prompt({ title, label, message, value, confirmLabel, placeholder }) {
    const r = await form({ title, message, confirmLabel, fields: [{ name: "v", label: label || "Value", value, placeholder }] });
    return r ? r.v : null;
  }

  async function confirm({ title, message, confirmLabel, danger }) {
    return await modal({
      title, content: h("p", {}, message),
      buttons: (api) => [
        h("button", { class: "btn", type: "button", onclick: () => api.close(false) }, "Cancel"),
        h("button", { class: "btn " + (danger ? "danger" : "primary"), type: "button", onclick: () => api.close(true) }, confirmLabel || "OK"),
      ],
    }) === true;
  }

  // Pick one item from a filterable list: items [{label, hint, value}] -> value or null
  function choose({ title, placeholder, items }) {
    const list = h("div", { class: "choose-list" });
    const input = h("input", { type: "search", placeholder: placeholder || "Filter…", autocomplete: "off", "aria-label": placeholder || "Filter" });
    let api = null;
    const paint = () => {
      const q = input.value.trim().toLowerCase();
      list.innerHTML = "";
      const shown = items.filter((i) => !q || (i.label + " " + (i.hint || "")).toLowerCase().includes(q)).slice(0, 60);
      shown.forEach((i) => list.appendChild(h("button", { class: "choose-item", type: "button", onclick: () => api.close(i.value) },
        [h("span", { class: "choose-label" }, i.label), i.hint ? h("span", { class: "muted choose-hint" }, i.hint) : null])));
      if (!shown.length) list.appendChild(h("div", { class: "muted choose-empty" }, "Nothing matches"));
    };
    input.addEventListener("input", paint);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); const f = list.querySelector("button"); if (f) f.click(); } });
    const content = h("div", { class: "field" }, [input, list]);
    paint();
    const result = modal({
      title, content, wide: true,
      buttons: (a) => { api = a; return [h("button", { class: "btn", type: "button", onclick: () => a.close(null) }, "Cancel")]; },
    });
    return result;
  }

  // Light / dark switch (stored under the Planner's key so both apps agree).
  function toggleTheme() {
    const root = document.documentElement;
    const dark = root.dataset.theme ? root.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    const next = dark ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("taskplanner-theme", next); } catch (e) { /* not remembered */ }
  }
  document.addEventListener("click", (e) => { if (e.target.closest("[data-theme-toggle]")) toggleTheme(); });

  window.ui = { toast, modal, form, prompt, confirm, choose };
})();
