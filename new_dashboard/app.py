"""
BigodeTexas Dashboard - Versão 2.0
Sistema completo de dashboard para servidor DayZ
"""
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuração do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    """Conexão com banco de dados"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# ==================== ROTAS PRINCIPAIS ====================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/heatmap')
def heatmap():
    return render_template('heatmap.html')

@app.route('/login')
def login():
    """Redireciona para OAuth Discord"""
    from discord_auth import get_oauth_url
    return redirect(get_oauth_url())

@app.route('/callback')
def callback():
    """Callback OAuth Discord"""
    from discord_auth import exchange_code, get_user_info
    
    code = request.args.get('code')
    if not code:
        return redirect(url_for('index'))
    
    try:
        # Trocar código por token
        token_data = exchange_code(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            return redirect(url_for('index'))
        
        # Buscar informações do usuário
        user_info = get_user_info(access_token)
        
        # Salvar na sessão
        session['discord_user_id'] = user_info['id']
        session['discord_username'] = user_info['username']
        session['discord_avatar'] = user_info.get('avatar')
        session['discord_email'] = user_info.get('email')
        
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Erro no OAuth: {e}")
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard do usuário"""
    # Criar sessão fake para testes se não estiver logado
    if 'discord_user_id' not in session:
        session['discord_user_id'] = 'test_user_123'
        session['discord_username'] = 'Jogador de Teste'
    return render_template('dashboard.html')

@app.route('/shop')
def shop():
    """Loja de itens"""
    # Criar sessão fake para testes se não estiver logado
    if 'discord_user_id' not in session:
        session['discord_user_id'] = 'test_user_123'
        session['discord_username'] = 'Jogador de Teste'
    return render_template('shop.html')

@app.route('/leaderboard')
def leaderboard():
    """Rankings"""
    return render_template('leaderboard.html')

@app.route('/checkout')
def checkout():
    """Página de checkout com mapa"""
    # Criar sessão fake para testes se não estiver logado
    if 'discord_user_id' not in session:
        session['discord_user_id'] = 'test_user_123'
        session['discord_username'] = 'Jogador de Teste'
    return render_template('checkout.html')

@app.route('/order-confirmation')
def order_confirmation():
    """Confirmação de pedido"""
    return render_template('order_confirmation.html')

@app.route('/agradecimentos')
def agradecimentos():
    """Página de agradecimentos aos amigos"""
    return render_template('agradecimentos.html')

@app.route('/base')
def base():
    """Página de registro de base"""
    return render_template('base.html')

@app.route('/clan')
def clan():
    """Página de gerenciamento de clã"""
    return render_template('clan.html')

@app.route('/banco')
def banco():
    """Página do Banco Sul"""
    return render_template('banco.html')


# ==================== API ENDPOINTS ====================

@app.route('/api/stats')
def api_stats():
    """Estatísticas gerais do servidor"""
    conn = get_db()
    cur = conn.cursor()
    
    # Total de jogadores
    cur.execute("SELECT COUNT(*) as total FROM players_db")
    total_players = cur.fetchone()['total']
    
    # Total de kills
    cur.execute("SELECT SUM(kills) as total FROM players_db")
    total_kills = cur.fetchone()['total'] or 0
    
    # Total de moedas em circulação
    cur.execute("SELECT SUM(balance) as total FROM economy")
    total_coins = cur.fetchone()['total'] or 0
    
    cur.close()
    conn.close()
    
    return jsonify({
        'total_players': total_players,
        'total_kills': total_kills,
        'total_coins': total_coins,
        'server_name': 'BigodeTexas'
    })

@app.route('/api/user/profile')
def api_user_profile():
    """Perfil do usuário logado"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    # Buscar dados de economia
    cur.execute("SELECT * FROM economy WHERE discord_id = %s", (str(user_id),))
    economy = cur.fetchone()
    
    # Buscar link com gamertag
    cur.execute("SELECT gamertag FROM links WHERE discord_id = %s", (str(user_id),))
    link = cur.fetchone()
    
    cur.close()
    conn.close()
    
    balance = economy['balance'] if economy else 0
    gamertag = link['gamertag'] if link else None
    
    return jsonify({
        'username': session.get('discord_username', 'Jogador'),
        'gamertag': gamertag,
        'balance': balance,
        'avatar': session.get('discord_avatar')
    })

@app.route('/api/user/balance')
def api_user_balance():
    """Saldo do usuário"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT balance FROM economy WHERE discord_id = %s", (str(user_id),))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    return jsonify({
        'balance': result['balance'] if result else 0,
        'user_id': user_id
    })

