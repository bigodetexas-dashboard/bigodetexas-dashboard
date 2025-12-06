// ==================== DASHBOARD.JS ====================
// Dashboard do usuário

document.addEventListener('DOMContentLoaded', function () {
    loadUserProfile();
    loadUserStats();
    loadPurchaseHistory();
    loadAchievements();
    setupLogout();
    setupTabs();
    loadUserSettings();
});

async function loadUserProfile() {
    try {
        const response = await fetch('/api/user/profile');
        const data = await response.json();

        const userName = document.getElementById('user-name');
        const userGamertag = document.getElementById('user-gamertag');
        const userBalance = document.getElementById('user-balance');
        const userAvatar = document.getElementById('user-avatar');

        if (userName) userName.textContent = data.username || 'Usuário';
        if (userGamertag) userGamertag.textContent = data.gamertag ? `Xbox: ${data.gamertag}` : 'Xbox: Não vinculado';
        if (userBalance) userBalance.textContent = formatNumber(data.balance || 0);

        // Avatar
        if (data.avatar && userAvatar) {
            userAvatar.style.backgroundImage = `url(${data.avatar})`;
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
    }
}

async function loadUserStats() {
    try {
        const response = await fetch('/api/user/stats');
        const data = await response.json();

        // Combate
        const statKills = document.getElementById('stat-kills');
        const statDeaths = document.getElementById('stat-deaths');
        const statKD = document.getElementById('stat-kd');
        const statZombies = document.getElementById('stat-zombies');

        if (statKills) statKills.textContent = data.kills || 0;
        if (statDeaths) statDeaths.textContent = data.deaths || 0;
        if (statKD) statKD.textContent = calculateKD(data.kills, data.deaths);
        if (statZombies) statZombies.textContent = data.zombie_kills || 0;

        // Sobrevivência
        const statPlaytime = document.getElementById('stat-playtime');
        const statDistance = document.getElementById('stat-distance');
        const statDriving = document.getElementById('stat-driving');
        const statBuilt = document.getElementById('stat-built');

        if (statPlaytime) statPlaytime.textContent = formatTime(data.total_playtime || 0);
        if (statDistance) statDistance.textContent = formatDistance(data.distance_walked || 0);
        if (statDriving) statDriving.textContent = formatDistance(data.vehicle_distance || 0);
        if (statBuilt) statBuilt.textContent = data.buildings_built || 0;
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

async function loadPurchaseHistory() {
    try {
        const response = await fetch('/api/user/purchases');
        const data = await response.json();

        const container = document.getElementById('purchase-history');

        if (!container) {
            console.warn('Elemento purchase-history não encontrado');
            return;
        }

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🛒</div>
                    <p>Nenhuma compra realizada ainda</p>
                </div>
            `;
            return;
        }

        container.innerHTML = data.map(purchase => `
            <div class="purchase-item">
                <div class="purchase-info">
                    <div class="purchase-date">${formatDate(purchase.date)}</div>
                    <div class="purchase-items">${purchase.items_count} itens - ${formatNumber(purchase.total)} 💰</div>
                </div>
                <div class="purchase-status ${purchase.status}">
                    ${purchase.status === 'delivered' ? '✅ Entregue' : '⏳ Pendente'}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar compras:', error);
    }
}

async function loadAchievements() {
    try {
        const response = await fetch('/api/user/achievements');
        const data = await response.json();

        const container = document.getElementById('achievements-list');

        if (!container) {
            console.warn('Elemento achievements-list não encontrado');
            return;
        }

        const achievements = [
            { id: 'first_kill', icon: '🎯', name: 'Primeira Morte', desc: 'Mate seu primeiro jogador', unlocked: data.first_kill },
            { id: 'survivor', icon: '🏃', name: 'Sobrevivente', desc: 'Sobreviva por 24h', unlocked: data.survivor },
            { id: 'rich', icon: '💰', name: 'Milionário', desc: 'Acumule 10.000 DZCoins', unlocked: data.rich },
            { id: 'builder', icon: '🏗️', name: 'Construtor', desc: 'Construa 10 bases', unlocked: data.builder },
            { id: 'hunter', icon: '🧟', name: 'Caçador', desc: 'Mate 1000 zumbis', unlocked: data.hunter },
            { id: 'explorer', icon: '🗺️', name: 'Explorador', desc: 'Ande 100km', unlocked: data.explorer }
        ];

        container.innerHTML = achievements.map(ach => `
            <div class="achievement-card ${ach.unlocked ? 'unlocked' : 'locked'}">
                <div class="achievement-icon">${ach.icon}</div>
                <div class="achievement-name">${ach.name}</div>
                <div class="achievement-desc">${ach.desc}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Erro ao carregar conquistas:', error);
    }
}

function setupLogout() {
    document.getElementById('logout-btn').addEventListener('click', function () {
        if (confirm('Deseja realmente sair?')) {
            window.location.href = '/logout';
        }
    });
}

// Utility functions
function calculateKD(kills, deaths) {
    if (deaths === 0) return kills.toFixed(2);
    return (kills / deaths).toFixed(2);
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    return `${hours}h`;
}

function formatDistance(meters) {
    if (meters >= 1000) {
        return `${(meters / 1000).toFixed(1)}km`;
    }
    return `${meters}m`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

// ==================== TABS SYSTEM ====================
function setupTabs() {
    console.log('🔧 Configurando sistema de tabs...');

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    console.log(`📊 Encontrados ${tabBtns.length} botões de tabs`);
    console.log(`📊 Encontrados ${tabContents.length} conteúdos de tabs`);

    if (tabBtns.length === 0) {
        console.error('❌ Nenhum botão de tab encontrado!');
        return;
    }

    tabBtns.forEach((btn, index) => {
        console.log(`✅ Registrando evento para tab ${index}: ${btn.getAttribute('data-tab')}`);

        btn.addEventListener('click', function (e) {
            e.preventDefault();
            console.log(`🖱️ Tab clicada: ${this.getAttribute('data-tab')}`);

            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            // Show corresponding tab content
            const tabId = this.getAttribute('data-tab');
            const tabContent = document.getElementById(`tab-${tabId}`);

            if (tabContent) {
                tabContent.classList.add('active');
                console.log(`✅ Tab ativada: ${tabId}`);
            } else {
                console.error(`❌ Conteúdo da tab não encontrado: tab-${tabId}`);
            }
        });
    });

    console.log('✅ Sistema de tabs configurado com sucesso!');
}

// ==================== GAMERTAG SYSTEM ====================
async function saveGamertag() {
    const gamertagInput = document.getElementById('gamertag-input');
    const statusDiv = document.getElementById('gamertag-status');
    const gamertag = gamertagInput.value.trim();

    if (!gamertag) {
        statusDiv.innerHTML = '<p class="text-danger">⚠️ Por favor, digite um Gamertag válido.</p>';
        return;
    }

    statusDiv.innerHTML = '<p class="text-muted">⏳ Salvando...</p>';

    try {
        const response = await fetch('/api/user/update-gamertag', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ gamertag: gamertag })
        });

        const data = await response.json();

        if (response.ok) {
            statusDiv.innerHTML = '<p class="text-success">✅ Gamertag salvo com sucesso!</p>';
            // Update display
            document.getElementById('user-gamertag').textContent = `Xbox: ${gamertag}`;

            // Clear status after 3 seconds
            setTimeout(() => {
                statusDiv.innerHTML = '';
            }, 3000);
        } else {
            statusDiv.innerHTML = `<p class="text-danger">❌ Erro: ${data.error || 'Falha ao salvar'}</p>`;
        }
    } catch (error) {
        console.error('Erro ao salvar gamertag:', error);
        statusDiv.innerHTML = '<p class="text-danger">❌ Erro ao conectar com o servidor.</p>';
    }
}

// ==================== USER SETTINGS ====================
async function loadUserSettings() {
    try {
        const response = await fetch('/api/user/profile');
        const data = await response.json();

        // Load gamertag if exists
        if (data.gamertag) {
            const gamertagInput = document.getElementById('gamertag-input');
            if (gamertagInput) {
                gamertagInput.value = data.gamertag;
            }
        }

        // Load notification preferences from localStorage
        const notifyPurchases = localStorage.getItem('notify-purchases') !== 'false';
        const notifyKills = localStorage.getItem('notify-kills') !== 'false';
        const notifyClan = localStorage.getItem('notify-clan') === 'true';

        const notifyPurchasesEl = document.getElementById('notify-purchases');
        const notifyKillsEl = document.getElementById('notify-kills');
        const notifyClanEl = document.getElementById('notify-clan');

        if (notifyPurchasesEl) notifyPurchasesEl.checked = notifyPurchases;
        if (notifyKillsEl) notifyKillsEl.checked = notifyKills;
        if (notifyClanEl) notifyClanEl.checked = notifyClan;

        // Setup listeners for notification toggles
        setupNotificationToggles();
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
    }
}

function setupNotificationToggles() {
    const toggles = ['notify-purchases', 'notify-kills', 'notify-clan'];

    toggles.forEach(toggleId => {
        const toggle = document.getElementById(toggleId);
        if (toggle) {
            toggle.addEventListener('change', (e) => {
                localStorage.setItem(toggleId, e.target.checked);
                console.log(`${toggleId} atualizado:`, e.target.checked);
            });
        }
    });
}

// Make saveGamertag available globally
window.saveGamertag = saveGamertag;

