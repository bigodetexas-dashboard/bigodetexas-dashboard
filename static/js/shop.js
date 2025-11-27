// ===== SHOP ECOMMERCE JAVASCRIPT =====

// Global State
let allItems = {};
let cart = [];
let userBalance = 0;
let currentCategory = 'armas';

// Category Info
const categoryInfo = {
    armas: { title: 'Armas', description: 'Rifles, pistolas e armas de combate', icon: 'gun' },
    municao: { title: 'Munições', description: 'Munição para todas as armas', icon: 'bullseye' },
    medico: { title: 'Médico', description: 'Itens médicos e de primeiros socorros', icon: 'medkit' },
    acessorios: { title: 'Acessórios', description: 'Miras, supressores e acessórios', icon: 'tools' },
    armadilhas: { title: 'Armadilhas', description: 'Armadilhas e explosivos', icon: 'bomb' },
    construcao: { title: 'Construção', description: 'Materiais para construir bases', icon: 'hammer' },
    veiculos: { title: 'Veículos', description: 'Peças e combustível para veículos', icon: 'car' },
    roupas: { title: 'Roupas', description: 'Roupas táticas e de proteção', icon: 'tshirt' },
    mochilas: { title: 'Mochilas', description: 'Mochilas de todos os tamanhos', icon: 'backpack' },
    comidas: { title: 'Comidas', description: 'Alimentos e bebidas', icon: 'utensils' },
    cacador: { title: 'Caçador', description: 'Equipamento de caça e sobrevivência', icon: 'crosshairs' }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadItems();
    loadUserBalance();
    loadCart();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const category = tab.dataset.category;
            switchCategory(category);
        });
    });

    // Cart toggle
    document.getElementById('cart-toggle').addEventListener('click', toggleCart);
    document.getElementById('close-cart').addEventListener('click', toggleCart);
    document.getElementById('cart-overlay').addEventListener('click', toggleCart);

    // Cart actions
    document.getElementById('btn-checkout').addEventListener('click', checkout);
    document.getElementById('btn-clear-cart').addEventListener('click', clearCart);
}

// Load Items from API
async function loadItems() {
    showLoading(true);
    try {
        const response = await fetch('/api/shop');
        const items = await response.json();

        // Organize items by category
        allItems = {};
        items.forEach(item => {
            if (!allItems[item.category]) {
                allItems[item.category] = [];
            }
            allItems[item.category].push(item);
        });

        displayCategory(currentCategory);
    } catch (error) {
        console.error('Error loading items:', error);
        showNotification('Erro ao carregar itens', 'error');
    } finally {
        showLoading(false);
    }
}

// Load User Balance
async function loadUserBalance() {
    try {
        const response = await fetch('/api/user/balance');
        const data = await response.json();
        userBalance = data.balance || 0;
        updateBalanceDisplay();
    } catch (error) {
        console.error('Error loading balance:', error);
        userBalance = 0;
        updateBalanceDisplay();
    }
}

// Update Balance Display
function updateBalanceDisplay() {
    document.getElementById('user-balance').textContent = userBalance.toLocaleString('pt-BR');
}

