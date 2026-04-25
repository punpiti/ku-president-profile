(() => {
  const carouselPanelStorageKey = "presentation-narrator.carousel.open";
  const statusClassMap = {
    "ผ่านแล้ว": "status-done",
    "พร้อมปรับ": "status-ready",
    "มี draft ตั้งต้น": "status-draft",
  };

  const readStoredCarouselPanelState = () => {
    try {
      return window.localStorage.getItem(carouselPanelStorageKey);
    } catch {
      return null;
    }
  };

  const writeStoredCarouselPanelState = (isOpen) => {
    try {
      window.localStorage.setItem(carouselPanelStorageKey, isOpen ? "open" : "closed");
    } catch {
      // Ignore storage failures and fall back to default collapsed behavior.
    }
  };

  document.querySelectorAll(".badge.status").forEach((badge) => {
    const text = badge.textContent.trim();
    const className = statusClassMap[text];
    if (className) badge.classList.add(className);
  });

  document.querySelectorAll("[data-collapsible-panel]").forEach((panel) => {
    const storedState = readStoredCarouselPanelState();
    if (storedState === "open") panel.open = true;
    if (storedState === "closed") panel.open = false;

    panel.addEventListener("toggle", () => {
      writeStoredCarouselPanelState(panel.open);
    });
  });

  document.querySelectorAll("[data-carousel-shell]").forEach((shell) => {
    const panel = shell.closest("[data-collapsible-panel]");
    const track = shell.querySelector("[data-carousel-track]");
    const prev = shell.querySelector("[data-carousel-prev]");
    const next = shell.querySelector("[data-carousel-next]");
    if (!track || !prev || !next) return;

    const scrollAmount = () => Math.max(track.clientWidth * 0.72, 180);
    const centerActiveSlide = () => {
      const active = track.querySelector(".thumb-card.active");
      if (!active || track.clientWidth <= 0) return;

      const trackRect = track.getBoundingClientRect();
      const activeRect = active.getBoundingClientRect();
      const activeCenter = activeRect.left - trackRect.left + track.scrollLeft + activeRect.width / 2;
      const left = Math.max(0, activeCenter - track.clientWidth / 2);
      track.scrollTo({ left, behavior: "auto" });
    };

    prev.addEventListener("click", () => {
      track.scrollBy({ left: -scrollAmount(), behavior: "smooth" });
    });

    next.addEventListener("click", () => {
      track.scrollBy({ left: scrollAmount(), behavior: "smooth" });
    });

    if (!panel || panel.open) {
      centerActiveSlide();
    }

    if (panel) {
      panel.addEventListener("toggle", () => {
        if (panel.open) centerActiveSlide();
      });
    }
  });
})();
