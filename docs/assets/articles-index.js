(function () {
  const root = document.querySelector("[data-archive-search]");
  if (!root || !window.ARTICLES_DATA) {
    return;
  }

  const input = root.querySelector(".search-input");
  const panel = root.querySelector("[data-search-suggestions]");
  if (!input || !panel) {
    return;
  }

  const articles = window.ARTICLES_DATA.map((article) => ({
    ...article,
    searchBlob: [
      article.title,
      article.category,
      article.summary,
      ...(article.tags || []),
    ]
      .join(" ")
      .toLowerCase(),
  }));

  let activeIndex = -1;
  let currentResults = [];

  function scoreArticle(article, query) {
    const title = article.title.toLowerCase();
    const category = article.category.toLowerCase();
    const tags = (article.tags || []).join(" ").toLowerCase();

    let score = 0;
    if (title.startsWith(query)) score += 10;
    if (title.includes(query)) score += 6;
    if (category.includes(query)) score += 4;
    if (tags.includes(query)) score += 3;
    if (article.searchBlob.includes(query)) score += 1;
    return score;
  }

  function closePanel() {
    panel.hidden = true;
    panel.innerHTML = "";
    input.setAttribute("aria-expanded", "false");
    activeIndex = -1;
    currentResults = [];
  }

  function renderResults(results) {
    currentResults = results;
    activeIndex = -1;

    if (results.length === 0) {
      closePanel();
      return;
    }

    panel.innerHTML = results
      .map(
        (article, index) => `
          <a class="search-suggestion" href="${article.archive_path}" data-index="${index}">
            <div class="search-suggestion__meta">${article.category} • ${article.display_date}</div>
            <div class="search-suggestion__title">${article.title}</div>
          </a>
        `
      )
      .join("");
    panel.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }

  function updateActiveItem() {
    const items = panel.querySelectorAll(".search-suggestion");
    items.forEach((item, index) => {
      item.classList.toggle("is-active", index === activeIndex);
    });
  }

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    if (!query) {
      closePanel();
      return;
    }

    const results = articles
      .map((article) => ({ ...article, score: scoreArticle(article, query) }))
      .filter((article) => article.score > 0)
      .sort((a, b) => b.score - a.score || b.date.localeCompare(a.date))
      .slice(0, 6);

    renderResults(results);
  });

  input.addEventListener("keydown", (event) => {
    if (panel.hidden || currentResults.length === 0) {
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      activeIndex = (activeIndex + 1) % currentResults.length;
      updateActiveItem();
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      activeIndex = (activeIndex - 1 + currentResults.length) % currentResults.length;
      updateActiveItem();
      return;
    }

    if (event.key === "Enter") {
      event.preventDefault();
      const target = activeIndex >= 0 ? currentResults[activeIndex] : currentResults[0];
      if (target) {
        window.location.href = target.archive_path;
      }
    }

    if (event.key === "Escape") {
      closePanel();
    }
  });

  document.addEventListener("click", (event) => {
    if (!root.contains(event.target)) {
      closePanel();
    }
  });

  const latestExpand = document.querySelector("[data-latest-expand]");
  const latestLess = document.querySelector("[data-latest-less]");
  const latestCollapse = document.querySelector("[data-latest-collapse]");
  if (!latestExpand || !latestLess || !latestCollapse) {
    return;
  }

  const extraItems = Array.from(document.querySelectorAll("[data-latest-extra]"));
  if (extraItems.length === 0) {
    const actionGroup = document.querySelector(".action-group");
    if (actionGroup) {
      actionGroup.hidden = true;
    }
    return;
  }

  let revealedCount = 0;
  function syncLatestButtons() {
    latestExpand.disabled = revealedCount >= extraItems.length;
    latestLess.disabled = revealedCount === 0;
    latestCollapse.disabled = revealedCount === 0;
  }

  function renderLatestItems() {
    extraItems.forEach((item, index) => {
      item.hidden = index >= revealedCount;
    });
    syncLatestButtons();
  }

  latestExpand.addEventListener("click", () => {
    revealedCount = Math.min(revealedCount + 3, extraItems.length);
    renderLatestItems();
  });

  latestLess.addEventListener("click", () => {
    revealedCount = Math.max(revealedCount - 3, 0);
    renderLatestItems();
  });

  latestCollapse.addEventListener("click", () => {
    revealedCount = 0;
    renderLatestItems();
  });

  renderLatestItems();

  document.querySelectorAll(".topic-card").forEach((card) => {
    const toggle = card.querySelector("[data-topic-toggle]");
    const extraItems = Array.from(card.querySelectorAll("[data-topic-extra]"));
    if (!toggle || extraItems.length === 0) {
      return;
    }

    let isExpanded = false;
    toggle.addEventListener("click", () => {
      isExpanded = !isExpanded;
      extraItems.forEach((item) => {
        item.hidden = !isExpanded;
      });
      if (isExpanded && toggle.hasAttribute("data-topic-other-toggle")) {
        const firstDetail = extraItems[0]?.querySelector("details");
        if (firstDetail) {
          firstDetail.open = true;
        }
      }
      toggle.textContent = isExpanded ? "ย่อกลับ" : "ดูทั้งหมด";
    });
  });
})();
