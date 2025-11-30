"""
Script de Teste - Heatmap System
Valida todas as funcionalidades implementadas
"""

import requests
import json

API_BASE = 'http://localhost:5001'

def test_heatmap_api():
    """Testa a API /api/heatmap"""
    print("\n🧪 Testando /api/heatmap...")
    
    try:
        response = requests.get(f'{API_BASE}/api/heatmap?range=all&grid=50')
        data = response.json()
        
        if data['success']:
            print(f"✅ API funcionando!")
            print(f"   - Pontos retornados: {len(data['points'])}")
            print(f"   - Total de eventos: {data['total_events']}")
            print(f"   - Range: {data['range']}")
            print(f"   - Grid size: {data['grid_size']}")
            return True
        else:
            print(f"❌ API retornou erro: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Erro ao chamar API: {e}")
        return False

def test_parse_log_api():
    """Testa a API /api/parse_log"""
    print("\n🧪 Testando /api/parse_log...")
    
    # Log de teste (formato 1)
    test_log = """
PlayerKill: Killer=TestKiller, Victim=TestVictim, Pos=<7500, 0, 7500>, Weapon=AKM, Distance=50m
PlayerKill: Killer=Sniper, Victim=Runner, Pos=<4500, 0, 10000>, Weapon=Mosin, Distance=300m
Kill: John killed Mike at [6000, 0, 8000] with M4A1
    """
    
    try:
        response = requests.post(
            f'{API_BASE}/api/parse_log',
            json={'text': test_log, 'source': 'test'},
            headers={'Content-Type': 'application/json'}
        )
        
        data = response.json()
        
        if data['success']:
            print(f"✅ Parser funcionando!")
            print(f"   - Eventos parseados: {data['events_parsed']}")
            print(f"   - Eventos salvos: {data['events_saved']}")
            return True
        else:
            print(f"❌ Parser retornou erro: {data.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Erro ao chamar parser: {e}")
        return False

def test_database():
    """Testa se o banco de dados existe e tem dados"""
    print("\n🧪 Testando banco de dados...")
    
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    try:
        from database import get_heatmap_data
        from datetime import datetime, timedelta
        
        # Buscar dados dos últimos 30 dias
        since = datetime.now() - timedelta(days=30)
        data = get_heatmap_data(since, grid_size=50)
        
        print(f"✅ Banco de dados funcionando!")
        print(f"   - Pontos agregados: {len(data)}")
        print(f"   - Total de eventos: {sum(p['count'] for p in data)}")
        
        if data:
            print(f"   - Exemplo de ponto: X={data[0]['x']}, Z={data[0]['z']}, Count={data[0]['count']}")
        
        return True
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def test_parser_function():
    """Testa a função parse_rpt_line diretamente"""
    print("\n🧪 Testando função parse_rpt_line...")
    
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    try:
        from database import parse_rpt_line
        
        # Testar formato 1
        line1 = "PlayerKill: Killer=John, Victim=Mike, Pos=<4500, 0, 10000>, Weapon=M4A1, Distance=120m"
        event1 = parse_rpt_line(line1)
        
        if event1:
            print(f"✅ Formato 1 reconhecido!")
            print(f"   - Killer: {event1['killer_name']}")
            print(f"   - Victim: {event1['victim_name']}")
            print(f"   - Coords: X={event1['game_x']}, Z={event1['game_z']}")
            print(f"   - Weapon: {event1['weapon']}")
        else:
            print(f"❌ Formato 1 não reconhecido")
            return False
        
        # Testar formato 2
        line2 = "Kill: Sniper killed Runner at [7500, 0, 7500] with Mosin"
        event2 = parse_rpt_line(line2)
        
        if event2:
            print(f"✅ Formato 2 reconhecido!")
            print(f"   - Killer: {event2['killer_name']}")
            print(f"   - Victim: {event2['victim_name']}")
            print(f"   - Coords: X={event2['game_x']}, Z={event2['game_z']}")
        else:
            print(f"❌ Formato 2 não reconhecido")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erro ao testar parser: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("=" * 60)
    print("🚀 TESTE COMPLETO DO SISTEMA HEATMAP")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Banco de dados
    results.append(("Banco de Dados", test_database()))
    
    # Teste 2: Função de parser
    results.append(("Parser de Logs", test_parser_function()))
    
    # Teste 3: API Heatmap
    results.append(("API /api/heatmap", test_heatmap_api()))
    
    # Teste 4: API Parse Log
    results.append(("API /api/parse_log", test_parse_log_api()))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\nSistema pronto para uso. Acesse:")
        print(f"   {API_BASE}/heatmap")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")

if __name__ == "__main__":
    main()
