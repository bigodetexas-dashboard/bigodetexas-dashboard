import discord
import asyncio
import os
from dotenv import load_dotenv
from killfeed import parse_log_line
import json

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Configuration
CONFIG_FILE = "config.json"

def load_json(filename):
    if not os.path.exists(filename): return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

async def main():
    if not TOKEN:
        print("❌ Erro: DISCORD_TOKEN não encontrado no .env")
        return

    config = load_json(CONFIG_FILE)
    channel_id = config.get("killfeed_channel")
    
    if not channel_id:
        print("❌ Erro: killfeed_channel não configurado no config.json")
        return

    print(f"Token encontrado. Tentando conectar...")
    print(f"Canal Alvo ID: {channel_id}")

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"✅ Logado como {client.user}")
        
        channel = client.get_channel(channel_id)
        if not channel:
            print(f"❌ Erro: Não foi possível encontrar o canal {channel_id}. Verifique se o bot está no servidor e tem permissão de ver o canal.")
            await client.close()
            return

        print(f"✅ Canal encontrado: {channel.name}")

        # Simula uma linha de log
        test_line = '2025-11-24 12:00:00 INFO Player "Survivor" (12345) killed by Player "Bandit" (67890) with M4A1 <1000.0, 200.0, 3000.0>'
        print(f"Simulando linha: {test_line}")

        embed = await parse_log_line(test_line)
        
        if embed:
            try:
                await channel.send(embed=embed)
                print("✅ Sucesso! Embed enviado para o canal.")
            except discord.Forbidden:
                print("❌ Erro: Permissão negada para enviar mensagem no canal.")
            except Exception as e:
                print(f"❌ Erro ao enviar mensagem: {e}")
        else:
            print("❌ Erro: parse_log_line retornou None.")

        await client.close()

    try:
        await client.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Erro: Token do Discord inválido.")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    asyncio.run(main())
