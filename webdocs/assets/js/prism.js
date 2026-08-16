(function () {
  "use strict";

  var STORAGE_KEY = "prism-theme";

  function getTheme() {
    try {
      var saved = localStorage.getItem(STORAGE_KEY);

      if (saved === "dark" || saved === "light") {
        return saved;
      }
    } catch (error) {
    }

    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function setTheme(theme) {
    document.documentElement.dataset.theme = theme;

    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    var themeButtons = document.querySelectorAll("[data-theme-toggle]");

    themeButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        var current = document.documentElement.dataset.theme;
        setTheme(current === "dark" ? "light" : "dark");
      });
    });

    var copyButtons = document.querySelectorAll("[data-copy-target]");

    copyButtons.forEach(function (button) {
      button.addEventListener("click", async function () {
        var targetId = button.getAttribute("data-copy-target");
        var target = document.getElementById(targetId);

        if (!target) {
          return;
        }

        var text = target.innerText;

        try {
          await navigator.clipboard.writeText(text);

          var oldText = button.textContent;
          button.textContent = "Copied";

          setTimeout(function () {
            button.textContent = oldText;
          }, 1200);
        } catch (error) {
          button.textContent = "Copy failed";

          setTimeout(function () {
            button.textContent = "Copy";
          }, 1200);
        }
      });
    });
  });
})();
