"""
Sistema de Banco de Dados PostgreSQL para BigodeTexas Bot
Gerencia players, economia, clãs e links Discord-Gamertag
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
from dotenv import load_dotenv

# Carrega variáveis do .env (override existing env vars)
load_dotenv(override=True)

# URLs de conexão
DATABASE_URL = os.getenv('DATABASE_URL', '')
POOLER_URL = os.getenv('SUPABASE_POOLER_URL', '')

def get_connection():
    """Cria conexão usando DATABASE_URL ou POOLER_URL."""
    url = DATABASE_URL or POOLER_URL
    if not url:
        print("Erro: nenhuma URL de conexão encontrada nas variáveis de ambiente")
        return None
    try:
        return psycopg2.connect(url, sslmode='require')
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def init_database():
    """Cria todas as tabelas necessárias"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # Tabela de jogadores (estatísticas)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS players (
                gamertag VARCHAR(255) PRIMARY KEY,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                best_killstreak INTEGER DEFAULT 0,
                longest_shot INTEGER DEFAULT 0,
                weapons_stats JSONB DEFAULT '{}',
                first_seen BIGINT,
                last_seen BIGINT
            )
        """)
        # Tabela de economia
        cur.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                discord_id VARCHAR(255) PRIMARY KEY,
                gamertag VARCHAR(255),
                balance INTEGER DEFAULT 0,
                last_daily TIMESTAMP,
                inventory JSONB DEFAULT '{}',
                transactions JSONB DEFAULT '[]',
                favorites JSONB DEFAULT '[]',
                achievements JSONB DEFAULT '{}'
            )
        """)
        # Tabela de clãs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clans (
                clan_name VARCHAR(255) PRIMARY KEY,
                leader VARCHAR(255),
                members JSONB DEFAULT '[]',
                created_at TIMESTAMP DEFAULT NOW(),
                total_kills INTEGER DEFAULT 0,
                total_deaths INTEGER DEFAULT 0
            )
        """)
        # Tabela de links Discord-Gamertag
        cur.execute("""
            CREATE TABLE IF NOT EXISTS links (
                discord_id VARCHAR(255) PRIMARY KEY,
                gamertag VARCHAR(255) UNIQUE,
                linked_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        conn.rollback()
        conn.close()
        return False

# ===== PLAYERS =====

def get_player(gamertag):
    """Busca dados de um jogador"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM players WHERE gamertag = %s", (gamertag,))
        player = cur.fetchone()
        cur.close()
        conn.close()
        return dict(player) if player else None
    except Exception as e:
        print(f"Erro ao buscar jogador: {e}")
        conn.close()
        return None

def save_player(gamertag, data):
    """Salva ou atualiza dados de um jogador"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO players (gamertag, kills, deaths, best_killstreak, longest_shot, weapons_stats, first_seen, last_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (gamertag) DO UPDATE SET
                kills = EXCLUDED.kills,
                deaths = EXCLUDED.deaths,
                best_killstreak = EXCLUDED.best_killstreak,
                longest_shot = EXCLUDED.longest_shot,
                weapons_stats = EXCLUDED.weapons_stats,
                last_seen = EXCLUDED.last_seen
        """,
            (
                gamertag,
                data.get('kills', 0),
                data.get('deaths', 0),
                data.get('best_killstreak', 0),
                data.get('longest_shot', 0),
                json.dumps(data.get('weapons_stats', {})),
                data.get('first_seen'),
                data.get('last_seen')
            ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar jogador: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_players():
    """Retorna todos os jogadores"""
    conn = get_connection()
    if not conn:
        return {}
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM players ORDER BY kills DESC")
        players = cur.fetchall()
        cur.close()
        conn.close()
        return {p['gamertag']: dict(p) for p in players}
    except Exception as e:
        print(f"Erro ao buscar jogadores: {e}")
        conn.close()
        return {}

# ===== ECONOMY =====

def get_economy(discord_id):
    """Busca dados de economia de um usuário"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM economy WHERE discord_id = %s", (str(discord_id),))
        eco = cur.fetchone()
        cur.close()
        conn.close()
        return dict(eco) if eco else None
    except Exception as e:
        print(f"Erro ao buscar economia: {e}")
        conn.close()
        return None

