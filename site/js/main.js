// VPNセキュリティーマスター — 共通JS
(function () {
  "use strict";

  // ---- モバイルナビ ----
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", nav.classList.contains("open") ? "true" : "false");
    });
  }

  // ---- 現在年 ----
  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();

  // ---- 汎用カルーセル ----
  function setupCarousel(opts) {
    var track = document.querySelector(opts.track);
    if (!track) return;
    var slides = track.children;
    var total = slides.length;
    if (total <= 1) return;
    var idx = 0;
    var dotsWrap = opts.dots ? document.querySelector(opts.dots) : null;
    var perView = opts.perView || 1;
    var maxIdx = Math.max(0, total - perView);

    function render() {
      var pct = (100 / perView) * idx;
      track.style.transform = "translateX(-" + pct + "%)";
      if (dotsWrap) {
        Array.prototype.forEach.call(dotsWrap.children, function (d, i) {
          d.classList.toggle("active", i === idx);
        });
      }
    }
    function go(n) { idx = (n < 0) ? maxIdx : (n > maxIdx ? 0 : n); render(); }

    var prev = document.querySelector(opts.prev);
    var next = document.querySelector(opts.next);
    if (prev) prev.addEventListener("click", function () { go(idx - 1); });
    if (next) next.addEventListener("click", function () { go(idx + 1); });

    if (dotsWrap) {
      for (var i = 0; i <= maxIdx; i++) {
        var b = document.createElement("button");
        b.setAttribute("aria-label", "スライド" + (i + 1));
        (function (n) { b.addEventListener("click", function () { go(n); }); })(i);
        dotsWrap.appendChild(b);
      }
    }

    if (opts.auto) {
      var timer = setInterval(function () { go(idx + 1); }, opts.auto);
      track.parentElement.addEventListener("mouseenter", function () { clearInterval(timer); });
    }
    render();
  }

  // ヒーロー（1枚ずつ・自動再生・ドット）
  setupCarousel({ track: ".hero-track", prev: ".hero-arrow.prev", next: ".hero-arrow.next", dots: ".hero-dots", perView: 1, auto: 5000 });
  // SPECIAL（中央寄せ風・矢印のみ）
  setupCarousel({ track: ".special-track", prev: ".special-arrow.prev", next: ".special-arrow.next", perView: window.innerWidth < 600 ? 1 : 1 });
})();
