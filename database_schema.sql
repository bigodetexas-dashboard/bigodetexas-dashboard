-- ==========================================
-- SCHEMA COMPLETO - BIGODETEXAS DAYZ SERVER
-- Sistema: BASE + CLAN + BANCO SUL
-- ==========================================

-- Tabela de Usuários (extendida)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    discord_username VARCHAR(100) NOT NULL,
    discord_avatar VARCHAR(255),
    nitrado_gamertag VARCHAR(100), -- NOVO: Gamertag do Xbox/Nitrado
    nitrado_verified BOOLEAN DEFAULT FALSE, -- NOVO: Se foi verificado nos logs
    nitrado_verified_at TIMESTAMP,
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Clãs
CREATE TABLE IF NOT EXISTS clans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    leader_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol_color1 VARCHAR(7) DEFAULT '#FF0000', -- Cor 1 do símbolo (hex)
    symbol_color2 VARCHAR(7) DEFAULT '#00FF00', -- Cor 2 do símbolo (hex)
    symbol_icon VARCHAR(50) DEFAULT 'shield', -- Ícone do clã
    balance INTEGER DEFAULT 0, -- Banco do clã
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Membros do Clã
CREATE TABLE IF NOT EXISTS clan_members (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER REFERENCES clans(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member', -- leader, moderator, member
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(clan_id, user_id)
);

-- Tabela de Bases
CREATE TABLE IF NOT EXISTS bases (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    clan_id INTEGER REFERENCES clans(id) ON DELETE SET NULL,
    coord_x FLOAT NOT NULL,
    coord_y FLOAT NOT NULL,
    coord_z FLOAT NOT NULL,
    protection_radius FLOAT DEFAULT 50.0, -- Raio de proteção em metros
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(owner_id) -- 1 base por usuário
);

-- Tabela de Transações Bancárias
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL, -- transfer, deposit, withdrawal, reward, purchase
    description TEXT,
    clan_id INTEGER REFERENCES clans(id) ON DELETE SET NULL, -- Se for transação do clã
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Estatísticas Semanais de PvP
CREATE TABLE IF NOT EXISTS weekly_pvp_stats (
    id SERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    clan_id INTEGER REFERENCES clans(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    raids_done INTEGER DEFAULT 0, -- Raids feitos
    raids_suffered INTEGER DEFAULT 0, -- Raids sofridos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_start, clan_id, user_id)
);

-- Tabela de Permissões de Base
CREATE TABLE IF NOT EXISTS base_permissions (
    id SERIAL PRIMARY KEY,
    base_id INTEGER REFERENCES bases(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    can_build BOOLEAN DEFAULT TRUE,
    can_use_storage BOOLEAN DEFAULT TRUE,
    can_use_fire BOOLEAN DEFAULT TRUE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_id, user_id)
);

-- Tabela de Logs de Ações na Base
CREATE TABLE IF NOT EXISTS base_logs (
    id SERIAL PRIMARY KEY,
    base_id INTEGER REFERENCES bases(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL, -- build, destroy, use_storage, use_fire
    details TEXT,
    coord_x FLOAT,
    coord_y FLOAT,
    coord_z FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_users_discord_id ON users(discord_id);
CREATE INDEX IF NOT EXISTS idx_users_nitrado_gamertag ON users(nitrado_gamertag);
CREATE INDEX IF NOT EXISTS idx_clan_members_clan_id ON clan_members(clan_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_user_id ON clan_members(user_id);
CREATE INDEX IF NOT EXISTS idx_bases_owner_id ON bases(owner_id);
CREATE INDEX IF NOT EXISTS idx_bases_clan_id ON bases(clan_id);
CREATE INDEX IF NOT EXISTS idx_transactions_from_user ON transactions(from_user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_to_user ON transactions(to_user_id);
CREATE INDEX IF NOT EXISTS idx_weekly_stats_week ON weekly_pvp_stats(week_start, week_end);
CREATE INDEX IF NOT EXISTS idx_base_logs_base_id ON base_logs(base_id);

-- Triggers para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clans_updated_at BEFORE UPDATE ON clans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bases_updated_at BEFORE UPDATE ON bases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
