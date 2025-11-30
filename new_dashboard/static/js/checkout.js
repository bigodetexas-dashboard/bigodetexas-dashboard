// ==================== CHECKOUT.JS ====================
// Sistema de checkout com mapa iZurvive

let cart = [];
let userBalance = 0;

document.addEventListener('DOMContentLoaded', function () {
    loadCheckoutCart();
    loadUserBalance();
    setupEventListeners();
});

// Carregar saldo do usuário
async function loadUserBalance() {
    try {
        const response = await fetch('/api/user/balance');
        const data = await response.json();
        userBalance = data.balance || 0;
        document.getElementById('user-balance').textContent = formatNumber(userBalance);
        document.getElementById('current-balance').textContent = formatNumber(userBalance) + ' DZCoins';
        updateBalanceAfter();
    } catch (error) {
        console.error('Erro ao carregar saldo:', error);
        userBalance = 0;
    }
}

function loadCheckoutCart() {
    const saved = localStorage.getItem('checkout-cart');
    if (!saved) {
        alert('Carrinho vazio! Redirecionando para a loja...');
        window.location.href = '/shop';
        return;
    }

    cart = JSON.parse(saved);
    renderOrderSummary();
}

function renderOrderSummary() {
    const container = document.getElementById('order-items');
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    container.innerHTML = cart.map(item => `
        <div style="display: flex; justify-content: space-between; padding: 1rem; background: rgba(30, 26, 24, 0.6); border: 1px solid rgba(90, 26, 26, 0.2); margin-bottom: 0.5rem; border-radius: 4px;">
            <div>
                <div style="font-weight: bold; color: var(--text-primary); margin-bottom: 0.25rem;">${item.name}</div>
                <div style="color: var(--text-secondary); font-size: 0.9rem;">Quantidade: ${item.quantity}</div>
            </div>
            <div style="color: var(--accent); font-weight: bold; font-size: 1.1rem;">${formatNumber(item.price * item.quantity)} 💰</div>
        </div>
    `).join('');

    document.getElementById('subtotal').textContent = formatNumber(total) + ' DZCoins';
    document.getElementById('total').textContent = formatNumber(total) + ' DZCoins';
    updateBalanceAfter();
}

function updateBalanceAfter() {
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const balanceAfter = userBalance - total;
    const balanceElement = document.getElementById('balance-after');
    balanceElement.textContent = formatNumber(balanceAfter) + ' DZCoins';

    if (balanceAfter < 0) {
        balanceElement.style.color = '#ff4757';
    } else {
        balanceElement.style.color = 'var(--accent)';
    }
}

function setupEventListeners() {
    // Confirmar pedido
    document.getElementById('btn-confirm-order').addEventListener('click', confirmOrder);

    // Validar coordenadas ao digitar
    document.getElementById('coord-x').addEventListener('input', validateCoords);
    document.getElementById('coord-z').addEventListener('input', validateCoords);
}

function validateCoords() {
    const x = document.getElementById('coord-x').value;
    const z = document.getElementById('coord-z').value;

    const btn = document.getElementById('btn-confirm-order');

    if (x && z && x >= 0 && x <= 15360 && z >= 0 && z <= 15360) {
        btn.disabled = false;
        btn.style.opacity = '1';
    } else {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    }
}

async function confirmOrder() {
    const x = parseInt(document.getElementById('coord-x').value);
    const z = parseInt(document.getElementById('coord-z').value);

    if (!x || !z || x < 0 || x > 15360 || z < 0 || z > 15360) {
        alert('Por favor, insira coordenadas válidas (0-15360)!');
        return;
    }

    const orderTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    if (orderTotal > userBalance) {
        alert(`Saldo insuficiente! Você tem ${formatNumber(userBalance)} DZCoins mas precisa de ${formatNumber(orderTotal)} DZCoins.`);
        return;
    }

    const orderData = {
        items: cart.map(item => ({
            code: item.code,
            name: item.name,
            quantity: item.quantity,
            price: item.price
        })),
        coordinates: { x, z },
        total: orderTotal
    };

    try {
        const response = await fetch('/api/shop/purchase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });

        const data = await response.json();

        if (data.success) {
            // Limpar carrinho
            localStorage.removeItem('cart');
            localStorage.removeItem('checkout-cart');

            // Redirecionar para confirmação
            localStorage.setItem('order-confirmation', JSON.stringify(data));
            window.location.href = '/order-confirmation';
        } else {
            alert('Erro ao processar pedido: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao confirmar pedido:', error);
        alert('Erro ao processar pedido. Tente novamente.');
    }
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
