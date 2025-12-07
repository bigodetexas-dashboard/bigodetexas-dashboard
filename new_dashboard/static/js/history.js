// ============================================
// HISTORY.JS - Conectar com API Real
// ============================================

// Dados de histórico
let historyData = [];
let displayedEvents = 5;
let currentFilter = 'all';
let currentPeriod = 'all';

// Carregar eventos da API
async function loadHistory() {
    try {
        const response = await fetch(`/api/history/events?type=${currentFilter}&period=${currentPeriod}&limit=100`);
        const data = await response.json();

        if (response.ok) {
            historyData = data;
            renderTimeline();
            await loadHistoryStats();
        } else {
            console.error('Erro ao carregar histórico:', data.error);
            loadMockHistory();
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        loadMockHistory();
    }
}

// Carregar estatísticas
async function loadHistoryStats() {
    try {
        const response = await fetch(`/api/history/stats?period=${currentPeriod}`);
        const data = await response.json();

        if (response.ok) {
            document.getElementById('totalEvents').textContent = data.total_events || 0;
            document.getElementById('totalKills').textContent = data.total_kills || 0;
            document.getElementById('totalDeaths').textContent = data.total_deaths || 0;
            document.getElementById('kdRatio').textContent = data.kd_ratio || '0.0';
            document.getElementById('avgSession').textContent = data.avg_session || '0h';
        }
    } catch (error) {
        console.error('Erro ao carregar stats:', error);
    }
}

// Dados mockados como fallback
function loadMockHistory() {
    historyData = [
        {
            type: 'kill',
            icon: '⚔️',
            title: 'Eliminação em Combate',
            description: 'Você eliminou o jogador "SniperPro123"',
            timestamp: new Date('2025-12-06T14:30:00'),
            details: {
                weapon: 'M4A1',
                distance: '245m',
                location: 'Elektro',
                headshot: 'Sim'
            }
        },
        {
            type: 'achievement',
            icon: '🏆',
            title: 'Conquista Desbloqueada',
            description: 'Você desbloqueou "Primeiro Sangue"',
            timestamp: new Date('2025-12-06T13:15:00'),
            details: {
                points: '+10 pontos',
                reward: '100 moedas',
                rarity: 'Comum'
            }
        },
        {
            type: 'death',
            icon: '💀',
            title: 'Morte em Combate',
            description: 'Você foi eliminado por "ClanLeader99"',
            timestamp: new Date('2025-12-06T12:00:00'),
            details: {
                weapon: 'SVD',
                location: 'NWAF',
                survivalTime: '3h 45m'
            }
        }
    ];
    renderTimeline();
    updateStats();
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes} minutos atrás`;
    if (hours < 24) return `${hours} horas atrás`;
    return `${days} dias atrás`;
}

function renderTimeline() {
    const timeline = document.getElementById('timeline');
    const filtered = filterEvents();

    if (filtered.length === 0) {
        timeline.innerHTML = `
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>Nenhum evento encontrado para os filtros selecionados</p>
            </div>
        `;
        return;
    }

    const toDisplay = filtered.slice(0, displayedEvents);

    timeline.innerHTML = toDisplay.map(event => `
        <div class="timeline-item">
            <div class="timeline-card">
                <div class="timeline-header">
                    <div class="timeline-type">
                        <span class="icon">${event.icon}</span>
                        <span>${event.title}</span>
                    </div>
                    <div class="timeline-time">${formatTimeAgo(event.timestamp)}</div>
                </div>
                <div class="timeline-content">
                    ${event.description}
                    <span class="event-badge badge-${event.type}">${event.type}</span>
                </div>
                <div class="timeline-details">
                    ${Object.entries(event.details || {}).map(([key, value]) => `
                        <div class="detail-item">
                            <div class="detail-label">${key}</div>
                            <div class="detail-value">${value}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `).join('');

    document.getElementById('loadMoreBtn').style.display =
        displayedEvents >= filtered.length ? 'none' : 'block';
}

function filterEvents() {
    return historyData.filter(event => {
        if (currentFilter !== 'all' && event.type !== currentFilter) return false;

        const eventDate = new Date(event.timestamp);
        const now = new Date();

        if (currentPeriod === 'today') {
            return eventDate.toDateString() === now.toDateString();
        } else if (currentPeriod === 'week') {
            const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
            return eventDate >= weekAgo;
        } else if (currentPeriod === 'month') {
            const monthAgo = new Date(now - 30 * 24 * 60 * 60 * 1000);
            return eventDate >= monthAgo;
        }

        return true;
    });
}

function updateStats() {
    const filtered = filterEvents();
    const kills = filtered.filter(e => e.type === 'kill').length;
    const deaths = filtered.filter(e => e.type === 'death').length;
    const kdRatio = deaths > 0 ? (kills / deaths).toFixed(2) : kills.toFixed(2);

    document.getElementById('totalEvents').textContent = filtered.length;
    document.getElementById('totalKills').textContent = kills;
    document.getElementById('totalDeaths').textContent = deaths;
    document.getElementById('kdRatio').textContent = kdRatio;
    document.getElementById('avgSession').textContent = '2.5h';
}

// Event listeners
document.getElementById('eventTypeFilter').addEventListener('change', (e) => {
    currentFilter = e.target.value;
    displayedEvents = 5;
    loadHistory();
});

document.getElementById('periodFilter').addEventListener('change', (e) => {
    currentPeriod = e.target.value;
    displayedEvents = 5;
    loadHistory();
});

document.getElementById('loadMoreBtn').addEventListener('click', () => {
    displayedEvents += 5;
    renderTimeline();
});

// Initial load
loadHistory();
