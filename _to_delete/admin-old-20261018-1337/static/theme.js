// Applies the saved theme before the page is drawn (same key as the Planner).
try {
  var saved = localStorage.getItem("taskplanner-theme");
  if (saved === "light" || saved === "dark") document.documentElement.setAttribute("data-theme", saved);
} catch (e) { /* storage blocked: follow the system theme */ }
