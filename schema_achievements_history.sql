-- ============================================
-- SCHEMA PARA ACHIEVEMENTS E HISTORY
-- BigodeBot Dashboard - Sistema Completo
-- ============================================

-- Tabela de Conquistas (Achievements)
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    achievement_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- combat, survival, exploration, social
    rarity VARCHAR(20), -- common, rare, epic, legendary, mythic
    tier VARCHAR(20), -- bronze, silver, gold, platinum, diamond
    points INTEGER DEFAULT 0,
    reward TEXT,
    icon VARCHAR(10),
    max_progress INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Conquistas dos Usuários
CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) NOT NULL,
    achievement_key VARCHAR(50) NOT NULL,
    progress INTEGER DEFAULT 0,
    unlocked BOOLEAN DEFAULT FALSE,
    unlocked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(discord_id, achievement_key),
    FOREIGN KEY (achievement_key) REFERENCES achievements(achievement_key)
);

-- Tabela de Histórico de Atividades
CREATE TABLE IF NOT EXISTS activity_history (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL, -- kill, death, login, logout, achievement, trade, purchase
    icon VARCHAR(10),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    details JSONB, -- Detalhes específicos do evento
    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de Configurações do Usuário
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(50) UNIQUE NOT NULL,
    -- Perfil
    display_name VARCHAR(100),
    bio TEXT,
    discord_username VARCHAR(100),
    -- Aparência
    dark_mode BOOLEAN DEFAULT TRUE,
    primary_color VARCHAR(7) DEFAULT '#4facfe',
    font_size VARCHAR(20) DEFAULT 'medium', -- small, medium, large
    animations_enabled BOOLEAN DEFAULT TRUE,
    -- Notificações
    notify_kills BOOLEAN DEFAULT TRUE,
    notify_achievements BOOLEAN DEFAULT TRUE,
    notify_events BOOLEAN DEFAULT TRUE,
    notify_group_messages BOOLEAN DEFAULT TRUE,
    notify_weekly_summary BOOLEAN DEFAULT FALSE,
    notify_server_updates BOOLEAN DEFAULT TRUE,
    -- Privacidade
    profile_public BOOLEAN DEFAULT TRUE,
    show_stats BOOLEAN DEFAULT TRUE,
    show_history BOOLEAN DEFAULT FALSE,
    show_online_status BOOLEAN DEFAULT TRUE,
    -- Jogo
    favorite_server VARCHAR(50) DEFAULT 'BRASIL SUL #1',
    auto_join BOOLEAN DEFAULT FALSE,
    crosshair_type VARCHAR(20) DEFAULT 'cruz',
    -- Segurança
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_user_achievements_discord ON user_achievements(discord_id);
CREATE INDEX IF NOT EXISTS idx_activity_history_discord ON activity_history(discord_id);
CREATE INDEX IF NOT EXISTS idx_activity_history_type ON activity_history(event_type);
CREATE INDEX IF NOT EXISTS idx_activity_history_timestamp ON activity_history(timestamp DESC);

-- ============================================
-- INSERIR CONQUISTAS PADRÃO
-- ============================================

INSERT INTO achievements (achievement_key, name, description, category, rarity, tier, points, reward, icon, max_progress) VALUES
-- Combate
('first_kill', 'Primeiro Sangue', 'Elimine seu primeiro jogador em combate PvP', 'combat', 'common', 'bronze', 10, '100 moedas', '⚔️', 1),
('killer_10', 'Assassino', 'Elimine 10 jogadores', 'combat', 'common', 'bronze', 15, '150 moedas', '🔪', 10),
('killer_50', 'Caçador', 'Elimine 50 jogadores', 'combat', 'rare', 'silver', 30, '300 moedas', '🎯', 50),
('killer_100', 'Lenda', 'Elimine 100 jogadores', 'combat', 'epic', 'gold', 50, '500 moedas + Skin exclusiva', '🏆', 100),
('killer_500', 'Exterminador', 'Elimine 500 jogadores', 'combat', 'legendary', 'platinum', 100, '1000 moedas + Título especial', '💀', 500),
('headshot_50', 'Headshot Master', 'Consiga 50 headshots em combate', 'combat', 'epic', 'gold', 60, '600 moedas', '🎯', 50),

-- Sobrevivência
('survivor_24h', 'Sobrevivente Experiente', 'Sobreviva por 24 horas consecutivas', 'survival', 'rare', 'silver', 25, '250 moedas', '🏕️', 24),
('survivor_7d', 'Mestre da Sobrevivência', 'Sobreviva por 7 dias consecutivos', 'survival', 'legendary', 'platinum', 100, '1000 moedas + Título especial', '👑', 7),
('survivor_30d', 'Imortal', 'Sobreviva por 30 dias consecutivos', 'survival', 'mythic', 'diamond', 200, '2000 moedas + Avatar exclusivo', '💎', 30),
('builder_10', 'Construtor', 'Construa uma base com 10 estruturas', 'survival', 'rare', 'silver', 40, '400 moedas', '🏗️', 10),

-- Exploração
('explorer_cities', 'Explorador do Mapa', 'Visite todas as cidades principais de Chernarus', 'exploration', 'rare', 'silver', 30, '300 moedas', '🗺️', 15),
('collector_weapons', 'Colecionador de Armas', 'Possua todas as armas raras do jogo', 'exploration', 'epic', 'gold', 75, '750 moedas + Caixa de armas', '🎖️', 12),

-- Social
('group_leader', 'Líder de Grupo', 'Forme um grupo com 5 ou mais jogadores', 'social', 'common', 'bronze', 15, '150 moedas', '👥', 5),
('medic_50', 'Médico de Campo', 'Cure 50 jogadores usando itens médicos', 'social', 'rare', 'silver', 35, '350 moedas', '💊', 50),
('loyal_friend', 'Amigo Fiel', 'Jogue 100 horas com o mesmo grupo', 'social', 'legendary', 'platinum', 90, '900 moedas + Emblema de grupo', '🤝', 100),

-- Riqueza
('rich_10k', 'Empreendedor', 'Acumule 10.000 DZCoins', 'wealth', 'common', 'bronze', 20, '200 moedas', '💰', 10000),
('rich_50k', 'Milionário', 'Acumule 50.000 DZCoins', 'wealth', 'rare', 'silver', 50, '500 moedas', '💎', 50000),
('rich_100k', 'Magnata', 'Acumule 100.000 DZCoins', 'wealth', 'epic', 'gold', 100, '1000 moedas + Título VIP', '👑', 100000)

ON CONFLICT (achievement_key) DO NOTHING;

-- ============================================
-- FUNÇÕES AUXILIARES
-- ============================================

-- Função para atualizar progresso de conquista
CREATE OR REPLACE FUNCTION update_achievement_progress(
    p_discord_id VARCHAR(50),
    p_achievement_key VARCHAR(50),
    p_progress_increment INTEGER DEFAULT 1
) RETURNS BOOLEAN AS $$
DECLARE
    v_current_progress INTEGER;
    v_max_progress INTEGER;
    v_already_unlocked BOOLEAN;
BEGIN
    -- Buscar progresso atual e max_progress
    SELECT ua.progress, ua.unlocked, a.max_progress
    INTO v_current_progress, v_already_unlocked, v_max_progress
    FROM user_achievements ua
    JOIN achievements a ON ua.achievement_key = a.achievement_key
    WHERE ua.discord_id = p_discord_id AND ua.achievement_key = p_achievement_key;
    
    -- Se não existe, criar
    IF NOT FOUND THEN
        SELECT max_progress INTO v_max_progress FROM achievements WHERE achievement_key = p_achievement_key;
        INSERT INTO user_achievements (discord_id, achievement_key, progress, unlocked)
        VALUES (p_discord_id, p_achievement_key, p_progress_increment, p_progress_increment >= v_max_progress);
        
        -- Se já completou, marcar como desbloqueado
        IF p_progress_increment >= v_max_progress THEN
            UPDATE user_achievements 
            SET unlocked = TRUE, unlocked_at = NOW()
            WHERE discord_id = p_discord_id AND achievement_key = p_achievement_key;
            RETURN TRUE;
        END IF;
        RETURN FALSE;
    END IF;
    
    -- Se já desbloqueado, não fazer nada
    IF v_already_unlocked THEN
        RETURN FALSE;
    END IF;
    
    -- Atualizar progresso
    v_current_progress := v_current_progress + p_progress_increment;
    
    UPDATE user_achievements
    SET progress = v_current_progress,
        unlocked = (v_current_progress >= v_max_progress),
        unlocked_at = CASE WHEN v_current_progress >= v_max_progress THEN NOW() ELSE NULL END,
        updated_at = NOW()
    WHERE discord_id = p_discord_id AND achievement_key = p_achievement_key;
    
    -- Retornar TRUE se desbloqueou agora
    RETURN (v_current_progress >= v_max_progress);
END;
$$ LANGUAGE plpgsql;

-- Função para adicionar evento ao histórico
CREATE OR REPLACE FUNCTION add_activity_event(
    p_discord_id VARCHAR(50),
    p_event_type VARCHAR(50),
    p_icon VARCHAR(10),
    p_title VARCHAR(200),
    p_description TEXT,
    p_details JSONB DEFAULT '{}'::JSONB
) RETURNS INTEGER AS $$
DECLARE
    v_event_id INTEGER;
BEGIN
    INSERT INTO activity_history (discord_id, event_type, icon, title, description, details)
    VALUES (p_discord_id, p_event_type, p_icon, p_title, p_description, p_details)
    RETURNING id INTO v_event_id;
    
    RETURN v_event_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS ÚTEIS
-- ============================================

-- View de conquistas com progresso do usuário
CREATE OR REPLACE VIEW v_user_achievements_full AS
SELECT 
    ua.discord_id,
    a.achievement_key,
    a.name,
    a.description,
    a.category,
    a.rarity,
    a.tier,
    a.points,
    a.reward,
    a.icon,
    a.max_progress,
    COALESCE(ua.progress, 0) as progress,
    COALESCE(ua.unlocked, FALSE) as unlocked,
    ua.unlocked_at
FROM achievements a
LEFT JOIN user_achievements ua ON a.achievement_key = ua.achievement_key;

-- View de estatísticas de conquistas por usuário
CREATE OR REPLACE VIEW v_user_achievement_stats AS
SELECT 
    discord_id,
    COUNT(*) FILTER (WHERE unlocked = TRUE) as total_unlocked,
    COUNT(*) as total_achievements,
    SUM(a.points) FILTER (WHERE ua.unlocked = TRUE) as total_points,
    COUNT(*) FILTER (WHERE ua.unlocked = TRUE AND a.rarity IN ('epic', 'legendary', 'mythic')) as rare_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE unlocked = TRUE) / NULLIF(COUNT(*), 0), 1) as completion_rate
FROM user_achievements ua
JOIN achievements a ON ua.achievement_key = a.achievement_key
GROUP BY discord_id;

COMMENT ON TABLE achievements IS 'Definições de todas as conquistas disponíveis';
COMMENT ON TABLE user_achievements IS 'Progresso de conquistas de cada usuário';
COMMENT ON TABLE activity_history IS 'Histórico de todas as atividades dos usuários';
COMMENT ON TABLE user_settings IS 'Configurações personalizadas de cada usuário';
