// Meva & Oziq-ovqat Do'koni Asosiy Dastur Logikasi

// Savat holati (LocalStorage dan o'qish)
let cart = JSON.parse(localStorage.getItem('baraka_cart')) || [];
let activeCategory = 'all';
let searchQuery = '';
let sortBy = 'popular';

// Narxni so'mda formatlash
function formatPrice(amount) {
  return new Intl.NumberFormat('uz-UZ').format(amount) + " so'm";
}

// Savatni saqlash
function saveCart() {
  localStorage.setItem('baraka_cart', JSON.stringify(cart));
  updateCartUI();
}

// Savat hisob-kitoblari
function getCartSummary() {
  const itemsCount = cart.reduce((total, item) => total + item.quantity, 0);
  const subtotal = cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  const isFreeDelivery = subtotal >= STORE_CONFIG.deliveryThreshold || subtotal === 0;
  const deliveryFee = subtotal === 0 ? 0 : (isFreeDelivery ? 0 : STORE_CONFIG.deliveryCost);
  const total = subtotal + deliveryFee;
  const amountToFreeDelivery = Math.max(0, STORE_CONFIG.deliveryThreshold - subtotal);

  return {
    itemsCount,
    subtotal,
    isFreeDelivery,
    deliveryFee,
    total,
    amountToFreeDelivery
  };
}

// Savat UI elementlarini yangilash
function updateCartUI() {
  const summary = getCartSummary();
  
  // Savat soni ko'rsatkichlari (header va floating tugmalarda)
  const cartBadges = document.querySelectorAll('.cart-badge-count');
  cartBadges.forEach(badge => {
    badge.textContent = summary.itemsCount;
    badge.classList.toggle('hidden', summary.itemsCount === 0);
    badge.classList.add('cart-bump');
    setTimeout(() => badge.classList.remove('cart-bump'), 450);
  });

  const cartTotalEls = document.querySelectorAll('.cart-total-display');
  cartTotalEls.forEach(el => {
    el.textContent = formatPrice(summary.subtotal);
  });

  // Savat ro'yxatini chiqarish
  renderCartDrawerItems(summary);
}

// Savatga mahsulot qo'shish
function addToCart(productId, qty = 1) {
  const product = PRODUCTS_DATA.find(p => p.id === productId);
  if (!product) return;

  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.quantity = Math.round((existing.quantity + qty) * 10) / 10;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      unit: product.unit,
      image: product.image,
      fallbackEmoji: product.fallbackEmoji,
      quantity: qty
    });
  }

  saveCart();
  showToast(`${product.name} savatga qo'shildi! (${qty} ${product.unit})`, 'success');
}

// Savatdagi miqdorni o'zgartirish
function updateCartQuantity(productId, delta) {
  const itemIndex = cart.findIndex(item => item.id === productId);
  if (itemIndex === -1) return;

  const item = cart[itemIndex];
  const newQty = Math.round((item.quantity + delta) * 10) / 10;

  if (newQty <= 0) {
    cart.splice(itemIndex, 1);
    showToast(`${item.name} savatdan olib tashlandi`, 'info');
  } else {
    item.quantity = newQty;
  }

  saveCart();
}

// Savatdan butunlay o'chirish
function removeFromCart(productId) {
  const item = cart.find(i => i.id === productId);
  cart = cart.filter(item => item.id !== productId);
  saveCart();
  if (item) {
    showToast(`${item.name} savatdan o'chirildi`, 'info');
  }
}

// Savatni tozalash
function clearCart() {
  if (cart.length === 0) return;
  if (confirm("Savatni butunlay tozalamoqchimisiz?")) {
    cart = [];
    saveCart();
    showToast("Savat tozalandi", 'info');
  }
}