def save_economy(discord_id, data):
    """Salva ou atualiza dados de economia"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO economy (discord_id, gamertag, balance, last_daily, inventory, transactions, favorites, achievements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (discord_id) DO UPDATE SET
                gamertag = EXCLUDED.gamertag,
                balance = EXCLUDED.balance,
                last_daily = EXCLUDED.last_daily,
                inventory = EXCLUDED.inventory,
                transactions = EXCLUDED.transactions,
                favorites = EXCLUDED.favorites,
                achievements = EXCLUDED.achievements
        """,
            (
                str(discord_id),
                data.get('gamertag'),
                data.get('balance', 0),
                data.get('last_daily'),
                json.dumps(data.get('inventory', {})),
                json.dumps(data.get('transactions', [])),
                json.dumps(data.get('favorites', [])),
                json.dumps(data.get('achievements', {}))
            ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar economia: {e}")
        conn.rollback()
        conn.close()
        return False

def get_all_economy():
    """Retorna todos os dados de economia"""
    conn = get_connection()
    if not conn:
        return {}
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM economy")
        economies = cur.fetchall()
        cur.close()
        conn.close()
        return {e['discord_id']: dict(e) for e in economies}
    except Exception as e:
        print(f"Erro ao buscar economias: {e}")
        conn.close()
        return {}

# ===== LINKS =====

def save_link(discord_id, gamertag):
    """Salva ou atualiza link Discord-Gamertag"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO links (discord_id, gamertag)
            VALUES (%s, %s)
            ON CONFLICT (discord_id) DO UPDATE SET
                gamertag = EXCLUDED.gamertag
        """, (str(discord_id), gamertag))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar link: {e}")
        conn.rollback()
        conn.close()
        return False

def get_link_by_discord(discord_id):
    """Busca gamertag vinculado a um Discord ID"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT gamertag FROM links WHERE discord_id = %s", (str(discord_id),))
        link = cur.fetchone()
        cur.close()
        conn.close()
        return link['gamertag'] if link else None
    except Exception as e:
        print(f"Erro ao buscar link: {e}")
        conn.close()
        return None

def get_link_by_gamertag(gamertag):
    """Busca Discord ID vinculado a um gamertag"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT discord_id FROM links WHERE gamertag = %s", (gamertag,))
        link = cur.fetchone()
        cur.close()
        conn.close()
        return link['discord_id'] if link else None
    except Exception as e:
        print(f"Erro ao buscar link: {e}")
        conn.close()
        return None

def get_all_links():
    """Retorna todos os links"""
    conn = get_connection()
    if not conn:
        return {}
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM links")
        links = cur.fetchall()
        cur.close()
        conn.close()
        return {l['discord_id']: l['gamertag'] for l in links}
    except Exception as e:
        print(f"Erro ao buscar links: {e}")
        conn.close()
        return {}

# ===== CLANS =====

def save_clan(clan_name, data):
    """Salva ou atualiza um clã"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO clans (clan_name, leader, members, total_kills, total_deaths)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (clan_name) DO UPDATE SET
                leader = EXCLUDED.leader,
                members = EXCLUDED.members,
                total_kills = EXCLUDED.total_kills,
                total_deaths = EXCLUDED.total_deaths
        """, (
            clan_name,
            data.get('leader'),
            json.dumps(data.get('members', [])),
            data.get('total_kills', 0),
            data.get('total_deaths', 0)
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao salvar clã: {e}")
        conn.rollback()
        conn.close()
        return False

def get_clan(clan_name):
    """Busca dados de um clã"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM clans WHERE clan_name = %s", (clan_name,))
        clan = cur.fetchone()
        cur.close()
        conn.close()
        return dict(clan) if clan else None
    except Exception as e:
        print(f"Erro ao buscar clã: {e}")
        conn.close()
        return None

def get_all_clans():
    """Retorna todos os clãs"""
    conn = get_connection()
    if not conn:
        return {}
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM clans")
        clans = cur.fetchall()
        cur.close()
        conn.close()
        return {c['clan_name']: dict(c) for c in clans}
    except Exception as e:
        print(f"Erro ao buscar clãs: {e}")
        conn.close()
        return {}
