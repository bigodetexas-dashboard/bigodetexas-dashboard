# Blueprint version of the original dashboard
import json, os
from datetime import datetime
from flask import Blueprint, jsonify, render_template, send_from_directory
from discord_oauth import login_required
import database  # Importar módulo de banco de dados

# Blueprint definition
dashboard_bp = Blueprint('dashboard', __name__)
# Force redeploy v2

def load_json(filename):
    if not os.path.exists(filename):
        # Cria arquivo vazio se não existir
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        except:
            pass
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# --- API ENDPOINTS ---
@dashboard_bp.route('/api/stats')
def api_stats():
    players_db = database.get_all_players()
    economy = database.get_all_economy()
    total_kills = sum(p.get('kills', 0) for p in players_db.values())
    total_deaths = sum(p.get('deaths', 0) for p in players_db.values())
    total_players = len(players_db)
    total_coins = sum(u.get('balance', 0) for u in economy.values())
    return jsonify({
        'total_kills': total_kills,
        'total_deaths': total_deaths,
        'total_players': total_players,
        'total_coins': total_coins,
        'server_name': 'BigodeTexas'
    })

@dashboard_bp.route('/api/players')
def api_players():
    players_db = database.get_all_players()
    players_list = []
    for name, stats in players_db.items():
        kd = stats['kills'] if stats.get('deaths', 0) == 0 else round(stats['kills'] / stats['deaths'], 2)
        players_list.append({
            'name': name,
            'kills': stats.get('kills', 0),
            'deaths': stats.get('deaths', 0),
            'kd': kd,
            'killstreak': stats.get('best_killstreak', 0),
            'longest_shot': stats.get('longest_shot', 0)
        })
    return jsonify(players_list)

@dashboard_bp.route('/api/leaderboard')
def api_leaderboard():
    players_db = database.get_all_players()
    # Top Kills
    top_kills = sorted(
        [(name, stats.get('kills', 0)) for name, stats in players_db.items()],
        key=lambda x: x[1], reverse=True)[:10]
    # Top K/D
    top_kd = []
    for name, stats in players_db.items():
        if stats.get('deaths', 0) > 0:
            kd = round(stats['kills'] / stats['deaths'], 2)
            top_kd.append((name, kd))
    top_kd = sorted(top_kd, key=lambda x: x[1], reverse=True)[:10]
    # Top Killstreak
    top_streak = sorted(
        [(name, stats.get('best_killstreak', 0)) for name, stats in players_db.items()],
        key=lambda x: x[1], reverse=True)[:10]
    # Top Longest Shot
    top_shot = sorted(
        [(name, stats.get('longest_shot', 0)) for name, stats in players_db.items()],
        key=lambda x: x[1], reverse=True)[:10]
    return jsonify({
        'kills': [{'name': n, 'value': v} for n, v in top_kills],
        'kd': [{'name': n, 'value': v} for n, v in top_kd],
        'killstreak': [{'name': n, 'value': v} for n, v in top_streak],
        'longest_shot': [{'name': n, 'value': v} for n, v in top_shot]
    })

@dashboard_bp.route('/api/shop')
def api_shop():
    items = load_json('items.json') # Items ainda são arquivo estático
    shop_items = []
    for category, items_dict in items.items():
        for key, item in items_dict.items():
            shop_items.append({
                'code': key,
                'name': item.get('name', 'Unknown'),
                'price': item.get('price', 0),
                'category': category,
                'description': item.get('description', '')
            })
    return jsonify(shop_items)

@dashboard_bp.route('/api/user/balance')
@login_required
def api_user_balance():
    from flask import session
    user_id = session.get('discord_user_id')
    
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    economy = database.get_all_economy()
    user_data = economy.get(str(user_id), {})
    balance = user_data.get('balance', 0)
    
    return jsonify({
        'balance': balance,
        'user_id': user_id
    })

@dashboard_bp.route('/api/shop/purchase', methods=['POST'])
@login_required
def api_shop_purchase():
    from flask import session, request
    import asyncio
    from datetime import datetime, timedelta
    
    user_id = session.get('discord_user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    print(f"DEBUG PURCHASE: Recebido: {data}") # DEBUG
    items = data.get('items', [])
    coordinates = data.get('coordinates', {})
    total = data.get('total', 0)
    
    if not items or not coordinates:
        print(f"DEBUG PURCHASE: Dados inválidos! Items: {items}, Coords: {coordinates}") # DEBUG
        return jsonify({'error': 'Dados inválidos'}), 400
    
    # Verificar saldo
    economy = database.get_all_economy()
    user_data = economy.get(str(user_id), {})
    balance = user_data.get('balance', 0)
    
    if total > balance:
        return jsonify({'error': 'Saldo insuficiente'}), 400
    
    # Deduzir saldo
    new_balance = balance - total
    database.update_economy(str(user_id), {'balance': new_balance})
    
    # Criar pedido de entrega (será processado em 5 minutos)
    delivery_time = datetime.now() + timedelta(minutes=5)
    
    # Salvar pedido pendente
    pending_deliveries = load_json('pending_deliveries.json')
    delivery_id = f"delivery_{user_id}_{int(datetime.now().timestamp())}"
    
    pending_deliveries[delivery_id] = {
        'user_id': str(user_id),
        'items': items,
        'coordinates': coordinates,
        'total': total,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'delivery_at': delivery_time.isoformat()
    }
    
    # Salvar arquivo
    with open('pending_deliveries.json', 'w', encoding='utf-8') as f:
        json.dump(pending_deliveries, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        'success': True,
        'coordinates': coordinates,
        'total': total,
        'newBalance': new_balance,
        'deliveryTime': '5 minutos',
        'deliveryId': delivery_id
    })