// Toast xabarnoma ko'rsatish
function showToast(message, type = 'success') {
  if (window.Swal) {
    const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 2200,
      timerProgressBar: true,
      didOpen: (toast) => {
        toast.onmouseenter = Swal.stopTimer;
        toast.onmouseleave = Swal.resumeTimer;
      }
    });
    Toast.fire({
      icon: type,
      title: message
    });
  } else {
    // Agar Swal yuklanmasa oddiy brauzer banneri
    const toast = document.createElement('div');
    toast.className = 'fixed bottom-5 right-5 z-50 bg-emerald-600 text-white px-5 py-3 rounded-xl shadow-2xl font-medium flex items-center gap-2 animate-bounce';
    toast.innerHTML = `<span>✓</span> <span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2200);
  }
}

// Savat Drawer ichini render qilish
function renderCartDrawerItems(summary) {
  const cartContainer = document.getElementById('cart-items-container');
  const cartEmptyState = document.getElementById('cart-empty-state');
  const cartSummaryBlock = document.getElementById('cart-summary-block');
  const cartFreeShippingProgress = document.getElementById('cart-free-shipping-progress');

  if (!cartContainer) return;

  if (cart.length === 0) {
    cartContainer.innerHTML = '';
    if (cartEmptyState) cartEmptyState.classList.remove('hidden');
    if (cartSummaryBlock) cartSummaryBlock.classList.add('hidden');
    return;
  }

  if (cartEmptyState) cartEmptyState.classList.add('hidden');
  if (cartSummaryBlock) cartSummaryBlock.classList.remove('hidden');

  // Bepul yetkazish progress bari
  if (cartFreeShippingProgress) {
    const progressPercent = Math.min(100, Math.round((summary.subtotal / STORE_CONFIG.deliveryThreshold) * 100));
    if (summary.isFreeDelivery) {
      cartFreeShippingProgress.innerHTML = `
        <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-3 rounded-xl flex items-center gap-2 text-xs font-semibold">
          <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600 shrink-0"></i>
          <span>Tabriklaymiz! Sizga yetkazib berish <b>MUTLAQO BEPUL</b>!</span>
        </div>
      `;
    } else {
      cartFreeShippingProgress.innerHTML = `
        <div class="bg-amber-50 border border-amber-200 p-3 rounded-xl">
          <div class="flex justify-between items-center text-xs font-medium text-amber-900 mb-1.5">
            <span>Bepul yetkazib berishgacha:</span>
            <span class="font-bold text-amber-700">${formatPrice(summary.amountToFreeDelivery)}</span>
          </div>
          <div class="w-full bg-amber-200/60 rounded-full h-2 overflow-hidden">
            <div class="bg-amber-500 h-2 rounded-full transition-all duration-500" style="width: ${progressPercent}%"></div>
          </div>
        </div>
      `;
    }
  }

  // Mahsulotlar ro'yxati
  cartContainer.innerHTML = cart.map(item => `
    <div class="flex items-center gap-3 p-3 bg-slate-50 hover:bg-slate-100/80 rounded-2xl transition border border-slate-100">
      <div class="w-16 h-16 rounded-xl overflow-hidden bg-white shrink-0 flex items-center justify-center border border-slate-200">
        <img src="${item.image}" alt="${item.name}" class="w-full h-full object-cover" onerror="this.outerHTML='<span class=\\'text-3xl\\'>${item.fallbackEmoji || '🍎'}</span>'">
      </div>
      <div class="flex-1 min-w-0">
        <h4 class="font-bold text-sm text-slate-800 truncate">${item.name}</h4>
        <p class="text-xs text-slate-500">${formatPrice(item.price)} / ${item.unit}</p>
        
        <!-- Miqdor nazorati -->
        <div class="flex items-center gap-2 mt-2">
          <button onclick="updateCartQuantity(${item.id}, -1)" class="w-7 h-7 flex items-center justify-center rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-rose-50 hover:border-rose-200 hover:text-rose-600 font-bold transition">
            -
          </button>
          <span class="text-xs font-bold text-slate-800 w-8 text-center">${item.quantity} ${item.unit}</span>
          <button onclick="updateCartQuantity(${item.id}, 1)" class="w-7 h-7 flex items-center justify-center rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-emerald-50 hover:border-emerald-200 hover:text-emerald-600 font-bold transition">
            +
          </button>
        </div>
      </div>
      <div class="text-right flex flex-col justify-between items-end h-16 py-1">
        <button onclick="removeFromCart(${item.id})" class="text-slate-400 hover:text-rose-500 transition p-1" title="O'chirish">
          <i data-lucide="trash-2" class="w-4 h-4"></i>
        </button>
        <span class="font-bold text-sm text-emerald-700">${formatPrice(item.price * item.quantity)}</span>
      </div>
    </div>
  `).join('');

  // Pastki xulosa blokidagi narxlar
  const subtotalEl = document.getElementById('cart-subtotal');
  const deliveryEl = document.getElementById('cart-delivery-cost');
  const finalTotalEl = document.getElementById('cart-final-total');

  if (subtotalEl) subtotalEl.textContent = formatPrice(summary.subtotal);
  if (deliveryEl) deliveryEl.textContent = summary.isFreeDelivery ? "BEPUL" : formatPrice(summary.deliveryFee);
  if (finalTotalEl) finalTotalEl.textContent = formatPrice(summary.total);

  if (window.lucide) lucide.createIcons();
}

// Mahsulotlar kartalarini render qilish
function renderProducts() {
  const container = document.getElementById('products-grid');
  const countBadge = document.getElementById('products-count-badge');
  if (!container) return;

  let filtered = PRODUCTS_DATA.filter(p => {
    const matchesCategory = activeCategory === 'all' || p.category === activeCategory;
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          p.origin.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Saralash
  if (sortBy === 'price-low') {
    filtered.sort((a, b) => a.price - b.price);
  } else if (sortBy === 'price-high') {
    filtered.sort((a, b) => b.price - a.price);
  } else if (sortBy === 'name') {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  } else {
    // Mashhurlik bo'yicha (isFeatured va rating)
    filtered.sort((a, b) => (b.isFeatured ? 1 : 0) - (a.isFeatured ? 1 : 0) || b.rating - a.rating);
  }

  if (countBadge) {
    countBadge.textContent = `${filtered.length} ta mahsulot topildi`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center">
        <div class="w-20 h-20 mx-auto mb-4 bg-amber-50 rounded-full flex items-center justify-center text-4xl">
          🔍
        </div>
        <h3 class="text-lg font-bold text-slate-800 mb-1">Kechirasiz, mahsulot topilmadi</h3>
        <p class="text-sm text-slate-500 mb-4">"${searchQuery}" so'rovi bo'yicha hech qanday meva yoki oziq-ovqat chiqmadi.</p>
        <button onclick="resetFilters()" class="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition">
          Barcha mahsulotlarni ko'rsatish
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(p => `
    <div class="product-card group bg-white rounded-3xl p-4 border border-slate-100 shadow-sm hover:shadow-xl transition-all flex flex-col justify-between relative overflow-hidden">
      <!-- Badge & Liked -->
      <div class="relative w-full aspect-square rounded-2xl overflow-hidden bg-slate-50 mb-4">
        ${p.badge ? `<span class="absolute top-3 left-3 z-10 text-[10px] font-extrabold tracking-wider text-white px-2.5 py-1 rounded-full uppercase shadow-sm ${p.badgeColor}">${p.badge}</span>` : ''}
        
        <button onclick="openQuickView(${p.id})" class="absolute top-3 right-3 z-10 w-9 h-9 rounded-full bg-white/90 backdrop-blur text-slate-600 hover:text-emerald-600 flex items-center justify-center shadow hover:scale-105 transition" title="Batafsil ko'rish">
          <i data-lucide="eye" class="w-4 h-4"></i>
        </button>

        <img src="${p.image}" alt="${p.name}" loading="lazy" class="w-full h-full object-cover group-hover:scale-108 transition-transform duration-500" onerror="this.outerHTML='<div class=\\'w-full h-full flex items-center justify-center text-7xl bg-slate-50\\'>${p.fallbackEmoji}</div>'">

        <div class="absolute bottom-2 left-2 bg-black/50 backdrop-blur-md px-2 py-0.5 rounded-md text-[11px] text-white font-medium flex items-center gap-1">
          <i data-lucide="map-pin" class="w-3 h-3 text-emerald-400"></i> ${p.origin}
        </div>
      </div>

      <!-- Mahsulot ma'lumotlari -->
      <div>
        <div class="flex items-center justify-between gap-1 mb-1.5">
          <span class="text-xs font-semibold text-emerald-600 uppercase tracking-wide">${p.categoryName}</span>
          <div class="flex items-center gap-1 text-amber-400 text-xs font-bold">
            <span>★</span>
            <span class="text-slate-700">${p.rating}</span>
            <span class="text-slate-400 font-normal">(${p.reviewsCount})</span>
          </div>
        </div>

        <h3 class="font-bold text-slate-800 text-base leading-snug mb-1 group-hover:text-emerald-700 transition cursor-pointer" onclick="openQuickView(${p.id})">
          ${p.name}
        </h3>
        
        <p class="text-xs text-slate-500 line-clamp-2 mb-3">
          ${p.description}
        </p>
      </div>

      <!-- Narx va Qo'shish paneli -->
      <div class="pt-3 border-t border-slate-100 flex items-center justify-between gap-2 mt-auto">
        <div>
          <div class="text-xs text-slate-400 font-medium">1 ${p.unit} narxi:</div>
          <div class="flex items-baseline gap-1.5">
            <span class="text-lg font-extrabold text-slate-900">${formatPrice(p.price)}</span>
            ${p.oldPrice ? `<span class="text-xs text-slate-400 line-through">${formatPrice(p.oldPrice)}</span>` : ''}
          </div>
        </div>

        <div class="flex items-center gap-1.5">
          <button onclick="addToCart(${p.id}, 1)" class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-bold text-xs px-3.5 py-2.5 rounded-xl shadow-md shadow-emerald-600/20 transition">
            <i data-lucide="shopping-bag" class="w-4 h-4"></i>
            <span>Savatga</span>
          </button>
        </div>
      </div>
    </div>
  `).join('');

  if (window.lucide) lucide.createIcons();
}

// Filtrni tiklash
function resetFilters() {
  activeCategory = 'all';
  searchQuery = '';
  const searchInput = document.getElementById('search-input');
  if (searchInput) searchInput.value = '';

  document.querySelectorAll('.category-filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.category === 'all');
  });

  renderProducts();
}

// Quick View Modal
function openQuickView(productId) {
  const p = PRODUCTS_DATA.find(item => item.id === productId);
  if (!p) return;

  const modal = document.getElementById('quick-view-modal');
  const modalContent = document.getElementById('quick-view-body');
  if (!modal || !modalContent) return;

  modalContent.innerHTML = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
      <div class="rounded-2xl overflow-hidden bg-slate-100 flex items-center justify-center aspect-square relative">
        <img src="${p.image}" alt="${p.name}" class="w-full h-full object-cover" onerror="this.outerHTML='<span class=\\'text-8xl\\'>${p.fallbackEmoji}</span>'">
        ${p.badge ? `<span class="absolute top-4 left-4 ${p.badgeColor} text-white font-bold text-xs px-3 py-1.5 rounded-full uppercase shadow">${p.badge}</span>` : ''}
      </div>
      <div class="flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-emerald-600 uppercase tracking-wider">${p.categoryName}</span>
            <div class="flex items-center gap-1 text-amber-500 font-bold text-sm">
              <span>★ ${p.rating}</span>
              <span class="text-slate-400 font-normal text-xs">(${p.reviewsCount} xaridorlar bahosi)</span>
            </div>
          </div>

          <h2 class="text-2xl font-extrabold text-slate-900 mb-2">${p.name}</h2>
          
          <div class="flex items-center gap-3 mb-4">
            <span class="text-2xl font-black text-emerald-700">${formatPrice(p.price)}</span>
            <span class="text-sm text-slate-500">/ 1 ${p.unit}</span>
            ${p.oldPrice ? `<span class="text-sm text-slate-400 line-through">${formatPrice(p.oldPrice)}</span>` : ''}
          </div>

          <p class="text-sm text-slate-600 leading-relaxed mb-6">
            ${p.description}
          </p>

          <div class="space-y-2 bg-slate-50 p-4 rounded-xl border border-slate-100 text-xs text-slate-700 mb-6">
            <div class="flex justify-between">
              <span class="text-slate-500">Yetkazib berilgan joy:</span>
              <span class="font-bold">${p.origin}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Holati:</span>
              <span class="font-bold text-emerald-600">${p.freshness}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Buyurtma uchun telefon:</span>
              <a href="tel:${STORE_CONFIG.phoneClean}" class="font-bold text-emerald-700 underline">${STORE_CONFIG.phone}</a>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center border border-slate-200 rounded-xl overflow-hidden bg-white">
            <button onclick="decrementModalQty()" class="px-3.5 py-3 text-slate-600 hover:bg-slate-100 font-bold text-base transition">-</button>
            <input type="number" id="modal-qty-input" value="1" min="1" max="100" class="w-12 text-center text-sm font-bold text-slate-800 border-none focus:outline-none">
            <button onclick="incrementModalQty()" class="px-3.5 py-3 text-slate-600 hover:bg-slate-100 font-bold text-base transition">+</button>
          </div>

          <button onclick="addModalItemToCart(${p.id})" class="flex-1 bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white font-bold py-3.5 px-6 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition">
            <i data-lucide="shopping-bag" class="w-5 h-5"></i>
            <span>Savatga qo'shish</span>
          </button>
        </div>
      </div>
    </div>
  `;

  modal.classList.remove('hidden');
  if (window.lucide) lucide.createIcons();
}

