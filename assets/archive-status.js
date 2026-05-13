(function () {
  if (document.querySelector(".archive-status")) return;

  var banner = document.createElement("div");
  banner.className = "archive-status";
  banner.setAttribute("role", "note");
  banner.innerHTML = [
    '<div class="archive-status__inner">',
    '  <div>',
    '    <span class="archive-status__label">Archive</span>',
    '    <span class="archive-status__text">เว็บไซต์นี้เก็บไว้เป็น archive ของกระบวนการสรรหาอธิการบดีมหาวิทยาลัยเกษตรศาสตร์ ปี 2569</span>',
    '  </div>',
    '  <a class="archive-status__link" href="https://punpiti.github.io/">เว็บไซต์งานปัจจุบัน</a>',
    '</div>'
  ].join("");

  document.body.insertBefore(banner, document.body.firstChild);
}());
