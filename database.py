import sqlite3
import os
from datetime import datetime

DB_NAME = "pvp_events.db"

def init_db():
    """Inicializa o banco de dados e cria a tabela de eventos se não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela de Eventos PvP (baseada na sugestão do GPT)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,        -- 'kill', 'death', 'hit'
        game_x REAL,            -- Coordenada X no jogo
        game_y REAL,            -- Coordenada Y (Altura)
        game_z REAL,            -- Coordenada Z (Norte/Sul)
        weapon TEXT,            -- Arma usada
        killer_name TEXT,       -- Nome do assassino
        victim_name TEXT,       -- Nome da vítima
        distance REAL,          -- Distância do tiro
        timestamp DATETIME      -- Data e hora do evento
    )
    ''')
    
    # Índices para performance (muito importante para filtros de data e posição)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_coords ON events(game_x, game_z)')
    
    conn.commit()
    conn.close()
    print(f"Banco de dados {DB_NAME} inicializado com sucesso.")

def add_event(event_type, x, y, z, weapon, killer, victim, distance, timestamp):
    """Adiciona um novo evento ao banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO events (event_type, game_x, game_y, game_z, weapon, killer_name, victim_name, distance, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (event_type, x, y, z, weapon, killer, victim, distance, timestamp))
    
    conn.commit()
    conn.close()

def get_heatmap_data(since_date, grid_size=50):
    """
    Retorna dados agregados para o heatmap.
    Implementa o 'Grid Clustering' sugerido pelo GPT.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Query inteligente que agrupa pontos próximos (buckets)
    # Arredonda as coordenadas para o múltiplo mais próximo de 'grid_size'
    query = f'''
    SELECT 
        (CAST(game_x / {grid_size} AS INT) * {grid_size}) as gx,
        (CAST(game_z / {grid_size} AS INT) * {grid_size}) as gz,
        COUNT(*) as intensity
    FROM events
    WHERE timestamp >= ? AND event_type = 'kill'
    GROUP BY gx, gz
    '''
    
    cursor.execute(query, (since_date,))
    rows = cursor.fetchall()
    conn.close()
    
    # Formata para JSON: [{x: 4500, z: 10000, count: 5}, ...]
    return [{'x': r[0], 'z': r[1], 'count': r[2]} for r in rows]

def parse_rpt_line(line):
    """
    Parser de logs RPT do DayZ.
    Extrai eventos de morte (PlayerKill) das linhas do log.
    
    Formatos suportados:
    - "PlayerKill: Killer=John, Victim=Mike, Pos=<09892.3, 0, 11234.9>, Weapon=M4A1, Distance=120m"
    - "Kill: John killed Mike at [4500, 0, 10000] with AKM (50m)"
    
    Retorna dict com dados do evento ou None se não encontrar padrão.
    """
    import re
    
    # Padrão 1: Formato detalhado
    pattern1 = r'PlayerKill: Killer=(?P<killer>[^,]+), Victim=(?P<victim>[^,]+), Pos=<(?P<x>[-0-9.]+),\s*[-0-9.]+,\s*(?P<z>[-0-9.]+)>, Weapon=(?P<weapon>[^,]+), Distance=(?P<dist>\d+)'
    match = re.search(pattern1, line)
    
    if match:
        return {
            'event_type': 'kill',
            'game_x': float(match.group('x')),
            'game_y': 0.0,
            'game_z': float(match.group('z')),
            'weapon': match.group('weapon').strip(),
            'killer_name': match.group('killer').strip(),
            'victim_name': match.group('victim').strip(),
            'distance': float(match.group('dist')),
            'timestamp': datetime.now()
        }
    
    # Padrão 2: Formato simplificado
    pattern2 = r'Kill: (?P<killer>\w+) killed (?P<victim>\w+) at \[(?P<x>[-0-9.]+),\s*[-0-9.]+,\s*(?P<z>[-0-9.]+)\] with (?P<weapon>\w+)'
    match = re.search(pattern2, line)
    
    if match:
        return {
            'event_type': 'kill',
            'game_x': float(match.group('x')),
            'game_y': 0.0,
            'game_z': float(match.group('z')),
            'weapon': match.group('weapon').strip(),
            'killer_name': match.group('killer').strip(),
            'victim_name': match.group('victim').strip(),
            'distance': 0.0,
            'timestamp': datetime.now()
        }
    
    return None

# Inicializar ao rodar o script
if __name__ == "__main__":
    init_db()
    
    # Adicionar alguns dados de teste se estiver vazio
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM events')
    if cursor.fetchone()[0] == 0:
        print("Adicionando dados de teste...")
        import random
        from datetime import timedelta
        
        # Gerar 100 mortes aleatórias em NWAF (aprox X: 4500, Z: 10000)
        now = datetime.now()
        for _ in range(100):
            x = 4500 + random.uniform(-300, 300)
            z = 10000 + random.uniform(-300, 300)
            add_event('kill', x, 0, z, 'M4-A1', 'Survivor', 'Bandit', 50, now - timedelta(hours=random.randint(0, 24)))
            
        # Gerar 50 mortes em Cherno (aprox X: 6500, Z: 2500)
        for _ in range(50):
            x = 6500 + random.uniform(-200, 200)
            z = 2500 + random.uniform(-200, 200)
            add_event('kill', x, 0, z, 'BK-18', 'Freshie', 'Camper', 10, now - timedelta(hours=random.randint(0, 24)))
            
        print("Dados de teste adicionados.")
    conn.close()

def get_all_clans():
    """Retorna todos os clãs do arquivo clans.json"""
    import json
    if not os.path.exists("clans.json"):
        return {}
    try:
        with open("clans.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def get_all_players():
    """Retorna todos os jogadores do arquivo players_db.json"""
    import json
    if not os.path.exists("players_db.json"):
        return {}
    try:
        with open("players_db.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}
        
def get_economy(user_id):
    """Retorna dados de economia do arquivo economy.json"""
    import json
    if not os.path.exists("economy.json"):
        return {}
    try:
        with open("economy.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(str(user_id), {})
    except:
        return {}

def save_economy(user_id, data):
    """Salva dados de economia no arquivo economy.json"""
    import json
    economy_data = {}
    if os.path.exists("economy.json"):
        try:
            with open("economy.json", 'r', encoding='utf-8') as f:
                economy_data = json.load(f)
        except:
            pass
    
    economy_data[str(user_id)] = data
    
    with open("economy.json", 'w', encoding='utf-8') as f:
        json.dump(economy_data, f, indent=4)

def get_player(gamertag):
    """Retorna dados de um jogador específico"""
    players = get_all_players()
    return players.get(gamertag, {})

def save_player(gamertag, data):
    """Salva dados de um jogador"""
    import json
    players = get_all_players()
    players[gamertag] = data
    with open("players_db.json", 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=4)

def get_link_by_gamertag(gamertag):
    """Retorna ID do Discord vinculado a gamertag"""
    import json
    if not os.path.exists("links.json"):
        return None
    try:
        with open("links.json", 'r', encoding='utf-8') as f:
            links = json.load(f)
            # links.json structure: {discord_id: gamertag}
            # We need reverse lookup
            for discord_id, tag in links.items():
                if tag.lower() == gamertag.lower():
                    return discord_id
    except:
        pass
    return None

def get_clan(tag):
    """Retorna dados de um clã específico"""
    clans = get_all_clans()
    return clans.get(tag.upper())

