(function () {
  "use strict";

  // ── Theme dropdown with System/Light/Dark button group ──
  function initTheme() {
    var btn = document.getElementById("theme-btn");
    var panel = document.getElementById("theme-panel");
    var group = document.getElementById("color-scheme-group");
    if (!btn || !panel || !group) return;

    var palette =
      document.documentElement.getAttribute("data-palette") || "default";
    var paletteClass =
      palette !== "default" ? "flydocs-palette-" + palette : "";
    var schemeIcons = { auto: "◑", light: "☀", dark: "☾" };
    var btnIcon = btn.querySelector("svg");

    function applyScheme(scheme) {
      var isDark;
      if (scheme === "dark") {
        isDark = true;
      } else if (scheme === "light") {
        isDark = false;
      } else {
        isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      }

      if (isDark) {
        document.documentElement.classList.add("pf-v6-theme-dark");
        if (paletteClass)
          document.documentElement.classList.add(paletteClass);
      } else {
        document.documentElement.classList.remove("pf-v6-theme-dark");
        if (paletteClass)
          document.documentElement.classList.remove(paletteClass);
      }

      var buttons = group.querySelectorAll(".flydocs-btn-group-item");
      buttons.forEach(function (b) {
        b.classList.toggle(
          "flydocs-btn-group-item--active",
          b.getAttribute("data-scheme") === scheme
        );
      });

      if (btnIcon) {
        btnIcon.style.display = "none";
      }
      Array.from(btn.childNodes).forEach(function (n) {
        if (n.nodeType === 3 && n.textContent.trim()) n.remove();
      });
      var iconText = document.createTextNode(schemeIcons[scheme] || "◑");
      btn.insertBefore(iconText, btn.querySelector(".flydocs-theme-chevron"));
    }

    var saved = localStorage.getItem("flydocs-theme");
    var current =
      saved === "light" || saved === "dark" || saved === "auto"
        ? saved
        : "auto";
    applyScheme(current);

    group.addEventListener("click", function (e) {
      var target = e.target.closest("[data-scheme]");
      if (!target) return;
      current = target.getAttribute("data-scheme");
      localStorage.setItem("flydocs-theme", current);
      applyScheme(current);
    });

    btn.addEventListener("click", function () {
      var open = panel.classList.toggle("flydocs-theme-panel--open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });

    document.addEventListener("click", function (e) {
      if (!e.target.closest("#theme-dropdown")) {
        panel.classList.remove("flydocs-theme-panel--open");
        btn.setAttribute("aria-expanded", "false");
      }
    });

    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", function () {
        if (current === "auto") applyScheme("auto");
      });
  }

  // ── Copy to clipboard ──
  function initCopyButtons() {
    document.querySelectorAll("pre").forEach(function (pre) {
      var btn = document.createElement("button");
      btn.className = "copy-btn";
      btn.textContent = "Copy";
      btn.addEventListener("click", function () {
        var code = pre.querySelector("code");
        var text = (code ? code.textContent : pre.textContent).trimEnd();
        navigator.clipboard
          .writeText(text)
          .then(function () {
            btn.textContent = "Copied!";
            btn.classList.add("copy-btn--copied");
            setTimeout(function () {
              btn.textContent = "Copy";
              btn.classList.remove("copy-btn--copied");
            }, 2000);
          })
          .catch(function () {
            btn.textContent = "Failed";
            setTimeout(function () {
              btn.textContent = "Copy";
            }, 2000);
          });
      });
      pre.style.position = "relative";
      pre.appendChild(btn);
    });
  }

  // ── Sidebar toggle (works on all viewports) ──
  function initSidebar() {
    var toggle = document.getElementById("sidebar-toggle");
    var sidebar = document.getElementById("sidebar");
    var backdrop = document.getElementById("backdrop");
    if (!toggle || !sidebar) return;

    var isMobile = function () {
      return window.innerWidth <= 768;
    };

    var savedCollapsed = localStorage.getItem("flydocs-sidebar-collapsed");
    if (savedCollapsed === "true" && !isMobile()) {
      sidebar.classList.add("flydocs-sidebar--collapsed");
    }

    toggle.addEventListener("click", function () {
      if (isMobile()) {
        var isOpen = sidebar.classList.toggle("flydocs-sidebar--open");
        if (backdrop)
          backdrop.classList.toggle("flydocs-backdrop--open", isOpen);
      } else {
        var collapsed = sidebar.classList.toggle(
          "flydocs-sidebar--collapsed"
        );
        localStorage.setItem("flydocs-sidebar-collapsed", collapsed);
      }
    });

    if (backdrop) {
      backdrop.addEventListener("click", function () {
        sidebar.classList.remove("flydocs-sidebar--open");
        backdrop.classList.remove("flydocs-backdrop--open");
      });
    }

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        sidebar.classList.remove("flydocs-sidebar--open");
        if (backdrop) backdrop.classList.remove("flydocs-backdrop--open");
      }
    });
  }

  // ── Init ──
  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initCopyButtons();
    initSidebar();
  });
})();
