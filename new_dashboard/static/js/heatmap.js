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
    // iZurvive usa tiles, mas vamos trabalhar com coordenadas virtuais
    imgWidth: 15360,
    imgHeight: 15360
};

function initMap() {
    // Inicializa Leaflet com CRS.Simple para usar coordenadas de pixels
    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -3,
        maxZoom: 2,
        zoomControl: true,
        attributionControl: false
    });

    // Define bounds para o mapa
    const bounds = [[0, 0], [MAP_CONFIG.imgHeight, MAP_CONFIG.imgWidth]];

    // Adiciona tiles do iZurvive (Chernarus+)
    L.tileLayer('https://tiles.izurvive.com/maps/chernarusplus/{z}/{x}/{y}.png', {
        minZoom: 0,
        maxZoom: 5,
        noWrap: true,
        tms: true,
        bounds: bounds
    }).addTo(map);

    map.fitBounds(bounds);
    map.setView([MAP_CONFIG.imgHeight / 2, MAP_CONFIG.imgWidth / 2], -1);

    // Configuração do heatmap.js (seguindo sugestão do GPT)
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
}

/**
 * Converte coordenadas do jogo (X, Z) para coordenadas Leaflet (Lat, Lng)
 * Implementação da fórmula sugerida pelo ChatGPT
 */
function gameToLatLng(gameX, gameZ) {
    // Normaliza para 0..1
    const nx = (gameX - MAP_CONFIG.minX) / (MAP_CONFIG.maxX - MAP_CONFIG.minX);
    const nz = (gameZ - MAP_CONFIG.minZ) / (MAP_CONFIG.maxZ - MAP_CONFIG.minZ);

    // Converte para pixels
    const px = nx * MAP_CONFIG.imgWidth;
    // Inverter Z porque a imagem tem origem no topo
    const pz = (1 - nz) * MAP_CONFIG.imgHeight;

    // Retorna como [lat, lng] para Leaflet CRS.Simple
    return [pz, px];
}

/**
 * Carrega dados do heatmap da API
 * Implementa o fluxo sugerido pelo ChatGPT
 */
async function loadHeatmapData(timeRange) {
    try {
        console.log(`Carregando heatmap para: ${timeRange}`);

        // Fetch da API (Grid Clustering já feito no backend)
        const response = await fetch(`/api/heatmap?range=${timeRange}&grid=50`);
        const result = await response.json();

        if (!result.success) {
            console.error('Erro ao carregar heatmap:', result.error);
            return;
        }

        console.log(`Recebidos ${result.points.length} pontos agregados`);
        console.log(`Total de eventos: ${result.total_events}`);

        // Converte pontos do jogo para coordenadas do mapa
        const heatmapData = {
            data: result.points.map(point => {
                const [lat, lng] = gameToLatLng(point.x, point.z);
                return {
                    lat: lat,
                    lng: lng,
                    count: point.count
                };
            })
        };

        // Atualiza a camada de calor
        heatLayer.setData(heatmapData);

        // Atualiza estatísticas na UI (opcional)
        updateStats(result);

    } catch (error) {
        console.error('Erro ao carregar heatmap:', error);
    }
}

/**
 * Atualiza estatísticas exibidas (opcional)
 */
function updateStats(data) {
    // Você pode adicionar elementos na UI para mostrar essas stats
    console.log('Estatísticas:', {
        range: data.range,
        totalEvents: data.total_events,
        gridSize: data.grid_size
    });
}

/**
 * Configura os controles de filtro (botões de tempo)
 */
function setupControls() {
    const buttons = document.querySelectorAll('.control-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove classe active de todos
            buttons.forEach(b => b.classList.remove('active'));

            // Adiciona ao clicado
            btn.classList.add('active');

            // Recarrega dados com novo filtro
            const timeRange = btn.dataset.time;
            loadHeatmapData(timeRange);
        });
    });
}
