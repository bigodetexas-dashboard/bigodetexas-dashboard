// ===== SHOPPING CART SYSTEM =====

let allShopItems = [];
let cart = [];
let userBalance = 0;
let currentCategory = 'armas';

// Initialize shop
async function initShop() {
  console.log('[DEBUG] initShop started');

  // Load items
  console.log('[DEBUG] Fetching shop items...');
  const items = await fetchAPI('shop');
  console.log('[DEBUG] Shop items response:', items);

  if (!items) {
    console.error('[DEBUG] Failed to load shop items');
    document.getElementById('items-container').innerHTML = '<p class="text-center text-danger">Erro ao carregar itens. Verifique o console.</p>';
    return;
  }

  allShopItems = items;
  console.log(`[DEBUG] Loaded ${items.length} items`);

  // Load user balance
  console.log('[DEBUG] Fetching user balance...');
  const balanceData = await fetchAPI('user/balance');
  console.log('[DEBUG] User balance response:', balanceData);

  if (balanceData) {
    userBalance = balanceData.balance;
    const balanceEl = document.getElementById('user-balance');
    if (balanceEl) {
      balanceEl.textContent = `${formatNumber(userBalance)} 💰`;
    }
  } else {
    console.warn('[DEBUG] Could not fetch balance (user might be logged out)');
    const balanceEl = document.getElementById('user-balance');
    if (balanceEl) {
      balanceEl.textContent = 'Faça Login';
    }
  }

  // Load cart from localStorage
  const savedCart = localStorage.getItem('bigode_cart');
  if (savedCart) {
    try {
      cart = JSON.parse(savedCart);
      console.log(`[DEBUG] Loaded ${cart.length} items from cart`);
    } catch (e) {
      console.error('[DEBUG] Error parsing cart:', e);
      cart = [];
    }
  }

  // Display initial category
  console.log('[DEBUG] Selecting initial category: armas');
  selectCategory('armas');
  updateCart();
  console.log('[DEBUG] initShop completed');
}

// Select category
function selectCategory(category) {
  currentCategory = category;

  // Update active tab
  document.querySelectorAll('.category-tab').forEach(tab => {
    tab.classList.remove('active');
  });
  document.querySelector(`[data-category="${category}"]`).classList.add('active');

  // Filter and display items
  const filtered = allShopItems.filter(item => item.category === category);
  renderItems(filtered);
}

// Render items
function renderItems(items) {
  const container = document.getElementById('items-container');
  if (!items || items.length === 0) {
    container.innerHTML = '<p class="text-muted text-center">Nenhum item nesta categoria</p>';
    return;
  }

  container.innerHTML = items.map(item => `
    <div class="card fade-in">
      <div class="card-header">
        <h3 class="card-title">${item.name}</h3>
        <span class="badge badge-primary">${item.category}</span>
      </div>
      <p class="text-muted">${item.description}</p>
      <div style="margin-top: auto; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-primary);">
            ${formatNumber(item.price)} 💰
          </span>
          <code style="font-size: 0.875rem; color: var(--text-muted);">${item.code}</code>
        </div>
        <button onclick="addToCart('${item.code}')" class="add-to-cart-btn">
          🛒 Adicionar ao Carrinho
        </button>
      </div>
    </div>
  `).join('');
}

// Add to cart
function addToCart(code) {
  const item = allShopItems.find(i => i.code === code);
  if (!item) return;

  // Check if already in cart
  const existing = cart.find(c => c.code === code);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({
      code: item.code,
      name: item.name,
      price: item.price,
      quantity: 1
    });
  }

  updateCart();

  // Visual feedback
  const btn = event.target;
  const originalText = btn.innerHTML;
  btn.innerHTML = '✅ Adicionado!';
  btn.style.background = 'rgba(34, 197, 94, 0.2)';
  setTimeout(() => {
    btn.innerHTML = originalText;
    btn.style.background = '';
  }, 1000);
}

// Remove from cart
function removeFromCart(code) {
  cart = cart.filter(item => item.code !== code);
  updateCart();
}

// Update cart display
function updateCart() {
  // Save to localStorage
  localStorage.setItem('bigode_cart', JSON.stringify(cart));

  // Update cart display
  const cartItems = document.getElementById('cart-items');
  const cartTotal = document.getElementById('cart-total');
  const checkoutBtn = document.getElementById('checkout-btn');

  if (cart.length === 0) {
    cartItems.innerHTML = '<p class="text-muted text-center">Carrinho vazio</p>';
    cartTotal.textContent = '0 💰';
    checkoutBtn.disabled = true;
    document.getElementById('balance-status').innerHTML = '';
    return;
  }

  // Render cart items
  cartItems.innerHTML = cart.map(item => `
    <div class="cart-item">
      <div>
        <div style="font-weight: 600;">${item.name}</div>
        <div style="font-size: 0.875rem; color: var(--text-muted);">
          ${item.quantity}x - ${formatNumber(item.price * item.quantity)} 💰
        </div>
      </div>
      <button class="cart-item-remove" onclick="removeFromCart('${item.code}')">
        ✕
      </button>
    </div>
  `).join('');

  // Calculate total
  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  cartTotal.textContent = `${formatNumber(total)} 💰`;

  // Validate balance
  validateBalance(total);
}

// Validate balance
function validateBalance(total) {
  const balanceStatus = document.getElementById('balance-status');
  const checkoutBtn = document.getElementById('checkout-btn');

  if (total > userBalance) {
    const deficit = total - userBalance;
    balanceStatus.innerHTML = `
      <div class="balance-warning">
        ⚠️ Saldo Insuficiente!<br>
        Faltam: ${formatNumber(deficit)} 💰
      </div>
    `;
    checkoutBtn.disabled = true;
  } else {
    balanceStatus.innerHTML = `
      <div class="balance-ok">
        ✅ Saldo Suficiente
      </div>
    `;
    checkoutBtn.disabled = false;
  }
}

// Checkout
async function checkout() {
  if (cart.length === 0) return;

  const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // Final balance check
  if (total > userBalance) {
    alert('⚠️ Saldo insuficiente! Remova alguns itens do carrinho.');
    return;
  }

  // Ask for coordinates
  const coords = prompt('📍 Digite as coordenadas de entrega (formato: X Z):\nExemplo: 4500 10200');

  if (!coords) {
    return; // User cancelled
  }

  // Validate coordinates format
  if (!coords.match(/^\d+\s+\d+$/)) {
    alert('⚠️ Formato inválido! Use: X Z (exemplo: 4500 10200)');
    return;
  }

  // TODO: Send bulk purchase to backend
  // For now, show success message
  alert(`✅ Compra realizada com sucesso!\n\nTotal: ${formatNumber(total)} 💰\nItens: ${cart.length}\nLocal: ${coords}\n\nOs itens serão entregues em breve!`);

  // Clear cart
  cart = [];
  updateCart();
}