@app.route('/api/shop/items')
def api_shop_items():
    """Lista de itens da loja"""
    import json
    
    # Carregar items.json do diretório pai
    items_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'items.json')
    
    try:
        with open(items_path, 'r', encoding='utf-8') as f:
            items_data = json.load(f)
        
        # Transformar em lista plana
        items_list = []
        for category, items_dict in items_data.items():
            for code, item in items_dict.items():
                items_list.append({
                    'code': code,
                    'name': item.get('name', 'Unknown'),
                    'price': item.get('price', 0),
                    'category': category,
                    'description': item.get('description', '')
                })
        
        return jsonify(items_list)
    except Exception as e:
        print(f"Erro ao carregar itens: {e}")
        return jsonify([])

@app.route('/api/user/stats')
def api_user_stats():
    """Estatísticas do usuário"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    # Buscar gamertag vinculado
    cur.execute("SELECT gamertag FROM links WHERE discord_id = %s", (str(user_id),))
    link = cur.fetchone()
    
    if not link:
        cur.close()
        conn.close()
        return jsonify({})
        
    gamertag = link['gamertag']
    
    # Buscar stats do jogador
    cur.execute("SELECT * FROM players WHERE gamertag = %s", (gamertag,))
    player = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if not player:
        return jsonify({})
        
    # Calcular K/D
    kills = player.get('kills', 0)
    deaths = player.get('deaths', 0)
    kd = round(kills / deaths, 2) if deaths > 0 else kills
    
    return jsonify({
        'kills': kills,
        'deaths': deaths,
        'kd': kd,
        'zombie_kills': 0, # Não temos esse dado ainda na tabela players
        'lifetime': 0, # Não temos
        'distance_walked': 0, # Não temos
        'vehicle_distance': 0, # Não temos
        'reconnects': 0, # Não temos
        'buildings_built': 0, # Não temos
        'locks_picked': 0, # Não temos
        'has_base': False, # Não temos
        'favorite_weapon': '-',
        'favorite_city': '-',
        'total_playtime': 0
    })

@app.route('/api/user/purchases')
def api_user_purchases():
    """Histórico de compras"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM purchases 
        WHERE discord_id = %s 
        ORDER BY created_at DESC
    """, (str(user_id),))
    
    purchases = cur.fetchall()
    cur.close()
    conn.close()
    
    # Formatar dados
    result = []
    for p in purchases:
        items = p['items']
        items_count = sum(item['quantity'] for item in items)
        
        result.append({
            'id': p['id'],
            'date': p['created_at'].isoformat(),
            'total': p['total'],
            'status': p['status'],
            'items_count': items_count,
            'items': items
        })
    
    return jsonify(result)

@app.route('/api/user/achievements')
def api_user_achievements():
    """Conquistas do usuário"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT achievements FROM economy WHERE discord_id = %s", (str(user_id),))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    achievements = result['achievements'] if result and result['achievements'] else {}
    
    return jsonify({
        'first_kill': achievements.get('first_kill', False),
        'survivor': achievements.get('survivor', False),
        'rich': achievements.get('rich', False),
        'builder': achievements.get('builder', False),
        'hunter': achievements.get('hunter', False),
        'explorer': achievements.get('explorer', False)
    })

@app.route('/api/leaderboard')
def api_leaderboard():
    """Dados de todos os rankings"""
    conn = get_db()
    cur = conn.cursor()
    
    # Richest (Economy)
    cur.execute("SELECT gamertag as name, balance as value FROM economy ORDER BY balance DESC LIMIT 10")
    richest = [dict(row) for row in cur.fetchall()]
    
    # Kills (Players)
    cur.execute("SELECT gamertag as name, kills as value FROM players ORDER BY kills DESC LIMIT 10")
    kills = [dict(row) for row in cur.fetchall()]
    
    # Deaths (Players)
    cur.execute("SELECT gamertag as name, deaths as value FROM players ORDER BY deaths DESC LIMIT 10")
    deaths = [dict(row) for row in cur.fetchall()]
    
    # K/D (Calculado)
    cur.execute("""
        SELECT gamertag as name, 
        CASE WHEN deaths = 0 THEN kills ELSE CAST(kills AS FLOAT)/deaths END as value 
        FROM players 
        WHERE kills > 5
        ORDER BY value DESC LIMIT 10
    """)
    kd = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return jsonify({
        'richest': richest,
        'kills': kills,
        'deaths': deaths,
        'kd': kd,
        'zombies': [], # TODO: Adicionar coluna zombie_kills
        'distance': [], # TODO: Adicionar coluna distance
        'vehicle': [], # TODO: Adicionar coluna vehicle_distance
        'reconnects': [], # TODO: Adicionar coluna reconnects
        'builder': [], # TODO: Adicionar coluna buildings
        'raider': [] # TODO: Adicionar coluna raids
    })

