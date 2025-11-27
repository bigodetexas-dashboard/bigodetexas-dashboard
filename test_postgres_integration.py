"""
Teste de Integração PostgreSQL
Verifica se as funções principais do bot funcionam com o banco de dados
"""
import database
import sys

def test_database_connection():
    """Testa conexão com banco"""
    print("=" * 60)
    print("TESTE 1: Conexão com Banco de Dados")
    print("=" * 60)
    
    conn = database.get_connection()
    if conn:
        print("✅ Conexão estabelecida com sucesso!")
        conn.close()
        return True
    else:
        print("❌ Falha na conexão!")
        return False

def test_player_functions():
    """Testa funções de jogador"""
    print("\n" + "=" * 60)
    print("TESTE 2: Funções de Jogador")
    print("=" * 60)
    
    # Buscar jogador existente
    player = database.get_player("Alaansl93")
    if player:
        print(f"✅ Jogador encontrado: {player['gamertag']}")
        print(f"   Kills: {player['kills']}, Deaths: {player['deaths']}")
    else:
        print("❌ Falha ao buscar jogador")
        return False
    
    # Listar todos os jogadores
    all_players = database.get_all_players()
    print(f"✅ Total de jogadores no banco: {len(all_players)}")
    
    return True

def test_economy_functions():
    """Testa funções de economia"""
    print("\n" + "=" * 60)
    print("TESTE 3: Funções de Economia")
    print("=" * 60)
    
    # Criar/buscar economia de teste
    test_discord_id = "123456789"
    
    eco = database.get_economy(test_discord_id)
    if eco:
        print(f"✅ Economia encontrada: Discord ID {test_discord_id}")
        print(f"   Saldo: {eco.get('balance', 0)} DZ Coins")
    else:
        print("ℹ️  Economia não existe, criando nova...")
        test_data = {
            "discord_id": test_discord_id,
            "balance": 1000,
            "gamertag": "TestPlayer",
            "inventory": {},
            "transactions": []
        }
        if database.save_economy(test_discord_id, test_data):
            print("✅ Economia criada com sucesso!")
        else:
            print("❌ Falha ao criar economia")
            return False
    
    return True

def test_link_functions():
    """Testa funções de link"""
    print("\n" + "=" * 60)
    print("TESTE 4: Funções de Link Discord-Gamertag")
    print("=" * 60)
    
    # Buscar link existente
    all_links = database.get_all_links()
    print(f"✅ Total de links no banco: {len(all_links)}")
    
    if all_links:
        first_discord_id = list(all_links.keys())[0]
        gamertag = database.get_link_by_discord(first_discord_id)
        print(f"✅ Link encontrado: Discord {first_discord_id} -> {gamertag}")
    
    return True

def test_clan_functions():
    """Testa funções de clã"""
    print("\n" + "=" * 60)
    print("TESTE 5: Funções de Clã")
    print("=" * 60)
    
    all_clans = database.get_all_clans()
    print(f"✅ Total de clãs no banco: {len(all_clans)}")
    
    # Criar clã de teste
    test_clan = {
        "leader": "123456789",
        "members": ["987654321"],
        "total_kills": 0,
        "total_deaths": 0
    }
    
    if database.save_clan("TEST_CLAN", test_clan):
        print("✅ Clã de teste criado com sucesso!")
        
        # Buscar clã criado
        clan = database.get_clan("TEST_CLAN")
        if clan:
            print(f"✅ Clã recuperado: {clan['clan_name']}")
            print(f"   Líder: {clan['leader']}")
        else:
            print("❌ Falha ao recuperar clã")
            return False
    else:
        print("❌ Falha ao criar clã")
        return False
    
    return True

def main():
    """Executa todos os testes"""
    print("\nINICIANDO TESTES DE INTEGRACAO POSTGRESQL\n")
    
    tests = [
        ("Conexão", test_database_connection),
        ("Jogadores", test_player_functions),
        ("Economia", test_economy_functions),
        ("Links", test_link_functions),
        ("Clãs", test_clan_functions)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ ERRO no teste {name}: {e}")
            results.append((name, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
