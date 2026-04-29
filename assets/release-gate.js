(() => {
  const releaseAt = new Date("2026-04-29T08:00:00+07:00");

  if (new Date() >= releaseAt) {
    return;
  }

  document.querySelectorAll("[data-release-hidden]").forEach((element) => {
    element.hidden = true;
  });
})();
