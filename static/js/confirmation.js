// ==================== CONFIRMATION.JS ====================

let deliveryTime = 300; // 5 minutos em segundos

document.addEventListener('DOMContentLoaded', function () {
    loadOrderDetails();
    startCountdown();
});

function loadOrderDetails() {
    const orderData = localStorage.getItem('order-confirmation');
    if (!orderData) {
        console.log('Nenhum pedido encontrado, redirecionando...');
        // Não redirecionar automaticamente para permitir testes
        // window.location.href = '/shop';
        return;
    }

    const order = JSON.parse(orderData);
    console.log('Dados do pedido:', order);

    // Preencher ID do pedido (se houver)
    if (order.id) {
        document.getElementById('order-id').textContent = '#' + order.id;
    } else {
        document.getElementById('order-id').textContent = '#' + Math.floor(Math.random() * 10000);
    }

    // Preencher coordenadas
    if (order.coordinates) {
        const coords = order.coordinates;
        document.getElementById('delivery-location').textContent = `X: ${coords.x}, Z: ${coords.z}`;

        // Posicionar marcador no mini-mapa (proporcionalmente)
        const marker = document.getElementById('map-marker-preview');
        if (marker) {
            const xPercent = (coords.x / 15360) * 100;
            const zPercent = (coords.z / 15360) * 100;
            marker.style.left = xPercent + '%';
            marker.style.top = zPercent + '%';
        }
    }

    // Limpar dados do localStorage após carregar
    // localStorage.removeItem('order-confirmation');
}

function startCountdown() {
    const timerElement = document.getElementById('countdown');

    const interval = setInterval(() => {
        deliveryTime--;

        const minutes = Math.floor(deliveryTime / 60);
        const seconds = deliveryTime % 60;

        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;

        if (deliveryTime <= 0) {
            clearInterval(interval);
            timerElement.textContent = 'Entregue!';
            timerElement.style.color = '#00ff00';
        }
    }, 1000);
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}
