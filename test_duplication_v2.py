import time
import sys
import os

# Adiciona o diretório atual ao path para importar bot_main
sys.path.append(os.getcwd())

try:
    import bot_main
except ImportError:
    print("Erro ao importar bot_main. Verifique se o arquivo está no diretório.")
    sys.exit(1)

def test_duplication():
    print("--- Testando Lógica de Duplicação ---")
    
    # Reset tracker
    bot_main.pickup_tracker = {}

    print("Teste 1: Coleta Normal (IDs diferentes)")
    bot_main.check_duplication("Player1", "M4A1", "111")
    bot_main.check_duplication("Player1", "AKM", "222")
    
    if len(bot_main.pickup_tracker.get("Player1", [])) == 2:
        print("✅ OK: Coleta normal registrada.")
    else:
        print("❌ FALHA: Coleta normal não registrada corretamente.")

    print("\nTeste 2: Duplicação (Mesmo ID 3x)")
    # 1ª vez
    bot_main.check_duplication("Player2", "M4A1", "999")
    # 2ª vez
    bot_main.check_duplication("Player2", "M4A1", "999")
    # 3ª vez (Deve acionar)
    is_dupe = bot_main.check_duplication("Player2", "M4A1", "999")
    
    if is_dupe:
        print("✅ SUCESSO: Duplicação detectada na 3ª tentativa!")
    else:
        print("❌ FALHA: Duplicação NÃO detectada.")

    print("\nTeste 3: ID Desconhecido (Ignorar)")
    res = bot_main.check_duplication("Player3", "M4A1", "Unknown")
    if not res:
        print("✅ OK: ID 'Unknown' ignorado.")
    else:
        print("❌ FALHA: ID 'Unknown' causou falso positivo.")

def test_constants():
    print("\n--- Testando Constantes ---")
    try:
        print(f"Salário Hora: {bot_main.HOURLY_SALARY}")
        print(f"Bônus Diário: {bot_main.DAILY_BONUS}")
        print(f"Bônus 10h: {bot_main.BONUS_10H}")
        print("✅ Constantes encontradas.")
    except AttributeError as e:
        print(f"❌ FALHA: Constante faltando: {e}")

if __name__ == "__main__":
    test_constants()
    test_duplication()
