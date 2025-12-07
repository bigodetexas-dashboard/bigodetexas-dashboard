// ==================== HEATMAP.JS (Versão Completa) ====================

document.addEventListener('DOMContentLoaded', function () {
    initMap();
    setupControls();
    setupCharts();

    // Carregamento inicial
    loadAllData('24h');
    loadWeaponList();
});

let map;
let heatLayer;
let markersLayer;
let timelineChart;
let hourlyChart;

// Configurações do mapa Chernarus (DayZ)
const MAP_CONFIG = {
    minX: 0, maxX: 15360,
    minZ: 0, maxZ: 15360
};

// Estado atual dos filtros
const currentFilters = {
    range: '24h',
    type: 'all',
    weapon: 'all'
};

function initMap() {
    console.log('🗺️ Inicializando mapa Chernarus (Tiles)...');

    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: 0,
        maxZoom: 7,
        zoomControl: false, // Usaremos controles customizados
        attributionControl: false
    });

    // Camada de Tiles (Mosaicos)
    // Estrutura: /static/tiles/{z}/{x}/{y}.png
    L.tileLayer('/static/tiles/{z}/{x}/{y}.png', {
        tileSize: 256,
        minZoom: 0,
        maxZoom: 7,
        noWrap: true,
        tms: false,
        attribution: 'Map data &copy; Bohemia Interactive, iZurvive'
    }).addTo(map);

    // Centralizar o mapa
    // O mapa tem 256x256 unidades no zoom 0
    // Centro = [128, 128] (mas Y é negativo no CRS.Simple padrão)
    map.setView([-128, 128], 2);

    // Configuração do heatmap
    const cfg = {
        radius: 0.0015, // Raio relativo ao tamanho do mapa (ajustado para tiles)
        maxOpacity: 0.8,
        scaleRadius: true, // Escalar com o zoom
        useLocalExtrema: false,
        latField: 'lat',
        lngField: 'lng',
        valueField: 'count',
        gradient: {
            0.0: 'rgba(0, 0, 255, 0)',
            0.2: 'rgba(0, 0, 255, 0.5)',
            0.4: 'rgba(0, 255, 255, 0.7)',
            0.6: 'rgba(0, 255, 0, 0.8)',
            0.8: 'rgba(255, 255, 0, 0.9)',
            1.0: 'rgba(255, 0, 0, 1)'
        }
    };

    heatLayer = new HeatmapOverlay(cfg).addTo(map);
    markersLayer = L.layerGroup().addTo(map);

    // Controles de Zoom Customizados
    document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
    document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());
    document.getElementById('resetView').addEventListener('click', () => {
        map.setView([-128, 128], 2);
    });
}

function setupCharts() {
    // Configuração comum para gráficos dark mode
    Chart.defaults.color = '#a0a0a0';
    Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';

    // Timeline Chart
    const ctxTimeline = document.getElementById('timelineChart').getContext('2d');
    timelineChart = new Chart(ctxTimeline, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Mortes PvP',
                borderColor: '#ff4757',
                backgroundColor: 'rgba(255, 71, 87, 0.2)',
                data: [],
                fill: true,
                tension: 0.4
            }, {
                label: 'Mortes PvE',
                borderColor: '#2ed573',
                backgroundColor: 'rgba(46, 213, 115, 0.2)',
                data: [],
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Hourly Chart
    const ctxHourly = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(ctxHourly, {
        type: 'bar',
        data: {
            labels: Array.from({ length: 24 }, (_, i) => `${i}h`),
            datasets: [{
                label: 'Atividade por Hora',
                backgroundColor: '#ffa502',
                data: []
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function setupControls() {
    // Filtros de Tempo
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilters.range = e.target.dataset.time;
            loadAllData(currentFilters.range);
        });
    });

    // Filtros de Tipo
    document.querySelectorAll('.type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.type-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilters.type = e.target.dataset.type;
            // Recarregar apenas o heatmap com filtro local (simulado por enquanto)
            // Idealmente o backend filtraria, mas vamos recarregar tudo por simplicidade
            loadAllData(currentFilters.range);
        });
    });

    // Filtro de Arma
    document.getElementById('weaponFilter').addEventListener('change', (e) => {
        currentFilters.weapon = e.target.value;
        // TODO: Implementar filtro de arma no backend
        console.log('Filtro de arma alterado:', currentFilters.weapon);
    });
}

function loadAllData(range) {
    loadHeatmapData(range);
    loadTopLocations(range);
    loadTimelineData(range);
    loadHourlyData(range);
    loadWeaponStats(range);
}

async function loadHeatmapData(range) {
    try {
        const response = await fetch(`/api/heatmap?range=${range}&grid=50`);
        const result = await response.json();

        if (result.success) {
            const heatmapData = {
                data: result.points.map(point => {
                    const [lat, lng] = gameToLatLng(point.x, point.z);
                    return { lat, lng, count: point.count };
                })
            };
            heatLayer.setData(heatmapData);

            // Atualizar Card de Total
            document.getElementById('totalDeaths').innerText = result.total_events;
        }
    } catch (error) {
        console.error('Erro heatmap:', error);
    }
}

