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

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
