// ==================== LEADERBOARD.JS ====================
// Sistema de rankings

let currentCategory = 'kills';
let rankingsData = {};

const categoryConfig = {
    kills: { label: 'Kills', icon: 'ri-sword-line', field: 'kills' },
    deaths: { label: 'Mortes', icon: 'ri-skull-line', field: 'deaths' },
    kd: { label: 'K/D Ratio', icon: 'ri-percent-line', field: 'kd' },
    balance: { label: 'DZCoins', icon: 'ri-money-dollar-circle-line', field: 'balance' },
    playtime: { label: 'Tempo Jogado', icon: 'ri-time-line', field: 'playtime' },
    longest_shot: { label: 'Longest Shot', icon: 'ri-crosshair-2-line', field: 'longest_shot' }
};

document.addEventListener('DOMContentLoaded', function () {
    loadRankings();
    setupEventListeners();
});

function setupEventListeners() {
    document.querySelectorAll('.control-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.dataset.category;
            renderRanking();
        });
    });
}

async function loadRankings() {
    try {
        const response = await fetch('/api/leaderboard');
        rankingsData = await response.json();
        renderRanking();
    } catch (error) {
        console.error('Erro ao carregar rankings:', error);
        renderEmptyRanking();
    }
}

function renderRanking() {
    const config = categoryConfig[currentCategory];
    const data = rankingsData[currentCategory] || [];

    // Atualizar cabeçalho da tabela
    document.getElementById('stat-header').textContent = config.label;

    // Renderizar pódio (Top 3)
    renderPodium(data.slice(0, 3));

    // Renderizar tabela completa
    renderTable(data);
}

function renderPodium(top3) {
    const podiumContainer = document.getElementById('podium-container');

    if (top3.length === 0) {
        podiumContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">Nenhum dado disponível</p>';
        return;
    }

    // Ordem do pódio: 2º, 1º, 3º (para visual correto)
    const podiumOrder = [
        top3[1] || null, // 2º lugar (esquerda)
        top3[0] || null, // 1º lugar (centro)
        top3[2] || null  // 3º lugar (direita)
    ];

    const positions = [2, 1, 3];
    const heights = ['120px', '150px', '100px'];
    const colors = ['#c0c0c0', '#ffd700', '#cd7f32'];

    podiumContainer.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: flex-end; gap: 2rem; margin: 2rem 0;">
            ${podiumOrder.map((player, idx) => {
        if (!player) return '';
        const position = positions[idx];
        return `
                    <div style="text-align: center;">
                        <div style="background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 1rem; margin-bottom: 1rem; border: 2px solid ${colors[idx]};">
                            <div style="font-size: 2rem; color: ${colors[idx]};">#${position}</div>
                            <div style="font-size: 1.2rem; font-weight: 700; margin: 0.5rem 0;">${player.name || player.gamertag}</div>
                            <div style="font-size: 1.5rem; color: var(--accent);">${formatValue(player.value, currentCategory)}</div>
                        </div>
                        <div style="background: ${colors[idx]}; height: ${heights[idx]}; border-radius: 0.5rem 0.5rem 0 0; opacity: 0.3;"></div>
                    </div>
                `;
    }).join('')}
        </div>
    `;
}

function renderTable(data) {
    const tbody = document.getElementById('leaderboard-body');

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-secondary);">Nenhum dado disponível</td></tr>';
        return;
    }

    tbody.innerHTML = data.map((player, index) => `
        <tr>
            <td><strong>#${index + 1}</strong></td>
            <td>${player.name || player.gamertag || 'Desconhecido'}</td>
            <td><strong>${formatValue(player.value, currentCategory)}</strong></td>
            <td style="color: var(--text-secondary); font-size: 0.9rem;">
                ${getPlayerDetails(player)}
            </td>
        </tr>
    `).join('');
}

function getPlayerDetails(player) {
    // Retorna detalhes adicionais baseado na categoria
    if (currentCategory === 'kd') {
        return `${player.kills || 0} kills / ${player.deaths || 0} mortes`;
    } else if (currentCategory === 'kills') {
        return `${player.deaths || 0} mortes`;
    } else if (currentCategory === 'deaths') {
        return `${player.kills || 0} kills`;
    }
    return 'Jogador ativo';
}

function formatValue(value, category) {
    if (!value && value !== 0) return '0';

    if (category === 'kd') {
        return Number(value).toFixed(2);
    } else if (category === 'balance') {
        return `${formatNumber(Math.floor(value))} 💰`;
    } else if (category === 'playtime') {
        return `${Math.floor(value)} horas`;
    } else if (category === 'longest_shot') {
        return `${Math.floor(value)}m`;
    } else {
        return formatNumber(Math.floor(value));
    }
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

function renderEmptyRanking() {
    document.getElementById('leaderboard-body').innerHTML = `
        <tr>
            <td colspan="4" style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                Carregando rankings...
            </td>
        </tr>
    `;
}
