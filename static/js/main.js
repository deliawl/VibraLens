/* ============================================================
   VIBRALENS · MAIN SCRIPT
   ============================================================ */

/* ============ LUCIDE ============ */
function renderIcons(root = document) {
  if (window.lucide) {
    lucide.createIcons({ nameAttr: 'data-lucide', attrs: {}, root });
  }
}
function setIcon(selector, name) {
  const el = document.querySelector(selector);
  if (el) el.setAttribute('data-lucide', name);
  return el;
}

/* ============ TOAST ============ */
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const iconName = type === 'success' ? 'check-circle' : 'info';
  const toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.innerHTML = `
    <span class="toast-icon"><i data-lucide="${iconName}"></i></span>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  renderIcons();
  setTimeout(() => {
    toast.classList.add('hide');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}
window.showToast = showToast;

/* ============ THEME ============ */
const html = document.documentElement;
let themeInitialized = false;

function applyTheme(theme) {
  html.setAttribute('data-theme', theme);
  localStorage.setItem('vibra-theme', theme);
  const isDark = theme === 'dark';
  setIcon('#themeIcon', isDark ? 'moon' : 'sun');
  renderIcons();
  document.dispatchEvent(new Event('themechange'));

  if (themeInitialized) {
    const lang = localStorage.getItem('vibra-lang') || 'id';
    const msg = isDark
      ? (lang === 'id' ? 'Mode gelap aktif' : 'Dark mode enabled')
      : (lang === 'id' ? 'Mode terang aktif' : 'Light mode enabled');
    showToast(msg, 'info');
  }
  themeInitialized = true;
}

function initTheme() {
  const saved = localStorage.getItem('vibra-theme');
  const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  applyTheme(saved || (prefersLight ? 'light' : 'dark'));
}

function toggleTheme() {
  const cur = html.getAttribute('data-theme');
  applyTheme(cur === 'dark' ? 'light' : 'dark');
}

document.getElementById('themeBtn')?.addEventListener('click', toggleTheme);
initTheme();

/* ============ DRAWER ============ */
const drawer = document.getElementById('drawer');
const drawerOverlay = document.getElementById('drawerOverlay');

function openDrawer() {
  drawer?.classList.add('open');
  drawerOverlay?.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeDrawer() {
  drawer?.classList.remove('open');
  drawerOverlay?.classList.remove('open');
  document.body.style.overflow = '';
}

document.getElementById('menuToggle')?.addEventListener('click', openDrawer);
document.getElementById('drawerClose')?.addEventListener('click', closeDrawer);
drawerOverlay?.addEventListener('click', closeDrawer);

/* ============ SCROLL PROGRESS ============ */
function initScrollProgress() {
  const bar = document.getElementById('scrollProgress');
  if (!bar) return;
  function update() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
    bar.style.width = Math.min(progress, 100) + '%';
  }
  window.addEventListener('scroll', update, { passive: true });
  update();
}

/* ============ COUNTER ANIMATION ============ */
function animateCounter(el, target, duration = 1400, decimals = 0) {
  if (!el) return;
  const startTime = performance.now();
  const isFloat = decimals > 0;
  const suffixEl = el.querySelector('small');
  const suffix = suffixEl ? suffixEl.outerHTML : '';
  el.classList.add('is-animating');

  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = target * eased;
    const formatted = isFloat ? value.toFixed(decimals) : Math.round(value).toString();
    el.innerHTML = formatted + suffix;
    if (progress < 1) requestAnimationFrame(tick);
    else {
      el.classList.remove('is-animating');
      const final = isFloat ? target.toFixed(decimals) : target.toString();
      el.innerHTML = final + suffix;
    }
  }
  requestAnimationFrame(tick);
}

function initCounters() {
  document.querySelectorAll('.ringkasan-value').forEach(el => {
    const text = el.textContent.trim();
    const match = text.match(/^([\d.,]+)/);
    if (!match) return;
    const raw = match[1].replace(',', '.');
    const value = parseFloat(raw);
    if (isNaN(value)) return;
    const decimals = raw.includes('.') ? raw.split('.')[1].length : 0;
    const suffixEl = el.querySelector('small');
    const suffix = suffixEl ? suffixEl.outerHTML : '';
    el.innerHTML = '0' + suffix;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(el, value, 1400, decimals);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.4 });
    observer.observe(el);
  });
}

/* ============ CARD RIPPLE ============ */
function initCardRipple() {
  document.querySelectorAll('.fitur-card').forEach(card => {
    card.addEventListener('click', function(e) {
      const rect = card.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.className = 'ripple';
      const size = Math.max(rect.width, rect.height);
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      card.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });
}

/* ============ LANGUAGE ============ */
const I18N = {
  id: {
    // brand & nav
    'brand.sub': 'Prodi Geofisika · Universitas Padjadjaran',
    'search.ph': 'Cari fitur, node, event…',
    'user.login': 'Masuk',
    'nav.home': 'Beranda',

    // hero
    'hero.title': 'Selamat Datang di VibraLens',
    'hero.desc': 'Sistem pemantauan getaran tanah real-time berbasis IoT dengan analisis Horizontal-to-Vertical Spectral Ratio (HVSR) untuk microzonasi seismik di kawasan Jatinangor, Universitas Padjadjaran.',
    'hero.more': 'Pelajari',
    'hero.cta.primary': 'Buka Dashboard',

    // stats hero
    'stat.node': 'Node',
    'stat.online': 'Online',
    'stat.monitoring': 'Monitoring',
    'stat.latency': 'Latency',
    'stat.method': 'Metode',

    // ringkasan sistem
    'ringkasan.eyebrow': 'Live Data',
    'ringkasan.title': 'Ringkasan Sistem',
    'ringkasan.live': 'Live',
    'ringkasan.total': 'Total Node',
    'ringkasan.online': 'Node Online',
    'ringkasan.pgv': 'PGV Maksimum',
    'ringkasan.update': 'Update Terakhir',
    'ringkasan.chart.title': 'PGV 24 Jam Terakhir',

    // HVSR
    'hvsr.eyebrow': 'Analisis Mikroseismik',
    'hvsr.title': 'Parameter HVSR',
    'hvsr.sub': 'Hasil pengolahan Horizontal-to-Vertical Spectral Ratio dari sinyal ambient noise.',
    'hvsr.f0': 'Frekuensi Dominan',
    'hvsr.f0.hint': 'Frekuensi natural tanah',
    'hvsr.a0': 'Amplifikasi',
    'hvsr.a0.hint': 'Penguatan getaran oleh tanah',
    'hvsr.kg': 'Indeks Kerentanan',
    'hvsr.kg.hint': 'A₀² / f₀ — Kanai',
    'hvsr.chart.title': 'Kurva HVSR Rata-rata',
    'hvsr.tbl.node': 'Node',
    'hvsr.tbl.zona': 'Zona Kerentanan',

    // fitur
    'fitur.eyebrow': 'Modul Utama',
    'fitur.title': 'Fitur Tersedia',
    'fitur.sub': 'Enam modul terintegrasi untuk pemantauan, analisis, dan pengelolaan data getaran.',
    'fitur.open': 'Buka',
    'fitur.live': 'LIVE',
    'fitur.monitoring': 'Monitoring Real-Time',
    'fitur.event': 'Event & Alarm',
    'fitur.analisis': 'Analisis Sinyal',
    'fitur.peta': 'Peta & Jaringan',
    'fitur.riwayat': 'Riwayat & Ekspor',
    'fitur.pengaturan': 'Pengaturan Sistem',

    // cara kerja
    'cara.eyebrow': 'Alur Sistem',
    'cara.title': 'Bagaimana VibraLens Bekerja',
    'cara.sub': 'Dari sensor di lapangan sampai analisis HVSR di layar Anda.',
    'cara.step1.title': 'Geophone',
    'cara.step1.desc': 'Sensor menangkap getaran tanah di lokasi pemasangan.',
    'cara.step2.title': 'Node LoRa',
    'cara.step2.desc': 'Data dikirim nirkabel lewat LoRa ke gateway terdekat.',
    'cara.step3.title': 'Analisis HVSR',
    'cara.step3.desc': 'Rasio spektrum H/V dihitung untuk ekstraksi f₀, A₀, K_g.',
    'cara.step4.title': 'Microzonasi',
    'cara.step4.desc': 'Peta zona kerentanan seismik kawasan kampus.',

    // FAQ
    'faq.eyebrow': 'Pertanyaan',
    'faq.title': 'Sering Ditanyakan',
    'faq.q1': 'Apa itu metode HVSR?',
    'faq.a1': 'HVSR (Horizontal-to-Vertical Spectral Ratio) adalah metode analisis mikroseismik yang memanfaatkan sinyal ambient noise untuk mengestimasi frekuensi dominan (f₀) dan amplifikasi (A₀) lapisan tanah. Diperkenalkan oleh Nakamura (1989).',
    'faq.q2': 'Apa arti f₀, A₀, dan K_g?',
    'faq.a2': 'f₀ adalah frekuensi dominan (Hz) — frekuensi natural tanah. A₀ adalah amplifikasi (rasio) — seberapa besar getaran diperkuat. K_g = A₀²/f₀ adalah indeks kerentanan seismik (Kanai).',
    'faq.q3': 'Bagaimana cara membaca zona kerentanan?',
    'faq.a3': 'K_g < 3 = aman, 3–10 = sedang, > 10 = rawan. Nilai K_g tinggi berarti tanah lebih rentan terhadap amplifikasi goncangan gempa.',
    'faq.q4': 'Seberapa sering data di-update?',
    'faq.a4': 'Data sensor dikirim setiap 10 detik. Analisis HVSR dilakukan per window 30 menit untuk stabilitas statistik.',

    // CTA
    'cta.title': 'Siap memetakan kerentanan seismik kampus?',
    'cta.sub': 'Semua parameter HVSR terintegrasi dalam satu dashboard. Mulai eksplorasi sekarang.',
    'cta.primary': 'Analisis HVSR',
    'cta.secondary': 'Lihat Peta Microzonasi',

    // about
    'about.title': 'Tentang VibraLens',
    'about.bg': 'Latar Belakang',
    'about.bg.text': 'VibraLens dikembangkan sebagai bagian dari tugas akhir Program Studi Geofisika, Universitas Padjadjaran, untuk menganalisis kerentanan seismik kawasan kampus Jatinangor menggunakan metode HVSR berbasis IoT.',
    'about.obj': 'Tujuan',
    'about.obj.text': 'Mengestimasi parameter f₀, A₀, dan K_g dari sinyal ambient noise untuk microzonasi seismik kawasan kampus.',
    'about.how': 'Cara Kerja',
    'about.how.text': 'Geophone → Node LoRa → Gateway LTE → Server → Analisis HVSR → Dashboard.',

    // common
    'back': 'Kembali ke Beranda',
    'placeholder.text': 'Halaman ini masih kosong — konten akan diisi pada tahap berikutnya.',

    // peta
    'peta.legend': 'Status Node',

    // 404
    'err.404.title': 'Halaman tidak ditemukan',
    'err.404.desc': 'Halaman yang Anda cari mungkin telah dipindahkan, dihapus, atau tidak pernah ada.',
    'err.404.cta': 'Kembali ke Beranda',

    // footer
    'footer.desc': 'Sistem pemantauan getaran tanah berbasis IoT dengan analisis HVSR untuk microzonasi seismik di kawasan Jatinangor.',
    'footer.col.product': 'Produk',
    'footer.col.help': 'Bantuan',
    'footer.col.contact': 'Kontak',
    'footer.guide': 'Panduan Pengguna',
    'footer.glossary': 'Glosarium HVSR',
    'footer.method': 'Metodologi Mikroseismik',
    'footer.reference': 'Referensi Nakamura & Kanai',
    'footer.about': 'Tentang',
    'footer.docs': 'Dokumentasi',
    'footer.faq': 'FAQ',
    'footer.contact': 'Kontak',
    'footer.privacy': 'Kebijakan Privasi',
    'footer.terms': 'Syarat & Ketentuan',
        // placeholder v2
    'placeholder.dev': 'Dalam Pengembangan',
    'placeholder.home': 'Kembali ke Beranda',
    'placeholder.catalog': 'Buka Katalog Data',
    'placeholder.related': 'Modul Lain yang Sudah Tersedia',
  },
  en: {
    // brand & nav
    'brand.sub': 'Geophysics Dept · Padjadjaran University',
    'search.ph': 'Search features, nodes, events…',
    'user.login': 'Sign in',
    'nav.home': 'Home',

    // hero
    'hero.title': 'Welcome to VibraLens',
    'hero.desc': 'IoT-based real-time ground vibration monitoring system with Horizontal-to-Vertical Spectral Ratio (HVSR) analysis for seismic microzonation in the Jatinangor area, Padjadjaran University.',
    'hero.more': 'Learn more',
    'hero.cta.primary': 'Open Dashboard',

    // stats hero
    'stat.node': 'Nodes',
    'stat.online': 'Online',
    'stat.monitoring': 'Monitoring',
    'stat.latency': 'Latency',
    'stat.method': 'Method',

    // ringkasan
    'ringkasan.eyebrow': 'Live Data',
    'ringkasan.title': 'System Summary',
    'ringkasan.live': 'Live',
    'ringkasan.total': 'Total Nodes',
    'ringkasan.online': 'Nodes Online',
    'ringkasan.pgv': 'Max PGV',
    'ringkasan.update': 'Last Update',
    'ringkasan.chart.title': 'PGV Last 24 Hours',

    // HVSR
    'hvsr.eyebrow': 'Microseismic Analysis',
    'hvsr.title': 'HVSR Parameters',
    'hvsr.sub': 'Horizontal-to-Vertical Spectral Ratio analysis from ambient noise signals.',
    'hvsr.f0': 'Dominant Frequency',
    'hvsr.f0.hint': 'Natural frequency of the soil',
    'hvsr.a0': 'Amplification',
    'hvsr.a0.hint': 'Ground motion amplification factor',
    'hvsr.kg': 'Vulnerability Index',
    'hvsr.kg.hint': 'A₀² / f₀ — Kanai',
    'hvsr.chart.title': 'Average HVSR Curve',
    'hvsr.tbl.node': 'Node',
    'hvsr.tbl.zona': 'Vulnerability Zone',

    // fitur
    'fitur.eyebrow': 'Main Modules',
    'fitur.title': 'Available Features',
    'fitur.sub': 'Six integrated modules for monitoring, analysis, and data management.',
    'fitur.open': 'Open',
    'fitur.live': 'LIVE',
    'fitur.monitoring': 'Real-Time Monitoring',
    'fitur.event': 'Events & Alarms',
    'fitur.analisis': 'Signal Analysis',
    'fitur.peta': 'Map & Network',
    'fitur.riwayat': 'History & Export',
    'fitur.pengaturan': 'System Settings',

    // cara kerja
    'cara.eyebrow': 'System Flow',
    'cara.title': 'How VibraLens Works',
    'cara.sub': 'From field sensors to HVSR analysis on your screen.',
    'cara.step1.title': 'Geophone',
    'cara.step1.desc': 'The sensor captures ground vibration at its location.',
    'cara.step2.title': 'LoRa Node',
    'cara.step2.desc': 'Data is sent wirelessly via LoRa to the nearest gateway.',
    'cara.step3.title': 'HVSR Analysis',
    'cara.step3.desc': 'H/V spectral ratios computed to extract f₀, A₀, K_g.',
    'cara.step4.title': 'Microzonation',
    'cara.step4.desc': 'Seismic vulnerability map of the campus area.',

    // FAQ
    'faq.eyebrow': 'FAQ',
    'faq.title': 'Frequently Asked',
    'faq.q1': 'What is the HVSR method?',
    'faq.a1': 'HVSR (Horizontal-to-Vertical Spectral Ratio) is a microseismic analysis method that uses ambient noise to estimate the dominant frequency (f₀) and amplification (A₀) of soil layers. Introduced by Nakamura (1989).',
    'faq.q2': 'What do f₀, A₀, and K_g mean?',
    'faq.a2': 'f₀ is the dominant frequency (Hz) — the natural frequency of the soil. A₀ is amplification (ratio) — how much ground motion is amplified. K_g = A₀²/f₀ is the seismic vulnerability index (Kanai).',
    'faq.q3': 'How to read vulnerability zones?',
    'faq.a3': 'K_g < 3 = safe, 3–10 = moderate, > 10 = vulnerable. Higher K_g means the soil is more susceptible to earthquake ground motion amplification.',
    'faq.q4': 'How often is data updated?',
    'faq.a4': 'Sensor data is sent every 10 seconds. HVSR analysis runs per 30-minute window for statistical stability.',

    // CTA
    'cta.title': 'Ready to map the campus seismic vulnerability?',
    'cta.sub': 'All HVSR parameters integrated in one dashboard. Start exploring now.',
    'cta.primary': 'HVSR Analysis',
    'cta.secondary': 'View Microzonation Map',

    // about
    'about.title': 'About VibraLens',
    'about.bg': 'Background',
    'about.bg.text': 'VibraLens was developed as part of a final thesis in the Geophysics Department, Padjadjaran University, to analyze seismic vulnerability of the Jatinangor campus area using an IoT-based HVSR method.',
    'about.obj': 'Objective',
    'about.obj.text': 'Estimate parameters f₀, A₀, and K_g from ambient noise signals for seismic microzonation of the campus area.',
    'about.how': 'How it works',
    'about.how.text': 'Geophone → LoRa node → LTE gateway → Server → HVSR analysis → Dashboard.',

    // common
    'back': 'Back to Home',
    'placeholder.text': 'This page is still empty — content will be added in the next stage.',

    // peta
    'peta.legend': 'Node Status',

    // 404
    'err.404.title': 'Page not found',
    'err.404.desc': 'The page you are looking for might have been moved, deleted, or never existed.',
    'err.404.cta': 'Back to Home',

    // footer
    'footer.desc': 'IoT-based ground vibration monitoring with HVSR analysis for seismic microzonation in the Jatinangor area.',
    'footer.col.product': 'Product',
    'footer.col.help': 'Help',
    'footer.col.contact': 'Contact',
    'footer.guide': 'User Guide',
    'footer.glossary': 'HVSR Glossary',
    'footer.method': 'Microseismic Methodology',
    'footer.reference': 'Nakamura & Kanai References',
    'footer.about': 'About',
    'footer.docs': 'Docs',
    'footer.faq': 'FAQ',
    'footer.contact': 'Contact',
    'footer.privacy': 'Privacy Policy',
    'footer.terms': 'Terms & Conditions',
        // placeholder v2
    'placeholder.dev': 'Under Development',
    'placeholder.home': 'Back to Home',
    'placeholder.catalog': 'Open Data Catalog',
    'placeholder.related': 'Other Available Modules',
  }
};

let langInitialized = false;

function applyLang(lang) {
  localStorage.setItem('vibra-lang', lang);
  const dict = I18N[lang] || I18N.id;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key] !== undefined) el.textContent = dict[key];
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (dict[key] !== undefined) el.placeholder = dict[key];
  });

  document.querySelectorAll('#langSeg button, #langSegMobile button').forEach(b => {
    b.classList.toggle('active', b.dataset.lang === lang);
  });

  updateClock();

  if (langInitialized) {
    showToast(lang === 'id' ? 'Bahasa: Indonesia' : 'Language: English', 'success');
  }
  langInitialized = true;
}

document.querySelectorAll('#langSeg button, #langSegMobile button').forEach(btn => {
  btn.addEventListener('click', () => applyLang(btn.dataset.lang));
});

applyLang(localStorage.getItem('vibra-lang') || 'id');

/* ============ CLOCK ============ */
function updateClock() {
  const now = new Date();
  const lang = localStorage.getItem('vibra-lang') || 'id';
  const locale = lang === 'id' ? 'id-ID' : 'en-GB';
  const timeStr = now.toLocaleTimeString(locale, {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  });
  const clockTime = document.querySelector('#clock .clock-time');
  if (clockTime) clockTime.textContent = timeStr;
}
setInterval(updateClock, 1000);
updateClock();

/* ============ FOCUS TRAP ============ */
function trapFocus(container) {
  const focusable = container.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  if (!focusable.length) return () => {};
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  function handler(e) {
    if (e.key !== 'Tab') return;
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
  container.addEventListener('keydown', handler);
  first.focus();
  return () => container.removeEventListener('keydown', handler);
}

/* ============ MODAL ============ */
const aboutModal = document.getElementById('aboutModal');
let releaseTrap = null;

if (aboutModal) {
  document.getElementById('aboutBtn')?.addEventListener('click', () => {
    aboutModal.classList.add('open');
    document.body.style.overflow = 'hidden';
    releaseTrap = trapFocus(aboutModal.querySelector('.modal-box'));
  });

  function closeModal() {
    aboutModal.classList.remove('open');
    document.body.style.overflow = '';
    if (releaseTrap) { releaseTrap(); releaseTrap = null; }
  }

  document.getElementById('aboutClose')?.addEventListener('click', closeModal);
  aboutModal.addEventListener('click', e => {
    if (e.target === aboutModal) closeModal();
  });
}

/* ============ KEYBOARD SHORTCUTS ============ */
document.addEventListener('keydown', e => {
  // Cmd+K / Ctrl+K → fokus search
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.querySelector('.search input');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }
  // ESC → tutup drawer/modal
  if (e.key === 'Escape') {
    closeDrawer();
    const modal = document.getElementById('aboutModal');
    if (modal?.classList.contains('open')) {
      modal.classList.remove('open');
      document.body.style.overflow = '';
      if (releaseTrap) { releaseTrap(); releaseTrap = null; }
    }
  }
});

/* ============ INIT ============ */
renderIcons();
initCounters();
initScrollProgress();
initCardRipple();
window.renderIcons = renderIcons;