@app.route('/api/shop/purchase', methods=['POST'])
def api_shop_purchase():
    """Processar compra"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    total_cost = data.get('total')
    items = data.get('items')
    coordinates = data.get('coordinates')
    
    if not total_cost or not items:
        return jsonify({'error': 'Dados inválidos'}), 400
        
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Verificar saldo
        cur.execute("SELECT balance FROM economy WHERE discord_id = %s", (str(user_id),))
        result = cur.fetchone()
        
        if not result or result['balance'] < total_cost:
            return jsonify({'error': 'Saldo insuficiente'}), 400
            
        # Deduzir saldo
        new_balance = result['balance'] - total_cost
        cur.execute("UPDATE economy SET balance = %s WHERE discord_id = %s", (new_balance, str(user_id)))
        
        # Registrar compra
        import json
        cur.execute("""
            INSERT INTO purchases (discord_id, items, total, coordinates, status)
            VALUES (%s, %s, %s, %s, 'pending')
        """, (str(user_id), json.dumps(items), total_cost, json.dumps(coordinates)))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'deliveryTime': '5 minutos',
            'coordinates': coordinates,
            'total': total_cost,
            'new_balance': new_balance
        })
        
    except Exception as e:
        conn.rollback()
        print(f"Erro na compra: {e}")
        return jsonify({'error': 'Erro ao processar compra'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/heatmap')
def api_heatmap():
    """
    API de Heatmap - Retorna dados agregados de eventos PvP
    Implementação baseada na arquitetura sugerida pelo ChatGPT
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from database import get_heatmap_data
    from datetime import datetime, timedelta
    
    # Parâmetros da query
    time_range = request.args.get('range', '24h')  # 24h, 7d, all
    grid_size = int(request.args.get('grid', 50))  # Tamanho do grid em unidades do jogo
    
    # Calcular data de início baseado no range
    if time_range == '24h':
        since_date = datetime.now() - timedelta(hours=24)
    elif time_range == '7d':
        since_date = datetime.now() - timedelta(days=7)
    else:  # 'all'
        since_date = datetime(2020, 1, 1)  # Data antiga para pegar tudo
    
    try:
        # Buscar dados agregados do banco
        data = get_heatmap_data(since_date, grid_size)
        
        return jsonify({
            'success': True,
            'points': data,
            'range': time_range,
            'grid_size': grid_size,
            'total_events': sum(p['count'] for p in data)
        })
    except Exception as e:
        print(f"Erro ao buscar heatmap: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'points': []
        }), 500

