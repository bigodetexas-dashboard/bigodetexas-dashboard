import discord
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("❌ Erro: DISCORD_TOKEN não encontrado no .env")
    exit(1)

CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    config = load_config()
    
    channels_to_test = {
        "Salary": config.get("salary_channel"),
        "Ban": config.get("ban_channel"),
        "Alarm": config.get("alarm_channel")
    }
    
    for name, channel_id in channels_to_test.items():
        if not channel_id:
            print(f"❌ {name} Channel ID not found in config!")
            continue
            
        try:
            channel = client.get_channel(channel_id)
            if not channel:
                # Tenta fetch se get retornar None (cache vazio)
                channel = await client.fetch_channel(channel_id)
            
            if channel:
                await channel.send(f"✅ Teste de verificação: Canal de **{name}** funcionando!")
                print(f"[OK] {name} Channel ({channel_id}): OK")
            else:
                print(f"[ERROR] {name} Channel ({channel_id}): Not Found (None)")
        except Exception as e:
            print(f"[ERROR] {name} Channel ({channel_id}): Error - {e}")
            
    await client.close()

client.run(TOKEN)
