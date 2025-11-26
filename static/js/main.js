// ===== BIGODE TEXAS DASHBOARD - MAIN JAVASCRIPT =====

// --- API HELPERS ---
async function fetchAPI(endpoint) {
  try {
    const response = await fetch(`/api/${endpoint}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error);
    return null;
  }
}

// --- NUMBER FORMATTING ---
function formatNumber(num) {
  return new Intl.NumberFormat('pt-BR').format(num);
}

// --- TIME FORMATTING ---
function formatTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hours.toString().padStart(2, '0')}h:${minutes.toString().padStart(2, '0')}m:${secs.toString().padStart(2, '0')}s`;
}

// --- LOADING STATE ---
function showLoading(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = '<div class="loading text-center">Carregando...</div>';
  }
}

function hideLoading(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.classList.remove('loading');
  }
}

// --- STATS PAGE ---
async function loadStats() {
  showLoading('stats-container');

  const stats = await fetchAPI('stats');
  if (!stats) return;

  document.getElementById('total-kills').textContent = formatNumber(stats.total_kills);
  document.getElementById('total-deaths').textContent = formatNumber(stats.total_deaths);
  document.getElementById('total-players').textContent = formatNumber(stats.total_players);
  document.getElementById('total-coins').textContent = formatNumber(stats.total_coins);

  hideLoading('stats-container');
}

// --- SHOP PAGE ---
let allShopItems = [];

async function loadShop() {
  const items = await fetchAPI('shop');
  if (!items) return;

  allShopItems = items;
  renderShopItems(items);
  hideLoading('shop-container');
}

function renderShopItems(items) {
  const shopContainer = document.getElementById('shop-container');
  if (shopContainer) {
    shopContainer.innerHTML = items.map(item => `
      <div class="card fade-in" data-category="${item.category}">
        <div class="card-header">
          <h3 class="card-title">${item.name}</h3>
          <span class="badge badge-primary">${item.category}</span>
        </div>
        <p class="text-muted">${item.description}</p>
        <div style="margin-top: auto; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-primary);">
              ${formatNumber(item.price)} 💰
            </span>
            <code style="font-size: 0.875rem; color: var(--text-muted);">${item.code}</code>
          </div>
          <button onclick="copyCommand('${item.code}')" class="copy-btn">
            📋 Copiar Comando
          </button>
        </div>
      </div>
    `).join('');
  }
}

function filterCategory(category) {
  // Update active button
  document.querySelectorAll('.category-filter').forEach(btn => {
    btn.classList.remove('active');
  });
  document.querySelector(`[data-category="${category}"]`).classList.add('active');

  // Filter items
  if (category === 'all') {
    renderShopItems(allShopItems);
  } else {
    const filtered = allShopItems.filter(item => item.category === category);
    renderShopItems(filtered);
  }
}

function copyCommand(code) {
  const command = `!comprar ${code}`;
  navigator.clipboard.writeText(command).then(() => {
    // Visual feedback
    const btn = event.target;
    const originalText = btn.innerHTML;
    btn.innerHTML = '✅ Copiado!';
    btn.style.background = 'rgba(34, 197, 94, 0.2)';

    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.style.background = '';
    }, 2000);
  }).catch(err => {
    console.error('Erro ao copiar:', err);
    alert('Erro ao copiar comando. Copie manualmente: ' + command);
  });
}

// --- LEADERBOARD PAGE ---
async function loadLeaderboard() {
  const data = await fetchAPI('leaderboard');
  if (!data) return;

  // Top Kills
  const topKills = document.getElementById('top-kills');
  if (topKills) {
    topKills.innerHTML = data.kills.map((player, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>${player.name}</td>
        <td>${formatNumber(player.value)}</td>
      </tr>
    `).join('');
  }

  // Top K/D
  const topKd = document.getElementById('top-kd');
  if (topKd) {
    topKd.innerHTML = data.kd.map((player, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>${player.name}</td>
        <td>${player.value.toFixed(2)}</td>
      </tr>
    `).join('');
  }

  // Top Killstreak
  const topStreak = document.getElementById('top-streak');
  if (topStreak) {
    topStreak.innerHTML = data.killstreak.map((player, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>${player.name}</td>
        <td>${formatNumber(player.value)}</td>
      </tr>
    `).join('');
  }

  // Top Longest Shot
  const topShot = document.getElementById('top-shot');
  if (topShot) {
    topShot.innerHTML = data.longest_shot.map((player, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>${player.name}</td>
        <td>${formatNumber(player.value)}m</td>
      </tr>
    `).join('');
  }
}

// --- WARS PAGE ---
async function loadWars() {
  const wars = await fetchAPI('wars');
  if (!wars) return;

  const warsContainer = document.getElementById('wars-container');
  if (warsContainer) {
    if (wars.length === 0) {
      warsContainer.innerHTML = '<div class="text-center text-muted">🕊️ Nenhuma guerra ativa no momento.</div>';
    } else {
      warsContainer.innerHTML = wars.map(war => `
        <div class="card fade-in">
          <div class="card-header">
            <h3 class="card-title">⚔️ ${war.clan1} vs ${war.clan2}</h3>
          </div>
          <div style="display: flex; justify-content: space-around; margin-top: 1rem;">
            <div class="text-center">
              <div class="stat-value">${war.score[war.clan1]}</div>
              <div class="stat-label">${war.clan1}</div>
            </div>
            <div class="text-center" style="align-self: center; font-size: 2rem; opacity: 0.5;">VS</div>
            <div class="text-center">
              <div class="stat-value">${war.score[war.clan2]}</div>
              <div class="stat-label">${war.clan2}</div>
            </div>
          </div>
        </div>
      `).join('');
    }
  }
}

// --- AUTO REFRESH ---
function startAutoRefresh(loadFunction, interval = 30000) {
  loadFunction();
  setInterval(loadFunction, interval);
}

// --- INITIALIZE ---
document.addEventListener('DOMContentLoaded', () => {
  // Highlight active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
});