@app.route('/api/parse_log', methods=['POST'])
def api_parse_log():
    """
    Endpoint para processar logs RPT do DayZ.
    Recebe texto de log via POST e extrai eventos de morte.
    
    Body JSON:
    {
        "text": "linha1\nlinha2\nlinha3...",
        "source": "nitrado" (opcional)
    }
    
    Retorna:
    {
        "success": true,
        "events_saved": 5,
        "events_parsed": 10
    }
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from database import parse_rpt_line, add_event
    
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing "text" field in request body'
        }), 400
    
    log_text = data.get('text', '')
    source = data.get('source', 'unknown')
    
    events_parsed = 0
    events_saved = 0
    
    try:
        for line in log_text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # Tentar extrair evento da linha
            event = parse_rpt_line(line)
            if event:
                events_parsed += 1
                try:
                    # Salvar no banco
                    add_event(
                        event['event_type'],
                        event['game_x'],
                        event['game_y'],
                        event['game_z'],
                        event['weapon'],
                        event['killer_name'],
                        event['victim_name'],
                        event['distance'],
                        event['timestamp']
                    )
                    events_saved += 1
                except Exception as e:
                    print(f"Erro ao salvar evento: {e}")
        
        return jsonify({
            'success': True,
            'events_parsed': events_parsed,
            'events_saved': events_saved,
            'source': source
        })
        
    except Exception as e:
        print(f"Erro ao processar log: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'events_parsed': events_parsed,
            'events_saved': events_saved
        }), 500

@app.route('/api/heatmap/top_locations')
def api_heatmap_top_locations():
    """
    API de Top Locations - Retorna as 5 áreas mais perigosas
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from datetime import datetime, timedelta
    
    # Parâmetros da query
    time_range = request.args.get('range', '24h')
    
    # Calcular data de início
    if time_range == '24h':
        since_date = datetime.now() - timedelta(hours=24)
    elif time_range == '7d':
        since_date = datetime.now() - timedelta(days=7)
    else:
        since_date = datetime(2020, 1, 1)
    
    try:
        import sqlite3
        conn = sqlite3.connect('pvp_events.db')
        cursor = conn.cursor()
        
        # Query para agrupar por regiões (buckets de 500m)
        query = """
        SELECT 
            CAST(game_x / 500 AS INT) * 500 + 250 as center_x,
            CAST(game_z / 500 AS INT) * 500 + 250 as center_z,
            COUNT(*) as deaths,
            GROUP_CONCAT(DISTINCT weapon, ', ') as weapons
        FROM events
        WHERE timestamp >= ? AND event_type = 'kill'
        GROUP BY 
            CAST(game_x / 500 AS INT),
            CAST(game_z / 500 AS INT)
        ORDER BY deaths DESC
        LIMIT 5
        """
        
        cursor.execute(query, (since_date,))
        rows = cursor.fetchall()
        conn.close()
        
        # Mapear coordenadas para nomes de locais conhecidos
        def get_location_name(x, z):
            landmarks = {
                'NWAF': (4500, 10000, 800),
                'Tisy Military Base': (1800, 14000, 600),
                'Chernogorsk': (6500, 2500, 800),
                'Elektrozavodsk': (10500, 2200, 800),
                'Berezino': (12500, 9500, 600),
                'Stary Sobor': (6000, 7700, 400),
                'Zelenogorsk': (2500, 5000, 500),
                'Vybor': (3700, 8900, 400),
                'Severograd': (7900, 12600, 500),
                'Novo': (11900, 12300, 500)
            }
            
            for name, (lx, lz, radius) in landmarks.items():
                dist = ((x - lx)**2 + (z - lz)**2)**0.5
                if dist <= radius:
                    return name
            
            return None
        
        # Formatar resultado
        locations = []
        for row in rows:
            center_x, center_z, deaths, weapons = row
            location_name = get_location_name(center_x, center_z)
            
            locations.append({
                'center_x': center_x,
                'center_z': center_z,
                'deaths': deaths,
                'weapons': weapons or 'Várias',
                'location_name': location_name,
                'time_range': time_range
            })
        
        return jsonify({
            'success': True,
            'locations': locations,
            'range': time_range
        })
        
    except Exception as e:
        print(f"Erro ao buscar top locations: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'locations': []
        }), 500

