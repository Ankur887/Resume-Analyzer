/**
 * main.js — Smart Resume Analyzer Frontend
 *
 * Modules (IIFE pattern, no globals leaked):
 *   1. Theme toggle (dark/light + localStorage + prefers-color-scheme)
 *   2. Mobile hamburger menu
 *   3. Flash / Toast system
 *   4. Upload zone (drag-drop, validation, progress)
 *   5. Dashboard — animated score rings & progress bars
 *   6. Dashboard — staggered skill tags & suggestions
 */

/* ═══════════════════════════════════════════════════════
   1. THEME TOGGLE
   Persists in localStorage; respects prefers-color-scheme
═══════════════════════════════════════════════════════ */
(function initTheme() {
  const root     = document.documentElement;
  const btn      = document.getElementById('theme-toggle');
  const icon     = document.getElementById('theme-icon');
  const DARK_CLS = 'dark';
  const LIGHT    = 'light';
  const DARK     = 'dark';
  const STORE_KEY = 'rsa_theme';

  function getPreferred() {
    const saved = localStorage.getItem(STORE_KEY);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? LIGHT : DARK;
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    if (icon) icon.textContent = theme === LIGHT ? '🌙' : '☀️';
    if (btn)  btn.setAttribute('aria-label', theme === LIGHT ? 'Switch to dark mode' : 'Switch to light mode');
  }

  applyTheme(getPreferred());

  if (btn) {
    btn.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === LIGHT ? DARK : LIGHT;
      applyTheme(next);
      try { localStorage.setItem(STORE_KEY, next); } catch (_) {}
    });
  }

  // Respond to OS preference changes (only when no saved pref)
  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
    if (!localStorage.getItem(STORE_KEY)) {
      applyTheme(e.matches ? LIGHT : DARK);
    }
  });
})();


/* ═══════════════════════════════════════════════════════
   2. MOBILE HAMBURGER MENU
═══════════════════════════════════════════════════════ */
(function initHamburger() {
  const burger = document.getElementById('hamburger');
  const drawer = document.getElementById('mobile-nav');
  if (!burger || !drawer) return;

  burger.addEventListener('click', () => {
    const open = drawer.classList.toggle('open');
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!burger.contains(e.target) && !drawer.contains(e.target)) {
      drawer.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    }
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      drawer.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
      burger.focus();
    }
  });
})();


/* ═══════════════════════════════════════════════════════
   3. TOAST / FLASH SYSTEM
   Usage: window.showToast('msg', 'success'|'error'|'warning'|'info', durationMs)
═══════════════════════════════════════════════════════ */
(function initToasts() {
  const ICONS = {
    success: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
    error:   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>',
    warning: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    info:    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
  };

  window.showToast = function(msg, type = 'error', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.setAttribute('role', 'alert');

    // Build content safely (no innerHTML for user text)
    const iconSpan = document.createElement('span');
    iconSpan.className = 'toast-icon';
    iconSpan.innerHTML = ICONS[type] || ICONS.info;

    const msgSpan = document.createElement('span');
    msgSpan.className = 'toast-msg';
    msgSpan.textContent = msg;

    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.setAttribute('aria-label', 'Dismiss notification');
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', () => dismiss(toast));

    toast.appendChild(iconSpan);
    toast.appendChild(msgSpan);
    toast.appendChild(closeBtn);
    container.appendChild(toast);

    const timer = setTimeout(() => dismiss(toast), duration);
    toast._dismissTimer = timer;
  };

  function dismiss(toast) {
    clearTimeout(toast._dismissTimer);
    toast.classList.add('toast-dismiss');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
    setTimeout(() => { if (toast.parentNode) toast.remove(); }, 500);
  }

  // Auto-dismiss Jinja flash messages
  document.querySelectorAll('.flash').forEach((el, i) => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 400);
    }, 4500 + i * 600);
  });
})();


