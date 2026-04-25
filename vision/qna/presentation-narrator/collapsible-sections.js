(function () {
  const OPEN_FOR_PASSED = new Set([
    "Answer I Will Actually Give",
    "Support Notes"
  ]);

  function makeCollapsible(section, isPassed) {
    const isNote = section.classList.contains("note");
    const titleNode = isNote
      ? section.querySelector(":scope > strong")
      : section.querySelector(":scope > h2");

    if (!titleNode) return;

    const title = titleNode.textContent.trim();
    const details = document.createElement("details");
    details.className = section.className + " collapsible-section";

    details.open = !isPassed || OPEN_FOR_PASSED.has(title);

    const summary = document.createElement("summary");
    summary.textContent = title;
    details.appendChild(summary);

    const content = document.createElement("div");
    content.className = "collapsible-content";

    let skipLeadingBreak = isNote;
    for (const node of Array.from(section.childNodes)) {
      if (node === titleNode) continue;

      if (skipLeadingBreak && node.nodeName === "BR") {
        skipLeadingBreak = false;
        continue;
      }

      if (content.childNodes.length === 0 && node.nodeType === Node.TEXT_NODE && !node.textContent.trim()) {
        continue;
      }

      content.appendChild(node);
      skipLeadingBreak = false;
    }

    details.appendChild(content);
    section.replaceWith(details);
  }

  function init() {
    const meta = document.querySelector(".meta");
    const isPassed = !!meta && /Status:\s*ผ่าน(?:แล้ว)?/.test(meta.textContent);
    const sections = document.querySelectorAll(".panel > .note, .panel > .thought-box");
    sections.forEach((section) => makeCollapsible(section, isPassed));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
