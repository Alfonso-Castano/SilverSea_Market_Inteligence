(function () {
  'use strict';

  /* ========================================
     Count-up animation
     ======================================== */
  function animateCount(el, target, duration) {
    duration = duration || 1200;
    if (target === 0) { el.textContent = '0'; return; }
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ========================================
     Dark mode toggle
     ======================================== */
  function initThemeToggle() {
    var toggle = document.getElementById('theme-toggle');
    var dot = document.getElementById('theme-toggle-dot');
    var iconLight = document.getElementById('theme-icon-light');
    var iconDark = document.getElementById('theme-icon-dark');
    if (!toggle) return;

    function updateVisuals() {
      var isDark = document.documentElement.classList.contains('dark');
      if (isDark) {
        dot.style.transform = 'translateX(24px)';
        iconLight.classList.add('hidden');
        iconDark.classList.remove('hidden');
      } else {
        dot.style.transform = 'translateX(0)';
        iconLight.classList.remove('hidden');
        iconDark.classList.add('hidden');
      }
    }

    toggle.addEventListener('click', function () {
      document.documentElement.classList.toggle('dark');
      var isDark = document.documentElement.classList.contains('dark');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
      updateVisuals();
    });

    updateVisuals();
  }

  /* ========================================
     Scroll progress bar
     ======================================== */
  function initScrollProgress() {
    var bar = document.getElementById('scroll-progress');
    if (!bar) return;
    window.addEventListener('scroll', function () {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      var progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = progress + '%';
    }, { passive: true });
  }

  /* ========================================
     Sticky scroll nav visibility
     ======================================== */
  function initScrollNav() {
    var scrollNav = document.getElementById('scroll-nav');
    var hero = document.getElementById('hero');
    if (!scrollNav || !hero) return;

    var observer = new IntersectionObserver(function (entries) {
      var heroVisible = entries[0].isIntersecting;
      if (heroVisible) {
        scrollNav.style.opacity = '0';
        scrollNav.style.transform = 'translateY(-8px)';
        scrollNav.classList.add('pointer-events-none');
      } else {
        scrollNav.style.opacity = '1';
        scrollNav.style.transform = 'translateY(0)';
        scrollNav.classList.remove('pointer-events-none');
      }
    }, { threshold: 0.1 });
    observer.observe(hero);

    // Active section highlighting
    var navLinks = document.querySelectorAll('.scroll-nav-link');
    if (navLinks.length === 0) return;
    var sections = [];
    navLinks.forEach(function (link) {
      var id = link.getAttribute('href').replace('#', '');
      var section = document.getElementById(id);
      if (section) sections.push({ el: section, link: link });
    });

    if (sections.length > 0) {
      var sectionObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var match = sections.find(function (s) { return s.el === entry.target; });
          if (match && entry.isIntersecting) {
            navLinks.forEach(function (l) { l.classList.remove('bg-white/15', 'text-white'); });
            match.link.classList.add('bg-white/15', 'text-white');
          }
        });
      }, { rootMargin: '-20% 0px -60% 0px', threshold: 0 });
      sections.forEach(function (s) { sectionObserver.observe(s.el); });
    }
  }

  /* ========================================
     Entity group collapse/expand
     ======================================== */
  function initEntityGroups() {
    document.querySelectorAll('.entity-group-toggle').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var group = btn.closest('.entity-group');
        if (group) group.classList.toggle('open');
      });
    });
  }

  /* ========================================
     Signal spotlight — inline focus mode
     ======================================== */
  function initSpotlight() {
    var overlay = document.getElementById('spotlight-overlay');

    function closeSpotlight() {
      document.body.classList.remove('spotlight-mode');
      if (overlay) overlay.classList.add('hidden');
      document.querySelectorAll('.signal-card.spotlight-active').forEach(function (c) {
        c.classList.remove('spotlight-active');
      });
    }

    document.addEventListener('click', function (e) {
      var card = e.target.closest('.signal-card');

      // If clicking a link inside the card, let it through
      if (e.target.closest('a')) return;

      if (card) {
        // If this card is already spotlighted, close
        if (card.classList.contains('spotlight-active')) {
          closeSpotlight();
          return;
        }
        // Close any existing spotlight first
        closeSpotlight();
        // Activate this card
        card.classList.add('spotlight-active');
        document.body.classList.add('spotlight-mode');
        if (overlay) overlay.classList.remove('hidden');
        // Scroll card into comfortable view
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });

    // Click overlay to dismiss
    if (overlay) {
      overlay.addEventListener('click', closeSpotlight);
    }

    // Escape key to dismiss
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeSpotlight();
    });
  }

  /* ========================================
     Staggered AOS delays for card grids
     ======================================== */
  function initStaggeredEntrance() {
    document.querySelectorAll('.signal-grid').forEach(function (grid) {
      var cards = grid.querySelectorAll('[data-aos]');
      cards.forEach(function (card, i) {
        card.setAttribute('data-aos-delay', String(i * 50));
      });
    });
  }

  /* ========================================
     Init all on DOMContentLoaded
     ======================================== */
  document.addEventListener('DOMContentLoaded', function () {
    // Count-up
    document.querySelectorAll('[data-count-target]').forEach(function (el) {
      var target = parseInt(el.getAttribute('data-count-target'), 10) || 0;
      animateCount(el, target);
    });

    initThemeToggle();
    initScrollProgress();
    initScrollNav();
    initEntityGroups();
    initSpotlight();
    initStaggeredEntrance();
  });

  window.animateCount = animateCount;
})();
