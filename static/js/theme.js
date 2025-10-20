(function(){
  const storageKey = 'theme';
  const root = document.documentElement; // toggle .dark on <html>

  function preferred() {
    const saved = localStorage.getItem(storageKey);
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function setTheme(mode) {
    const isDark = mode === 'dark';
    root.classList.toggle('dark', isDark);
    localStorage.setItem(storageKey, mode);
    updateToggle();
  }

  function updateToggle() {
    const btn = document.getElementById('theme-toggle');
    const icon = document.getElementById('theme-icon');
    const label = document.getElementById('theme-text');
    if (!btn || !icon || !label) return;
    const isDark = root.classList.contains('dark');
    if (isDark) {
      icon.className = 'fas fa-sun';
      label.textContent = '浅色';
      btn.setAttribute('aria-pressed', 'true');
      btn.setAttribute('title', '切换为浅色');
    } else {
      icon.className = 'fas fa-moon';
      label.textContent = '深色';
      btn.setAttribute('aria-pressed', 'false');
      btn.setAttribute('title', '切换为深色');
    }
  }

  function toggle() {
    setTheme(root.classList.contains('dark') ? 'light' : 'dark');
  }

  function init() {
    setTheme(preferred());
    const btn = document.getElementById('theme-toggle');
    if (btn) {
      btn.addEventListener('click', toggle);
      btn.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggle();
        }
      });
    }
    if (window.matchMedia) {
      const mm = window.matchMedia('(prefers-color-scheme: dark)');
      if (mm.addEventListener) {
        mm.addEventListener('change', (e) => {
          const saved = localStorage.getItem(storageKey);
          if (!saved) setTheme(e.matches ? 'dark' : 'light');
        });
      }
    }
  }

  window.Theme = { init, set: setTheme, toggle };
  document.addEventListener('DOMContentLoaded', init);
})();
