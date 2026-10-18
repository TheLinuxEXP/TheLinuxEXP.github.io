"use strict";
// Add, remove and reorder the rows of the header and footer forms.
document.querySelectorAll("[data-rows]").forEach((container) => {
  const name = container.dataset.rows;
  const template = document.querySelector(`template[data-template="${name}"]`);
  let counter = container.querySelectorAll("[data-row]").length;
  const addButton = document.querySelector(`[data-add="${name}"]`);

  addButton.addEventListener("click", () => {
    container.insertAdjacentHTML("beforeend", template.innerHTML.replaceAll("__i__", String(counter++)));
    container.lastElementChild.querySelector("input").focus();
  });

  container.addEventListener("click", (event) => {
    const row = event.target.closest("[data-row]");
    if (!row) return;
    if (event.target.closest("[data-remove]")) row.remove();
    const mover = event.target.closest("[data-move]");
    if (mover) {
      const step = Number(mover.dataset.move);
      const sibling = step < 0 ? row.previousElementSibling : row.nextElementSibling;
      if (sibling) step < 0 ? sibling.before(row) : sibling.after(row);
    }
  });
});