function closeQuickView() {
  const modal = document.getElementById('quick-view-modal');
  if (modal) modal.classList.add('hidden');
}

function incrementModalQty() {
  const input = document.getElementById('modal-qty-input');
  if (input) input.value = parseInt(input.value || 1) + 1;
}

function decrementModalQty() {
  const input = document.getElementById('modal-qty-input');
  if (input && parseInt(input.value) > 1) {
    input.value = parseInt(input.value) - 1;
  }
}

function addModalItemToCart(productId) {
  const input = document.getElementById('modal-qty-input');
  const qty = parseInt(input ? input.value : 1) || 1;
  addToCart(productId, qty);
  closeQuickView();
}

// Savat Drawerini ochish / yopish
function toggleCartDrawer(open = null) {
  const drawer = document.getElementById('cart-drawer');
  const backdrop = document.getElementById('cart-backdrop');
  if (!drawer || !backdrop) return;

  const shouldOpen = open !== null ? open : drawer.classList.contains('translate-x-full');
  
  if (shouldOpen) {
    drawer.classList.remove('translate-x-full');
    backdrop.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  } else {
    drawer.classList.add('translate-x-full');
    backdrop.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }
}

// Checkout Modalini ochish
function openCheckoutModal() {
  if (cart.length === 0) {
    showToast("Savat bo'sh, iltimos oldin mahsulot tanlang!", "error");
    return;
  }

  toggleCartDrawer(false);
  const checkoutModal = document.getElementById('checkout-modal');
  if (!checkoutModal) return;

  const summary = getCartSummary();
  const summaryList = document.getElementById('checkout-items-summary');
  if (summaryList) {
    summaryList.innerHTML = cart.map(item => `
      <div class="flex justify-between items-center text-xs py-1 border-b border-slate-100 last:border-none">
        <span class="text-slate-700 font-medium">${item.name} (${item.quantity} ${item.unit})</span>
        <span class="font-bold text-slate-900">${formatPrice(item.price * item.quantity)}</span>
      </div>
    `).join('');
  }

  const checkoutTotalEl = document.getElementById('checkout-total-sum');
  if (checkoutTotalEl) checkoutTotalEl.textContent = formatPrice(summary.total);

  checkoutModal.classList.remove('hidden');
  document.body.classList.add('overflow-hidden');
  if (window.lucide) lucide.createIcons();
}

