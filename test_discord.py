import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1441892129591922782/20eO0Z6wurnlD47-BgQ7yP5ePt0mK-2pXF8iQUuLfllqkPyVGdkVuSdTr6vd5sBEWCz2"

message = "💀 **Teste** matou **Sobrevivente**\n🔫 Arma: **M4A1**\n📍 Local: `<1500, 200, 3000>`"

data = {
    "content": message,
    "username": "DayZ Killfeed",
    "avatar_url": "https://i.imgur.com/4M34hi2.png"
}

print("Enviando teste para o Discord...")
try:
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Mensagem de teste enviada com sucesso!")
    else:
        print(f"Erro ao enviar: {response.status_code}")
except Exception as e:
    print(f"Erro: {e}")
