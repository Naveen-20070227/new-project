/* ==========================================================================
   Yojana.ai — Interactive JavaScript Logic
   ========================================================================== */

(function () {
  "use strict";

  var reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  /* ---------- Navbar Glass Density Scroll Toggle (Section 8) ---------- */
  var navWrapper = document.getElementById("navbarWrapper");
  var navEl = document.getElementById("navbar");
  function handleNavScroll() {
    var isScrolled = window.scrollY > 20;
    if (navWrapper) navWrapper.classList.toggle("scrolled", isScrolled);
    if (navEl) navEl.classList.toggle("scrolled", isScrolled);
  }
  window.addEventListener("scroll", handleNavScroll, { passive: true });
  handleNavScroll();

  /* ---------- Mobile Menu Panel Toggle ---------- */
  var navToggle = document.getElementById("navToggle");
  var mobilePanel = document.getElementById("mobilePanel");
  if (navToggle && mobilePanel) {
    navToggle.addEventListener("click", function () {
      var isOpen = mobilePanel.classList.toggle("open");
      navToggle.classList.toggle("open", isOpen);
      navToggle.setAttribute("aria-expanded", isOpen);
    });

    document
      .querySelectorAll(".mobile-panel .mobile-link")
      .forEach(function (link) {
        link.addEventListener("click", function () {
          mobilePanel.classList.remove("open");
          navToggle.classList.remove("open");
          navToggle.setAttribute("aria-expanded", "false");
        });
      });

    // Close mobile menu when clicking outside
    document.addEventListener("click", function (e) {
      if (mobilePanel && mobilePanel.classList.contains("open")) {
        if (!mobilePanel.contains(e.target) && !navToggle.contains(e.target)) {
          mobilePanel.classList.remove("open");
          navToggle.classList.remove("open");
          navToggle.setAttribute("aria-expanded", "false");
        }
      }
    });
  }

  /* ---------- Smooth Anchor Link Scroll ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (e) {
      var id = this.getAttribute("href");
      if (id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;

      e.preventDefault();
      var targetRect = target.getBoundingClientRect();
      var targetCenter = targetRect.top + window.pageYOffset + (targetRect.height / 2);
      var top = targetCenter - (window.innerHeight / 2);

      window.scrollTo({
        top: Math.max(0, top),
        behavior: reduceMotion ? "auto" : "smooth",
      });
    });
  });

  /* ---------- Active Nav Link Observer ---------- */
  var sectionIds = ["who-we-are", "services", "features", "faq", "contact"];
  var sections = sectionIds
    .map(function (id) {
      return document.getElementById(id);
    })
    .filter(Boolean);
  var navAnchors = document.querySelectorAll(
    ".nav-links a, .mobile-panel .mobile-link",
  );

  var activePill = document.getElementById("activePill");

  function moveActivePill(activeEl) {
    if (!activePill || !activeEl) return;
    var navLinksContainer = activeEl.closest(".nav-links");
    if (!navLinksContainer) return; // Only move for desktop nav

    var navLinksRect = navLinksContainer.getBoundingClientRect();
    var elRect = activeEl.getBoundingClientRect();

    var left = elRect.left - navLinksRect.left;
    var width = elRect.width;

    activePill.style.opacity = 1;
    activePill.style.transform = "translate(" + left + "px, -50%)";
    activePill.style.width = width + "px";
  }

  function setActive(id) {
    var desktopActive = null;
    navAnchors.forEach(function (a) {
      var isActive = a.dataset.nav === id;
      a.classList.toggle("active", isActive);
      if (isActive && a.closest(".nav-links")) {
        desktopActive = a;
      }
    });
    if (desktopActive) {
      moveActivePill(desktopActive);
    }
  }

  // Initialize pill position quickly on load
  setTimeout(function () {
    var firstActive =
      document.querySelector(".nav-links a.active") ||
      document.querySelector(".nav-links a");
    if (firstActive && activePill) {
      activePill.style.transition = "none";
      moveActivePill(firstActive);
      // Force reflow
      void activePill.offsetWidth;
      activePill.style.transition =
        "transform 0.5s cubic-bezier(0.22, 1, 0.36, 1), width 0.5s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.3s";
    }
  }, 50);

  var activeObserver = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setActive(entry.target.id);
        }
      });
    },
    { rootMargin: "-30% 0px -40% 0px", threshold: 0 },
  );

  sections.forEach(function (s) {
    if (s) activeObserver.observe(s);
  });

  /* ---------- Scroll Reveal Animations ---------- */
  var revealEls = document.querySelectorAll(".reveal, .reveal-l, .reveal-r");
  var revealObserver = new IntersectionObserver(
    function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 },
  );

  revealEls.forEach(function (el) {
    revealObserver.observe(el);
  });

  /* ---------- FAQ Accordion ---------- */
  var faqItems = document.querySelectorAll(".faq-item");
  faqItems.forEach(function (item) {
    var btn = item.querySelector(".faq-q");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var isOpen = item.classList.contains("open");
      faqItems.forEach(function (other) {
        other.classList.remove("open");
        var otherBtn = other.querySelector(".faq-q");
        if (otherBtn) otherBtn.setAttribute("aria-expanded", "false");
      });
      if (!isOpen) {
        item.classList.add("open");
        btn.setAttribute("aria-expanded", "true");
      }
    });
  });

  /* ---------- Animated Loan Journey Flow ---------- */
  var steps = document.querySelectorAll(".journey-step");
  var progressLine = document.getElementById("journeyProgress");
  var orb = document.getElementById("journeyOrb");
  var currentStep = 0;
  var stepCount = steps.length;
  var journeyTimer = null;

  function updateJourneyStep(index) {
    currentStep = index;
    steps.forEach(function (step, i) {
      step.classList.toggle("active", i === index);
    });

    // Progress line & traveling light orb percentages
    var positions = [15, 50, 85];
    var pct = positions[index] || 15;

    if (progressLine) progressLine.style.width = pct + "%";
    if (orb) orb.style.left = pct + "%";
  }

  function startJourneyAnimation() {
    if (reduceMotion) return;
    if (journeyTimer) clearInterval(journeyTimer);
    journeyTimer = setInterval(function () {
      var nextStep = (currentStep + 1) % stepCount;
      updateJourneyStep(nextStep);
    }, 2400);
  }

  // Interactive click and hover on steps
  steps.forEach(function (step, i) {
    step.addEventListener("click", function () {
      updateJourneyStep(i);
      startJourneyAnimation();
    });

    step.addEventListener("mouseenter", function () {
      updateJourneyStep(i);
      if (journeyTimer) clearInterval(journeyTimer);
    });

    step.addEventListener("mouseleave", function () {
      startJourneyAnimation();
    });
  });

  if (steps.length > 0) {
    updateJourneyStep(0);
    startJourneyAnimation();
  }

  /* ---------- Contact Card Click to Copy Effect ---------- */
  var contactCards = document.querySelectorAll(".contact-card");
  contactCards.forEach(function (card) {
    card.addEventListener("click", function () {
      var copyText = card.getAttribute("data-copy");
      if (!copyText) return;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(copyText).then(function () {
          showToast("Copied: " + copyText);
        });
      } else {
        showToast("Contact: " + copyText);
      }
    });
  });

  function showToast(message) {
    var toast = document.querySelector(".toast-notice");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "toast-notice";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");
    setTimeout(function () {
      toast.classList.remove("show");
    }, 2500);
  }

  /* ---------- Who Are We — GSAP ScrollReveal Word-by-Word Animation ---------- */
  (function initWhoWeAreScrollReveal() {
    var section = document.getElementById("who-we-are");
    if (!section) return;

    var title = section.querySelector(".who-title");
    var paragraph = section.querySelector(".who-text p");
    if (!paragraph) return;

    // Check reduced motion preference
    var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) return;

    // Verify GSAP & ScrollTrigger exist
    if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") return;

    gsap.registerPlugin(ScrollTrigger);

    var container = section.querySelector(".who-container");

    // Clean up any pre-existing ScrollTrigger instance on this container
    if (container) {
      ScrollTrigger.getAll().forEach(function (st) {
        if (st.trigger === container || (st.vars && st.vars.trigger === container)) {
          st.kill();
        }
      });
    }

    function splitElementWords(el) {
      if (!el) return;
      var nodes = Array.from(el.childNodes);
      el.innerHTML = "";

      nodes.forEach(function (node) {
        if (node.nodeType === Node.TEXT_NODE) {
          var parts = node.textContent.split(/(\s+)/);
          parts.forEach(function (part) {
            if (part.trim().length > 0) {
              var span = document.createElement("span");
              span.className = "sr-word";
              span.textContent = part;
              el.appendChild(span);
            } else if (part.length > 0) {
              el.appendChild(document.createTextNode(part));
            }
          });
        } else if (node.nodeType === Node.ELEMENT_NODE) {
          if (node.tagName.toLowerCase() === "strong") {
            var strongSpan = document.createElement("strong");
            var parts = node.textContent.split(/(\s+)/);
            parts.forEach(function (part) {
              if (part.trim().length > 0) {
                var span = document.createElement("span");
                span.className = "sr-word sr-accent";
                span.textContent = part;
                strongSpan.appendChild(span);
              } else if (part.length > 0) {
                strongSpan.appendChild(document.createTextNode(part));
              }
            });
            el.appendChild(strongSpan);
          } else {
            el.appendChild(node.cloneNode(true));
          }
        }
      });
    }

    if (title) splitElementWords(title);
    splitElementWords(paragraph);

    var words = section.querySelectorAll(".sr-word");

    // Initial word styling: subtle 8px blur & 0.12 opacity
    gsap.set(words, {
      opacity: 0.12,
      filter: "blur(8px)",
      willChange: "opacity, filter",
    });

    // Initial container tilt: 3.5deg subtle rotation
    if (container) {
      gsap.set(container, {
        rotation: 3.5,
        transformOrigin: "center center",
        willChange: "transform",
      });
    }

    // ScrollTrigger timeline: Starts at viewport bottom (top 90%), completes 100% at screen midpoint (center center)
    var tl = gsap.timeline({
      scrollTrigger: {
        trigger: container || section,
        start: "top 90%",
        end: "center center",
        scrub: 1.0,
        invalidateOnRefresh: true,
      },
    });

    tl.to(
      words,
      {
        opacity: 1,
        filter: "blur(0px)",
        stagger: {
          amount: 0.4,
          ease: "power1.inOut",
        },
        ease: "power2.out",
      },
      0
    );

    if (container) {
      tl.to(
        container,
        {
          rotation: 0,
          ease: "power1.out",
        },
        0
      );
    }
  })();
})();

