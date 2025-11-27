// Sistema de Carrinho de Compras
let cart = [];
let userBalance = 0;

// Carregar saldo do usuário
async function loadUserBalance() {
    try {
        const response = await fetch('/api/user/balance');
        if (response.ok) {
            const data = await response.json();
            userBalance = data.balance || 0;
            updateCartDisplay();
        }
    } catch (error) {
        console.error('[CART] Erro ao carregar saldo:', error);
    }
}

// Adicionar item ao carrinho
function addToCart(code, name, price, category) {
    const existingItem = cart.find(item => item.code === code);

    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            code,
            name,
            price,
            category,
            quantity: 1
        });
    }

    updateCartDisplay();
    showNotification(`${name} adicionado ao carrinho!`, 'success');
}

// Remover item do carrinho
function removeFromCart(code) {
    const index = cart.findIndex(item => item.code === code);
    if (index > -1) {
        cart.splice(index, 1);
        updateCartDisplay();
        showNotification('Item removido do carrinho', 'info');
    }
}

// Atualizar quantidade
function updateQuantity(code, change) {
    const item = cart.find(item => item.code === code);
    if (item) {
        item.quantity += change;
        if (item.quantity <= 0) {
            removeFromCart(code);
        } else {
            updateCartDisplay();
        }
    }
}

// Calcular total do carrinho
function getCartTotal() {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
}

// Atualizar exibição do carrinho
function updateCartDisplay() {
    const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartTotal = getCartTotal();

    // Atualizar badge do carrinho
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = cartCount;
        badge.style.display = cartCount > 0 ? 'block' : 'none';
    }

    // Atualizar total
    const totalElement = document.getElementById('cart-total');
    if (totalElement) {
        totalElement.textContent = `${cartTotal} 💰`;
    }

    // Atualizar saldo
    const balanceElement = document.getElementById('user-balance');
    if (balanceElement) {
        balanceElement.textContent = `Saldo: ${userBalance} 💰`;

        // Verificar se tem saldo suficiente
        if (cartTotal > userBalance) {
            balanceElement.style.color = '#ef4444';
        } else {
            balanceElement.style.color = '#22c55e';
        }
    }

    // Renderizar itens do carrinho
    renderCartItems();
}

// Renderizar itens do carrinho
function renderCartItems() {
    const container = document.getElementById('cart-items');
    if (!container) return;

    if (cart.length === 0) {
        container.innerHTML = '<p class="text-muted">Carrinho vazio</p>';
        return;
    }

    container.innerHTML = cart.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${item.price} 💰 x ${item.quantity}</div>
            </div>
            <div class="cart-item-controls">
                <button onclick="updateQuantity('${item.code}', -1)" class="qty-btn">-</button>
                <span class="qty-display">${item.quantity}</span>
                <button onclick="updateQuantity('${item.code}', 1)" class="qty-btn">+</button>
                <button onclick="removeFromCart('${item.code}')" class="remove-btn">🗑️</button>
            </div>
        </div>
    `).join('');
}

// Abrir modal de checkout
function openCheckout() {
    const total = getCartTotal();

    if (cart.length === 0) {
        showNotification('Carrinho vazio!', 'error');
        return;
    }

    if (total > userBalance) {
        showNotification('Saldo insuficiente!', 'error');
        return;
    }

    // Abrir modal de seleção de coordenadas
    document.getElementById('checkout-modal').style.display = 'flex';
    initializeMap();
}

// Fechar modal
function closeCheckout() {
    document.getElementById('checkout-modal').style.display = 'none';
}

// Inicializar mapa de Chernarus
function initializeMap() {
    const mapContainer = document.getElementById('map-container');
    mapContainer.innerHTML = `
        <div class="map-instructions">
            <h3>📍 Selecione o local de entrega</h3>
            <p>Clique no mapa para escolher onde seus itens serão entregues</p>
        </div>
        <div class="map-image-container">
            <img src="/static/images/chernarus_map.jpg" alt="Mapa de Chernarus" id="chernarus-map">
            <div id="map-marker" class="map-marker"></div>
        </div>
        <div class="coordinates-display">
            <span id="selected-coords">Nenhuma coordenada selecionada</span>
        </div>
    `;

    const mapImage = document.getElementById('chernarus-map');
    const marker = document.getElementById('map-marker');

    mapImage.addEventListener('click', (e) => {
        const rect = mapImage.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        // Converter para coordenadas do jogo (0-15360 para Chernarus)
        const gameX = Math.round((x / rect.width) * 15360);
        const gameY = Math.round((y / rect.height) * 15360);

        // Posicionar marcador
        marker.style.left = `${x}px`;
        marker.style.top = `${y}px`;
        marker.style.display = 'block';

        // Atualizar coordenadas selecionadas
        document.getElementById('selected-coords').textContent = `X: ${gameX}, Y: ${gameY}`;

        // Salvar coordenadas
        window.selectedCoords = { x: gameX, y: gameY };
    });
}

// Finalizar compra
async function finalizePurchase() {
    if (!window.selectedCoords) {
        showNotification('Selecione um local de entrega no mapa!', 'error');
        return;
    }

    const total = getCartTotal();

    if (total > userBalance) {
        showNotification('Saldo insuficiente!', 'error');
        return;
    }

    try {
        const response = await fetch('/api/shop/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                items: cart,
                coordinates: window.selectedCoords,
                total: total
            })
        });

        if (response.ok) {
            const data = await response.json();

            // Limpar carrinho
            cart = [];
            updateCartDisplay();
            closeCheckout();

            // Mostrar confirmação
            showPurchaseConfirmation(data);
        } else {
            const error = await response.json();
            showNotification(error.message || 'Erro ao processar compra', 'error');
        }
    } catch (error) {
        console.error('[CART] Erro ao finalizar compra:', error);
        showNotification('Erro ao processar compra. Tente novamente.', 'error');
    }
}

// Mostrar confirmação de compra
function showPurchaseConfirmation(data) {
    const modal = document.createElement('div');
    modal.className = 'confirmation-modal';
    modal.innerHTML = `
        <div class="confirmation-content">
            <div class="confirmation-icon">✅</div>
            <h2>Compra Realizada com Sucesso!</h2>
            <p>Seus itens serão entregues em:</p>
            <div class="delivery-info">
                <p><strong>📍 Coordenadas:</strong> X: ${data.coordinates.x}, Y: ${data.coordinates.y}</p>
                <p><strong>⏱️ Tempo de entrega:</strong> ${data.deliveryTime || '5-10 minutos'}</p>
                <p><strong>💰 Total pago:</strong> ${data.total} DZCoins</p>
                <p><strong>💵 Saldo restante:</strong> ${data.newBalance} DZCoins</p>
            </div>
            <p class="delivery-note">
                ⚠️ Os itens aparecerão em um baú no local selecionado.<br>
                Certifique-se de estar próximo ao local para coletar!
            </p>
            <button onclick="closeConfirmation()" class="btn-primary">Entendido</button>
        </div>
    `;
    document.body.appendChild(modal);

    // Atualizar saldo
    userBalance = data.newBalance;
    updateCartDisplay();
}

// Fechar confirmação
function closeConfirmation() {
    const modal = document.querySelector('.confirmation-modal');
    if (modal) {
        modal.remove();
    }
}

// Mostrar notificação
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Inicializar ao carregar
document.addEventListener('DOMContentLoaded', () => {
    loadUserBalance();
    updateCartDisplay();
});
