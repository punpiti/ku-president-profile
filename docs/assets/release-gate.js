(() => {
  const releaseAt = new Date("2026-04-29T08:00:00+07:00");
  const gatedPaths = new Set([
    "context.html",
    "roles.html",
    "goals.html",
    "strategy.html",
    "four-year-plan.html",
  ]);

  if (new Date() >= releaseAt) {
    return;
  }

  const style = document.createElement("style");
  style.textContent = `
    .release-gate-backdrop {
      position: fixed;
      inset: 0;
      z-index: 9998;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
      background: rgba(7, 22, 23, 0.6);
      backdrop-filter: blur(8px);
    }

    .release-gate-backdrop.is-open {
      display: flex;
    }

    .release-gate-dialog {
      width: min(640px, calc(100vw - 24px));
      padding: 24px;
      border: 1px solid rgba(0, 102, 100, 0.12);
      border-radius: 28px;
      background: rgba(255, 253, 248, 0.98);
      box-shadow: 0 28px 64px rgba(0, 68, 67, 0.18);
      color: #1c3134;
      font-family: "Sarabun", "Noto Sans Thai", sans-serif;
    }

    .release-gate-kicker {
      color: #006664;
      font-size: 0.84rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .release-gate-title {
      margin-top: 10px;
      color: #14335a;
      font-size: clamp(1.5rem, 3vw, 2rem);
      line-height: 1.2;
      font-weight: 700;
      letter-spacing: -0.03em;
    }

    .release-gate-body {
      margin-top: 14px;
      color: #203234;
      line-height: 1.85;
      font-size: 1rem;
    }

    .release-gate-actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 18px;
    }

    .release-gate-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 42px;
      padding: 0 16px;
      border: 0;
      border-radius: 999px;
      background: linear-gradient(135deg, #006664, #014846);
      color: #fff;
      font: inherit;
      font-size: 0.96rem;
      font-weight: 600;
      cursor: pointer;
    }
  `;
  document.head.appendChild(style);

  const backdrop = document.createElement("div");
  backdrop.className = "release-gate-backdrop";
  backdrop.innerHTML = `
    <div class="release-gate-dialog" role="dialog" aria-modal="true" aria-labelledby="release-gate-title">
      <div class="release-gate-kicker">Coming Soon</div>
      <div class="release-gate-title" id="release-gate-title">เนื้อหาส่วนนี้จะแสดงหลังการนำเสนอวิสัยทัศน์</div>
      <div class="release-gate-body">
        ขอเชิญติดตามการนำเสนอวิสัยทัศน์ของ <strong>รศ.ดร.พันธุ์ปิติ เปี่ยมสง่า</strong><br>
        เปิดเวลา <strong>08:00 น. วันที่ 29 เมษายน 2026</strong><br>
        ณ <strong>มหาวิทยาลัยเกษตรศาสตร์</strong>
      </div>
      <div class="release-gate-actions">
        <button class="release-gate-button" type="button">รับทราบ</button>
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);

  const close = () => backdrop.classList.remove("is-open");
  const open = () => backdrop.classList.add("is-open");

  backdrop.addEventListener("click", (event) => {
    if (event.target === backdrop) {
      close();
    }
  });

  backdrop.querySelector(".release-gate-button")?.addEventListener("click", close);

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      close();
    }
  });

  const anchors = Array.from(document.querySelectorAll("a[href]"));
  anchors.forEach((anchor) => {
    const rawHref = anchor.getAttribute("href");
    if (!rawHref || rawHref.startsWith("#")) {
      return;
    }

    const normalized = rawHref.replace(/^\.\.\//, "");
    if (!gatedPaths.has(normalized)) {
      return;
    }

    anchor.dataset.releaseHref = rawHref;
    anchor.setAttribute("href", "#");
    anchor.addEventListener("click", (event) => {
      event.preventDefault();
      open();
    });
  });
})();
