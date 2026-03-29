document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.querySelector('[data-nav-toggle]');
  const navLinks = document.querySelector('[data-nav-links]');
  const navSearchToggle = document.querySelector('[data-nav-search-toggle]');
  const navSearchPanel = document.querySelector('[data-nav-search-panel]');
  const navSearchWrap = document.querySelector('[data-nav-search-wrap]');

  const closeNavSearch = () => {
    if (!navSearchToggle || !navSearchPanel) return;
    navSearchPanel.classList.remove('open');
    navSearchToggle.setAttribute('aria-expanded', 'false');
  };

  if (navSearchToggle && navSearchPanel && navSearchWrap) {
    navSearchToggle.addEventListener('click', () => {
      const isOpen = navSearchPanel.classList.toggle('open');
      navSearchToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    document.addEventListener('click', (event) => {
      if (navSearchWrap.contains(event.target)) return;
      closeNavSearch();
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') closeNavSearch();
    });
  }

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      navToggle.textContent = isOpen ? 'Close' : 'Menu';
      if (isOpen) closeNavSearch();
    });

    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
        navToggle.textContent = 'Menu';
        closeNavSearch();
      });
    });
  }

  const targets = document.querySelectorAll(
    '.hero, .home-hero, .hero-inner, .section-head, .dash-header, .property-card, .card, .stat-card, .auth-box'
  );

  if (!('IntersectionObserver' in window)) {
    targets.forEach((el) => el.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -32px 0px' }
  );

  targets.forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = `${Math.min(i * 35, 220)}ms`;
    observer.observe(el);
  });
});
