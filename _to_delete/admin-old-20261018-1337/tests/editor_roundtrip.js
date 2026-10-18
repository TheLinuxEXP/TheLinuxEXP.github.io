/* Optional browser check of the visual editor (needs Node, the `playwright` package and a browser).
 *
 *   1. Start the admin:            ./admin/start.sh
 *   2. Run:   ADMIN_USER=nick ADMIN_PASSWORD=... node admin/tests/editor_roundtrip.js
 *
 * It opens every article in the editor, saves nothing, and checks that the Markdown the editor would
 * write back is identical, byte for byte, to the file. Run it after updating markdown-it or editing md-editor.js.
 */
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1360, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
  page.on("pageerror", (e) => errors.push("pageerror: " + e.message));
  page.on("requestfailed", (r) => errors.push("failed: " + r.url()));
  await page.goto("http://127.0.0.1:4001/login");
  await page.fill("#username", process.env.ADMIN_USER || "admin"); await page.fill("#password", process.env.ADMIN_PASSWORD || "");
  await page.click("button[type=submit]");
  await page.waitForURL("http://127.0.0.1:4001/");
  const links = await page.$$eval("a.entry", (as) => as.map((a) => a.getAttribute("href")));
  console.log("articles", links.length);
  // round trip: no edit -> the Markdown must come back byte for byte
  let bad = 0;
  for (const href of links) {
    await page.goto("http://127.0.0.1:4001" + href);
    await page.waitForSelector(".md-editor");
    const r = await page.evaluate(() => new Promise((resolve) => {
      const form = document.querySelector("form.edit");
      const ta = form.elements.body;
      const original = ta.defaultValue;
      form.addEventListener("submit", (e) => { e.preventDefault(); resolve({ same: ta.value === original, len: original.length, got: ta.value.length }); });
      form.requestSubmit();
    }));
    if (!r.same) { bad++; console.log("DIFF", href, r); }
  }
  console.log("roundtrip mismatches:", bad);
  console.log("errors:", errors.filter((e) => !/failed:|404/.test(e)).slice(0, 10));
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
