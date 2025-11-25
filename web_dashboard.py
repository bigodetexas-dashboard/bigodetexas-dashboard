# Blueprint version of the original dashboard
import json, os
from datetime import datetime
from flask import Blueprint, jsonify, render_template, send_from_directory
from discord_oauth import login_required

# Blueprint definition
dashboard_bp = Blueprint('dashboard', __name__)

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# --- API ENDPOINTS ---
@dashboard_bp.route('/api/stats')
def api_stats():
    players_db = load_json('players_db.json')
    economy = load_json('economy.json')
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
    players_db = load_json('players_db.json')
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
    players_db = load_json('players_db.json')
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
    items = load_json('items.json')
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
    clans = load_json('clans.json')
    wars = clans.get('wars', {})
    active_wars = []
    for war_id, war_data in wars.items():
        if war_data.get('active'):
            active_wars.append({
                'id': war_id,
                'clan1': war_data['clan1'],
                'clan2': war_data['clan2'],
                'score': war_data['score'],
                'start_time': war_data.get('start_time', '')
            })
    return jsonify(active_wars)

@dashboard_bp.route('/api/heatmap')
def api_heatmap():
    heatmap_data = load_json('heatmap_data.json')
    return jsonify(heatmap_data.get('points', []))

@dashboard_bp.route('/api/player/<name>')
@login_required
def api_player(name):
    players_db = load_json('players_db.json')
    economy = load_json('economy.json')
    if name not in players_db:
        return jsonify({'error': 'Player not found'}), 404
    stats = players_db[name]
    kd = stats['kills'] if stats.get('deaths', 0) == 0 else round(stats['kills'] / stats['deaths'], 2)
    links = load_json('links.json')
    discord_id = None
    for gt, did in links.items():
        if gt.lower() == name.lower():
            discord_id = str(did)
            break
    balance = 0
    achievements = []
    if discord_id and discord_id in economy:
        balance = economy[discord_id].get('balance', 0)
        achievements = economy[discord_id].get('achievements', {})
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
    return render_template('shop.html')

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
    players_db = load_json('players_db.json')
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
    players_db = load_json('players_db.json')
    economy = load_json('economy.json')
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
