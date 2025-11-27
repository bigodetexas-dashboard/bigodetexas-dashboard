// ===== CHECKOUT WITH GINFO-STYLE MAP ENGINE =====

let cart = [];
let total = 0;
let userBalance = 0;
let selectedCoords = null;
let map = null;
let marker = null;
// Initialize Leaflet Map (GINFO Style)
function initializeLeafletMap() {
    // Create map with Simple CRS (Coordinate Reference System)
    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -2,
        maxZoom: 6, // Allow deep zoom for high-res feel
        zoomSnap: 0.5,
        zoomControl: true,
        attributionControl: false
    });

    // Define bounds for Chernarus (15360x15360)
    // Leaflet CRS.Simple: [y, x]
    const bounds = [[0, 0], [MAP_SIZE, MAP_SIZE]];

    // === MAP DATA SOURCE ===
    // Currently using local image. 
    const imageUrl = '/static/img/chernarus_map.png';
    const imageOverlay = L.imageOverlay(imageUrl, bounds);

    // DEBUG: Event listeners for image loading
    imageOverlay.on('load', () => {
        console.log("✅ MAP IMAGE LOADED SUCCESSFULLY");
    });

    imageOverlay.on('error', (e) => {
        console.error("❌ MAP IMAGE FAILED TO LOAD", e);
        alert(`ERRO: A imagem do mapa não carregou.\nURL: ${imageUrl}\nVerifique sua conexão ou se existe algum bloqueador.`);

        // Fallback: Show a colored background so user knows map area exists
        document.getElementById('map').style.backgroundColor = '#2a2a2a';
        document.getElementById('map').innerHTML += '<p style="color:white; text-align:center; padding-top:50px;">Erro ao carregar imagem do mapa.</p>';
    });

    imageOverlay.addTo(map);

    // Fit map to bounds initially
    map.fitBounds(bounds);

    // Add scale control (Meters)
    L.control.scale({
        imperial: false,
        metric: true,
        maxWidth: 200
    }).addTo(map);

    // DEBUG: Check container size
    setTimeout(() => {
        const mapDiv = document.getElementById('map');
        console.log(`Map Size: ${mapDiv.offsetWidth}x${mapDiv.offsetHeight}`);
        if (mapDiv.offsetHeight < 100) {
            alert(`ALERTA: O mapa está muito pequeno (${mapDiv.offsetHeight}px). Isso pode ser um erro de CSS.`);
            mapDiv.style.height = '700px'; // Force fix
            map.invalidateSize();
        }
    }, 1000);

    // Click event handler
    map.on('click', function (e) {
        // In CRS.Simple with bounds [[0,0], [H,W]]:
        // e.latlng.lng = X coordinate
        // e.latlng.lat = Y coordinate (from bottom 0 to top H)

        const x = Math.round(e.latlng.lng);
        const z = Math.round(e.latlng.lat);

        // Validate coordinates
        if (x >= 0 && x <= MAP_SIZE && z >= 0 && z <= MAP_SIZE) {
            setCoordinates(x, z, e.latlng);
        }
    });
}

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('btn-confirm-order').addEventListener('click', confirmOrder);
}

// Set Coordinates
function setCoordinates(gameX, gameZ, latLng) {
    selectedCoords = { x: gameX, z: gameZ };

    // Update coordinate inputs
    document.getElementById('coord-x').value = gameX;
    document.getElementById('coord-z').value = gameZ;

    // Remove existing marker
    if (marker) map.removeLayer(marker);

    // Add new marker
    const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `
            <div style="position: relative;">
                <i class="fas fa-map-pin" style="
                    font-size: 2.5rem; 
                    color: #ff4757; 
                    filter: drop-shadow(0 0 10px rgba(255, 71, 87, 0.8));
                "></i>
            </div>
        `,
        iconSize: [30, 42],
        iconAnchor: [15, 42]
    });

    marker = L.marker(latLng, { icon: customIcon }).addTo(map);

    // Add popup
    marker.bindPopup(`
        <div style="text-align: center; padding: 8px; font-family: Arial;">
            <strong style="color: #ff6b35; font-size: 1.1em;">📍 Local Selecionado</strong><br>
            <div style="margin-top: 8px; padding: 8px; background: rgba(255, 107, 53, 0.1); border-radius: 6px;">
                <span style="font-weight: 600;">X:</span> ${gameX}m<br>
                <span style="font-weight: 600;">Z:</span> ${gameZ}m
            </div>
        </div>
    `, {
        maxWidth: 200,
        className: 'custom-popup'
    }).openPopup();

    // Enable confirm button
    document.getElementById('btn-confirm-order').disabled = false;
}