/* ==========================================================================
   DotField — High-Performance Interactive Canvas Dot Field
   ========================================================================== */
(function initDotField() {
  "use strict";

  var container = document.getElementById("dot-field");
  if (!container) return;

  // --- Target Configuration Settings (Light SaaS Multi-Gradient Theme) ---
  var CONFIG = {
    dotRadius: 1.3,
    dotSpacing: 16,
    bulgeStrength: 45,
    glowRadius: 180,
    sparkle: true,
    waveAmplitude: 0,
    gradientFrom: "rgba(99, 102, 241, 0.28)",
    gradientTo: "rgba(14, 165, 233, 0.18)",
    glowColor: "rgba(79, 70, 229, 0.35)",
    bgBase: "#F8FAFC",
  };

  var canvas = document.createElement("canvas");
  var ctx = canvas.getContext("2d");
  container.appendChild(canvas);

  var dots = [];
  var width = 0;
  var height = 0;
  var dpr = window.devicePixelRatio || 1;

  var mouse = {
    x: -1000,
    y: -1000,
    targetX: -1000,
    targetY: -1000,
    active: false,
  };

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  // Helper to parse rgba string values
  function parseRGBA(colorStr) {
    var match = colorStr.match(
      /rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)/,
    );
    if (match) {
      return {
        r: parseInt(match[1], 10),
        g: parseInt(match[2], 10),
        b: parseInt(match[3], 10),
        a: match[4] !== undefined ? parseFloat(match[4]) : 1.0,
      };
    }
    return { r: 99, g: 102, b: 241, a: 0.35 };
  }

  var colorFrom = parseRGBA(CONFIG.gradientFrom);
  var colorTo = parseRGBA(CONFIG.gradientTo);

  function resize() {
    dpr = window.devicePixelRatio || 1;
    width = window.innerWidth;
    height = window.innerHeight;

    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";

    initGrid();
  }

  function initGrid() {
    dots = [];
    var spacing = CONFIG.dotSpacing;
    var cols = Math.ceil(width / spacing) + 1;
    var rows = Math.ceil(height / spacing) + 1;

    var offsetX = (width - (cols - 1) * spacing) / 2;
    var offsetY = (height - (rows - 1) * spacing) / 2;

    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var bx = offsetX + c * spacing;
        var by = offsetY + r * spacing;

        // Subtle gradient interpolation across screen
        var t = (bx / width + by / height) / 2;
        t = Math.max(0, Math.min(1, t));

        var cr = Math.round(colorFrom.r + (colorTo.r - colorFrom.r) * t);
        var cg = Math.round(colorFrom.g + (colorTo.g - colorFrom.g) * t);
        var cb = Math.round(colorFrom.b + (colorTo.b - colorFrom.b) * t);
        var ca = colorFrom.a + (colorTo.a - colorFrom.a) * t;

        // Sparkle initialization (subtle 15% random distribution)
        var isSparkleDot = CONFIG.sparkle && Math.random() < 0.15;

        dots.push({
          baseX: bx,
          baseY: by,
          x: bx,
          y: by,
          r: cr,
          g: cg,
          b: cb,
          baseAlpha: ca,
          isSparkle: isSparkleDot,
          sparkleTimer: Math.random() * Math.PI * 2,
          sparkleSpeed:
            (0.008 + Math.random() * 0.015) * (Math.random() < 0.5 ? 1 : -1),
        });
      }
    }
  }

  // Event Handlers
  function onMouseMove(e) {
    mouse.targetX = e.clientX;
    mouse.targetY = e.clientY;
    mouse.active = true;
  }

  function onTouchMove(e) {
    if (e.touches && e.touches.length > 0) {
      mouse.targetX = e.touches[0].clientX;
      mouse.targetY = e.touches[0].clientY;
      mouse.active = true;
    }
  }

  function onMouseLeave() {
    mouse.active = false;
  }

  window.addEventListener("mousemove", onMouseMove, { passive: true });
  window.addEventListener("touchstart", onTouchMove, { passive: true });
  window.addEventListener("touchmove", onTouchMove, { passive: true });
  window.addEventListener("mouseleave", onMouseLeave, { passive: true });
  window.addEventListener("touchend", onMouseLeave, { passive: true });
  window.addEventListener("resize", resize, { passive: true });

  // Main Render Loop
  function render() {
    ctx.save();
    ctx.scale(dpr, dpr);

    // Clear frame
    ctx.fillStyle = CONFIG.bgBase;
    ctx.fillRect(0, 0, width, height);

    // Interpolate cursor movement smoothly
    if (mouse.active) {
      mouse.x += (mouse.targetX - mouse.x) * 0.12;
      mouse.y += (mouse.targetY - mouse.y) * 0.12;

      // Soft glow aura under cursor
      var glowGrad = ctx.createRadialGradient(
        mouse.x,
        mouse.y,
        0,
        mouse.x,
        mouse.y,
        CONFIG.glowRadius,
      );
      glowGrad.addColorStop(0, "rgba(79, 70, 229, 0.10)");
      glowGrad.addColorStop(0.5, "rgba(14, 165, 233, 0.04)");
      glowGrad.addColorStop(1, "rgba(79, 70, 229, 0)");

      ctx.fillStyle = glowGrad;
      ctx.fillRect(0, 0, width, height);
    }

    var glowRadiusSq = CONFIG.glowRadius * CONFIG.glowRadius;
    var maxDisplacement = CONFIG.bulgeStrength * 0.12; // Scaled displacement

    for (var i = 0; i < dots.length; i++) {
      var dot = dots[i];
      var targetX = dot.baseX;
      var targetY = dot.baseY;
      var glowFactor = 0;

      if (!prefersReducedMotion && mouse.active) {
        var dx = dot.baseX - mouse.x;
        var dy = dot.baseY - mouse.y;
        var distSq = dx * dx + dy * dy;

        if (distSq < glowRadiusSq) {
          var dist = Math.sqrt(distSq);
          var normDist = dist / CONFIG.glowRadius;
          glowFactor = Math.pow(Math.cos(normDist * Math.PI * 0.5), 2);

          var angle = Math.atan2(dy, dx);
          var push = maxDisplacement * glowFactor;

          // Bulge movement towards/around cursor
          targetX = dot.baseX - Math.cos(angle) * push;
          targetY = dot.baseY - Math.sin(angle) * push;
        }
      }

      // Smooth position spring returning to baseline
      if (!prefersReducedMotion) {
        dot.x += (targetX - dot.x) * 0.1;
        dot.y += (targetY - dot.y) * 0.1;
      } else {
        dot.x = dot.baseX;
        dot.y = dot.baseY;
      }

      // Sparkle animation
      var sparkleExtra = 0;
      if (!prefersReducedMotion && dot.isSparkle) {
        dot.sparkleTimer += dot.sparkleSpeed;
        var sVal = (Math.sin(dot.sparkleTimer) + 1) * 0.5;
        if (sVal > 0.82) {
          sparkleExtra = (sVal - 0.82) * 1.2 * 0.25;
        }
      }

      var currentAlpha = Math.min(
        1.0,
        dot.baseAlpha + glowFactor * 0.55 + sparkleExtra,
      );
      var currentRadius = CONFIG.dotRadius + glowFactor * 0.8;

      // Draw dot arc
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, currentRadius, 0, Math.PI * 2);

      if (glowFactor > 0.15) {
        ctx.shadowBlur = glowFactor * 8;
        ctx.shadowColor = CONFIG.glowColor;
      } else {
        ctx.shadowBlur = 0;
      }

      ctx.fillStyle =
        "rgba(" +
        dot.r +
        "," +
        dot.g +
        "," +
        dot.b +
        "," +
        currentAlpha.toFixed(3) +
        ")";
      ctx.fill();
    }

    ctx.restore();
    requestAnimationFrame(render);
  }

  resize();
  requestAnimationFrame(render);
})();