async function loadTopLocations(range) {
    try {
        const response = await fetch(`/api/heatmap/top_locations?range=${range}`);
        const result = await response.json();

        if (result.success) {
            updateTopLocationsUI(result.locations);
            updateMapMarkers(result.locations);
        }
    } catch (error) {
        console.error('Erro top locations:', error);
    }
}

async function loadTimelineData(range) {
    try {
        const response = await fetch(`/api/heatmap/timeline?range=${range}`);
        const result = await response.json();

        if (result.success) {
            timelineChart.data.labels = result.timeline.map(t => {
                const date = new Date(t.period);
                return range === '24h' ?
                    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) :
                    date.toLocaleDateString();
            });
            timelineChart.data.datasets[0].data = result.timeline.map(t => t.pvp);
            timelineChart.data.datasets[1].data = result.timeline.map(t => t.pve);
            timelineChart.update();

            // Calcular porcentagens
            const totalPvP = result.timeline.reduce((acc, curr) => acc + curr.pvp, 0);
            const totalPvE = result.timeline.reduce((acc, curr) => acc + curr.pve, 0);
            const total = totalPvP + totalPvE;

            if (total > 0) {
                document.getElementById('pvpPercent').innerText = Math.round((totalPvP / total) * 100) + '%';
                document.getElementById('pvePercent').innerText = Math.round((totalPvE / total) * 100) + '%';
            }
        }
    } catch (error) {
        console.error('Erro timeline:', error);
    }
}

async function loadHourlyData(range) {
    try {
        const response = await fetch(`/api/heatmap/hourly?range=${range}`);
        const result = await response.json();

        if (result.success) {
            hourlyChart.data.datasets[0].data = result.hourly;
            hourlyChart.update();
        }
    } catch (error) {
        console.error('Erro hourly:', error);
    }
}

async function loadWeaponStats(range) {
    try {
        const response = await fetch(`/api/heatmap/weapons?range=${range}`);
        const result = await response.json();

        if (result.success && result.weapons.length > 0) {
            const topWeapon = result.weapons[0];
            document.getElementById('topWeapon').innerText = topWeapon.name;
        } else {
            document.getElementById('topWeapon').innerText = '-';
        }
    } catch (error) {
        console.error('Erro weapons:', error);
    }
}

async function loadWeaponList() {
    try {
        const response = await fetch('/api/heatmap/weapons?range=30d'); // Pegar histórico maior
        const result = await response.json();

        if (result.success) {
            const select = document.getElementById('weaponFilter');
            result.weapons.forEach(w => {
                const option = document.createElement('option');
                option.value = w.name;
                option.innerText = `${w.name} (${w.count})`;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro lista armas:', error);
    }
}

function updateTopLocationsUI(locations) {
    const grid = document.getElementById('topLocations');
    if (!grid) return;

    grid.innerHTML = '';
    locations.forEach((loc, index) => {
        const dangerLevel = loc.deaths > 50 ? 'high' : loc.deaths > 20 ? 'medium' : 'low';
        const dangerText = loc.deaths > 50 ? 'Extremo' : loc.deaths > 20 ? 'Alto' : 'Médio';

        const card = document.createElement('div');
        card.className = 'location-card';
        card.innerHTML = `
            <span class="rank">#${index + 1}</span>
            <div class="loc-info">
                <h3>${loc.location_name || `Zona ${index + 1}`}</h3>
                <p>${loc.deaths} Mortes</p>
            </div>
            <div class="danger-level ${dangerLevel}">${dangerText}</div>
        `;

        card.addEventListener('click', () => {
            const [lat, lng] = gameToLatLng(loc.center_x, loc.center_z);
            map.setView([lat, lng], 0);
        });

        grid.appendChild(card);
    });
}

function updateMapMarkers(locations) {
    markersLayer.clearLayers();
    locations.forEach((loc, index) => {
        const [lat, lng] = gameToLatLng(loc.center_x, loc.center_z);
        const marker = L.circleMarker([lat, lng], {
            radius: 10 + (5 - index) * 2,
            fillColor: index === 0 ? '#ff0000' : '#ffaa00',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.7
        });

        marker.bindPopup(`<b>${loc.location_name || 'Zona Quente'}</b><br>Mortes: ${loc.deaths}`);
        marker.addTo(markersLayer);
    });
}

function gameToLatLng(gameX, gameZ) {
    const nx = (gameX - MAP_CONFIG.minX) / (MAP_CONFIG.maxX - MAP_CONFIG.minX);
    const nz = (gameZ - MAP_CONFIG.minZ) / (MAP_CONFIG.maxZ - MAP_CONFIG.minZ);

    // No L.CRS.Simple com tiles padrão, o mundo tem tamanho 256x256 no zoom 0
    const mapSize = 256;

    const px = nx * mapSize;
    const py = (1 - nz) * mapSize; // Inverter Y (DayZ 0,0 é bottom-left)

    // Retorna [lat, lng]. Em CRS.Simple, lat é -y (geralmente)
    return [-py, px];
}
