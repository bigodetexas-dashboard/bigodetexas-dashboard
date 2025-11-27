import os
from dotenv import load_dotenv
import database

load_dotenv()

print("Testando conexão com banco de dados...")
print(f"DATABASE_URL configurado: {'Sim' if os.getenv('DATABASE_URL') else 'Não'}")

# Testar conexão
players = database.get_all_players()
print(f"\nTotal de jogadores no banco: {len(players)}")

if players:
    print("\nPrimeiros 5 jogadores:")
    for i, (name, stats) in enumerate(list(players.items())[:5]):
        print(f"{i+1}. {name}: {stats.get('kills', 0)} kills, {stats.get('deaths', 0)} deaths")
else:
    print("\n⚠️ AVISO: Nenhum jogador encontrado no banco!")
    print("Isso pode explicar por que o leaderboard está vazio.")

# Testar economia
economy = database.get_all_economy()
print(f"\nTotal de usuários com economia: {len(economy)}")

print("\n✅ Teste concluído!")
