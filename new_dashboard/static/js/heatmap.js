// ==================== HEATMAP.JS (Versão Real - ChatGPT Architecture) ====================

document.addEventListener('DOMContentLoaded', function () {
    initMap();
    setupControls();
    loadHeatmapData('24h'); // Carregar dados das últimas 24h por padrão
});

let map;
let heatLayer;

// Configurações do mapa Chernarus (DayZ)
const MAP_CONFIG = {
    // Dimensões do mundo do jogo (coordenadas DayZ)
    minX: 0,
    maxX: 15360,
    minZ: 0,
    maxZ: 15360,

    // Dimensões da imagem do mapa (pixels)
    imgWidth: 15360,
    imgHeight: 15360
};

function initMap() {
    // Inicializa Leaflet com CRS.Simple
    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -3,
        maxZoom: 2,
        zoomControl: true,
        attributionControl: false
    });

    const bounds = [[0, 0], [MAP_CONFIG.imgHeight, MAP_CONFIG.imgWidth]];

    // Criar fundo cinza com grid (fallback visual)
    const canvas = document.createElement('canvas');
    canvas.width = 1024;
    canvas.height = 1024;
    const ctx = canvas.getContext('2d');

    // Fundo escuro
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, 1024, 1024);

    // Grid
    ctx.strokeStyle = '#333333';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 1024; i += 64) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, 1024);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(1024, i);
        ctx.stroke();
    }

    const fallbackUrl = canvas.toDataURL();

    // Adicionar fundo de fallback
    L.imageOverlay(fallbackUrl, bounds, { opacity: 0.5 }).addTo(map);

    // Tentar carregar tiles do iZurvive
    const tileLayer = L.tileLayer('https://tiles.izurvive.com/maps/chernarusplus/{z}/{x}/{y}.png', {
        minZoom: 0,
        maxZoom: 5,
        noWrap: true,
        tms: true,
        errorTileUrl: fallbackUrl
    });

    tileLayer.on('tileerror', function () {
        console.warn('⚠️ Tiles do iZurvive não carregaram. Usando fundo de fallback.');
    });

    tileLayer.addTo(map);

    map.fitBounds(bounds);
    map.setView([MAP_CONFIG.imgHeight / 2, MAP_CONFIG.imgWidth / 2], -1);

    // Configuração do heatmap.js
    const cfg = {
        radius: 30,
        maxOpacity: 0.8,
        scaleRadius: false,
        useLocalExtrema: false,
        latField: 'lat',
        lngField: 'lng',
        valueField: 'count',
        gradient: {
            0.0: 'blue',
            0.4: 'cyan',
            0.6: 'lime',
            0.8: 'yellow',
            1.0: 'red'
        }
    };

    heatLayer = new HeatmapOverlay(cfg).addTo(map);

    console.log('✅ Mapa inicializado. Aguardando dados...');
}

function gameToLatLng(gameX, gameZ) {
    const nx = (gameX - MAP_CONFIG.minX) / (MAP_CONFIG.maxX - MAP_CONFIG.minX);
    const nz = (gameZ - MAP_CONFIG.minZ) / (MAP_CONFIG.maxZ - MAP_CONFIG.minZ);
    const px = nx * MAP_CONFIG.imgWidth;
    const pz = (1 - nz) * MAP_CONFIG.imgHeight;
    return [pz, px];
}

async function loadHeatmapData(timeRange) {
    try {
        console.log(`🔄 Carregando heatmap para: ${timeRange}`);

        const response = await fetch(`/api/heatmap?range=${timeRange}&grid=50`);
        const result = await response.json();

        if (!result.success) {
            console.error('❌ Erro ao carregar heatmap:', result.error);
            return;
        }

        console.log(`✅ Recebidos ${result.points.length} pontos agregados`);
        console.log(`📊 Total de eventos: ${result.total_events}`);

        const heatmapData = {
            data: result.points.map(point => {
                const [lat, lng] = gameToLatLng(point.x, point.z);
                return { lat, lng, count: point.count };
            })
        };

        heatLayer.setData(heatmapData);
        updateStats(result);

    } catch (error) {
        console.error('❌ Erro ao carregar heatmap:', error);
    }
}

function updateStats(data) {
    console.log('📈 Estatísticas:', {
        range: data.range,
        totalEvents: data.total_events,
        gridSize: data.grid_size
    });
}

function setupControls() {
    const buttons = document.querySelectorAll('.control-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const timeRange = btn.dataset.time;
            loadHeatmapData(timeRange);
        });
    });
}