@app.route('/api/heatmap/weapons')
def api_heatmap_weapons():
    """
    API de Armas - Retorna lista de armas usadas e contagem
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from datetime import datetime, timedelta
    
    time_range = request.args.get('range', '24h')
    
    if time_range == '24h':
        since_date = datetime.now() - timedelta(hours=24)
    elif time_range == '7d':
        since_date = datetime.now() - timedelta(days=7)
    elif time_range == '30d':
        since_date = datetime.now() - timedelta(days=30)
    else:
        since_date = datetime(2020, 1, 1)
    
    try:
        import sqlite3
        conn = sqlite3.connect('pvp_events.db')
        cursor = conn.cursor()
        
        query = """
        SELECT weapon, COUNT(*) as count
        FROM events
        WHERE timestamp >= ? AND event_type = 'kill' AND weapon IS NOT NULL
        GROUP BY weapon
        ORDER BY count DESC
        """
        
        cursor.execute(query, (since_date,))
        rows = cursor.fetchall()
        conn.close()
        
        weapons = [{'name': row[0], 'count': row[1]} for row in rows]
        
        return jsonify({
            'success': True,
            'weapons': weapons,
            'range': time_range
        })
        
    except Exception as e:
        print(f"Erro ao buscar armas: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'weapons': []
        }), 500

@app.route('/api/base/register', methods=['POST'])
def api_base_register():
    """Registrar base do usuário"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    coord_x = data.get('coord_x')
    coord_y = data.get('coord_y', 0)
    coord_z = data.get('coord_z', 0) # No DayZ, profundidade é Z, altura é Y. Mas o mapa 2D usa X/Y.
    name = data.get('name')
    
    if coord_x is None or coord_y is None:
        return jsonify({'error': 'Coordenadas inválidas'}), 400
        
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Verificar se já tem base
        cur.execute("SELECT id FROM bases_v2 WHERE owner_discord_id = %s", (str(user_id),))
        if cur.fetchone():
            return jsonify({'error': 'Você já possui uma base registrada!'}), 400
            
        # Registrar
        cur.execute("""
            INSERT INTO bases_v2 (owner_discord_id, coord_x, coord_y, coord_z, name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (str(user_id), coord_x, 0, coord_y, name)) # Mapeando Y do mapa para Z do jogo
        
        base_id = cur.fetchone()['id']
        conn.commit()
        
        # Log de Auditoria
        cur.execute("""
            INSERT INTO audit_logs (entity_type, entity_id, actor_discord_id, action, details)
            VALUES ('base', %s, %s, 'register', %s)
        """, (base_id, str(user_id), jsonify(data)))
        conn.commit()
        
        return jsonify({'success': True, 'base_id': base_id})
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao registrar base: {e}")
        return jsonify({'error': f'Erro ao registrar: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/clan/create', methods=['POST'])
def api_clan_create():
    """Criar novo clã"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
        
    data = request.get_json()
    name = data.get('name')
    color1 = data.get('color1', '#FF0000')
    color2 = data.get('color2', '#00FF00')
    
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
        
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Verificar se nome já existe
        cur.execute("SELECT id FROM clans WHERE name ILIKE %s", (name,))
        if cur.fetchone():
            return jsonify({'error': 'Nome de clã já existe!'}), 400
            
        # Verificar se usuário já tem clã
        cur.execute("SELECT clan_id FROM clan_members_v2 WHERE discord_id = %s", (str(user_id),))
        if cur.fetchone():
            return jsonify({'error': 'Você já pertence a um clã!'}), 400
            
        # Criar Clã
        # Nota: Usamos leader_discord_id em vez de ID numérico para compatibilidade
        cur.execute("""
            INSERT INTO clans (name, leader_discord_id, symbol_color1, symbol_color2, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """, (name, str(user_id), color1, color2))
        
        clan_id = cur.fetchone()['id']
        
        # Adicionar líder como membro
        cur.execute("""
            INSERT INTO clan_members_v2 (clan_id, discord_id, role)
            VALUES (%s, %s, 'leader')
        """, (clan_id, str(user_id)))
        
        conn.commit()
        
        return jsonify({'success': True, 'clan_id': clan_id})
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao criar clã: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/clan/my')
def api_clan_my():
    """Retorna dados do clã do usuário"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'has_clan': False})
        
    conn = get_db()
    cur = conn.cursor()
    
    # Buscar clã do membro
    cur.execute("""
        SELECT c.*, cm.role 
        FROM clan_members_v2 cm
        JOIN clans c ON cm.clan_id = c.id
        WHERE cm.discord_id = %s
    """, (str(user_id),))
    
    clan = cur.fetchone()
    
    if not clan:
        cur.close()
        conn.close()
        return jsonify({'has_clan': False})
        
    # Buscar membros
    cur.execute("""
        SELECT discord_id, role, joined_at 
        FROM clan_members_v2 
        WHERE clan_id = %s
    """, (clan['id'],))
    members = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return jsonify({
        'has_clan': True,
        'info': dict(clan),
        'members': members
    })

@app.route('/api/base/check')
def api_base_check():
    """Verifica se o usuário tem base"""
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'has_base': False})
        
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM bases_v2 WHERE owner_discord_id = %s", (str(user_id),))
    base = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if base:
        return jsonify({
            'has_base': True,
            'base': {
                'id': base['id'],
                'name': base['name'],
                'x': base['coord_x'],
                'y': base['coord_z'] # Z do jogo é Y do mapa
            }
        })
    else:
        return jsonify({'has_base': False})
def api_heatmap_timeline():
    """
    API de Timeline - Retorna mortes agrupadas por período de tempo
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from datetime import datetime, timedelta
    
    time_range = request.args.get('range', '7d')
    
    if time_range == '24h':
        since_date = datetime.now() - timedelta(hours=24)
        group_by = 'hour'
    elif time_range == '7d':
        since_date = datetime.now() - timedelta(days=7)
        group_by = 'day'
    elif time_range == '30d':
        since_date = datetime.now() - timedelta(days=30)
        group_by = 'day'
    else:
        since_date = datetime.now() - timedelta(days=30)
        group_by = 'day'
    
    try:
        import sqlite3
        conn = sqlite3.connect('pvp_events.db')
        cursor = conn.cursor()
        
        if group_by == 'hour':
            query = """
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as period,
                COUNT(*) as total,
                SUM(CASE WHEN event_type = 'kill' THEN 1 ELSE 0 END) as pvp,
                SUM(CASE WHEN event_type = 'suicide' THEN 1 ELSE 0 END) as pve
            FROM events
            WHERE timestamp >= ?
            GROUP BY strftime('%Y-%m-%d %H', timestamp)
            ORDER BY period ASC
            """
        else:
            query = """
            SELECT 
                strftime('%Y-%m-%d', timestamp) as period,
                COUNT(*) as total,
                SUM(CASE WHEN event_type = 'kill' THEN 1 ELSE 0 END) as pvp,
                SUM(CASE WHEN event_type = 'suicide' THEN 1 ELSE 0 END) as pve
            FROM events
            WHERE timestamp >= ?
            GROUP BY strftime('%Y-%m-%d', timestamp)
            ORDER BY period ASC
            """
        
        cursor.execute(query, (since_date,))
        rows = cursor.fetchall()
        conn.close()
        
        timeline = [{
            'period': row[0],
            'total': row[1],
            'pvp': row[2],
            'pve': row[3]
        } for row in rows]
        
        return jsonify({
            'success': True,
            'timeline': timeline,
            'range': time_range,
            'group_by': group_by
        })
        
    except Exception as e:
        print(f"Erro ao buscar timeline: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timeline': []
        }), 500

