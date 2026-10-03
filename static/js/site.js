(function () {
  // Mobil menyu
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
    });
  }

  // Toast xabarlarini yashirish
  var toasts = document.querySelector(".toasts");
  if (toasts) setTimeout(function () { toasts.remove(); }, 6000);

  // Hero: sekin suzuvchi zarrachalar
  var canvas = document.querySelector(".hero-canvas");
  if (!canvas || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var ctx = canvas.getContext("2d"), dots = [], w, h;
  function resize() {
    var r = canvas.getBoundingClientRect();
    w = canvas.width = r.width; h = canvas.height = r.height;
    dots = Array.from({ length: Math.min(46, Math.floor(w / 26)) }, function () {
      return { x: Math.random() * w, y: Math.random() * h, vx: (Math.random() - .5) * .25, vy: (Math.random() - .5) * .25, r: Math.random() * 1.4 + .4 };
    });
  }
  function frame() {
    ctx.clearRect(0, 0, w, h);
    dots.forEach(function (d) {
      d.x = (d.x + d.vx + w) % w; d.y = (d.y + d.vy + h) % h;
      ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, 6.283);
      ctx.fillStyle = "rgba(160,190,255,.55)"; ctx.fill();
    });
    requestAnimationFrame(frame);
  }
  window.addEventListener("resize", resize);
  resize(); frame();
})();
