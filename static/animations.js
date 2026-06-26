(function () {
  'use strict';

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

  document.addEventListener('DOMContentLoaded', function () {
    // Count-up for all elements with data-count-target
    document.querySelectorAll('[data-count-target]').forEach(function (el) {
      var target = parseInt(el.getAttribute('data-count-target'), 10) || 0;
      animateCount(el, target);
    });

    // Sticky scroll nav visibility
    var scrollNav = document.getElementById('scroll-nav');
    var hero = document.getElementById('hero');
    if (scrollNav && hero) {
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
    }

    // Active section highlighting in scroll nav
    var navLinks = document.querySelectorAll('.scroll-nav-link');
    if (navLinks.length > 0) {
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
            if (match) {
              if (entry.isIntersecting) {
                navLinks.forEach(function (l) { l.classList.remove('bg-white/15', 'text-white'); });
                match.link.classList.add('bg-white/15', 'text-white');
              }
            }
          });
        }, { rootMargin: '-20% 0px -60% 0px', threshold: 0 });

        sections.forEach(function (s) { sectionObserver.observe(s.el); });
      }
    }
  });

  window.animateCount = animateCount;
})();
