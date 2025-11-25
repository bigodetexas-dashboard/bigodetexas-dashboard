from flask import Flask, render_template, jsonify, send_from_directory
from datetime import datetime
import json
import os

app = Flask(__name__)

# Helper functions
def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# --- API ENDPOINTS ---
@app.route('/api/stats')
def api_stats():
    """Estatísticas gerais do servidor"""
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

@app.route('/api/players')
def api_players():
    """Lista de jogadores com stats"""
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

@app.route('/api/leaderboard')
def api_leaderboard():
    """Top players por categoria"""
    players_db = load_json('players_db.json')
    
    # Top Kills
    top_kills = sorted(
        [(name, stats.get('kills', 0)) for name, stats in players_db.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
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
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Top Longest Shot
    top_shot = sorted(
        [(name, stats.get('longest_shot', 0)) for name, stats in players_db.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    return jsonify({
        'kills': [{'name': n, 'value': v} for n, v in top_kills],
        'kd': [{'name': n, 'value': v} for n, v in top_kd],
        'killstreak': [{'name': n, 'value': v} for n, v in top_streak],
        'longest_shot': [{'name': n, 'value': v} for n, v in top_shot]
    })

# --- PAGES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/shop')
def shop():
    return render_template('shop.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/heatmap')
def heatmap():
    return render_template('heatmap.html')

@app.route('/profile/<name>')
def profile(name):
    return render_template('profile.html', player_name=name)

# --- STATIC FILES ---
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("BigodeTexas Dashboard - Versao Simplificada")
    print("="*60)
    print("\nAcesse: http://localhost:5000")
    print("Pressione CTRL+C para parar\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
