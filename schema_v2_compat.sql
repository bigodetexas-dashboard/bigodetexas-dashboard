-- ==========================================
-- SCHEMA DE COMPATIBILIDADE V2 - BIGODETEXAS
-- Adapta a estrutura existente para suportar Bases e Clãs avancados
-- Respeita o uso de discord_id (TEXT) como chave principal
-- ==========================================

-- 1. Melhorar tabela CLANS existente
-- Verifica se colunas existem antes de adicionar
DO $$
BEGIN
    -- Adicionar colunas de customizacao se faltarem
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clans' AND column_name='banner_url') THEN
        ALTER TABLE clans ADD COLUMN banner_url TEXT;
    END IF;
    
    -- Garantir que temos saldo do cla
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='clans' AND column_name='balance') THEN
        ALTER TABLE clans ADD COLUMN balance INTEGER DEFAULT 0;
    END IF;
END $$;

-- 2. Tabela de Membros do Cla (Melhorada)
-- Se a tabela ja existe, vamos garantir que tenha as colunas necessarias
CREATE TABLE IF NOT EXISTS clan_members_v2 (
    id SERIAL PRIMARY KEY,
    clan_id INTEGER, -- FK manual para clans.id (evita erro se FK nao existir)
    discord_id TEXT NOT NULL,
    gamertag TEXT, -- Cache do nome
    role VARCHAR(20) DEFAULT 'member', -- leader, moderator, member
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(clan_id, discord_id)
);

-- Migrar dados da tabela antiga se existir e estiver vazia a nova
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='clan_members') AND 
       NOT EXISTS (SELECT 1 FROM clan_members_v2 LIMIT 1) THEN
       -- Tenta copiar dados da estrutura antiga se compativel
       NULL; -- Por enquanto nao vamos forcar migracao automatica para nao quebrar
    END IF;
END $$;

-- 3. Tabela de BASES (Avancada)
-- Vamos criar uma tabela nova ou alterar a existente com segurança
CREATE TABLE IF NOT EXISTS bases_v2 (
    id SERIAL PRIMARY KEY,
    owner_discord_id TEXT UNIQUE NOT NULL, -- Dono da base (Discord ID)
    clan_id INTEGER, -- Opcional: Base de cla
    name VARCHAR(100) DEFAULT 'Base Principal',
    coord_x FLOAT NOT NULL,
    coord_y FLOAT DEFAULT 0,
    coord_z FLOAT NOT NULL,
    radius INTEGER DEFAULT 50, -- Raio de protecao
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela de Permissoes de Base
CREATE TABLE IF NOT EXISTS base_permissions (
    id SERIAL PRIMARY KEY,
    base_id INTEGER REFERENCES bases_v2(id) ON DELETE CASCADE,
    discord_id TEXT NOT NULL, -- Quem tem permissao
    can_build BOOLEAN DEFAULT FALSE,
    can_access_storage BOOLEAN DEFAULT FALSE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(base_id, discord_id)
);

-- 5. Logs de Auditoria de Clã/Base
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20), -- 'clan', 'base', 'economy'
    entity_id INTEGER, -- ID do cla ou base
    actor_discord_id TEXT, -- Quem fez a acao
    action VARCHAR(50), -- 'withdraw', 'invite', 'build'
    details JSONB, -- Detalhes flexiveis
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabela de Verificação Nitrado (Vinculo Real)
CREATE TABLE IF NOT EXISTS nitrado_links (
    id SERIAL PRIMARY KEY,
    discord_id TEXT UNIQUE NOT NULL,
    gamertag TEXT NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(10), -- Codigo temporario para verificar no chat
    linked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_bases_owner ON bases_v2(owner_discord_id);
CREATE INDEX IF NOT EXISTS idx_clan_members_discord ON clan_members_v2(discord_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);