function closeCheckoutModal() {
  const checkoutModal = document.getElementById('checkout-modal');
  if (checkoutModal) {
    checkoutModal.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  }
}

// Buyurtmani jo'natish (Submit Order)
function handleOrderSubmit(e) {
  e.preventDefault();

  const nameInput = document.getElementById('order-name');
  const phoneInput = document.getElementById('order-phone');
  const addressInput = document.getElementById('order-address');
  const noteInput = document.getElementById('order-note');
  const paymentMethodInput = document.querySelector('input[name="payment-method"]:checked');

  const customerName = nameInput ? nameInput.value.trim() : '';
  const customerPhone = phoneInput ? phoneInput.value.trim() : '';
  const customerAddress = addressInput ? addressInput.value.trim() : '';
  const notes = noteInput ? noteInput.value.trim() : '';
  const paymentMethod = paymentMethodInput ? paymentMethodInput.value : 'Naqd pul';

  if (!customerName || !customerPhone || !customerAddress) {
    alert("Iltimos, Ismingiz, Telefon raqamingiz va Manzilingizni to'ldiring!");
    return;
  }

  const summary = getCartSummary();
  const orderNumber = "BF-" + Math.floor(100000 + Math.random() * 900000);

  // Telegram xabari formatini tayyorlash
  let orderMessage = `🛒 YANGI BUYURTMA #${orderNumber}\n\n`;
  orderMessage += `👤 Xaridor: ${customerName}\n`;
  orderMessage += `📞 Telefon: ${customerPhone}\n`;
  orderMessage += `📍 Manzil: ${customerAddress}\n`;
  orderMessage += `💳 To'lov turi: ${paymentMethod}\n`;
  if (notes) orderMessage += `📝 Izoh: ${notes}\n`;
  orderMessage += `\n📦 MAHSULOTLAR RO'YXATI:\n`;

  cart.forEach((item, idx) => {
    orderMessage += `${idx + 1}. ${item.name} — ${item.quantity} ${item.unit} x ${formatPrice(item.price)} = ${formatPrice(item.price * item.quantity)}\n`;
  });

  orderMessage += `\n💵 Mahsulotlar: ${formatPrice(summary.subtotal)}\n`;
  orderMessage += `🚚 Yetkazib berish: ${summary.isFreeDelivery ? 'BEPUL' : formatPrice(summary.deliveryFee)}\n`;
  orderMessage += `💰 JAMI TO'LOV: ${formatPrice(summary.total)}\n`;

  // Muvaffaqiyatli buyurtma modali
  closeCheckoutModal();

  if (window.Swal) {
    Swal.fire({
      icon: 'success',
      title: 'Buyurtmangiz qabul qilindi!',
      html: `
        <div class="text-left text-sm space-y-2 mt-4 p-3 bg-slate-50 rounded-xl border border-slate-200">
          <p><b>Buyurtma raqami:</b> <span class="text-emerald-700 font-bold">${orderNumber}</span></p>
          <p><b>Jami to'lov:</b> ${formatPrice(summary.total)}</p>
          <p><b>Tezkor aloqa operatori:</b> <a href="tel:${STORE_CONFIG.phoneClean}" class="text-emerald-700 font-bold underline">${STORE_CONFIG.phone}</a></p>
          <p class="text-xs text-slate-500 pt-2 border-t">Operatorimiz 5 daqiqa ichida buyurtmani tasdiqlash uchun siz bilan bog'lanadi!</p>
        </div>
      `,
      showCancelButton: true,
      confirmButtonText: '📱 Telegram orqali yuborish',
      cancelButtonText: '📞 Qo\'ng\'iroq qilish (' + STORE_CONFIG.phoneDisplay + ')',
      confirmButtonColor: '#10b981',
      cancelButtonColor: '#0284c7'
    }).then((result) => {
      if (result.isConfirmed) {
        // Telegram orqali yuborish
        const encoded = encodeURIComponent(orderMessage);
        window.open(`https://t.me/share/url?url=${encoded}&text=Baraka%20Marketga%20Buyurtma`, '_blank');
      } else if (result.dismiss === Swal.DismissReason.cancel) {
        // Qo'ng'iroq qilish
        window.location.href = `tel:${STORE_CONFIG.phoneClean}`;
      }
    });
  } else {
    alert(`Buyurtmangiz muvaffaqiyatli qabul qilindi! Buyurtma kodi: ${orderNumber}. Tez orada sizga qo'ng'iroq qilamiz.`);
  }

  // Savatni tozalash
  cart = [];
  saveCart();
}

