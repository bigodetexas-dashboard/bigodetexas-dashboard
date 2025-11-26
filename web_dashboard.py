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

@dashboard_bp.route('/api/user/balance')
@login_required
def api_user_balance():
    """Returns the logged-in user's balance"""
    from flask import session
    discord_id = session.get('discord_id')
    
    if not discord_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    eco_data = database.get_economy(str(discord_id))
    balance = eco_data.get('balance', 0) if eco_data else 0
    
    return jsonify({
        'balance': balance,
        'discord_id': str(discord_id)
    })


# --- PAGES ---
@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/stats')
@login_required
def stats():
    return render_template('stats.html')

@dashboard_bp.route('/shop')
@login_required
def shop():
    return render_template('store.html')

@dashboard_bp.route('/loja')
@login_required
def loja():
    return render_template('loja.html')

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
