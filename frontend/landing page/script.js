/* ==========================================================================
   Yojana.ai — Interactive JavaScript Logic
   ========================================================================== */

(function () {
  "use strict";

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Navbar Elevated Scroll Effect ---------- */
  var navbarWrapper = document.getElementById('navbarWrapper');
  function onScrollNav() {
    if (window.scrollY > 15) {
      navbarWrapper.classList.add('scrolled');
    } else {
      navbarWrapper.classList.remove('scrolled');
    }
  }
  onScrollNav();
  window.addEventListener('scroll', onScrollNav, { passive: true });

  /* ---------- Mobile Menu Panel Toggle ---------- */
  var navToggle = document.getElementById('navToggle');
  var mobilePanel = document.getElementById('mobilePanel');
  if (navToggle && mobilePanel) {
    navToggle.addEventListener('click', function () {
      var isOpen = mobilePanel.classList.toggle('open');
      navToggle.classList.toggle('open', isOpen);
      navToggle.setAttribute('aria-expanded', isOpen);
    });

    document.querySelectorAll('.mobile-panel .mobile-link').forEach(function (link) {
      link.addEventListener('click', function () {
        mobilePanel.classList.remove('open');
        navToggle.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- Smooth Anchor Link Scroll ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var id = this.getAttribute('href');
      if (id.length < 2) return;
      var target = document.querySelector(id);
      if (!target) return;
      
      e.preventDefault();
      var navWrapper = document.getElementById('navbarWrapper');
      var isScrolled = navWrapper && navWrapper.classList.contains('scrolled');
      var navh = isScrolled ? 74 : 86;
      var top = target.getBoundingClientRect().top + window.pageYOffset - navh;
      
      window.scrollTo({
        top: Math.max(0, top),
        behavior: reduceMotion ? 'auto' : 'smooth'
      });
    });
  });

  /* ---------- Active Nav Link Observer ---------- */
  var sectionIds = ['who-we-are', 'services', 'features', 'faq', 'contact'];
  var sections = sectionIds.map(function (id) {
    return document.getElementById(id);
  }).filter(Boolean);
  var navAnchors = document.querySelectorAll('.nav-links a, .mobile-panel .mobile-link');

  function setActive(id) {
    navAnchors.forEach(function (a) {
      a.classList.toggle('active', a.dataset.nav === id);
    });
  }

  var activeObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        setActive(entry.target.id);
      }
    });
  }, { rootMargin: '-30% 0px -40% 0px', threshold: 0 });

  sections.forEach(function (s) {
    if (s) activeObserver.observe(s);
  });

  /* ---------- Scroll Reveal Animations ---------- */
  var revealEls = document.querySelectorAll('.reveal, .reveal-l, .reveal-r');
  var revealObserver = new IntersectionObserver(function (entries, obs) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  revealEls.forEach(function (el) {
    revealObserver.observe(el);
  });

  /* ---------- FAQ Accordion ---------- */
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    var btn = item.querySelector('.faq-q');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      faqItems.forEach(function (other) {
        other.classList.remove('open');
        var otherBtn = other.querySelector('.faq-q');
        if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* ---------- Animated Loan Journey Flow ---------- */
  var steps = document.querySelectorAll('.journey-step');
  var progressLine = document.getElementById('journeyProgress');
  var orb = document.getElementById('journeyOrb');
  var currentStep = 0;
  var stepCount = steps.length;
  var journeyTimer = null;

  function updateJourneyStep(index) {
    currentStep = index;
    steps.forEach(function (step, i) {
      step.classList.toggle('active', i === index);
    });

    // Progress line & traveling light orb percentages
    var positions = [15, 50, 85];
    var pct = positions[index] || 15;

    if (progressLine) progressLine.style.width = pct + '%';
    if (orb) orb.style.left = pct + '%';
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
    step.addEventListener('click', function () {
      updateJourneyStep(i);
      startJourneyAnimation();
    });

    step.addEventListener('mouseenter', function () {
      updateJourneyStep(i);
      if (journeyTimer) clearInterval(journeyTimer);
    });

    step.addEventListener('mouseleave', function () {
      startJourneyAnimation();
    });
  });

  if (steps.length > 0) {
    updateJourneyStep(0);
    startJourneyAnimation();
  }

  /* ---------- Contact Card Click to Copy Effect ---------- */
  var contactCards = document.querySelectorAll('.contact-card');
  contactCards.forEach(function (card) {
    card.addEventListener('click', function () {
      var copyText = card.getAttribute('data-copy');
      if (!copyText) return;

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(copyText).then(function () {
          showToast('Copied: ' + copyText);
        });
      } else {
        showToast('Contact: ' + copyText);
      }
    });
  });

  function showToast(message) {
    var toast = document.querySelector('.toast-notice');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'toast-notice';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(function () {
      toast.classList.remove('show');
    }, 2500);
  }

})();