// Load Checkout Data
function loadCheckoutData() {
    let cartData = sessionStorage.getItem('checkout_cart');
    let totalData = sessionStorage.getItem('checkout_total');

    if (!cartData) {
        const localCart = localStorage.getItem('shop_cart');
        if (localCart) {
            const parsedCart = JSON.parse(localCart);
            if (parsedCart.length > 0) {
                cartData = localCart;
                totalData = parsedCart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
                sessionStorage.setItem('checkout_cart', cartData);
                sessionStorage.setItem('checkout_total', totalData);
            }
        }
    }

    if (!cartData || !totalData) {
        alert('Carrinho vazio! Redirecionando para a loja...');
        window.location.href = '/shop';
        return;
    }

    cart = JSON.parse(cartData);
    total = parseInt(totalData);
    displayOrderSummary();
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

// Display Order Summary
function displayOrderSummary() {
    const itemsContainer = document.getElementById('order-items');
    itemsContainer.innerHTML = cart.map(item => `
        <div class="order-item">
            <div class="order-item-info">
                <div class="order-item-name">${item.name}</div>
                <div class="order-item-qty">Quantidade: ${item.quantity}</div>
            </div>
            <div class="order-item-price">${(item.price * item.quantity).toLocaleString('pt-BR')} DZ</div>
        </div>
    `).join('');

    document.getElementById('subtotal').textContent = `${total.toLocaleString('pt-BR')} DZ Coins`;
    document.getElementById('total').textContent = `${total.toLocaleString('pt-BR')} DZ Coins`;
}

// Update Balance Display
function updateBalanceDisplay() {
    document.getElementById('user-balance').textContent = userBalance.toLocaleString('pt-BR');
    document.getElementById('current-balance').textContent = `${userBalance.toLocaleString('pt-BR')} DZ Coins`;

    const balanceAfter = userBalance - total;
    const balanceAfterEl = document.getElementById('balance-after');
    balanceAfterEl.textContent = `${balanceAfter.toLocaleString('pt-BR')} DZ Coins`;

    if (balanceAfter < 0) {
        balanceAfterEl.classList.add('negative');
        balanceAfterEl.classList.remove('balance-after');
    } else {
        balanceAfterEl.classList.remove('negative');
        balanceAfterEl.classList.add('balance-after');
    }
}

// Confirm Order
async function confirmOrder() {
    if (!selectedCoords) {
        alert('Por favor, selecione um local de entrega no mapa!');
        return;
    }
    if (total > userBalance) {
        alert('Saldo insuficiente!');
        return;
    }

    const orderData = {
        items: cart,
        coordinates: selectedCoords,
        total: total
    };

    try {
        document.getElementById('btn-confirm-order').disabled = true;
        document.getElementById('btn-confirm-order').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';

        const response = await fetch('/api/shop/purchase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(orderData)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            sessionStorage.removeItem('checkout_cart');
            sessionStorage.removeItem('checkout_total');
            localStorage.removeItem('shop_cart');
            window.location.href = `/order-confirmation?id=${result.deliveryId}&x=${selectedCoords.x}&z=${selectedCoords.z}`;
        } else {
            alert(result.error || 'Erro ao processar pedido!');
            document.getElementById('btn-confirm-order').disabled = false;
            document.getElementById('btn-confirm-order').innerHTML = '<i class="fas fa-check-circle"></i> Confirmar Pedido';
        }
    } catch (error) {
        console.error('Error confirming order:', error);
        alert('Erro ao processar pedido!');
        document.getElementById('btn-confirm-order').disabled = false;
        document.getElementById('btn-confirm-order').innerHTML = '<i class="fas fa-check-circle"></i> Confirmar Pedido';
    }
}

// Add CSS for marker animation
const style = document.createElement('style');
style.textContent = `
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);