// Qayta qo'ng'iroq so'rash formasi
function handleCallbackRequest(e) {
  e.preventDefault();
  const phoneInput = document.getElementById('callback-phone');
  const phone = phoneInput ? phoneInput.value.trim() : '';

  if (!phone) {
    alert("Iltimos, telefon raqamingizni kiriting!");
    return;
  }

  if (window.Swal) {
    Swal.fire({
      icon: 'success',
      title: 'So\'rovingiz qabul qilindi!',
      text: `Mutaxassisimiz tez orada ${phone} raqamingizga qo'ng'iroq qiladi. Do'konimiz raqami: ${STORE_CONFIG.phone}`,
      confirmButtonColor: '#10b981'
    });
  } else {
    alert(`Rahmat! Tez orada sizga qo'ng'iroq qilamiz. Telefon: ${STORE_CONFIG.phone}`);
  }

  if (phoneInput) phoneInput.value = '';
}

// DOM yuklanganda ishga tushish
document.addEventListener('DOMContentLoaded', () => {
  // Boshlang'ich UI yuklash
  updateCartUI();
  renderProducts();

  // Kategoriya tugmalari bosilganda
  const categoryButtons = document.querySelectorAll('.category-filter-btn');
  categoryButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      categoryButtons.forEach(b => {
        b.classList.remove('bg-emerald-600', 'text-white', 'shadow-md');
        b.classList.add('bg-white', 'text-slate-700', 'border-slate-200');
      });

      btn.classList.add('bg-emerald-600', 'text-white', 'shadow-md');
      btn.classList.remove('bg-white', 'text-slate-700', 'border-slate-200');

      activeCategory = btn.dataset.category || 'all';
      renderProducts();
    });
  });

  // Qidiruv maydoni
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      renderProducts();
    });
  }

  // Saralash dropdowni
  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      sortBy = e.target.value;
      renderProducts();
    });
  }

  // Lucide ikonlarini chizish
  if (window.lucide) {
    lucide.createIcons();
  }
});