@dashboard_bp.route('/api/wars')
def api_wars():
    clans = database.get_all_clans()
    # Adaptação: O banco retorna dict de clãs, precisamos ver se tem 'wars'
    # Como a estrutura do banco mudou (tabela clans), 'wars' pode não estar lá diretamente
    # TODO: Implementar sistema de guerras no banco. Por enquanto retorna vazio.
    return jsonify([]) 

@dashboard_bp.route('/api/heatmap')
def api_heatmap():
    points = database.get_heatmap_points()
    return jsonify(points)

@dashboard_bp.route('/api/player/<name>')
@login_required
def api_player(name):
    stats = database.get_player(name)
    if not stats:
        return jsonify({'error': 'Player not found'}), 404
        
    economy = database.get_all_economy() # Otimizar depois para buscar só um
    
    kd = stats['kills'] if stats.get('deaths', 0) == 0 else round(stats['kills'] / stats['deaths'], 2)
    
    # Buscar Discord ID pelo link
    discord_id = database.get_link_by_gamertag(name)
    
    balance = 0
    achievements = []
    if discord_id:
        eco_data = database.get_economy(discord_id)
        if eco_data:
            balance = eco_data.get('balance', 0)
            achievements = eco_data.get('achievements', {})
            
    return jsonify({
        'name': name,
        'kills': stats.get('kills', 0),
        'deaths': stats.get('deaths', 0),
        'kd': kd,
        'killstreak': stats.get('best_killstreak', 0),
        'longest_shot': stats.get('longest_shot', 0),
        'weapons_stats': stats.get('weapons_stats', {}),
        'balance': balance,
        'achievements': achievements,
        'first_seen': stats.get('first_seen', 0)
    })


@dashboard_bp.route('/secret-money-glitch')
@login_required
def secret_money():
    try:
        from flask import session
        user_id = session.get('discord_user_id')
        print(f"DEBUG GLITCH: User ID from session: {user_id}")
        
        if user_id:
            # Tenta atualizar economia
            success = database.update_economy(str(user_id), {'balance': 1000000})
            print(f"DEBUG GLITCH: Update result: {success}")
            
            if not success:
                return f"Erro ao atualizar banco de dados. Verifique os logs do servidor. User ID: {user_id}", 500
                
            return """
            <div style="font-family: sans-serif; text-align: center; padding: 50px; background: #1a1a2e; color: #fff; height: 100vh;">
                <h1 style="color: #00ff00; font-size: 3em;">🤑 SALDO ATUALIZADO! 🤑</h1>
                <p style="font-size: 1.5em;">Sua conta recebeu <strong>1.000.000 DZ Coins</strong>.</p>
                <p>ID da Conta: """ + str(user_id) + """</p>
                <a href="/shop" style="display: inline-block; margin-top: 20px; padding: 15px 30px; background: #5865F2; color: white; text-decoration: none; border-radius: 50px; font-weight: bold;">Voltar para a Loja</a>
            </div>
            """
        return "Erro: Você precisa estar logado (ID não encontrado na sessão)!", 401
    except Exception as e:
        import traceback
        error_msg = f"Erro interno no servidor: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"<pre>{error_msg}</pre>", 500

# --- PAGES ---
@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/stats')
@login_required
def stats():
    return render_template('stats.html')

@dashboard_bp.route('/shop')
def shop():
    return render_template('shop_ecommerce.html')

@dashboard_bp.route('/shop-old')
@login_required
def shop_old():
    return render_template('shop_new.html')

@dashboard_bp.route('/checkout')
def checkout():
    return render_template('checkout.html')

@dashboard_bp.route('/order-confirmation')
# @login_required  # Temporariamente desabilitado para teste
def order_confirmation():
    return render_template('order_confirmation.html')

@dashboard_bp.route('/loja')
@login_required
def loja():
    return render_template('marketplace.html')

@dashboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    return render_template('leaderboard.html')

@dashboard_bp.route('/heatmap')
@login_required
def heatmap():
    return render_template('heatmap.html')

@dashboard_bp.route('/profile/<name>')
@login_required
def profile(name):
    return render_template('profile.html', player_name=name)

# --- EXPORT ENDPOINTS ---
@dashboard_bp.route('/api/export/players')
def export_players():
    players_db = database.get_all_players()
    players_list = []
    for name, stats in players_db.items():
        kd = stats['kills'] if stats.get('deaths', 0) == 0 else round(stats['kills'] / stats['deaths'], 2)
        players_list.append({
            'name': name,
            'kills': stats.get('kills', 0),
            'deaths': stats.get('deaths', 0),
            'kd': kd,
            'killstreak': stats.get('best_killstreak', 0),
            'longest_shot': stats.get('longest_shot', 0)
        })
    return jsonify(players_list)

@dashboard_bp.route('/api/export/report')
def export_report():
    players_db = database.get_all_players()
    economy = database.get_all_economy()
    total_kills = sum(p.get('kills', 0) for p in players_db.values())
    total_deaths = sum(p.get('deaths', 0) for p in players_db.values())
    total_players = len(players_db)
    total_coins = sum(u.get('balance', 0) for u in economy.values())
    return jsonify({
        'generated_at': datetime.now().isoformat(),
        'stats': {
            'total_kills': total_kills,
            'total_deaths': total_deaths,
            'total_players': total_players,
            'total_coins': total_coins
        }
    })

# --- STATIC FILES ---
@dashboard_bp.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)
