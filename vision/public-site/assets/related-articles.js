(function () {
  const relatedRoot = document.querySelector("[data-related-articles]");
  if (!relatedRoot || !window.ARTICLES_DATA) {
    return;
  }

  const slug = relatedRoot.dataset.currentSlug;
  const tagSource = relatedRoot.dataset.currentTags || "";
  const currentTags = tagSource
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);

  if (!slug || currentTags.length === 0) {
    return;
  }

  const related = window.ARTICLES_DATA
    .filter((article) => article.slug !== slug)
    .map((article) => {
      const overlap = article.tags.filter((tag) => currentTags.includes(tag));
      return { ...article, overlap, score: overlap.length };
    })
    .filter((article) => article.score > 0)
    .sort((a, b) => b.score - a.score || a.title.localeCompare(b.title))
    .slice(0, 3);

  relatedRoot.innerHTML = "";

  if (related.length === 0) {
    const emptyCard = document.createElement("div");
    emptyCard.className = "related-card";
    emptyCard.innerHTML =
      "<h3>กำลังรอบทความที่ใช้ tag ใกล้เคียงกัน</h3><p>เมื่อมีบทความเพิ่ม ระบบจะแสดงรายการอ่านต่อจาก tag ที่ตรงกันในส่วนนี้โดยอัตโนมัติ</p>";
    relatedRoot.appendChild(emptyCard);
    return;
  }

  related.forEach((article) => {
    const card = document.createElement("a");
    card.className = "related-card";
    card.href = article.path;

    const tagText = article.overlap.join(", ");
    card.innerHTML = `
      <img class="related-thumb" src="../${article.image_index}" alt="${article.image_alt}">
      <div class="related-copy">
        <h3>${article.title}</h3>
        <p>${article.summary}</p>
        <p>Related tags: ${tagText}</p>
      </div>
    `;

    relatedRoot.appendChild(card);
  });
})();
