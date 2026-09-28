/**
 * AERO-SUSHI MENU ENGINE (UZBEK)
 * Dinamik katalog, toifa tablari, filtrlash, qidiruv va kvant spetsifikatsiyasi modali
 */

let currentCategory = 'all';
let currentFilter = 'all'; // 'all', 'veg', 'spicy', 'chef', 'zerog'
let currentSearch = '';

function renderMenuGrid() {
  const container = document.getElementById('menu-items-grid');
  const countEl = document.getElementById('menu-results-count');
  if (!container) return;

  if (typeof MENU_ITEMS === 'undefined' || MENU_ITEMS.length === 0) {
    container.innerHTML = `<div class="col-span-full text-center py-12 text-slate-400">Kvant menyusi yuklanmoqda...</div>`;
    return;
  }

  // Elementlarni filtrlash
  const filtered = MENU_ITEMS.filter(item => {
    // 1. Toifa filtri
    const matchCategory = currentCategory === 'all' || item.category === currentCategory;

    // 2. Teg filtri
    let matchTag = true;
    if (currentFilter === 'veg') matchTag = item.isVeg;
    else if (currentFilter === 'spicy') matchTag = item.isSpicy;
    else if (currentFilter === 'chef') matchTag = item.isChefSpecial;
    else if (currentFilter === 'zerog') matchTag = item.isZeroG;

    // 3. Qidiruv so‘rovi
    let matchSearch = true;
    if (currentSearch.trim() !== '') {
      const q = currentSearch.toLowerCase();
      matchSearch = item.name.toLowerCase().includes(q) ||
                    item.desc.toLowerCase().includes(q) ||
                    item.code.toLowerCase().includes(q) ||
                    item.ingredients.some(ing => ing.toLowerCase().includes(q));
    }

    return matchCategory && matchTag && matchSearch;
  });

  if (countEl) {
    countEl.textContent = `${filtered.length} ta taom topildi`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full py-16 text-center glass-panel rounded-2xl border border-slate-800">
        <div class="w-16 h-16 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center mx-auto text-slate-500 mb-4 animate-levitate">
          <i data-lucide="search-x" class="w-8 h-8"></i>
        </div>
        <h3 class="font-cyber font-bold text-lg text-slate-200">SIZNING SO‘ROVINGIZ BO‘YICHA TAOM TOPILMADI</h3>
        <p class="text-xs text-slate-400 font-light mt-1 max-w-sm mx-auto">Filtrlarni tozalang yoki qidiruv so‘zini o‘zgartirib ko‘ring.</p>
        <button onclick="resetMenuFilters()" class="mt-4 px-4 py-2 rounded-xl btn-cyber-cyan text-xs font-mono uppercase">
          Filtrlarni qayta tiklash
        </button>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  let html = '';
  filtered.forEach(item => {
    // Belgilar
    let badgeHtml = '';
    if (item.isChefSpecial) {
      badgeHtml += `<span class="tag-cyber">OSHPAZ TANLOVI</span>`;
    }
    if (item.isSpicy) {
      badgeHtml += `<span class="tag-pink">ACHCHIQ</span>`;
    }
    if (item.isVeg) {
      badgeHtml += `<span class="tag-purple">VEGETARIAN</span>`;
    }
    if (item.isZeroG) {
      badgeHtml += `<span class="tag-cyber">ZERO-G</span>`;
    }

    html += `
      <div class="glass-card rounded-2xl p-4 flex flex-col group border border-cyan-500/20 hover:border-cyan-400/60 relative overflow-hidden transition-all duration-300">
        
        <!-- Rasm va Kiber-skan chiziqlari -->
        <div class="relative h-52 rounded-xl overflow-hidden mb-4 cursor-pointer" onclick="openItemModal('${item.id}')">
          <img src="${item.image}" alt="${item.name}" loading="lazy"
               class="w-full h-full object-cover group-hover:scale-110 transition duration-700 ease-out" />
          
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent"></div>

          <!-- Belgilar -->
          <div class="absolute top-2.5 left-2.5 flex flex-wrap gap-1 max-w-[80%]">
            ${badgeHtml}
          </div>

          <!-- Narx -->
          <div class="absolute bottom-2.5 right-2.5 bg-slate-950/90 backdrop-blur-md px-3 py-1 rounded-lg border border-cyan-400/40 text-xs font-cyber font-bold text-cyan-300 box-glow-cyan">
            $${item.price.toFixed(2)}
          </div>

          <!-- Tezkor ko‘rish ishorasi -->
          <div class="absolute inset-0 bg-cyan-950/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
            <span class="px-3 py-1.5 rounded-full bg-slate-900/90 border border-cyan-400 text-[11px] font-mono text-cyan-300">
              Kvant xususiyatlarini ko‘rish
            </span>
          </div>
        </div>

        <!-- Taom ma'lumotlari -->
        <div class="flex-1 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-mono-tech text-cyan-400 tracking-wider">${item.code}</span>
              <div class="flex items-center gap-1 text-amber-400 text-xs font-mono">
                <i data-lucide="star" class="w-3.5 h-3.5 fill-current"></i>
                <span>${item.rating}</span>
              </div>
            </div>
            
            <h3 class="font-cyber font-bold text-base text-white group-hover:text-cyan-300 transition mt-1">
              ${item.name}
            </h3>

            <p class="text-xs text-slate-300 font-light mt-2 leading-relaxed line-clamp-2">
              ${item.desc}
            </p>

            <!-- Tarkibiy qismlar -->
            <div class="flex flex-wrap gap-1.5 mt-3">
              ${item.ingredients.slice(0, 3).map(ing => `
                <span class="text-[10px] font-mono text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-800">${ing}</span>
              `).join('')}
              ${item.ingredients.length > 3 ? `<span class="text-[10px] font-mono text-slate-500 self-center">+${item.ingredients.length - 3}</span>` : ''}
            </div>
          </div>

          <!-- Harakatlar paneli -->
          <div class="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between">
            <span class="text-[10px] font-mono text-slate-400 truncate max-w-[130px]">${item.specs.split('|')[0]}</span>
            
            <div class="flex items-center gap-2">
              <button onclick="openItemModal('${item.id}')" 
                      class="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition" title="Batafsil">
                <i data-lucide="info" class="w-4 h-4"></i>
              </button>

              <button onclick="CartManager.addItem('${item.id}', 1)" 
                      class="px-3.5 py-2 rounded-lg btn-cyber-cyan text-xs font-cyber uppercase tracking-wider flex items-center gap-1.5">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                <span>Qo‘shish</span>
              </button>
            </div>
          </div>

        </div>

      </div>
    `;
  });

  container.innerHTML = html;
  lucide.createIcons();
}

function setCategory(cat, btn) {
  audioFX.soundClick();
  currentCategory = cat;

  document.querySelectorAll('.category-tab-btn').forEach(b => {
    b.classList.remove('bg-cyan-500', 'text-black', 'border-cyan-400', 'font-bold');
    b.classList.add('bg-slate-900/60', 'text-slate-300', 'border-slate-800');
  });

  if (btn) {
    btn.classList.add('bg-cyan-500', 'text-black', 'border-cyan-400', 'font-bold');
    btn.classList.remove('bg-slate-900/60', 'text-slate-300', 'border-slate-800');
  }

  renderMenuGrid();
}

function setFilter(filterType, btn) {
  audioFX.soundClick();
  currentFilter = filterType;

  document.querySelectorAll('.filter-pill-btn').forEach(b => {
    b.classList.remove('border-pink-500', 'text-pink-300', 'bg-pink-950/40');
    b.classList.add('border-slate-800', 'text-slate-400');
  });

  if (btn) {
    btn.classList.add('border-pink-500', 'text-pink-300', 'bg-pink-950/40');
    btn.classList.remove('border-slate-800', 'text-slate-400');
  }

  renderMenuGrid();
}

function handleSearchInput(e) {
  currentSearch = e.target.value;
  renderMenuGrid();
}

function resetMenuFilters() {
  audioFX.soundClick();
  currentCategory = 'all';
  currentFilter = 'all';
  currentSearch = '';

  const searchInput = document.getElementById('menu-search-input');
  if (searchInput) searchInput.value = '';

  const firstCategoryBtn = document.querySelector('.category-tab-btn');
  if (firstCategoryBtn) setCategory('all', firstCategoryBtn);

  const firstFilterBtn = document.querySelector('.filter-pill-btn');
  if (firstFilterBtn) setFilter('all', firstFilterBtn);

  renderMenuGrid();
}

function openItemModal(itemId) {
  audioFX.soundClick();
  const item = MENU_ITEMS.find(m => m.id === itemId);
  if (!item) return;

  const modal = document.getElementById('item-spec-modal');
  if (!modal) return;

  document.getElementById('modal-item-img').src = item.image;
  document.getElementById('modal-item-name').textContent = item.name;
  document.getElementById('modal-item-code').textContent = item.code;
  document.getElementById('modal-item-price').textContent = `$${item.price.toFixed(2)}`;
  document.getElementById('modal-item-desc').textContent = item.desc;
  document.getElementById('modal-item-specs').textContent = item.specs;

  const ingContainer = document.getElementById('modal-item-ingredients');
  ingContainer.innerHTML = item.ingredients.map(ing => `
    <span class="px-2.5 py-1 rounded-md bg-slate-900 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
      ${ing}
    </span>
  `).join('');

  const addBtn = document.getElementById('modal-add-cart-btn');
  addBtn.onclick = () => {
    CartManager.addItem(item.id, 1);
    closeItemModal();
  };

  modal.classList.remove('hidden');
}

function closeItemModal() {
  audioFX.soundClick();
  const modal = document.getElementById('item-spec-modal');
  if (modal) modal.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
  renderMenuGrid();
});
