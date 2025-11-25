import asyncio
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

try:
    import bot_main
except ImportError:
    print("ERRO: bot_main.py não encontrado.")
    sys.exit(1)

class TestRewards(unittest.IsolatedAsyncioTestCase):
    async def test_daily_bonus(self):
        print("\n--- TESTE DE DAILY BONUS ---")
        
        # Mock
        mock_channel = MagicMock()
        future = asyncio.Future()
        future.set_result(None)
        mock_channel.send.return_value = future
        bot_main.bot.get_channel = MagicMock(return_value=mock_channel)
        
        # Mock Economy
        bot_main.load_json = MagicMock(return_value={"123": {"balance": 0, "last_daily": None}})
        bot_main.save_json = MagicMock()
        bot_main.get_discord_id_by_gamertag = MagicMock(return_value=123)
        
        # Simula Login
        log_line = '20:00:00 | Player "Novato" is connected'
        await bot_main.parse_log_line(log_line)
        
        # Verifica se pagou
        self.assertTrue(bot_main.save_json.called)
        args = bot_main.save_json.call_args[0]
        balance = args[1]["123"]["balance"]
        self.assertEqual(balance, 500, "Deve pagar 500 de Daily")
        print("[SUCESSO] Daily Bonus pago corretamente.")

    async def test_salary(self):
        print("\n--- TESTE DE SALÁRIO ---")
        
        # Mock
        mock_channel = MagicMock()
        future = asyncio.Future()
        future.set_result(None)
        mock_channel.send.return_value = future
        bot_main.bot.get_channel = MagicMock(return_value=mock_channel)
        
        bot_main.get_discord_id_by_gamertag = MagicMock(return_value=123)
        bot_main.update_balance = MagicMock()
        
        # 1. Simula Login (1 hora atrás)
        bot_main.active_sessions["Trabalhador"] = time.time() - 3600 
        
        # 2. Simula Logout
        log_line = '21:00:00 | Player "Trabalhador" has been disconnected'
        await bot_main.parse_log_line(log_line)
        
        # Verifica Pagamento (Aprox 1000)
        self.assertTrue(bot_main.update_balance.called)
        args = bot_main.update_balance.call_args[0]
        amount = args[1]
        # Pode variar milissegundos, aceitamos 999-1001
        self.assertTrue(990 <= amount <= 1010, f"Salário incorreto: {amount}")
        print(f"[SUCESSO] Salário pago: {amount}")

if __name__ == "__main__":
    unittest.main()
