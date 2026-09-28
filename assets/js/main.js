/**
 * AERO-SUSHI: ANTI-GRAVITY CYBER EXPERIENCE ENGINE (UZBEK)
 * Savatcha tizimi, Audio Sintezator, Muallaq Zarrachalar, Xabarnoma Tizimi
 */

// ==========================================
// 1. WEB AUDIO SCI-FI SINTEZATOR
// ==========================================
class CyberSoundEngine {
  constructor() {
    this.ctx = null;
    this.isMuted = localStorage.getItem('aero_sound_muted') === 'true';
  }

  init() {
    if (!this.ctx && typeof AudioContext !== 'undefined') {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    localStorage.setItem('aero_sound_muted', this.isMuted);
    return this.isMuted;
  }

  playBeep(freq = 600, duration = 0.08, type = 'sine', gainVal = 0.04) {
    if (this.isMuted) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {}
  }

  soundClick() {
    this.playBeep(880, 0.05, 'sine', 0.03);
  }

  soundCartAdd() {
    this.playBeep(587.33, 0.08, 'triangle', 0.05);
    setTimeout(() => this.playBeep(880, 0.12, 'sine', 0.05), 80);
    setTimeout(() => this.playBeep(1174.66, 0.18, 'sine', 0.04), 160);
  }

  soundSuccess() {
    this.playBeep(523.25, 0.1, 'sine', 0.05); // C5
    setTimeout(() => this.playBeep(659.25, 0.1, 'sine', 0.05), 90);
    setTimeout(() => this.playBeep(783.99, 0.12, 'sine', 0.05), 180);
    setTimeout(() => this.playBeep(1046.50, 0.25, 'sine', 0.06), 270);
  }

  soundLevitate() {
    if (this.isMuted) return;
    try {
      this.init();
      if (!this.ctx) return;
      if (this.ctx.state === 'suspended') this.ctx.resume();

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(200, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(800, this.ctx.currentTime + 0.4);

      gain.gain.setValueAtTime(0.04, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.4);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.4);
    } catch (e) {}
  }
}

const audioFX = new CyberSoundEngine();

// ==========================================
// 2. SAVATCHA BOSHQARUVI (LOCAL STORAGE)
// ==========================================
const CartManager = {
  getCart() {
    try {
      const saved = localStorage.getItem('aero_cart');
      return saved ? JSON.parse(saved) : [];
    } catch (e) {
      return [];
    }
  },

  saveCart(cart) {
    localStorage.setItem('aero_cart', JSON.stringify(cart));
    this.updateCartBadge();
  },

  addItem(itemId, qty = 1) {
    const cart = this.getCart();
    const existing = cart.find(i => i.id === itemId);

    let itemInfo = null;
    if (typeof MENU_ITEMS !== 'undefined') {
      itemInfo = MENU_ITEMS.find(m => m.id === itemId);
    }

    if (existing) {
      existing.qty += qty;
    } else {
      cart.push({
        id: itemId,
        qty: qty,
        name: itemInfo ? itemInfo.name : 'Orbital Roll',
        price: itemInfo ? itemInfo.price : 25,
        image: itemInfo ? itemInfo.image : '',
        code: itemInfo ? itemInfo.code : '#AG'
      });
    }

    this.saveCart(cart);
    audioFX.soundCartAdd();
    showToast(
      'Kvant Laganchasiga Qo‘shildi',
      `${itemInfo ? itemInfo.name : 'Taom'} muallaq laganchaga joylashtirildi.`,
      'sushi'
    );
    this.renderCartDrawer();
  },

  updateQty(itemId, delta) {
    let cart = this.getCart();
    const item = cart.find(i => i.id === itemId);
    if (!item) return;

    item.qty += delta;
    if (item.qty <= 0) {
      cart = cart.filter(i => i.id !== itemId);
    }

    this.saveCart(cart);
    audioFX.soundClick();
    this.renderCartDrawer();
  },

  removeItem(itemId) {
    let cart = this.getCart();
    cart = cart.filter(i => i.id !== itemId);
    this.saveCart(cart);
    audioFX.soundClick();
    this.renderCartDrawer();
  },

  clearCart() {
    localStorage.removeItem('aero_cart');
    this.updateCartBadge();
    this.renderCartDrawer();
  },

  getCount() {
    return this.getCart().reduce((sum, i) => sum + i.qty, 0);
  },

  getSubtotal() {
    return this.getCart().reduce((sum, i) => sum + (i.price * i.qty), 0);
  },

  updateCartBadge() {
    const count = this.getCount();
    const badges = document.querySelectorAll('.cart-count-badge');
    badges.forEach(badge => {
      badge.textContent = count;
      if (count > 0) {
        badge.classList.remove('hidden');
        badge.classList.add('flex');
      } else {
        badge.classList.add('hidden');
        badge.classList.remove('flex');
      }
    });
  },

  renderCartDrawer() {
    const container = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');
    const totalEl = document.getElementById('cart-total');
    const emptyState = document.getElementById('cart-empty-state');
    const footerEl = document.getElementById('cart-footer-section');

    if (!container) return;

    const cart = this.getCart();

    if (cart.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.classList.remove('hidden');
      if (footerEl) footerEl.classList.add('hidden');
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');
    if (footerEl) footerEl.classList.remove('hidden');

    let html = '';
    cart.forEach(item => {
      html += `
        <div class="flex items-center gap-3 p-3 rounded-xl bg-slate-900/60 border border-cyan-500/20 hover:border-cyan-400/40 transition">
          <img src="${item.image || 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=150&q=80'}" 
               alt="${item.name}" 
               class="w-16 h-16 rounded-lg object-cover border border-cyan-500/30 flex-shrink-0" />
          <div class="flex-1 min-w-0">
            <span class="text-[10px] text-cyan-400 font-mono-tech tracking-wider">${item.code || '#AG'}</span>
            <h4 class="text-sm font-semibold text-slate-100 truncate">${item.name}</h4>
            <div class="text-xs text-pink-400 font-cyber font-bold mt-0.5">$${item.price.toFixed(2)}</div>
          </div>
          <div class="flex items-center gap-1.5 bg-slate-950/80 px-2 py-1 rounded-lg border border-slate-700">
            <button onclick="CartManager.updateQty('${item.id}', -1)" class="text-slate-400 hover:text-cyan-400 font-bold px-1 transition text-sm">-</button>
            <span class="text-xs font-mono-tech text-white px-1">${item.qty}</span>
            <button onclick="CartManager.updateQty('${item.id}', 1)" class="text-slate-400 hover:text-cyan-400 font-bold px-1 transition text-sm">+</button>
          </div>
          <button onclick="CartManager.removeItem('${item.id}')" class="text-slate-500 hover:text-pink-500 transition p-1" title="O‘chirish">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
          </button>
        </div>
      `;
    });

    container.innerHTML = html;
    const subtotal = this.getSubtotal();
    if (subtotalEl) subtotalEl.textContent = `$${subtotal.toFixed(2)}`;
    if (totalEl) totalEl.textContent = `$${subtotal.toFixed(2)}`; // Bepul Zero-G stabilizatsiyasi
  }
};

// ==========================================
// 3. SAVATCHA OCHISH VA YOPISH
// ==========================================
function openCartDrawer() {
  audioFX.soundClick();
  const drawer = document.getElementById('cart-drawer');
  const backdrop = document.getElementById('cart-backdrop');
  if (drawer && backdrop) {
    CartManager.renderCartDrawer();
    backdrop.classList.remove('hidden');
    setTimeout(() => {
      backdrop.classList.remove('opacity-0');
      drawer.classList.remove('translate-x-full');
    }, 10);
  }
}

function closeCartDrawer() {
  audioFX.soundClick();
  const drawer = document.getElementById('cart-drawer');
  const backdrop = document.getElementById('cart-backdrop');
  if (drawer && backdrop) {
    drawer.classList.add('translate-x-full');
    backdrop.classList.add('opacity-0');
    setTimeout(() => {
      backdrop.classList.add('hidden');
    }, 300);
  }
}

// Kvant Buyurtmasini Rasmiylashtirish
function initiateQuantumCheckout() {
  const cart = CartManager.getCart();
  if (cart.length === 0) return;

  closeCartDrawer();
  audioFX.soundSuccess();

  const checkoutModal = document.getElementById('checkout-success-modal');
  if (checkoutModal) {
    const orderIdEl = document.getElementById('checkout-order-id');
    const orderTotalEl = document.getElementById('checkout-order-total');
    if (orderIdEl) orderIdEl.textContent = 'QO-' + Math.floor(100000 + Math.random() * 900000);
    if (orderTotalEl) orderTotalEl.textContent = `$${CartManager.getSubtotal().toFixed(2)}`;

    checkoutModal.classList.remove('hidden');
  }

  CartManager.clearCart();
}

function closeCheckoutModal() {
  audioFX.soundClick();
  const checkoutModal = document.getElementById('checkout-success-modal');
  if (checkoutModal) {
    checkoutModal.classList.add('hidden');
  }
}

// ==========================================
// 4. MUALLAQ ZARRACHALAR KANVASI (ZERO-G)
// ==========================================
function initZeroGCanvas() {
  const canvas = document.getElementById('zero-g-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = [];
  const particleCount = Math.min(Math.floor(window.innerWidth / 22), 55);

  const colors = [
    'rgba(0, 240, 255, ',
    'rgba(255, 83, 118, ',
    'rgba(157, 78, 221, ',
    'rgba(255, 255, 255, '
  ];

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2.2 + 0.8,
      speedX: (Math.random() - 0.5) * 0.4,
      speedY: -Math.random() * 0.5 - 0.15,
      colorBase: colors[Math.floor(Math.random() * colors.length)],
      alpha: Math.random() * 0.6 + 0.2,
      pulse: Math.random() * 0.02 + 0.005
    });
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    particles.forEach(p => {
      p.x += p.speedX;
      p.y += p.speedY;
      p.alpha += p.pulse;

      if (p.alpha > 0.8 || p.alpha < 0.15) {
        p.pulse = -p.pulse;
      }

      if (p.y < -10) {
        p.y = height + 10;
        p.x = Math.random() * width;
      }
      if (p.x < -10) p.x = width + 10;
      if (p.x > width + 10) p.x = -10;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.colorBase + Math.max(0, Math.min(p.alpha, 1)) + ')';
      ctx.shadowBlur = 8;
      ctx.shadowColor = p.colorBase + '0.5)';
      ctx.fill();
    });

    requestAnimationFrame(render);
  }