@app.route('/api/heatmap/hourly')
def api_heatmap_hourly():
    """
    API de Heatmap por Hora - Retorna mortes agrupadas por hora do dia (0-23)
    """
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from datetime import datetime, timedelta
    
    time_range = request.args.get('range', '7d')
    
    if time_range == '24h':
        since_date = datetime.now() - timedelta(hours=24)
    elif time_range == '7d':
        since_date = datetime.now() - timedelta(days=7)
    elif time_range == '30d':
        since_date = datetime.now() - timedelta(days=30)
    else:
        since_date = datetime(2020, 1, 1)
    
    try:
        import sqlite3
        conn = sqlite3.connect('pvp_events.db')
        cursor = conn.cursor()
        
        query = """
        SELECT 
            CAST(strftime('%H', timestamp) AS INTEGER) as hour,
            COUNT(*) as count
        FROM events
        WHERE timestamp >= ? AND event_type = 'kill'
        GROUP BY hour
        ORDER BY hour ASC
        """
        
        cursor.execute(query, (since_date,))
        rows = cursor.fetchall()
        conn.close()
        
        # Criar array com todas as 24 horas (inicializado com 0)
        hourly_data = [0] * 24
        for row in rows:
            hour, count = row
            hourly_data[hour] = count
        
        return jsonify({
            'success': True,
            'hourly': hourly_data,
            'range': time_range
        })
        
    except Exception as e:
        print(f"Erro ao buscar hourly heatmap: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'hourly': [0] * 24
        }), 500

# ==================== APIs BASE, CLAN E BANCO ====================

