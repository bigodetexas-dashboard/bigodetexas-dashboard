// ===== AUTHENTICATION MANAGER =====
// Gerencia estado de autenticação do usuário

class AuthManager {
    constructor() {
        this.user = null;
        this.balance = 0;
        this.isAuthenticated = false;
    }

    async init() {
        await this.checkAuth();
    }
}

updateUI() {
    const authContainer = document.getElementById('auth-container');
    if (!authContainer) return;

    if (this.isAuthenticated) {
        authContainer.innerHTML = this.getAuthenticatedHTML();
    } else {
        authContainer.innerHTML = this.getUnauthenticatedHTML();
    }
}

getAuthenticatedHTML() {
    const username = this.user?.username || 'Usuário';
    const avatar = this.user?.avatar
        ? `https://cdn.discordapp.com/avatars/${this.user.id}/${this.user.avatar}.png`
        : 'https://cdn.discordapp.com/embed/avatars/0.png';

    return `
            <div class="user-info">
                <div class="user-avatar">
                    <img src="${avatar}" alt="${username}" onerror="this.src='https://cdn.discordapp.com/embed/avatars/0.png'">
                </div>
                <div class="user-details">
                    <span class="username">${username}</span>
                    <span class="balance">
                        <i class="fas fa-coins"></i> ${this.balance.toLocaleString('pt-BR')} DZ
                    </span>
                </div>
                <a href="/logout" class="btn-logout" title="Sair">
                    <i class="fas fa-sign-out-alt"></i>
                </a>
            </div>
        `;
}

getUnauthenticatedHTML() {
    return `
            <a href="/login" class="btn-login">
                <i class="fab fa-discord"></i>
                <span>Login</span>
            </a>
        `;
}

    // Método para atualizar saldo após compra
    async refreshBalance() {
    if (this.isAuthenticated) {
        await this.checkAuth();
        this.updateUI();
    }
}
}

// Instância global
const authManager = new AuthManager();

// Inicializar quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => authManager.init());
} else {
    authManager.init();
}

// Exportar para uso em outros scripts
window.authManager = authManager;