// Switch Category
function switchCategory(category) {
    currentCategory = category;

    // Update active tab
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-category="${category}"]`).classList.add('active');

    // Update header
    const info = categoryInfo[category];
    document.getElementById('category-title').textContent = info.title;
    document.getElementById('category-description').textContent = info.description;

    // Display items
    displayCategory(category);
}

// Display Category Items
function displayCategory(category) {
    const grid = document.getElementById('products-grid');
    const items = allItems[category] || [];

    if (items.length === 0) {
        grid.innerHTML = '<p style="text-align: center; color: var(--text-dim); grid-column: 1/-1;">Nenhum item disponível nesta categoria.</p>';
        return;
    }

    grid.innerHTML = items.map(item => `
        <div class="product-card" onclick="addToCart('${item.code}', '${item.category}')">
            <div class="product-icon">
                <i class="fas fa-${getItemIcon(item.category)}"></i>
            </div>
            <div class="product-name">${item.name}</div>
            <div class="product-code">${item.code}</div>
            <div class="product-description">${item.description}</div>
            <div class="product-footer">
                <div class="product-price">
                    <i class="fas fa-coins"></i>
                    ${item.price.toLocaleString('pt-BR')}
                </div>
                <button class="btn-add-cart" onclick="event.stopPropagation(); addToCart('${item.code}', '${item.category}')">
                    <i class="fas fa-cart-plus"></i>
                    Adicionar
                </button>
            </div>
        </div>
    `).join('');
}

// Get Item Icon
function getItemIcon(category) {
    return categoryInfo[category]?.icon || 'box';
}

// Add to Cart
function addToCart(code, category) {
    const items = allItems[category] || [];
    const item = items.find(i => i.code === code);

    if (!item) return;

    const existingItem = cart.find(i => i.code === code);

    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            code: item.code,
            name: item.name,
            price: item.price,
            category: item.category,
            quantity: 1
        });
    }

    saveCart();
    updateCartDisplay();
    showNotification(`${item.name} adicionado ao carrinho!`, 'success');

    // Animate cart button
    const cartBtn = document.getElementById('cart-toggle');
    cartBtn.style.transform = 'scale(1.2)';
    setTimeout(() => {
        cartBtn.style.transform = 'scale(1)';
    }, 200);
}

// Remove from Cart
function removeFromCart(code) {
    cart = cart.filter(item => item.code !== code);
    saveCart();
    updateCartDisplay();
}

// Update Item Quantity
function updateQuantity(code, delta) {
    const item = cart.find(i => i.code === code);
    if (!item) return;

    item.quantity += delta;

    if (item.quantity <= 0) {
        removeFromCart(code);
    } else {
        saveCart();
        updateCartDisplay();
    }
}

// Update Cart Display
function updateCartDisplay() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartCount = document.getElementById('cart-count');
    const cartTotal = document.getElementById('cart-total');

    // Update count
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    cartCount.textContent = totalItems;

    // Update total
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    cartTotal.textContent = `${total.toLocaleString('pt-BR')} DZ Coins`;

    // Update items list
    if (cart.length === 0) {
        cartItemsContainer.innerHTML = `
            <div class="cart-empty">
                <i class="fas fa-shopping-cart"></i>
                <p>Seu carrinho está vazio</p>
            </div>
        `;
        return;
    }

    cartItemsContainer.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${item.price.toLocaleString('pt-BR')} DZ Coins</div>
            </div>
            <div class="cart-item-controls">
                <button class="qty-btn" onclick="updateQuantity('${item.code}', -1)">-</button>
                <span class="qty-display">${item.quantity}</span>
                <button class="qty-btn" onclick="updateQuantity('${item.code}', 1)">+</button>
                <button class="btn-remove" onclick="removeFromCart('${item.code}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// Toggle Cart
function toggleCart() {
    const drawer = document.getElementById('cart-drawer');
    const overlay = document.getElementById('cart-overlay');

    drawer.classList.toggle('open');
    overlay.classList.toggle('active');
}

// Clear Cart
function clearCart() {
    if (cart.length === 0) return;

    if (confirm('Tem certeza que deseja limpar o carrinho?')) {
        cart = [];
        saveCart();
        updateCartDisplay();
        showNotification('Carrinho limpo!', 'info');
    }
}

// Checkout
async function checkout() {
    if (cart.length === 0) {
        showNotification('Seu carrinho está vazio!', 'error');
        return;
    }

    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    if (total > userBalance) {
        showNotification('Saldo insuficiente!', 'error');
        return;
    }

    // Redirect to checkout page with cart data
    sessionStorage.setItem('checkout_cart', JSON.stringify(cart));
    sessionStorage.setItem('checkout_total', total);
    window.location.href = '/checkout';
}

// Save Cart to LocalStorage
function saveCart() {
    localStorage.setItem('shop_cart', JSON.stringify(cart));
}

// Load Cart from LocalStorage
function loadCart() {
    const saved = localStorage.getItem('shop_cart');
    if (saved) {
        cart = JSON.parse(saved);
        updateCartDisplay();
    }
}

// Show Loading
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (show) {
        spinner.classList.add('active');
    } else {
        spinner.classList.remove('active');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'success' ? '#00d9ff' : type === 'error' ? '#ff4757' : '#ffa502'};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 10px;
        font-weight: 600;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add animations to document
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
