(function() {
  'use strict';

  // ── Theme toggle (three-way: light → dark → auto) ──
  function initTheme() {
    var toggle = document.getElementById('theme-toggle');
    if (!toggle) return;

    var icons = { light: '☀', dark: '☾', auto: '◑' };
    var labels = { light: 'Light mode (click for dark)', dark: 'Dark mode (click for auto)', auto: 'Auto mode (click for light)' };
    var cycle = { light: 'dark', dark: 'auto', auto: 'light' };
    var palette = document.documentElement.getAttribute('data-palette') || 'default';
    var paletteClass = palette !== 'default' ? 'flydocs-palette-' + palette : '';

    function applyTheme(mode) {
      var isDark;
      if (mode === 'dark') {
        isDark = true;
      } else if (mode === 'light') {
        isDark = false;
      } else {
        isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      }

      if (isDark) {
        document.documentElement.classList.add('pf-v6-theme-dark');
        if (paletteClass) document.documentElement.classList.add(paletteClass);
      } else {
        document.documentElement.classList.remove('pf-v6-theme-dark');
        if (paletteClass) document.documentElement.classList.remove(paletteClass);
      }
      toggle.textContent = icons[mode];
      toggle.setAttribute('aria-label', labels[mode]);
    }

    var saved = localStorage.getItem('flydocs-theme');
    var current = (saved === 'light' || saved === 'dark' || saved === 'auto') ? saved : 'auto';
    applyTheme(current);

    toggle.addEventListener('click', function() {
      current = cycle[current];
      localStorage.setItem('flydocs-theme', current);
      applyTheme(current);
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function() {
      if (current === 'auto') applyTheme('auto');
    });
  }

  // ── Copy to clipboard ──
  function initCopyButtons() {
    document.querySelectorAll('pre').forEach(function(pre) {
      var btn = document.createElement('button');
      btn.className = 'copy-btn';
      btn.textContent = 'Copy';
      btn.addEventListener('click', function() {
        var code = pre.querySelector('code');
        var text = (code ? code.textContent : pre.textContent).trimEnd();
        navigator.clipboard.writeText(text).then(function() {
          btn.textContent = 'Copied!';
          btn.classList.add('copy-btn--copied');
          setTimeout(function() { btn.textContent = 'Copy'; btn.classList.remove('copy-btn--copied'); }, 2000);
        }).catch(function() {
          btn.textContent = 'Failed';
          setTimeout(function() { btn.textContent = 'Copy'; }, 2000);
        });
      });
      pre.style.position = 'relative';
      pre.appendChild(btn);
    });
  }

  // ── Mobile sidebar toggle ──
  function initSidebar() {
    var toggle = document.getElementById('sidebar-toggle');
    var sidebar = document.getElementById('sidebar');
    var backdrop = document.getElementById('backdrop');
    if (!toggle || !sidebar) return;

    function openSidebar() {
      sidebar.classList.add('flydocs-sidebar--open');
      if (backdrop) backdrop.classList.add('flydocs-backdrop--open');
    }

    function closeSidebar() {
      sidebar.classList.remove('flydocs-sidebar--open');
      if (backdrop) backdrop.classList.remove('flydocs-backdrop--open');
    }

    toggle.addEventListener('click', function() {
      if (sidebar.classList.contains('flydocs-sidebar--open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });

    if (backdrop) {
      backdrop.addEventListener('click', closeSidebar);
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') closeSidebar();
    });
  }

  // ── Init ──
  document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initCopyButtons();
    initSidebar();
  });
})();
