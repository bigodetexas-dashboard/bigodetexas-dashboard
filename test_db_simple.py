"""
Teste de Integracao PostgreSQL - Versao Simplificada
Verifica se as funcoes principais do bot funcionam com o banco de dados
"""
import database
import sys

print("\n" + "="*60)
print("TESTES DE INTEGRACAO POSTGRESQL")
print("="*60 + "\n")

# TESTE 1: Conexao
print("TESTE 1: Conexao com Banco de Dados")
print("-" * 60)
conn = database.get_connection()
if conn:
    print("[OK] Conexao estabelecida com sucesso!")
    conn.close()
else:
    print("[ERRO] Falha na conexao!")
    sys.exit(1)

# TESTE 2: Jogadores
print("\nTESTE 2: Funcoes de Jogador")
print("-" * 60)
player = database.get_player("Alaansl93")
if player:
    print(f"[OK] Jogador encontrado: {player['gamertag']}")
    print(f"     Kills: {player['kills']}, Deaths: {player['deaths']}")
else:
    print("[ERRO] Falha ao buscar jogador")
    sys.exit(1)

all_players = database.get_all_players()
print(f"[OK] Total de jogadores no banco: {len(all_players)}")

# TESTE 3: Economia
print("\nTESTE 3: Funcoes de Economia")
print("-" * 60)
test_discord_id = "999999999"
eco = database.get_economy(test_discord_id)

if not eco:
    print("[INFO] Economia nao existe, criando nova...")
    test_data = {
        "discord_id": test_discord_id,
        "balance": 1000,
        "gamertag": "TestPlayer",
        "inventory": {},
        "transactions": []
    }
    if database.save_economy(test_discord_id, test_data):
        print("[OK] Economia criada com sucesso!")
    else:
        print("[ERRO] Falha ao criar economia")
        sys.exit(1)
else:
    print(f"[OK] Economia encontrada: Discord ID {test_discord_id}")
    print(f"     Saldo: {eco.get('balance', 0)} DZ Coins")

# TESTE 4: Links
print("\nTESTE 4: Funcoes de Link Discord-Gamertag")
print("-" * 60)
all_links = database.get_all_links()
print(f"[OK] Total de links no banco: {len(all_links)}")

if all_links:
    first_discord_id = list(all_links.keys())[0]
    gamertag = database.get_link_by_discord(first_discord_id)
    print(f"[OK] Link encontrado: Discord {first_discord_id} -> {gamertag}")

# TESTE 5: Clans
print("\nTESTE 5: Funcoes de Cla")
print("-" * 60)
all_clans = database.get_all_clans()
print(f"[OK] Total de clas no banco: {len(all_clans)}")

test_clan = {
    "leader": "123456789",
    "members": ["987654321"],
    "total_kills": 0,
    "total_deaths": 0
}

if database.save_clan("TEST_CLAN", test_clan):
    print("[OK] Cla de teste criado com sucesso!")
    
    clan = database.get_clan("TEST_CLAN")
    if clan:
        print(f"[OK] Cla recuperado: {clan['clan_name']}")
        print(f"     Lider: {clan['leader']}")
    else:
        print("[ERRO] Falha ao recuperar cla")
        sys.exit(1)
else:
    print("[ERRO] Falha ao criar cla")
    sys.exit(1)

# RESUMO
print("\n" + "="*60)
print("RESUMO DOS TESTES")
print("="*60)
print("[OK] Conexao")
print("[OK] Jogadores")
print("[OK] Economia")
print("[OK] Links")
print("[OK] Clas")
print("\nTODOS OS TESTES PASSARAM COM SUCESSO!")
print("="*60 + "\n")
