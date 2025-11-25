// ===== CHART.JS INTEGRATION =====

// --- KILLS OVER TIME CHART ---
async function createKillsChart() {
    const players = await fetchAPI('players');
    if (!players) return;

    // Simulate time-based data (in production, this would come from timestamped data)
    const labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
    const data = labels.map(() => Math.floor(Math.random() * 50) + 10);

    const ctx = document.getElementById('killsChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Kills por Dia',
                data: data,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#f9fafb' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#d1d5db' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#d1d5db' }
                }
            }
        }
    });
}

// --- WEAPON USAGE CHART ---
async function createWeaponsChart() {
    const players = await fetchAPI('players');
    if (!players) return;

    // Aggregate weapon stats from all players
    const weaponStats = {};
    players.forEach(player => {
        // In production, this would come from actual weapon stats
        const weapons = ['M4A1', 'AK-74', 'Mosin', 'SVD', 'KA-M'];
        weapons.forEach(w => {
            weaponStats[w] = (weaponStats[w] || 0) + Math.floor(Math.random() * 20);
        });
    });

    const ctx = document.getElementById('weaponsChart');
    if (!ctx) return;

    const sortedWeapons = Object.entries(weaponStats)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sortedWeapons.map(w => w[0]),
            datasets: [{
                data: sortedWeapons.map(w => w[1]),
                backgroundColor: [
                    '#f59e0b',
                    '#ef4444',
                    '#10b981',
                    '#3b82f6',
                    '#8b5cf6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f9fafb' }
                }
            }
        }
    });
}

// --- K/D DISTRIBUTION CHART ---
async function createKDChart() {
    const players = await fetchAPI('players');
    if (!players) return;

    // Group players by K/D ranges
    const ranges = {
        '0-0.5': 0,
        '0.5-1': 0,
        '1-2': 0,
        '2-3': 0,
        '3+': 0
    };

    players.forEach(p => {
        if (p.kd < 0.5) ranges['0-0.5']++;
        else if (p.kd < 1) ranges['0.5-1']++;
        else if (p.kd < 2) ranges['1-2']++;
        else if (p.kd < 3) ranges['2-3']++;
        else ranges['3+']++;
    });

    const ctx = document.getElementById('kdChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(ranges),
            datasets: [{
                label: 'Número de Jogadores',
                data: Object.values(ranges),
                backgroundColor: 'rgba(245, 158, 11, 0.8)',
                borderColor: '#f59e0b',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#f9fafb' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#d1d5db' }
                },
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#d1d5db' }
                }
            }
        }
    });
}
