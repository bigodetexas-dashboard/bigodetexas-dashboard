// ===== ORDER CONFIRMATION JAVASCRIPT =====

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const orderId = urlParams.get('id');
const coordX = urlParams.get('x');
const coordZ = urlParams.get('z');

// Delivery time in seconds (5 minutes)
let remainingTime = 300;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    displayOrderInfo();
    startCountdown();
    displayMapMarker();
});

// Display Order Info
function displayOrderInfo() {
    if (orderId) {
        document.getElementById('order-id').textContent = orderId;
    }

    if (coordX && coordZ) {
        document.getElementById('delivery-location').textContent = `X: ${coordX}, Z: ${coordZ}`;
    }
}

// Start Countdown
function startCountdown() {
    const countdownEl = document.getElementById('countdown');

    const interval = setInterval(() => {
        remainingTime--;

        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;

        countdownEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (remainingTime <= 0) {
            clearInterval(interval);
            countdownEl.textContent = 'Entregue!';
            countdownEl.style.color = 'var(--success)';
            showDeliveryNotification();
        }
    }, 1000);
}

// Display Map Marker
function displayMapMarker() {
    if (!coordX || !coordZ) return;

    const MAP_SIZE = 15360;
    const marker = document.getElementById('map-marker-preview');
    const map = document.getElementById('mini-map');

    const rect = map.getBoundingClientRect();
    const pixelX = (coordX / MAP_SIZE) * rect.width;
    const pixelY = (coordZ / MAP_SIZE) * rect.height;

    marker.style.left = `${pixelX}px`;
    marker.style.top = `${pixelY}px`;
}

// Show Delivery Notification
function showDeliveryNotification() {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--success);
        color: white;
        padding: 30px 50px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0, 217, 255, 0.5);
        z-index: 10000;
        font-size: 1.5rem;
        font-weight: 700;
        text-align: center;
        animation: scaleIn 0.5s ease;
    `;
    notification.innerHTML = `
        <i class="fas fa-box-open" style="font-size: 3rem; display: block; margin-bottom: 15px;"></i>
        Seus itens foram entregues!<br>
        <small style="font-size: 1rem; font-weight: 400; opacity: 0.9;">Vá até o local para pegá-los</small>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 5000);
}
