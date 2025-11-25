# -*- coding: utf-8 -*-
"""
Script de Teste - Novas Funcionalidades BigodeTexas Bot
========================================================

Testa os 3 novos sistemas implementados:
1. Leaderboard
2. Admin Spawner
3. Editor de Gameplay

Uso: python test_new_features.py
"""

import discord
from discord.ext import commands
import asyncio
import os
import sys
from dotenv import load_dotenv

# Configura encoding para UTF-8 no Windows para evitar erros de emoji
if sys.platform == 'win32':
    import codecs
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

# Carrega variaveis de ambiente
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TEST_CHANNEL_ID = int(os.getenv("TEST_CHANNEL_ID", "0"))

# Cria bot de teste
intents = discord.Intents.default()
intents.message_content = True
test_bot = commands.Bot(command_prefix="!", intents=intents)

# Lista de testes a executar
TESTS = [
    {"name": "Leaderboard - Menu", "command": "!top", "expected": "LEADERBOARD"},
    {"name": "Leaderboard - Kills", "command": "!top kills", "expected": "MATADORES"},
    {"name": "Leaderboard - K/D", "command": "!top kd", "expected": "K/D RATIO"},
    {"name": "Leaderboard - Coins", "command": "!top coins", "expected": "MAIS RICOS"},
    {"name": "Spawner - Lista", "command": "!spawn_list", "expected": ["SPAWNS", "spawn pendente"]},
    {"name": "Gameplay - Menu", "command": "!gameplay", "expected": "Gameplay"},
    {"name": "Gameplay - Ajuda", "command": "!gameplay ajuda", "expected": "EDITOR"},
    {"name": "Gameplay - View", "command": "!gameplay view", "expected": "CATEGORIAS"},
    {"name": "Gameplay - Buffs", "command": "!gameplay view Buffs", "expected": "Buffs"},
]

test_results = []

@test_bot.event
async def on_ready():
    print("\n" + "="*60)
    print(f"BOT CONECTADO: {test_bot.user}")
    print("="*60 + "\n")
    
    if TEST_CHANNEL_ID == 0:
        print("[ERRO] TEST_CHANNEL_ID nao configurado!")
        await test_bot.close()
        return
    
    channel = test_bot.get_channel(TEST_CHANNEL_ID)
    if not channel:
        print(f"[ERRO] Canal {TEST_CHANNEL_ID} nao encontrado!")
        await test_bot.close()
        return
    
    print(f"[OK] Canal encontrado: {channel.id}\n")
    print("="*60)
    print("INICIANDO TESTES")
    print("="*60 + "\n")
    
    for i, test in enumerate(TESTS, 1):
        print(f"[{i}/{len(TESTS)}] {test['name']}: {test['command']}")
        
        try:
            await channel.send(test['command'])
            
            def check(m):
                return m.author != test_bot.user and m.channel == channel
            
            try:
                response = await test_bot.wait_for('message', timeout=5.0, check=check)
                
                expected = test['expected']
                if isinstance(expected, list):
                    found = any(exp in response.content or 
                               (response.embeds and exp in str(response.embeds[0].to_dict())) 
                               for exp in expected)
                else:
                    found = (expected in response.content or 
                            (response.embeds and expected in str(response.embeds[0].to_dict())))
                
                if found:
                    print(f"  [OK] PASSOU")
                    test_results.append({"test": test['name'], "status": "OK"})
                else:
                    print(f"  [!] AVISO - Texto nao encontrado")
                    test_results.append({"test": test['name'], "status": "AVISO"})
                
            except asyncio.TimeoutError:
                print(f"  [X] TIMEOUT")
                test_results.append({"test": test['name'], "status": "TIMEOUT"})
            
        except Exception as e:
            print(f"  [X] ERRO: {e}")
            test_results.append({"test": test['name'], "status": "ERRO"})
        
        await asyncio.sleep(2)
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    
    passed = sum(1 for r in test_results if r['status'] == 'OK')
    warnings = sum(1 for r in test_results if r['status'] == 'AVISO')
    failed = sum(1 for r in test_results if r['status'] in ['TIMEOUT', 'ERRO'])
    
    print(f"\n[OK] Passou: {passed}/{len(TESTS)}")
    print(f"[!] Avisos: {warnings}/{len(TESTS)}")
    print(f"[X] Falhou: {failed}/{len(TESTS)}\n")
    
    for r in test_results:
        prefix = "[OK]" if r['status'] == 'OK' else "[!]" if r['status'] == 'AVISO' else "[X]"
        print(f"{prefix} {r['test']}")
    
    summary_embed = discord.Embed(
        title="RESUMO DOS TESTES",
        description="Novas Funcionalidades",
        color=discord.Color.green() if failed == 0 else discord.Color.orange()
    )
    
    summary_embed.add_field(name="Passou", value=str(passed), inline=True)
    summary_embed.add_field(name="Avisos", value=str(warnings), inline=True)
    summary_embed.add_field(name="Falhou", value=str(failed), inline=True)
    
    await channel.send(embed=summary_embed)
    
    print("\n" + "="*60)
    print("TESTES CONCLUIDOS!")
    print("="*60 + "\n")
    
    await test_bot.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTE - NOVAS FUNCIONALIDADES")
    print("="*60)
    print("\nIniciando em 3 segundos...\n")
    
    import time
    time.sleep(3)
    
    try:
        test_bot.run(TOKEN)
    except KeyboardInterrupt:
        print("\nTestes interrompidos")
    except Exception as e:
        print(f"\nErro: {e}")
