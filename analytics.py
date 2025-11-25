import json
import csv
import os
from datetime import datetime, timedelta

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- DATA EXPORT ---
def export_players_csv():
    """Exporta dados de jogadores para CSV"""
    players_db = load_json('players_db.json')
    
    with open('exports/players_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Nome', 'Kills', 'Deaths', 'K/D', 'Killstreak', 'Longest Shot'])
        
        for name, stats in players_db.items():
            kd = stats['kills'] if stats.get('deaths', 0) == 0 else round(stats['kills'] / stats['deaths'], 2)
            writer.writerow([
                name,
                stats.get('kills', 0),
                stats.get('deaths', 0),
                kd,
                stats.get('best_killstreak', 0),
                stats.get('longest_shot', 0)
            ])
    
    return 'exports/players_export.csv'

def export_economy_csv():
    """Exporta dados de economia para CSV"""
    economy = load_json('economy.json')
    links = load_json('links.json')
    
    # Reverse links for lookup
    id_to_gt = {str(v): k for k, v in links.items()}
    
    with open('exports/economy_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Discord ID', 'Gamertag', 'Balance', 'Total Transactions'])
        
        for user_id, data in economy.items():
            gamertag = id_to_gt.get(user_id, 'Unknown')
            writer.writerow([
                user_id,
                gamertag,
                data.get('balance', 0),
                len(data.get('transactions', []))
            ])
    
    return 'exports/economy_export.csv'

# --- WEEKLY REPORTS ---
def generate_weekly_report():
    """Gera relatório semanal de atividades"""
    players_db = load_json('players_db.json')
    economy = load_json('economy.json')
    
    # Calculate stats
    total_kills = sum(p.get('kills', 0) for p in players_db.values())
    total_deaths = sum(p.get('deaths', 0) for p in players_db.values())
    total_players = len(players_db)
    total_coins = sum(u.get('balance', 0) for u in economy.values())
    
    # Top players
    top_killers = sorted(
        [(name, stats.get('kills', 0)) for name, stats in players_db.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    report = {
        'date': datetime.now().isoformat(),
        'period': 'weekly',
        'stats': {
            'total_kills': total_kills,
            'total_deaths': total_deaths,
            'total_players': total_players,
            'total_coins': total_coins,
            'avg_kills_per_player': round(total_kills / total_players, 2) if total_players > 0 else 0
        },
        'top_killers': [{'name': n, 'kills': k} for n, k in top_killers]
    }
    
    # Save report
    os.makedirs('reports', exist_ok=True)
    filename = f'reports/weekly_report_{datetime.now().strftime("%Y%m%d")}.json'
    save_json(filename, report)
    
    return report

if __name__ == '__main__':
    # Create exports directory
    os.makedirs('exports', exist_ok=True)
    
    print("Generating exports...")
    players_file = export_players_csv()
    economy_file = export_economy_csv()
    
    print(f"✅ Players exported to: {players_file}")
    print(f"✅ Economy exported to: {economy_file}")
    
    print("\nGenerating weekly report...")
    report = generate_weekly_report()
    print(f"✅ Report generated with {report['stats']['total_kills']} total kills")
