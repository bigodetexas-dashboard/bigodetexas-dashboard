import discord
import asyncio
import os
import json
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Tenta carregar o canal do config.json
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        CHANNEL_ID = int(config.get("killfeed_channel", 1384336968736837712))
except:
    CHANNEL_ID = 1384336968736837712

print(f"Usando Token: {TOKEN[:5]}... e Canal: {CHANNEL_ID}")

class SimulationClient(discord.Client):
    async def on_ready(self):
        print(f'Logado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if not channel:
            print("Canal não encontrado!")
            await self.close()
            return

        print("--- INICIANDO SIMULAÇÃO DE TESTES ---")
        await channel.send("🧪 **INICIANDO BATERIA DE TESTES DE CONFIGURAÇÃO** 🧪")
        await asyncio.sleep(1)

        # 1. TESTE: BANIMENTO POR DUPLICAÇÃO
        print("1. Simulando Duplicação...")
        embed_dup = discord.Embed(title="🚫 BANIMENTO AUTOMÁTICO", color=discord.Color.red())
        embed_dup.description = "O jogador **DupadorTeste** foi banido por Duplicação de Item (Duping)!\nItem: M4A1 (ID: 12345)"
        embed_dup.set_footer(text="BigodeTexas • Sistema de Segurança")
        await channel.send(embed=embed_dup)
        await asyncio.sleep(2)

        # 2. TESTE: RECOMPENSA POR TEMPO ONLINE
        print("2. Simulando Recompensa Online...")
        embed_reward = discord.Embed(description="💸 **SALÁRIO RECEBIDO!**\n**SobreviventeFiel** jogou por 2h 30m e ganhou **2500 DZ Coins**.", color=discord.Color.green())
        embed_reward.set_footer(text="BigodeTexas • Economia")
        await channel.send(embed=embed_reward)
        await asyncio.sleep(2)

        # 3. TESTE: BANIMENTO POR CONSTRUÇÃO ILEGAL
        print("3. Simulando Construção Ilegal...")
        embed_build = discord.Embed(title="🚫 BANIMENTO AUTOMÁTICO", color=discord.Color.dark_red())
        embed_build.description = "O jogador **ConstrutorGlitch** foi banido por plantar GardenPlot (Proibido)!"
        embed_build.set_footer(text="BigodeTexas • Anti-Glitch")
        await channel.send(embed=embed_build)
        await asyncio.sleep(2)

        # 4. TESTE: ALARME DE BASE
        print("4. Simulando Alarme de Base...")
        embed_alarm = discord.Embed(title="🚨 ALARME DE BASE DISPARADO!", color=discord.Color.red())
        embed_alarm.description = "**Atividade detectada na base BaseAlpha!**\n\n💀 **Evento:** Morte de Invasor\n🔫 **Assassino:** Sentinela\n📍 **Local:** Perto de Vybor (300m)\n📏 **Distância do Centro:** 50.0m"
        embed_alarm.set_footer(text="Sistema de Segurança BigodeTexas")
        await channel.send(embed=embed_alarm)
        
        await channel.send("✅ **FIM DA SIMULAÇÃO**")
        print("Testes concluídos.")
        await self.close()

intents = discord.Intents.default()
client = SimulationClient(intents=intents)
client.run(TOKEN)
