// ==================== DASHBOARD.JS ====================
// Dashboard do usuário

document.addEventListener('DOMContentLoaded', function () {
    loadUserProfile();
    loadUserStats();
    setupLogout();
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