  render();
}

// ==========================================
// 5. TOAST XABARNOMA TIZIMI
// ==========================================
function showToast(title, message, type = 'cyan') {
  let container = document.getElementById('cyber-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'cyber-toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = 'cyber-toast';

  const iconSvg = type === 'sushi' 
    ? `<svg class="w-6 h-6 text-pink-400 flex-shrink-0 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`
    : `<svg class="w-6 h-6 text-cyan-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`;

  toast.innerHTML = `
    ${iconSvg}
    <div class="flex-1">
      <div class="text-xs font-cyber font-bold tracking-wider text-cyan-300 uppercase">${title}</div>
      <div class="text-xs text-slate-300 font-sans mt-0.5">${message}</div>
    </div>
    <button onclick="this.parentElement.remove()" class="text-slate-500 hover:text-white transition text-xs">✕</button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px) scale(0.95)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ==========================================
// 6. ZERO-G GRAVITATSIYA BOSHQARUVI
// ==========================================
let zeroGActive = false;
function toggleZeroGLevitator() {
  audioFX.soundLevitate();
  zeroGActive = !zeroGActive;

  const body = document.body;
  const gravIndicator = document.getElementById('grav-status-label');
  const gravBtn = document.getElementById('grav-toggle-btn');

  if (zeroGActive) {
    body.classList.add('zero-g-hyper');
    if (gravIndicator) gravIndicator.textContent = '0.01G [MIKRO-DRIFT]';
    if (gravBtn) gravBtn.classList.add('border-pink-500', 'text-pink-400');
    showToast(
      'Akustik Levitator Kuchaytirildi',
      'Gravitatsiya 0.01G ga tushirildi. Taomlar to‘liq vaznsizlik holatida.',
      'cyan'
    );
  } else {
    body.classList.remove('zero-g-hyper');
    if (gravIndicator) gravIndicator.textContent = '0.12G [BARQAROR]';
    if (gravBtn) gravBtn.classList.remove('border-pink-500', 'text-pink-400');
    showToast(
      'Gravitatsiya Barqarorlashdi',
      'Atmosfera maydoni 0.12G orbital holatga qaytarildi.',
      'cyan'
    );
  }
}

// ==========================================
// 7. XABARNOMAGA OBUNA BO‘LISH
// ==========================================
function handleNewsletterSubmit(e) {
  e.preventDefault();
  const input = e.target.querySelector('input[type="email"]');
  if (!input || !input.value) return;

  audioFX.soundSuccess();
  showToast(
    'Signal Qabul Qilindi',
    `Chastota ulandi: ${input.value} Orbital VIP xabarlar ro‘yxatiga kiritildi.`,
    'cyan'
  );
  input.value = '';
}

// ==========================================
// 8. MOBIL MENYU BOSHQARUVI
// ==========================================
function toggleMobileMenu() {
  audioFX.soundClick();
  const menu = document.getElementById('mobile-nav-menu');
  if (menu) {
    menu.classList.toggle('hidden');
  }
}

// ==========================================
// 9. DOKUMENT YUKLANGANDA ISHGA TUSHIRISH
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  CartManager.updateCartBadge();
  initZeroGCanvas();

  document.querySelectorAll('button, a.btn-cyber-cyan, a.btn-cyber-outline, a.btn-cyber-pink').forEach(btn => {
    btn.addEventListener('click', () => {
      audioFX.soundClick();
    });
  });

  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('text-cyan-400', 'border-b-2', 'border-cyan-400');
      link.classList.remove('text-slate-300');
    }
  });
});