/* ═══════════════════════════════════════════════════════
   4. UPLOAD ZONE — Drag & Drop, Validation, Progress
═══════════════════════════════════════════════════════ */
(function initUploadZone() {
  const zone       = document.getElementById('upload-zone');
  const fileInput  = document.getElementById('resume-file');
  const fileInfo   = document.getElementById('file-selected-info');
  const fileName   = document.getElementById('selected-file-name');
  const form       = document.getElementById('upload-form');
  const submitBtn  = document.getElementById('submit-btn');
  const zoneErr    = document.getElementById('zone-error');
  const progressBar = document.getElementById('upload-progress');
  const progressFill = document.getElementById('upload-progress-fill');

  if (!zone) return; // not on upload page

  // Click zone → trigger file input
  zone.addEventListener('click', (e) => {
    if (!e.target.closest('#file-selected-info') && !e.target.closest('#zone-error')) {
      fileInput.click();
    }
  });

  // Keyboard activation
  zone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  });

  // File selected via dialog
  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFileSelection(fileInput.files[0]);
  });

  // Drag events
  ['dragenter', 'dragover'].forEach(evt => {
    zone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.add('drag-over');
    });
  });

  ['dragleave', 'dragend'].forEach(evt => {
    zone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      zone.classList.remove('drag-over');
    });
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      handleFileSelection(file);
    }
  });

  function handleFileSelection(file) {
    clearZoneError();

    const ext = file.name.split('.').pop().toLowerCase();
    const MAX_SIZE = 5 * 1024 * 1024;

    if (!['pdf', 'docx'].includes(ext)) {
      showZoneError('Only PDF and DOCX files are supported.');
      return;
    }

    if (file.size > MAX_SIZE) {
      showZoneError(`File too large (${(file.size / 1048576).toFixed(1)} MB). Max: 5 MB.`);
      return;
    }

    // Success state
    fileName.textContent = `${file.name}  (${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.classList.add('visible');
    zone.classList.remove('has-error');
    zone.style.borderColor = 'var(--success)';
  }

  function showZoneError(msg) {
    zoneErr.textContent = msg;
    zoneErr.classList.add('visible');
    zone.classList.add('has-error');
    zone.style.borderColor = '';
    fileInput.value = '';
    fileInfo.classList.remove('visible');
  }

  function clearZoneError() {
    zoneErr.textContent = '';
    zoneErr.classList.remove('visible');
    zone.classList.remove('has-error');
    zone.style.borderColor = '';
  }

  // Form submit — validate then show loading state with fake progress
  if (form) {
    form.addEventListener('submit', (e) => {
      if (!fileInput.files.length) {
        e.preventDefault();
        showZoneError('Please select a resume file before submitting.');
        return;
      }

      const role = document.getElementById('target-role')?.value;
      if (!role) {
        e.preventDefault();
        showZoneError('Please select a target role.');
        return;
      }

      // Show loading
      submitBtn.classList.add('loading');
      submitBtn.setAttribute('aria-busy', 'true');
      submitBtn.disabled = true;

      // Fake progress animation for perceived speed
      if (progressBar && progressFill) {
        progressBar.classList.add('visible');
        let pct = 0;
        const tick = setInterval(() => {
          pct = Math.min(pct + Math.random() * 12, 85);
          progressFill.style.width = pct + '%';
          if (pct >= 85) clearInterval(tick);
        }, 300);
      }
    });
  }
})();


/* ═══════════════════════════════════════════════════════
   5. DASHBOARD — Animated Score Rings & Counters
═══════════════════════════════════════════════════════ */
(function initScoreRings() {
  const rings = document.querySelectorAll('.score-ring-progress');
  if (!rings.length) return;

  const CIRCUMFERENCE = 440; // 2π × r=70 ≈ 440

  function animateRing(ring) {
    const score  = parseFloat(ring.dataset.score) || 0;
    const offset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        ring.style.strokeDashoffset = offset;
      });
    });
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateRing(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  rings.forEach(ring => observer.observe(ring));

  // Animate score counters
  document.querySelectorAll('.score-number[data-target]').forEach(el => {
    const target   = parseFloat(el.dataset.target) || 0;
    const duration = 1600;
    const startTs  = performance.now();

    function update(now) {
      const elapsed  = now - startTs;
      const progress = Math.min(elapsed / duration, 1);
      const eased    = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      el.textContent = Math.round(eased * target);
      if (progress < 1) requestAnimationFrame(update);
    }

    // Small delay so it syncs with ring animation start
    setTimeout(() => requestAnimationFrame(update), 200);
  });
})();


/* ═══════════════════════════════════════════════════════
   6. DASHBOARD — Progress Bars (IntersectionObserver)
═══════════════════════════════════════════════════════ */
(function initProgressBars() {
  const bars = document.querySelectorAll('.progress-bar-fill[data-width]');
  if (!bars.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const pct = entry.target.dataset.width;
        entry.target.style.width = pct + '%';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  bars.forEach(bar => observer.observe(bar));
})();


/* ═══════════════════════════════════════════════════════
   7. STAGGERED ANIMATIONS — skill tags, suggestions
═══════════════════════════════════════════════════════ */
(function initStaggered() {
  document.querySelectorAll('.skill-tag').forEach((tag, i) => {
    tag.style.animationDelay = `${i * 0.045}s`;
  });

  document.querySelectorAll('.suggestion-item').forEach((item, i) => {
    item.style.animationDelay = `${i * 0.07}s`;
  });

  document.querySelectorAll('.fade-in').forEach((el, i) => {
    if (!el.style.animationDelay) {
      el.style.animationDelay = `${i * 0.08}s`;
    }
  });
})();
