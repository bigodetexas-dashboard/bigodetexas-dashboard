import asyncio
import aiohttp
import datetime
from datetime import timedelta
import time

# --- CONFIGURAÇÃO ---
# ⚠️ VOCÊ PRECISA COLOCAR SEU TOKEN AQUI
# Gere em: https://server.nitrado.net/usa/pages/developer
NITRADO_TOKEN = "FumKsv7MGrfa6zG0bxY7C3kqigM0zloo1FlQH3JqLeQ7siSoqw8DvLbAojdYqr_iheYUt-RYGcTC8rIHfoL662exac8yR8It21vS" 

# ID inferido do seu usuário (ni3622181_1)
SERVICE_ID = "3622181" 

async def restart_server():
    """Envia comando de restart para a API da Nitrado."""
    if NITRADO_TOKEN == "SEU_TOKEN_AQUI":
        print("❌ ERRO: Você precisa configurar o NITRADO_TOKEN no arquivo!")
        return False

    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/restart"
    headers = {"Authorization": f"Bearer {NITRADO_TOKEN}"}
    
    print(f"Tentando reiniciar servidor ID {SERVICE_ID}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        print(f"[{datetime.datetime.now()}] ✅ SUCESSO: Servidor reiniciando!")
                        return True
                    else:
                        print(f"[{datetime.datetime.now()}] ⚠️ AVISO: API respondeu, mas houve erro: {data}")
                else:
                    print(f"[{datetime.datetime.now()}] ❌ ERRO API: {response.status} - {await response.text()}")
                    return False
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

async def scheduler():
    print(f"\n=== BOT DE RESTART NITRADO ===")
    print(f"Service ID: {SERVICE_ID}")
    print(f"Token Configurado: {'NÃO' if NITRADO_TOKEN == 'SEU_TOKEN_AQUI' else 'SIM'}")
    print(f"Aguardando horários de Raid (Sáb/Dom - 21:00 e 23:00)...\n")
    
    while True:
        # Horário de Brasília (UTC-3)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        br_time = utc_now - timedelta(hours=3)
        
        weekday = br_time.weekday() # 5=Sábado, 6=Domingo
        hour = br_time.hour
        minute = br_time.minute
        second = br_time.second
        
        # Formata hora para display
        time_str = br_time.strftime("%H:%M:%S")
        print(f"\rHorário Atual: {time_str} | Dia: {weekday} (5=Sáb, 6=Dom)", end="")
        
        # Apenas Sábado e Domingo
        if weekday in [5, 6]:
            # 21:00 -> Restart para Ativar Raid
            if hour == 21 and minute == 0 and second < 5:
                print("\n\n⏰ HORA DO RAID! Reiniciando servidor...")
                await restart_server()
                await asyncio.sleep(60) # Espera 1 minuto para não spammar
                
            # 23:00 -> Restart para Desativar Raid
            if hour == 23 and minute == 0 and second < 5:
                print("\n\n⏰ FIM DO RAID! Reiniciando servidor...")
                await restart_server()
                await asyncio.sleep(60)
                
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(scheduler())
    except KeyboardInterrupt:
        print("\nBot encerrado.")
