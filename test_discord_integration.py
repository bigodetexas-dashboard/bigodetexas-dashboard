import discord
import asyncio
import os
import json
from dotenv import load_dotenv
from killfeed import parse_log_line

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CONFIG_FILE = "config.json"

def load_json(filename):
    if not os.path.exists(filename): return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

async def main():
    print("--- Iniciando Teste de Integração com Discord ---")
    
    if not TOKEN:
        print("❌ Erro: DISCORD_TOKEN não encontrado no .env")
        return

    config = load_json(CONFIG_FILE)
    channel_id = config.get("killfeed_channel")
    
    if not channel_id:
        print("❌ Erro: killfeed_channel não configurado no config.json")
        return

    print(f"Token presente. ID do Canal: {channel_id}")

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"✅ Logado como {client.user}")
        
        channel = client.get_channel(channel_id)
        if not channel:
            print(f"❌ Erro: Canal {channel_id} não encontrado ou sem permissão.")
            await client.close()
            return

        print(f"✅ Canal acessível: {channel.name}")

        # Test Line
        test_line = '2025-11-24 12:00:00 INFO Player "Survivor" (12345) killed by Player "Bandit" (67890) with M4A1 <1000.0, 200.0, 3000.0>'
        print(f"Processando linha de teste: {test_line}")

        embed = await parse_log_line(test_line)
        
        if embed:
            print("✅ Embed gerado com sucesso.")
            try:
                await channel.send(embed=embed)
                print("✅ SUCESSO: Embed enviado para o Discord!")
            except discord.Forbidden:
                print("❌ Erro: Permissão negada (Forbidden). Verifique as permissões do bot no canal.")
            except Exception as e:
                print(f"❌ Erro ao enviar: {e}")
        else:
            print("❌ Erro: parse_log_line retornou None (falha na lógica).")

        await client.close()

    try:
        await client.start(TOKEN)
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

if __name__ == "__main__":
    asyncio.run(main())
