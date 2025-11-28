// ===== CHECKOUT WITH GINFO-STYLE MAP ENGINE =====

let cart = [];
let total = 0;
let userBalance = 0;
let selectedCoords = null;
let map = null;
let marker = null;

// Chernarus Map Configuration (15360x15360 meters)
const MAP_SIZE = 15360;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 CHECKOUT SCRIPT v3.0 LOADED - WITH FALLBACK");

    loadCheckoutData();
    loadUserBalance();

    // Small delay to ensure container is rendered
    setTimeout(() => {
        initializeLeafletMap();
        // Force map resize calculation
        if (map) {
            map.invalidateSize();
        }
    }, 100);

    setupEventListeners();
});

// Test if a tile URL works
async function testTileUrl(urlTemplate) {
    return new Promise((resolve) => {
        const testUrl = urlTemplate.replace('{z}', '2').replace('{x}', '1').replace('{y}', '1');
        const img = new Image();
        img.crossOrigin = 'anonymous';
        let loaded = false;

        img.onload = () => {
            loaded = true;
            resolve(true);
        };

        img.onerror = () => {
            resolve(false);
        };

        img.src = testUrl;

        // Timeout after 2 seconds
        setTimeout(() => resolve(loaded), 2000);
    });
}

// Initialize Leaflet Map (GINFO Style with Fallback)
async function initializeLeafletMap() {
    // Create map with Simple CRS (Coordinate Reference System)
    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -2,
        maxZoom: 6,
        zoomSnap: 0.5,
        zoomControl: true,
        attributionControl: false
    });

    // Define bounds for Chernarus (15360x15360)
    const bounds = [[0, 0], [MAP_SIZE, MAP_SIZE]];

    // Fit map to bounds initially
    map.fitBounds(bounds);

    // Add scale control (Meters)
    L.control.scale({
        imperial: false,
        metric: true,
        maxWidth: 200
    }).addTo(map);

    // === TRY PUBLIC TILE SERVERS FIRST ===
    const tileCandidates = [
        'https://tiles.dayz.gg/chernarus/{z}/{x}/{y}.png',
        'https://dayz.xam.nu/tiles/chernarusplus/{z}/{x}/{y}.png',
        '/static/tiles/{z}/{x}/{y}.png' // Local tiles if you add them later
    ];

    let tileLayerLoaded = false;

    for (const tileUrl of tileCandidates) {
        try {
            console.log('🔍 Testing tile server:', tileUrl);
            const works = await testTileUrl(tileUrl);
            if (works) {
                console.log('✅ Using tile server:', tileUrl);
                L.tileLayer(tileUrl, {
                    tileSize: 256,
                    noWrap: true,
                    bounds: bounds,
                    minZoom: -2,
                    maxZoom: 6
                }).addTo(map);
                tileLayerLoaded = true;
                break;
            } else {
                console.warn('❌ Tile server failed:', tileUrl);
            }
        } catch (e) {
            console.warn('❌ Error testing tile:', tileUrl, e);
        }
    }

    // === FALLBACK: USE LOCAL IMAGE ===
    if (!tileLayerLoaded) {
        console.log('📦 No tile server available - using local image fallback');

        const imageUrl = '/static/img/chernarus_map.png';
        const imageOverlay = L.imageOverlay(imageUrl, bounds);

        imageOverlay.on('load', () => {
            console.log("✅ MAP IMAGE LOADED");
        });

        imageOverlay.on('error', (e) => {
            console.warn("⚠️ Image failed, map will show placeholder");
            // Show placeholder message
            document.getElementById('map').style.backgroundColor = '#2a2a2a';
            const msg = document.createElement('p');
            msg.style.cssText = 'color:white; text-align:center; padding-top:50px; font-size:14px;';
            msg.textContent = 'Mapa em modo placeholder - clique para selecionar coordenadas';
            document.getElementById('map').appendChild(msg);
        });

        imageOverlay.addTo(map);
    }

    // Setup click handler
    map.on('click', function (e) {
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