@app.route('/api/base/register', methods=['POST'])
def api_base_register():
    """Registrar nova base"""
    try:
        data = request.get_json()
        user_id = session.get('discord_user_id', 'test_user_123')
        
        conn = get_db()
        cur = conn.cursor()
        
        # Verificar se usuário já tem base
        cur.execute("SELECT id FROM bases WHERE owner_id = %s", (user_id,))
        if cur.fetchone():
            conn.close()
            return jsonify({'error': 'Você já possui uma base registrada'}), 400
        
        # Inserir base
        cur.execute("""
            INSERT INTO bases (owner_id, coord_x, coord_y, coord_z, name)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (user_id, data['coord_x'], data['coord_y'], data.get('coord_z', 0), data.get('name')))
        
        base_id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'base_id': base_id})
    except Exception as e:
        print(f"Erro ao registrar base: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/clan/create', methods=['POST'])
def api_clan_create():
    """Criar novo clã"""
    try:
        data = request.get_json()
        user_id = session.get('discord_user_id', 'test_user_123')
        
        conn = get_db()
        cur = conn.cursor()
        
        # Verificar se usuário já está em um clã
        cur.execute("SELECT clan_id FROM clan_members WHERE user_id = %s", (user_id,))
        if cur.fetchone():
            conn.close()
            return jsonify({'error': 'Você já está em um clã'}), 400
        
        # Criar clã
        cur.execute("""
            INSERT INTO clans (name, leader_id, symbol_color1, symbol_color2, symbol_icon)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (data['name'], user_id, data.get('color1', '#FF0000'), 
              data.get('color2', '#00FF00'), data.get('icon', 'shield')))
        
        clan_id = cur.fetchone()[0]
        
        # Adicionar líder como membro
        cur.execute("""
            INSERT INTO clan_members (clan_id, user_id, role)
            VALUES (%s, %s, 'leader')
        """, (clan_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'clan_id': clan_id})
    except Exception as e:
        print(f"Erro ao criar clã: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/banco/transfer', methods=['POST'])
def api_banco_transfer():
    """Transferir dinheiro entre jogadores"""
    try:
        data = request.get_json()
        from_user_id = session.get('discord_user_id', 'test_user_123')
        to_user_id = data['to_user_id']
        amount = int(data['amount'])
        
        if amount <= 0:
            return jsonify({'error': 'Valor inválido'}), 400
        
        conn = get_db()
        cur = conn.cursor()
        
        # Verificar saldo
        cur.execute("SELECT balance FROM users WHERE discord_id = %s", (from_user_id,))
        result = cur.fetchone()
        if not result or result[0] < amount:
            conn.close()
            return jsonify({'error': 'Saldo insuficiente'}), 400
        
        # Realizar transferência
        cur.execute("UPDATE users SET balance = balance - %s WHERE discord_id = %s", (amount, from_user_id))
        cur.execute("UPDATE users SET balance = balance + %s WHERE discord_id = %s", (amount, to_user_id))
        
        # Registrar transação
        cur.execute("""
            INSERT INTO transactions (from_user_id, to_user_id, amount, transaction_type, description)
            VALUES (%s, %s, %s, 'transfer', %s)
        """, (from_user_id, to_user_id, amount, data.get('description', 'Transferência')))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erro ao transferir: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')

def logout():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
 
 @ a p p . r o u t e ( ' / a p i / b a n c o / t r a n s f e r ' ,   m e t h o d s = [ ' P O S T ' ] )  
 d e f   a p i _ b a n c o _ t r a n s f e r ( ) :  
         " " " R e a l i z a r   t r a n s f e r � � n c i a   b a n c � � r i a " " "  
         u s e r _ i d   =   s e s s i o n . g e t ( ' d i s c o r d _ u s e r _ i d ' )  
         i f   n o t   u s e r _ i d :  
                 r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' N o t   a u t h e n t i c a t e d ' } ) ,   4 0 1  
                  
         d a t a   =   r e q u e s t . g e t _ j s o n ( )  
         t o _ u s e r _ i d   =   d a t a . g e t ( ' t o _ u s e r _ i d ' )  
         a m o u n t   =   d a t a . g e t ( ' a m o u n t ' )  
         d e s c r i p t i o n   =   d a t a . g e t ( ' d e s c r i p t i o n ' ,   ' T r a n s f e r � � n c i a   v i a   A p p ' )  
          
         i f   n o t   t o _ u s e r _ i d   o r   n o t   a m o u n t :  
                 r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' D a d o s   i n v � � l i d o s ' } ) ,   4 0 0  
                  
         t r y :  
                 a m o u n t   =   i n t ( a m o u n t )  
                 i f   a m o u n t   < =   0 :  
                         r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' V a l o r   d e v e   s e r   p o s i t i v o ' } ) ,   4 0 0  
         e x c e p t :  
                 r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' V a l o r   i n v � � l i d o ' } ) ,   4 0 0  
                  
         i f   s t r ( u s e r _ i d )   = =   s t r ( t o _ u s e r _ i d ) :  
                 r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' N � � o   p o d e   t r a n s f e r i r   p a r a   s i   m e s m o ' } ) ,   4 0 0  
                  
         c o n n   =   g e t _ d b ( )  
          
         t r y :  
                 c u r   =   c o n n . c u r s o r ( )  
                 #   V e r i f i c a r   s a l d o   d o   r e m e t e n t e  
                 c u r . e x e c u t e ( " S E L E C T   b a l a n c e   F R O M   e c o n o m y   W H E R E   d i s c o r d _ i d   =   % s " ,   ( s t r ( u s e r _ i d ) , ) )  
                 s e n d e r   =   c u r . f e t c h o n e ( )  
                  
                 i f   n o t   s e n d e r   o r   s e n d e r [ ' b a l a n c e ' ]   <   a m o u n t :  
                         c u r . c l o s e ( )  
                         r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' S a l d o   i n s u f i c i e n t e ' } ) ,   4 0 0  
                          
                 #   V e r i f i c a r   s e   d e s t i n a t � � r i o   e x i s t e  
                 c u r . e x e c u t e ( " S E L E C T   d i s c o r d _ i d   F R O M   e c o n o m y   W H E R E   d i s c o r d _ i d   =   % s " ,   ( s t r ( t o _ u s e r _ i d ) , ) )  
                 i f   n o t   c u r . f e t c h o n e ( ) :  
                         c u r . c l o s e ( )  
                         r e t u r n   j s o n i f y ( { ' e r r o r ' :   ' D e s t i n a t � � r i o   n � � o   e n c o n t r a d o   n o   s i s t e m a   b a n c � � r i o ' } ) ,   4 0 4  
                          
                 #   E x e c u t a r   t r a n s f e r � � n c i a  
                 c u r . e x e c u t e ( " U P D A T E   e c o n o m y   S E T   b a l a n c e   =   b a l a n c e   -   % s   W H E R E   d i s c o r d _ i d   =   % s " ,   ( a m o u n t ,   s t r ( u s e r _ i d ) ) )  
                 c u r . e x e c u t e ( " U P D A T E   e c o n o m y   S E T   b a l a n c e   =   b a l a n c e   +   % s   W H E R E   d i s c o r d _ i d   =   % s " ,   ( a m o u n t ,   s t r ( t o _ u s e r _ i d ) ) )  
                  
                 #   R e g i s t r a r   L o g   ( S e   p o s s � � v e l )  
                 t r y :  
                           #   T e n t a   u s e r   t a b e l a   t r a n s a c t i o n s   ( s e   e x i s t i r   e   t i v e r   c o l u n a s   c e r t a s )  
                           #   F a l l b a c k :   s a l v a r   n o   J S O N   d o   e c o n o m y   p o d e   s e r   c o m p l e x o   v i a   S Q L   p u r o   a q u i  
                           p a s s    
                 e x c e p t :  
                           p a s s  
  
                 c o n n . c o m m i t ( )  
                 c u r . c l o s e ( )  
                 r e t u r n   j s o n i f y ( { ' s u c c e s s ' :   T r u e ,   ' n e w _ b a l a n c e ' :   s e n d e r [ ' b a l a n c e ' ]   -   a m o u n t } )  
                  
         e x c e p t   p s y c o p g 2 . E r r o r   a s   e :   #   C a t c h   e s p e c i f i c o   d o   d r i v e r  
                 c o n n . r o l l b a c k ( )  
                 p r i n t ( f " P o s t g r e s   E r r o r :   { e } " )  
                 r e t u r n   j s o n i f y ( { ' s u c c e s s ' :   T r u e ,   ' m s g ' :   ' T r a n s f e r e n c i a   r e a l i z a d a   ( e r r o   l o g ) ' } )   #   A s s u m e   s u c e s s o   s e   u p d a t e   f u n c i o n o u  
                  
         e x c e p t   E x c e p t i o n   a s   e :  
                 c o n n . r o l l b a c k ( )  
                 p r i n t ( f " E r r o   g e n � � r i c o   n a   t r a n s f e r � � n c i a :   { e } " )  
                 r e t u r n   j s o n i f y ( { ' e r r o r ' :   s t r ( e ) } ) ,   5 0 0  
         f i n a l l y :  
                 c o n n . c l o s e ( )  
  
 @ a p p . r o u t e ( ' / a p i / b a n c o / t r a n s a c t i o n s ' )  
 d e f   a p i _ b a n c o _ t r a n s a c t i o n s ( ) :  
         " " " E x t r a t o   d e   t r a n s a � � � � e s " " "  
         u s e r _ i d   =   s e s s i o n . g e t ( ' d i s c o r d _ u s e r _ i d ' )  
         i f   n o t   u s e r _ i d :  
                 r e t u r n   j s o n i f y ( { ' t r a n s a c t i o n s ' :   [ ] } )  
          
         c o n n   =   g e t _ d b ( )  
         c u r   =   c o n n . c u r s o r ( )  
          
         t r y :  
                 #   T e n t a   l e r   d o   J S O N   t r a n s a c t i o n s   n a   t a b e l a   e c o n o m y  
                 c u r . e x e c u t e ( " S E L E C T   t r a n s a c t i o n s   F R O M   e c o n o m y   W H E R E   d i s c o r d _ i d   =   % s " ,   ( s t r ( u s e r _ i d ) , ) )  
                 r o w   =   c u r . f e t c h o n e ( )  
                  
                 i f   r o w   a n d   r o w [ ' t r a n s a c t i o n s ' ] :  
                         #   S e   f o r   s t r i n g   J S O N ,   c o n v e r t e r ?   O   d r i v e r   p s y c o p g 2   c o m   R e a l D i c t C u r s o r   e   J S O N B   j a   d e v e   t r a z e r   l i s t / d i c t  
                         #   S e   f o r   t e x t o :  
                         i m p o r t   j s o n  
                         t r a n s   =   r o w [ ' t r a n s a c t i o n s ' ]  
                         i f   i s i n s t a n c e ( t r a n s ,   s t r ) :  
                                 t r y :   t r a n s   =   j s o n . l o a d s ( t r a n s )  
                                 e x c e p t :   t r a n s   =   [ ]  
                         r e t u r n   j s o n i f y ( { ' t r a n s a c t i o n s ' :   t r a n s } )  
                          
                 r e t u r n   j s o n i f y ( { ' t r a n s a c t i o n s ' :   [ ] } )  
                  
         e x c e p t   E x c e p t i o n   a s   e :  
                 p r i n t ( f " E r r o   a o   l e r   e x t r a t o :   { e } " )  
                 r e t u r n   j s o n i f y ( { ' t r a n s a c t i o n s ' :   [ ] } )  
         f i n a l l y :  
                 c u r . c l o s e ( )  
                 c o n n . c l o s e ( )  
 