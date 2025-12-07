// ============================================
// SETTINGS.JS - Conectar com API Real
// ============================================

let currentSettings = {};
let currentSection = 'profile';

// Carregar configurações da API
async function loadSettings() {
    try {
        const response = await fetch('/api/settings/get');
        const data = await response.json();

        if (response.ok) {
            currentSettings = data;
            populateForm(data);
        } else {
            console.error('Erro ao carregar configurações:', data.error);
            loadDefaultSettings();
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        loadDefaultSettings();
    }
}

// Configurações padrão
function loadDefaultSettings() {
    currentSettings = {
        display_name: 'Jogador123',
        bio: '',
        discord_username: '',
        dark_mode: true,
        primary_color: '#4facfe',
        font_size: 'medium',
        animations_enabled: true,
        notify_kills: true,
        notify_achievements: true,
        notify_events: true,
        notify_group_messages: true,
        notify_weekly_summary: false,
        notify_server_updates: true,
        profile_public: true,
        show_stats: true,
        show_history: false,
        show_online_status: true,
        favorite_server: 'BRASIL SUL #1',
        auto_join: false,
        crosshair_type: 'cruz',
        two_factor_enabled: false
    };
    populateForm(currentSettings);
}

// Preencher formulário com dados
function populateForm(settings) {
    // Perfil
    const displayNameInput = document.querySelector('input[placeholder="Seu nome"]');
    if (displayNameInput) displayNameInput.value = settings.display_name || '';

    const bioInput = document.querySelector('input[placeholder="Sua bio"]');
    if (bioInput) bioInput.value = settings.bio || '';

    const discordInput = document.querySelector('input[placeholder="usuario#1234"]');
    if (discordInput) discordInput.value = settings.discord_username || '';

    // Aparência
    const colorPicker = document.querySelector('input[type="color"]');
    if (colorPicker) colorPicker.value = settings.primary_color || '#4facfe';

    const fontSizeSelect = document.querySelector('select');
    if (fontSizeSelect) fontSizeSelect.value = settings.font_size || 'medium';

    // Atualizar todos os toggles
    updateToggles(settings);
}

// Atualizar estado dos toggles
function updateToggles(settings) {
    const toggleMap = {
        'dark_mode': settings.dark_mode,
        'animations_enabled': settings.animations_enabled,
        'notify_kills': settings.notify_kills,
        'notify_achievements': settings.notify_achievements,
        'notify_events': settings.notify_events,
        'notify_group_messages': settings.notify_group_messages,
        'notify_weekly_summary': settings.notify_weekly_summary,
        'notify_server_updates': settings.notify_server_updates,
        'profile_public': settings.profile_public,
        'show_stats': settings.show_stats,
        'show_history': settings.show_history,
        'show_online_status': settings.show_online_status,
        'auto_join': settings.auto_join,
        'two_factor_enabled': settings.two_factor_enabled
    };

    // Atualizar visualmente os toggles (assumindo que estão em ordem)
    const toggles = document.querySelectorAll('.toggle-switch');
    let index = 0;
    for (const [key, value] of Object.entries(toggleMap)) {
        if (toggles[index]) {
            if (value) {
                toggles[index].classList.add('active');
            } else {
                toggles[index].classList.remove('active');
            }
        }
        index++;
    }
}

// Coletar dados do formulário
function getFormData() {
    const data = {};

    // Perfil
    const displayNameInput = document.querySelector('input[placeholder="Seu nome"]');
    if (displayNameInput) data.display_name = displayNameInput.value;

    const bioInput = document.querySelector('input[placeholder="Sua bio"]');
    if (bioInput) data.bio = bioInput.value;

    const discordInput = document.querySelector('input[placeholder="usuario#1234"]');
    if (discordInput) data.discord_username = discordInput.value;

    // Aparência
    const colorPicker = document.querySelector('input[type="color"]');
    if (colorPicker) data.primary_color = colorPicker.value;

    const fontSizeSelect = document.querySelector('select');
    if (fontSizeSelect) data.font_size = fontSizeSelect.value;

    // Toggles (coletar estado de todos)
    const toggles = document.querySelectorAll('.toggle-switch');
    const toggleKeys = [
        'dark_mode', 'animations_enabled', 'notify_kills', 'notify_achievements',
        'notify_events', 'notify_group_messages', 'notify_weekly_summary',
        'notify_server_updates', 'profile_public', 'show_stats', 'show_history',
        'show_online_status', 'auto_join', 'two_factor_enabled'
    ];

    toggles.forEach((toggle, index) => {
        if (toggleKeys[index]) {
            data[toggleKeys[index]] = toggle.classList.contains('active');
        }
    });

    return data;
}

// Salvar configurações
async function saveSettings() {
    const data = getFormData();

    try {
        const response = await fetch('/api/settings/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Mostrar mensagem de sucesso
            const successMessage = document.getElementById('successMessage');
            if (successMessage) {
                successMessage.classList.add('show');
                setTimeout(() => {
                    successMessage.classList.remove('show');
                }, 3000);
            }

            currentSettings = result.settings;
        } else {
            console.error('Erro ao salvar:', result.error);
            alert('Erro ao salvar configurações: ' + result.error);
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        alert('Erro ao salvar configurações. Tente novamente.');
    }
}

// Toggle switch
function toggleSwitch(element) {
    element.classList.toggle('active');
}

// Navegação entre seções
function showSection(sectionName) {
    // Esconder todas as seções
    document.querySelectorAll('.settings-section').forEach(section => {
        section.classList.remove('active');
    });

    // Mostrar seção selecionada
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Atualizar sidebar
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeItem = document.querySelector(`.sidebar-item[data-section="${sectionName}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }

    currentSection = sectionName;
}

// Event listeners para sidebar
document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('click', () => {
        const section = item.dataset.section;
        showSection(section);
    });
});

// Initial load
loadSettings();
