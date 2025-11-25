import asyncio
import unittest
from unittest.mock import MagicMock
import sys
import os

# Adiciona diretório atual
sys.path.append(os.getcwd())

try:
    import bot_main
except ImportError:
    print("ERRO: bot_main.py não encontrado.")
    sys.exit(1)

class TestKillfeedLive(unittest.IsolatedAsyncioTestCase):
    async def test_real_log_examples(self):
        print("\n--- TESTE DE KILLFEED (LOGS REAIS) ---")
        
        # Mock do bot
        bot_main.bot.fetch_user = MagicMock()
        bot_main.bot.get_channel = MagicMock()
        
        # Exemplos de Logs (Baseados no padrão DayZ Xbox Nitrado)
        logs = [
            # 1. Kill com Arma
            '20:15:30 | Player "Survivor" (id=Unknown) killed by Player "Bandit" (id=Unknown) with M4A1 at <4500, 100, 10200>',
            # 2. Kill com Punhos (Zombie ou Player) - Às vezes o formato muda, mas vamos testar o padrão
            '20:16:00 | Player "Noob" (id=Unknown) killed by Player "Pro" (id=Unknown) with Fists at <12000, 50, 9000>',
            # 3. Morte Natural (Zumbi/Queda)
            '20:17:00 | Player "Explorer" (id=Unknown) died at <5000, 10, 5000>',
            # 4. Suicídio (Deve ignorar)
            '20:18:00 | Player "Sad" (id=Unknown) committed suicide'
        ]

        print(f"Testando {len(logs)} linhas de log...")

        for line in logs:
            print(f"\nProcessando: {line}")
            embed = await bot_main.parse_log_line(line)
            
            if "committed suicide" in line:
                if embed is None:
                    print("[SUCESSO] Suicídio ignorado corretamente.")
                else:
                    print("[ERRO] Suicídio não deveria gerar embed.")
            
            elif "died" in line and "killed by" not in line:
                if embed and "morreu" in embed.description:
                    print(f"[SUCESSO] Morte Natural detectada.")
                else:
                    print("[ERRO] Morte natural não detectada.")

            elif "killed by" in line:
                if embed and embed.title == "🤠 KILLFEED TEXAS":
                    # Verifica campos
                    fields = {f.name: f.value for f in embed.fields}
                    killer_field = fields.get("🔫 Pistoleiro (Assassino)")
                    victim_field = fields.get("⚰️ Finado (Vítima)")
                    
                    if "Bandit" in killer_field or "Pro" in killer_field:
                        print(f"[SUCESSO] Kill detectada corretamente!")
                        print(f"   Assassino: {killer_field.split('**')[1]}")
                        print(f"   Vítima: {victim_field.split('**')[1]}")
                    else:
                        print(f"[ERRO] Nomes incorretos no embed.")
                else:
                    print("[ERRO] Kill não gerou embed correto.")

if __name__ == "__main__":
    unittest.main()
