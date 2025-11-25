import asyncio
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.getcwd())

try:
    import bot_main
except ImportError:
    print("ERRO: bot_main.py não encontrado.")
    sys.exit(1)

class TestConstructionBan(unittest.IsolatedAsyncioTestCase):
    async def test_garden_plot_ban(self):
        print("\n--- TESTE DE BANIMENTO (GARDEN PLOT) ---")
        
        # Mock das dependências
        mock_channel = MagicMock()
        # Configura o send para retornar um Future (awaitable)
        future = asyncio.Future()
        future.set_result(None)
        mock_channel.send.return_value = future
        
        bot_main.bot.get_channel = MagicMock(return_value=mock_channel)
        bot_main.ban_player = MagicMock()
        bot_main.load_json = MagicMock(return_value={"killfeed_channel": 123})
        
        # Log simulado de construção
        # Formato exato precisa ser verificado. Geralmente é:
        # 20:00:00 | Player "Glitcher" (id=...) placed "GardenPlot" at <100, 100, 100>
        log_line = '20:00:00 | Player "Glitcher" (id=Unknown) placed "GardenPlot" at <1000, 100, 1000>'

        print(f"Processando linha: {log_line}")
        
        # Executa o parser
        await bot_main.parse_log_line(log_line)
        
        # Verifica se chamou a função de banir
        if bot_main.ban_player.called:
            args = bot_main.ban_player.call_args[0]
            print(f"[SUCESSO] Função ban_player chamada para: {args[0]}")
            print(f"           Motivo: {args[1]}")
        else:
            print("[ERRO] Função ban_player NÃO foi chamada.")

if __name__ == "__main__":
    unittest.main()
