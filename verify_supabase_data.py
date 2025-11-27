"""
Script para Verificar Dados no Supabase
Exibe o conteudo de todas as tabelas do banco de dados
"""
import database
import json

def print_separator(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_json_field(data, field_name):
    """Imprime campo JSON de forma legivel"""
    value = data.get(field_name)
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except:
            pass
    return value

# JOGADORES
print_separator("TABELA: PLAYERS")
players = database.get_all_players()
print(f"\nTotal de jogadores: {len(players)}\n")

if players:
    for i, (gamertag, data) in enumerate(players.items(), 1):
        print(f"{i}. {gamertag}")
        print(f"   Kills: {data.get('kills', 0)} | Deaths: {data.get('deaths', 0)} | K/D: {data.get('kills', 0) / max(data.get('deaths', 1), 1):.2f}")
        print(f"   Best Killstreak: {data.get('best_killstreak', 0)} | Longest Shot: {data.get('longest_shot', 0)}m")
        
        weapons = print_json_field(data, 'weapons_stats')
        if weapons:
            print(f"   Armas: {', '.join([f'{k}({v})' for k, v in weapons.items()])}")
        print()
else:
    print("Nenhum jogador encontrado.")

# ECONOMIA
print_separator("TABELA: ECONOMY")
economy = database.get_all_economy()
print(f"\nTotal de contas: {len(economy)}\n")

if economy:
    for i, (discord_id, data) in enumerate(economy.items(), 1):
        print(f"{i}. Discord ID: {discord_id}")
        print(f"   Gamertag: {data.get('gamertag', 'N/A')}")
        print(f"   Saldo: {data.get('balance', 0)} DZ Coins")
        
        inventory = print_json_field(data, 'inventory')
        if inventory:
            print(f"   Inventario: {len(inventory)} itens")
        
        transactions = print_json_field(data, 'transactions')
        if transactions:
            print(f"   Transacoes: {len(transactions)}")
        print()
else:
    print("Nenhuma conta de economia encontrada.")

# LINKS
print_separator("TABELA: LINKS")
links = database.get_all_links()
print(f"\nTotal de links: {len(links)}\n")

if links:
    for i, (discord_id, gamertag) in enumerate(links.items(), 1):
        print(f"{i}. Discord ID: {discord_id} <-> Gamertag: {gamertag}")
else:
    print("Nenhum link encontrado.")

# CLANS
print_separator("TABELA: CLANS")
clans = database.get_all_clans()
print(f"\nTotal de clas: {len(clans)}\n")

if clans:
    for i, (clan_name, data) in enumerate(clans.items(), 1):
        print(f"{i}. {clan_name}")
        print(f"   Lider: {data.get('leader', 'N/A')}")
        
        members = print_json_field(data, 'members')
        if members:
            print(f"   Membros: {len(members)}")
        
        print(f"   Total Kills: {data.get('total_kills', 0)} | Total Deaths: {data.get('total_deaths', 0)}")
        print()
else:
    print("Nenhum cla encontrado.")

# RESUMO
print_separator("RESUMO")
print(f"""
Total de Registros no Supabase:
  - Jogadores: {len(players)}
  - Contas de Economia: {len(economy)}
  - Links Discord-Gamertag: {len(links)}
  - Clas: {len(clans)}

Status: Banco de dados operacional!
""")
print("="*70 + "\n")
